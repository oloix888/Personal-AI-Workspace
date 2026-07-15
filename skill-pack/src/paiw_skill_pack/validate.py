from __future__ import annotations

from pathlib import Path
import re

import yaml

from .frontmatter import FrontmatterError, parse_skill_frontmatter

LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")
REQUIRED_OPENAI_INTERFACE_FIELDS = (
    "display_name",
    "short_description",
    "brand_color",
    "default_prompt",
)


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

    for markdown in sorted(root.rglob("*.md")):
        text = markdown.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            if "://" in target or target.startswith("mailto:") or target.startswith("#"):
                continue
            clean = target.split("#", 1)[0]
            resolved = (markdown.parent / clean).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"{markdown.relative_to(root)} link escapes skill root: {target}")
                continue
            if clean and not resolved.exists():
                errors.append(f"{markdown.relative_to(root)} has broken link: {target}")
    return errors


def assert_valid_skill(root: Path) -> None:
    errors = validate_skill_root(root)
    if errors:
        raise ValueError("\n".join(errors))
