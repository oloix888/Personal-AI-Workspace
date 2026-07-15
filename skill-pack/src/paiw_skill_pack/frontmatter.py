from __future__ import annotations

import re
from typing import Any

import yaml


class FrontmatterError(ValueError):
    pass


def parse_skill_frontmatter(text: str) -> dict[str, Any]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        raise FrontmatterError("SKILL.md must start with YAML frontmatter")
    payload = yaml.safe_load(match.group(1))
    if not isinstance(payload, dict):
        raise FrontmatterError("frontmatter must be a mapping")
    name = payload.get("name")
    description = payload.get("description")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9-]+", name):
        raise FrontmatterError("name must use lowercase letters, digits, and hyphens")
    if not isinstance(description, str) or not description.startswith("Use when"):
        raise FrontmatterError("description must begin with 'Use when'")
    if "Do not use" not in description:
        raise FrontmatterError("description must include a negative activation boundary")
    return payload
