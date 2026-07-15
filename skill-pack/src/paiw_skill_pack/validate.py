from __future__ import annotations

from pathlib import Path
import re

from .frontmatter import FrontmatterError, parse_skill_frontmatter

LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")


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
    if not (root / "agents/openai.yaml").is_file():
        errors.append("missing agents/openai.yaml")
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
