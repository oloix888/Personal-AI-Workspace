#!/usr/bin/env python3
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]

required = [
    "README.md",
    "LICENSE",
    "NOTICE",
    "AUTHORS.md",
    "ATTRIBUTION.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "docs/index.html",
    "docs/install.html",
    "docs/what-it-does.html",
    "docs/styles.css",
    "docs/site-v2.css",
    "docs/app.js",
    "docs/wizard.js",
    "docs/assets/required-chatgpt-codex.svg",
    "docs/assets/required-notion.svg",
    "release-index.json",
]

for relative_path in required:
    assert (root / relative_path).is_file(), f"Missing {relative_path}"

index = (root / "docs/index.html").read_text(encoding="utf-8")
what_it_does = (root / "docs/what-it-does.html").read_text(encoding="utf-8")
install = (root / "docs/install.html").read_text(encoding="utf-8")
wizard = (root / "docs/wizard.js").read_text(encoding="utf-8")
app = (root / "docs/app.js").read_text(encoding="utf-8")
styles = (root / "docs/styles.css").read_text(encoding="utf-8")
site_v2 = (root / "docs/site-v2.css").read_text(encoding="utf-8")

for token in [
    "Personal AI Workspace",
    "v1.5.1",
    "Michał Poliński",
    "Emma ✨",
    "Apache-2.0",
]:
    assert token in index, token

assert 'lang="en"' in index
assert "#fff" in styles.lower()

# Installation-wizard regressions.
choice_css = re.search(r"\.wizard-choice\{([^}]+)\}", site_v2)
assert choice_css, "Missing site-v2 wizard choice style"
assert "grid-template-columns:28px minmax(0,1fr)" in choice_css.group(1)
assert ".wizard-choice strong,.wizard-choice span{grid-column:2" in site_v2

connect_notion = wizard.split("'connect-notion':", 1)[1].split("'connection-help':", 1)[0]
assert "notDoneDisabled: true" in connect_notion
assert "This connection is mandatory" in connect_notion

# Public site must not depend on unreliable remote brand images after JS initializes.
for token in [
    "localizeBrandMarks",
    "assets/required-chatgpt-codex.svg",
    "assets/required-notion.svg",
    "'LinkedIn Ads': ['linkedin-ads', 'in']",
    "'Contacts': ['contacts', 'C']",
    "'Adobe': ['adobe', 'A']",
]:
    assert token in app, token

# Benefits copy must describe the actual proactive workflow without inventing background work.
for page in [index, what_it_does]:
    assert "Why should I use it?" in page
    assert "structured knowledge base" in page
    assert "scheduled task or" in page
    assert "mental-health" in page
    assert "external" in page

assert "What will I gain?" not in index
assert "What do I gain?" not in what_it_does
assert "Notion" in install and "ChatGPT or Codex" in install

print("Repository structure, public site, wizard and benefits copy validated")
