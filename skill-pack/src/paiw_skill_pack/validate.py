from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import yaml

from .frontmatter import FrontmatterError, parse_skill_frontmatter

INLINE_LINK_RE = re.compile(
    r"\[[^\]\n]+\]\(\s*(?:<(?P<angle>[^>\n]+)>|(?P<bare>[^()\s]+))"
    r"(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^()\n]*\)))?\s*\)",
)
REFERENCE_DEFINITION_RE = re.compile(
    r"^[ \t]{0,3}\[[^\]\n]+\]:[ \t]*(?:<(?P<angle>[^>\n]*)>|(?P<bare>\S+))",
    re.MULTILINE,
)
HTML_LINK_ATTRIBUTES = frozenset(
    {
        "action",
        "background",
        "cite",
        "data",
        "formaction",
        "href",
        "poster",
        "src",
        "srcset",
        "xlink:href",
    }
)
REQUIRED_OPENAI_INTERFACE_FIELDS = (
    "display_name",
    "short_description",
    "brand_color",
    "default_prompt",
)
CANONICAL_LEGAL_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_LEGAL_FILENAMES = ("LICENSE", "NOTICE")
REQUIRED_LEGAL_MARKERS = {
    "LICENSE": ("Apache License", "Version 2.0"),
    "NOTICE": ("Personal AI Workspace", "Apache License, Version 2.0"),
}
WINDOWS_DRIVE_PATH_RE = re.compile(r"^[A-Za-z]:[\\/]")


class _HTMLLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect(attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect(attrs)

    def _collect(self, attrs: list[tuple[str, str | None]]) -> None:
        for attribute, value in attrs:
            if value is None or attribute.lower() not in HTML_LINK_ATTRIBUTES:
                continue
            if attribute.lower() == "srcset":
                self.targets.extend(
                    candidate.strip().split(maxsplit=1)[0]
                    for candidate in value.split(",")
                    if candidate.strip()
                )
            else:
                self.targets.append(value)


def _markdown_link_targets(text: str) -> list[str]:
    targets: list[str] = []
    for expression in (INLINE_LINK_RE, REFERENCE_DEFINITION_RE):
        for match in expression.finditer(text):
            targets.append(match.group("angle") or match.group("bare"))
    return targets


def _html_link_targets(text: str) -> list[str]:
    parser = _HTMLLinkParser()
    parser.feed(text)
    parser.close()
    return parser.targets


def _validate_link_target(root: Path, markdown: Path, target: str) -> str | None:
    target = target.strip()
    if not target or target.startswith("#"):
        return None

    parsed = urlsplit(target)
    if (
        parsed.scheme.lower() == "file"
        or target.startswith(("//", "\\\\"))
        or WINDOWS_DRIVE_PATH_RE.match(target)
    ):
        return (
            f"{markdown.relative_to(root)} local or host filesystem link is not allowed: "
            f"{target}"
        )
    if parsed.scheme or parsed.netloc:
        return None
    clean = unquote(parsed.path)
    if not clean:
        return None

    resolved = (markdown.parent / clean).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return f"{markdown.relative_to(root)} link escapes skill root: {target}"
    if not resolved.exists():
        return f"{markdown.relative_to(root)} has broken link: {target}"
    return None


def _validate_openai_metadata(path: Path) -> list[str]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return ["agents/openai.yaml contains invalid YAML"]

    if not isinstance(payload, dict):
        return ["agents/openai.yaml must contain a mapping"]

    errors: list[str] = []
    interface = payload.get("interface")
    if not isinstance(interface, dict):
        errors.append("agents/openai.yaml interface must be a mapping")
    else:
        for field in REQUIRED_OPENAI_INTERFACE_FIELDS:
            value = interface.get(field)
            if value is None:
                errors.append(f"agents/openai.yaml interface missing required field: {field}")
            elif not isinstance(value, str) or not value.strip():
                errors.append(
                    f"agents/openai.yaml interface field must be a non-empty string: {field}"
                )

    policy = payload.get("policy")
    if not isinstance(policy, dict):
        errors.append("agents/openai.yaml policy must be a mapping")
    elif not isinstance(policy.get("allow_implicit_invocation"), bool):
        errors.append(
            "agents/openai.yaml policy.allow_implicit_invocation must be a boolean"
        )
    return errors


def _validate_legal_files(root: Path) -> list[str]:
    errors: list[str] = []
    for filename in CANONICAL_LEGAL_FILENAMES:
        path = root / filename
        if not path.is_file():
            errors.append(f"missing {filename}")
            continue
        try:
            actual = path.read_bytes()
        except OSError:
            errors.append(f"unable to read {filename}")
            continue
        try:
            contents = actual.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{filename} must be UTF-8 text")
            continue
        if not all(marker in contents for marker in REQUIRED_LEGAL_MARKERS[filename]):
            if filename == "NOTICE":
                errors.append("NOTICE missing required attribution")
            else:
                errors.append("LICENSE missing Apache-2.0 text")
        canonical_path = CANONICAL_LEGAL_ROOT / filename
        try:
            canonical = canonical_path.read_bytes()
        except OSError:
            errors.append(f"unable to read canonical {filename}")
            continue
        if actual != canonical:
            errors.append(f"{filename} does not match canonical repository legal file")
    return errors


def validate_skill_root(root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return ["missing SKILL.md"]
    try:
        metadata = parse_skill_frontmatter(skill_md.read_text(encoding="utf-8"))
    except FrontmatterError as exc:
        errors.append(str(exc))
        metadata = {}
    if metadata.get("name") and metadata["name"] != root.name:
        errors.append("frontmatter name must match skill directory")
    openai_metadata = root / "agents/openai.yaml"
    if not openai_metadata.is_file():
        errors.append("missing agents/openai.yaml")
    else:
        errors.extend(_validate_openai_metadata(openai_metadata))
    if not (root / "VERSION").is_file():
        errors.append("missing VERSION")
    errors.extend(_validate_legal_files(root))

    for markdown in sorted(root.rglob("*.md")):
        text = markdown.read_text(encoding="utf-8")
        for target in _markdown_link_targets(text) + _html_link_targets(text):
            error = _validate_link_target(root, markdown, target)
            if error:
                errors.append(error)
    return errors


def assert_valid_skill(root: Path) -> None:
    errors = validate_skill_root(root)
    if errors:
        raise ValueError("\n".join(errors))
