# Skill Pack Integration, Documentation, Prerelease, and Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the two standalone Personal AI Workspace skills into the public repository, produce verifiable distribution artifacts and documentation, prepare an explicitly gated prerelease, and collect pilot evidence before any stable release.

**Architecture:** Consume the deterministic builder and validators from the foundation plan plus the completed installer-upgrader and context-bootstrap source trees. A repository-level orchestrator builds two standalone ZIPs and one combined Skill Pack ZIP, validates public safety, emits checksums, and exposes artifacts through CI; documentation and GitHub Pages keep the Markdown creator as the universal fallback. Publication is separated from building by a manually confirmed prerelease workflow, while stability is decided from structured pilot reports.

**Tech Stack:** Python 3.11+, pytest, JSON Schema, GitHub Actions, GitHub Releases, Markdown, static GitHub Pages HTML/CSS/JavaScript.

## Global Constraints

- Implement only after the foundation, installer-upgrader, and context-bootstrap plans are merged and passing.
- The initial Skill Pack version is exactly `0.1.0-beta.1` and targets Personal AI Workspace framework `1.5.1`.
- Produce two separately installable skill ZIPs plus one combined convenience ZIP and `SHA256SUMS.txt`.
- The Markdown creator v1.5.1 remains the recommended universal fallback during the beta.
- Public documentation is English-only.
- No public package, fixture, artifact, workflow log, or pilot report may contain private Emma Workspace identifiers, private accounts, private repositories, contacts, Gmail content, or secrets.
- Apache-2.0, NOTICE, the original project name, and creator attribution remain in every distributed package.
- Active Google Tasks paths are prohibited.
- No prerelease or stable release is published without explicit owner approval for that exact version.
- No live private Workspace migration is part of this plan.
- ChatGPT and Codex compatibility claims require recorded evidence; unsupported surfaces remain unclaimed.
- A final persistent artifact generated for a private Workspace follows that Workspace's verified Google Drive upload policy, but public GitHub release artifacts are stored and verified through GitHub Releases.
- Every task follows TDD and ends with a focused commit.

---

## File Map

```text
skill-pack/
├── manifest.json
├── pilots/
│   ├── README.md
│   ├── pilot-report.schema.json
│   └── report-template.json
├── scripts/
│   ├── build_all.py
│   ├── release_candidate_audit.py
│   ├── summarize_pilots.py
│   └── validate_manual_evidence.py
└── tests/
    ├── fixtures/manual-evidence/
    │   ├── valid-chatgpt.json
    │   └── invalid-missing-evidence.json
    ├── fixtures/pilots/
    │   ├── fresh-install.json
    │   ├── supported-upgrade.json
    │   └── context-bootstrap.json
    ├── test_build_all.py
    ├── test_docs.py
    ├── test_manual_evidence.py
    ├── test_release_candidate_audit.py
    └── test_summarize_pilots.py

docs/
├── INSTALLATION.md
├── skills.html
├── pilot.html
├── index.html
└── styles.css

.github/
├── ISSUE_TEMPLATE/skill-pilot-feedback.yml
└── workflows/
    ├── build-skill-pack.yml
    └── publish-skill-pack-prerelease.yml

releases/
└── skill-pack-v0.1.0-beta.1.md

README.md
SUPPORT.md
ROADMAP.md
```

---

### Task 1: Build all standalone and combined distribution artifacts

**Files:**
- Create: `skill-pack/manifest.json`
- Create: `skill-pack/scripts/build_all.py`
- Create: `skill-pack/tests/test_build_all.py`

**Interfaces:**
- Consumes: `paiw_skill_pack.build.build_skill`, `paiw_skill_pack.validate.assert_valid_skill`, `paiw_skill_pack.scanner.assert_public_safe`, `paiw_skill_pack.package.create_deterministic_zip`, and `paiw_skill_pack.package.write_checksums` from the foundation plan.
- Produces: `build_all(repo_root: Path, output_root: Path, version: str) -> dict[str, Path]`.
- Produces exact files:
  - `Personal-AI-Workspace-Installer-Upgrader-0.1.0-beta.1.zip`
  - `Personal-AI-Workspace-Context-Bootstrap-0.1.0-beta.1.zip`
  - `Personal-AI-Workspace-Skill-Pack-0.1.0-beta.1.zip`
  - `SHA256SUMS.txt`

- [ ] **Step 1: Write the failing combined-build test**

```python
# skill-pack/tests/test_build_all.py
from pathlib import Path
import zipfile

from skill_pack.scripts.build_all import build_all

ROOT = Path(__file__).resolve().parents[2]


def test_build_all_produces_three_reproducible_archives_and_checksums(tmp_path: Path) -> None:
    first = build_all(ROOT, tmp_path / "first", "0.1.0-beta.1")
    second = build_all(ROOT, tmp_path / "second", "0.1.0-beta.1")

    expected = {
        "installer": "Personal-AI-Workspace-Installer-Upgrader-0.1.0-beta.1.zip",
        "bootstrap": "Personal-AI-Workspace-Context-Bootstrap-0.1.0-beta.1.zip",
        "combined": "Personal-AI-Workspace-Skill-Pack-0.1.0-beta.1.zip",
        "checksums": "SHA256SUMS.txt",
    }
    assert {key: value.name for key, value in first.items()} == expected
    assert {key: value.read_bytes() for key, value in first.items()} == {
        key: value.read_bytes() for key, value in second.items()
    }

    with zipfile.ZipFile(first["combined"]) as archive:
        names = set(archive.namelist())
        assert "Personal-AI-Workspace-Installer-Upgrader-0.1.0-beta.1.zip" in names
        assert "Personal-AI-Workspace-Context-Bootstrap-0.1.0-beta.1.zip" in names
        assert "manifest.json" in names
        assert "NOTICE" in names
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_build_all.py -v
```

Expected: import failure because `skill_pack.scripts.build_all` does not exist.

- [ ] **Step 3: Add the public Skill Pack manifest**

```json
// skill-pack/manifest.json
{
  "project": "Personal AI Workspace",
  "skill_pack_version": "0.1.0-beta.1",
  "framework_target": "1.5.1",
  "release_channel": "beta",
  "skills": [
    {
      "name": "personal-ai-workspace-installer-upgrader",
      "archive": "Personal-AI-Workspace-Installer-Upgrader-0.1.0-beta.1.zip",
      "implicit_invocation": false
    },
    {
      "name": "personal-ai-workspace-context-bootstrap",
      "archive": "Personal-AI-Workspace-Context-Bootstrap-0.1.0-beta.1.zip",
      "implicit_invocation": true
    }
  ],
  "fallback": {
    "type": "markdown-creator",
    "version": "1.5.1",
    "url": "https://github.com/oloix888/Personal-AI-Workspace/releases/latest"
  },
  "license": "Apache-2.0",
  "notice_required": true
}
```

- [ ] **Step 4: Implement the build orchestrator**

```python
# skill-pack/scripts/build_all.py
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
from typing import Final

from paiw_skill_pack.build import build_skill
from paiw_skill_pack.package import create_deterministic_zip, write_checksums
from paiw_skill_pack.scanner import assert_public_safe
from paiw_skill_pack.validate import assert_valid_skill

PUBLIC_EMAIL: Final = "michal24749@gmail.com"
SKILLS: Final = {
    "installer": (
        "personal-ai-workspace-installer-upgrader",
        "Personal-AI-Workspace-Installer-Upgrader-{version}.zip",
    ),
    "bootstrap": (
        "personal-ai-workspace-context-bootstrap",
        "Personal-AI-Workspace-Context-Bootstrap-{version}.zip",
    ),
}


def build_all(repo_root: Path, output_root: Path, version: str) -> dict[str, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    build_root = output_root / "built-skills"
    if build_root.exists():
        shutil.rmtree(build_root)
    build_root.mkdir(parents=True)

    artifacts: dict[str, Path] = {}
    for key, (skill_name, archive_pattern) in SKILLS.items():
        built = build_skill(
            repo_root / "skills" / skill_name,
            repo_root / "skills" / "_shared",
            build_root,
            version,
        )
        assert_valid_skill(built)
        assert_public_safe(built, PUBLIC_EMAIL)
        archive = output_root / archive_pattern.format(version=version)
        artifacts[key] = create_deterministic_zip(built, archive)

    combined_root = output_root / "combined"
    if combined_root.exists():
        shutil.rmtree(combined_root)
    combined_root.mkdir()
    for key in ("installer", "bootstrap"):
        shutil.copy2(artifacts[key], combined_root / artifacts[key].name)
    shutil.copy2(repo_root / "skill-pack" / "manifest.json", combined_root / "manifest.json")
    shutil.copy2(repo_root / "LICENSE", combined_root / "LICENSE")
    shutil.copy2(repo_root / "NOTICE", combined_root / "NOTICE")
    shutil.copy2(repo_root / "ATTRIBUTION.md", combined_root / "ATTRIBUTION.md")

    combined = output_root / f"Personal-AI-Workspace-Skill-Pack-{version}.zip"
    artifacts["combined"] = create_deterministic_zip(combined_root, combined)
    artifacts["checksums"] = write_checksums(
        [artifacts["installer"], artifacts["bootstrap"], artifacts["combined"]],
        output_root / "SHA256SUMS.txt",
    )
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Personal AI Workspace Skill Pack artifacts")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("skill-pack/dist"))
    parser.add_argument("--version", default="0.1.0-beta.1")
    args = parser.parse_args()
    artifacts = build_all(args.repo_root.resolve(), args.output.resolve(), args.version)
    print(json.dumps({key: str(path) for key, path in artifacts.items()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Create package markers so the test import is stable:

```python
# skill-pack/__init__.py
"""Repository-local Skill Pack orchestration package."""
```

```python
# skill-pack/scripts/__init__.py
"""Command-line entry points for Skill Pack builds and release checks."""
```

- [ ] **Step 5: Run the combined-build test**

```bash
python -m pytest skill-pack/tests/test_build_all.py -v
```

Expected: `1 passed`.

- [ ] **Step 6: Run the actual local build and inspect names**

```bash
python skill-pack/scripts/build_all.py --output skill-pack/dist --version 0.1.0-beta.1
ls -1 skill-pack/dist
```

Expected output includes exactly the three ZIP names and `SHA256SUMS.txt`.

- [ ] **Step 7: Commit**

```bash
git add skill-pack/manifest.json skill-pack/__init__.py skill-pack/scripts/__init__.py skill-pack/scripts/build_all.py skill-pack/tests/test_build_all.py
git commit -m "feat: build complete Skill Pack distributions"
```

---

### Task 2: Publish a canonical English installation guide

**Files:**
- Create: `docs/INSTALLATION.md`
- Create: `skill-pack/tests/test_docs.py`
- Modify: `README.md` after the existing `Start here` section
- Modify: `SUPPORT.md` installation-help section

**Interfaces:**
- Produces: one stable repository URL for fresh installation, upgrade selection, ChatGPT skill upload, Codex installation, fallback creator usage, and connector prerequisites.

- [ ] **Step 1: Write the failing documentation test**

```python
# skill-pack/tests/test_docs.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_installation_guide_covers_all_supported_paths() -> None:
    text = (ROOT / "docs/INSTALLATION.md").read_text(encoding="utf-8")
    required = [
        "Fresh installation",
        "Upgrade an existing Workspace",
        "Install in ChatGPT Skills",
        "Install in Codex",
        "Markdown creator fallback",
        "Connector capability checklist",
        "Feature & Integration Registry",
        "Do not use Google Tasks",
        "Troubleshooting",
    ]
    for phrase in required:
        assert phrase in text


def test_readme_links_to_canonical_installation_guide() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "[Installation guide](docs/INSTALLATION.md)" in text
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_docs.py -v
```

Expected: file-not-found and missing-link failures.

- [ ] **Step 3: Create the complete installation guide**

```markdown
<!-- docs/INSTALLATION.md -->
# Personal AI Workspace Installation Guide

This guide covers the public Markdown creator and the Personal AI Workspace Skill Pack beta. The Markdown creator remains the universal fallback when Skills are unavailable.

## Choose your path

| Situation | Recommended path |
|---|---|
| No Workspace exists | Fresh installation with the Installer & Upgrader skill or the Markdown creator |
| An older or partial Workspace exists | Run the Installer & Upgrader skill in detection mode, review the migration preview, then approve the exact scope |
| You only need current operational context | Install and invoke Context Bootstrap after your Workspace exists |
| ChatGPT Skills are unavailable | Use the Markdown creator v1.5.1 |

## Connector capability checklist

The installer audits capabilities at runtime. Typical capabilities include Notion read/write, Google Drive upload/readback, GitHub issue read/write, Gmail read/draft/send, Calendar event read/write and Contacts read/write. Missing capabilities are reported; they are never invented.

At minimum, a full Notion installation requires access to the intended Notion account and permission to create and update content. Optional features remain disabled or pending when their connectors are unavailable.

## Fresh installation

1. Download `Personal-AI-Workspace-Installer-Upgrader-0.1.0-beta.1.zip` from the Skill Pack prerelease.
2. Install the skill using the ChatGPT or Codex instructions below.
3. Invoke it explicitly and ask it to inspect your environment for a fresh Personal AI Workspace installation.
4. Review the connector report and complete structural blueprint.
5. Approve only the exact blueprint you want.
6. Allow the skill to create and verify the approved structure.
7. Copy the generated Personalization and project-instruction text.
8. Run the end-to-end Constitution, task, connector and Context Bootstrap tests.

## Upgrade an existing Workspace

1. Do not start a fresh installation blindly.
2. Invoke the Installer & Upgrader skill and ask it to detect the existing installation.
3. Review the detected state: `PARTIAL`, `INSTALLED_SUPPORTED`, `INSTALLED_UNKNOWN` or `DAMAGED`.
4. For a supported version, review the sequential migration path and rollback checkpoint.
5. Approve the exact migration scope.
6. Verify every changed page, module, schema and registry by readback.
7. Do not automatically downgrade an unknown newer version.

## Install in ChatGPT Skills

1. Open the ChatGPT Skills interface on a supported account and surface.
2. Choose the option to upload a skill from your computer.
3. Upload one standalone ZIP at a time:
   - `Personal-AI-Workspace-Installer-Upgrader-0.1.0-beta.1.zip`
   - `Personal-AI-Workspace-Context-Bootstrap-0.1.0-beta.1.zip`
4. Review requested tool access and connector availability.
5. Explicitly invoke Installer & Upgrader for structural work.
6. Use Context Bootstrap at conversation start or when asking for the current operational briefing.

Skills may need separate installation on different ChatGPT surfaces. Do not claim compatibility on a surface until it has been tested and recorded.

## Install in Codex

Extract each standalone skill into the user-global scope:

```text
$HOME/.agents/skills/personal-ai-workspace-installer-upgrader
$HOME/.agents/skills/personal-ai-workspace-context-bootstrap
```

Verify that each directory contains `SKILL.md`, `agents/openai.yaml`, `VERSION`, `references/` and any packaged `scripts/`.

## Markdown creator fallback

Download `Personal-AI-Workspace-Creator-v1.5.1.md`, attach it to a completely new ChatGPT conversation and send:

```text
Follow the instructions in the attached file and guide me through the complete configuration from beginning to end. Do not summarize the file—start with the first stage.
```

## Feature & Integration Registry

The owner chooses which optional features are enabled. Disabled features remain disabled through upgrades. Disabling a feature stops future operations but does not silently delete historical data.

## Task backend

GitHub Issues are the recommended external task backend. Notion Task Outbox is the canonical ledger and fallback. Google Calendar is used only for events and time blocks. **Do not use Google Tasks** as an active backend.

## Final artifact handling

When a private installation generates persistent user-facing files and Google Drive upload is enabled, completion requires upload and readback of the exact final artifact. GitHub release ZIPs and checksums are verified through GitHub Releases.

## Troubleshooting

- Wrong account: stop and connect the intended account before reading or writing personal data.
- Partial connector access: continue only with a truthful reduced scope and list unavailable capabilities.
- Truncated Constitution or connector response: load smaller modules or narrower queries and report incomplete coverage.
- Unknown newer Workspace version: remain read-only and request a reviewed migration specification.
- Drive upload failure: keep the workflow visibly incomplete and provide the local artifact without claiming it is archived.
- Installation rerun creates duplicates: stop, classify the installation as partial or damaged, and use idempotent repair rather than another fresh install.
```

- [ ] **Step 4: Add README and support links**

Add this sentence immediately after the existing quick-start code block in `README.md`:

```markdown
For prerequisites, fresh installation, upgrades, ChatGPT Skills, Codex and troubleshooting, read the [Installation guide](docs/INSTALLATION.md).
```

Add this section to `SUPPORT.md`:

```markdown
## Installation and upgrades

Start with the [canonical installation guide](docs/INSTALLATION.md). When asking for help, include the detected installation state, framework version, Skill Pack version, connector coverage and any readback failure. Remove private data and secrets before posting publicly.
```

- [ ] **Step 5: Run documentation tests**

```bash
python -m pytest skill-pack/tests/test_docs.py -v
```

Expected: `2 passed`.

- [ ] **Step 6: Commit**

```bash
git add docs/INSTALLATION.md README.md SUPPORT.md skill-pack/tests/test_docs.py
git commit -m "docs: add canonical Skill Pack installation guide"
```

---

### Task 3: Add GitHub Pages pages for Skills and pilot participation

**Files:**
- Create: `docs/skills.html`
- Create: `docs/pilot.html`
- Modify: `docs/index.html` navigation and community section
- Modify: `docs/styles.css` append Skill Pack and pilot styles
- Extend: `skill-pack/tests/test_docs.py`

**Interfaces:**
- Produces: `/skills.html` and `/pilot.html` public pages using the existing orange/amber design system.

- [ ] **Step 1: Extend the failing docs test**

```python
# append to skill-pack/tests/test_docs.py

def test_github_pages_exposes_skill_pack_and_pilot_pages() -> None:
    skills = (ROOT / "docs/skills.html").read_text(encoding="utf-8")
    pilot = (ROOT / "docs/pilot.html").read_text(encoding="utf-8")
    index = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    for phrase in [
        "Installer & Upgrader",
        "Context Bootstrap",
        "0.1.0-beta.1",
        "Markdown creator fallback",
    ]:
        assert phrase in skills
    for phrase in ["Pilot the Skill Pack", "No private data", "Report evidence"]:
        assert phrase in pilot
    assert 'href="skills.html"' in index
    assert 'href="pilot.html"' in index
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_docs.py::test_github_pages_exposes_skill_pack_and_pilot_pages -v
```

Expected: missing-file failure.

- [ ] **Step 3: Create `docs/skills.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="Install the Personal AI Workspace Skill Pack beta for ChatGPT and Codex.">
  <title>Personal AI Workspace Skill Pack</title>
  <link rel="icon" href="assets/favicon.svg">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header">
    <a class="brand" href="index.html">Personal AI Workspace</a>
    <nav><a href="index.html">Home</a><a href="INSTALLATION.md">Installation</a><a href="pilot.html">Pilot</a></nav>
  </header>
  <main>
    <section class="subhero">
      <div><p class="section-kicker">Skill Pack beta · 0.1.0-beta.1</p><h1>Two focused skills. One human-governed Workspace.</h1><p>Install or upgrade safely, then start every conversation with current operational context.</p></div>
    </section>
    <section class="section skill-pair">
      <article><h2>Installer & Upgrader</h2><p>Detects fresh, partial, supported, unknown and damaged installations; previews the exact migration scope; writes only after approval; verifies by readback.</p></article>
      <article><h2>Context Bootstrap</h2><p>Loads active tasks, projects, commitments, reviews, risks and feature state without blindly loading the full historical Workspace.</p></article>
    </section>
    <section class="section latest-release">
      <div class="latest-copy"><h2>Install the beta</h2><p>Download the standalone ZIPs or the combined convenience package from the Skill Pack prerelease. The Markdown creator fallback remains supported.</p><div class="hero-actions"><a class="button light" href="https://github.com/oloix888/Personal-AI-Workspace/releases/tag/skill-pack-v0.1.0-beta.1">View prerelease</a><a class="text-link" href="INSTALLATION.md">Read installation guide →</a></div></div>
    </section>
  </main>
  <footer><span>Personal AI Workspace · Apache-2.0</span><span>Originally created by Michał Poliński & Emma ✨</span></footer>
</body>
</html>
```

- [ ] **Step 4: Create `docs/pilot.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="Pilot the Personal AI Workspace Skill Pack and report structured evidence.">
  <title>Pilot the Personal AI Workspace Skill Pack</title>
  <link rel="icon" href="assets/favicon.svg">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header"><a class="brand" href="index.html">Personal AI Workspace</a><nav><a href="index.html">Home</a><a href="skills.html">Skills</a><a href="INSTALLATION.md">Installation</a></nav></header>
  <main>
    <section class="subhero"><div><p class="section-kicker">Evidence before stable</p><h1>Pilot the Skill Pack.</h1><p>Test a fresh install, supported upgrade, partial installation, context briefing or Codex installation and report what actually happened.</p></div></section>
    <section class="section pilot-rules">
      <article><h2>No private data</h2><p>Use a disposable or sanitized Workspace. Never post tokens, private IDs, email bodies, confidential records or real connector exports.</p></article>
      <article><h2>Report evidence</h2><p>Include tested surface, versions, scenario, expected result, actual result, logs or screenshots with private information removed, and whether rollback was needed.</p></article>
      <article><h2>Open a pilot report</h2><p><a href="https://github.com/oloix888/Personal-AI-Workspace/issues/new?template=skill-pilot-feedback.yml">Submit structured pilot feedback on GitHub</a>.</p></article>
    </section>
  </main>
  <footer><span>Personal AI Workspace · Skill Pack pilot</span><span>Owner-governed, source-backed, open source</span></footer>
</body>
</html>
```

- [ ] **Step 5: Update navigation and append styles**

In `docs/index.html`, add `Skills` and `Pilot` links to the header navigation and add the following links to the community section:

```html
<a href="skills.html">Skill Pack beta</a>
<a href="pilot.html">Join the pilot</a>
```

Append to `docs/styles.css`:

```css
.subhero{min-height:52vh;display:grid;align-items:end;padding:9rem clamp(1.5rem,6vw,7rem) 5rem;background:linear-gradient(125deg,#7c2d12 0%,#ea580c 52%,#fbbf24 100%);color:#fff}.subhero>div{max-width:860px}.subhero h1{font-size:clamp(3rem,8vw,7rem);line-height:.92;margin:.6rem 0 1.5rem}.subhero p{max-width:760px;font-size:clamp(1.1rem,2vw,1.45rem)}.skill-pair,.pilot-rules{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.5rem}.skill-pair article,.pilot-rules article{border-top:4px solid #ea580c;padding:1.5rem 0}.skill-pair h2,.pilot-rules h2{margin:.2rem 0 .8rem}@media(max-width:720px){.subhero{padding-top:7rem;min-height:44vh}}
```

- [ ] **Step 6: Run tests and validate HTML links**

```bash
python -m pytest skill-pack/tests/test_docs.py -v
python skill-pack/scripts/validate_skill_pack.py --site docs
```

Expected: docs tests pass and site validation reports no missing local links.

- [ ] **Step 7: Commit**

```bash
git add docs/index.html docs/styles.css docs/skills.html docs/pilot.html skill-pack/tests/test_docs.py
git commit -m "docs: add Skill Pack and pilot pages"
```

---

### Task 4: Build and retain Skill Pack artifacts in CI

**Files:**
- Create: `.github/workflows/build-skill-pack.yml`

**Interfaces:**
- Produces: a GitHub Actions artifact named `personal-ai-workspace-skill-pack-0.1.0-beta.1` for every relevant pull request and manual run.

- [ ] **Step 1: Add a failing workflow contract test**

```python
# append to skill-pack/tests/test_docs.py
import yaml


def test_build_workflow_runs_tests_builds_and_uploads_artifacts() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/build-skill-pack.yml").read_text(encoding="utf-8"))
    steps = workflow["jobs"]["build"]["steps"]
    rendered = "\n".join(str(step) for step in steps)
    assert "python -m pytest" in rendered
    assert "python skill-pack/scripts/build_all.py" in rendered
    assert "actions/upload-artifact" in rendered
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_docs.py::test_build_workflow_runs_tests_builds_and_uploads_artifacts -v
```

Expected: missing workflow file.

- [ ] **Step 3: Create the workflow**

```yaml
# .github/workflows/build-skill-pack.yml
name: Build Skill Pack

on:
  pull_request:
    paths:
      - "skills/**"
      - "skill-pack/**"
      - "docs/INSTALLATION.md"
      - ".github/workflows/build-skill-pack.yml"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
          cache: pip
      - run: python -m pip install -e '.[dev]'
      - run: python -m pytest -v
      - run: python skill-pack/scripts/build_all.py --output skill-pack/dist --version 0.1.0-beta.1
      - run: python skill-pack/scripts/release_candidate_audit.py skill-pack/dist
      - uses: actions/upload-artifact@v4
        with:
          name: personal-ai-workspace-skill-pack-0.1.0-beta.1
          path: |
            skill-pack/dist/*.zip
            skill-pack/dist/SHA256SUMS.txt
          if-no-files-found: error
          retention-days: 14
```

- [ ] **Step 4: Run the workflow contract test**

```bash
python -m pytest skill-pack/tests/test_docs.py::test_build_workflow_runs_tests_builds_and_uploads_artifacts -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/build-skill-pack.yml skill-pack/tests/test_docs.py
git commit -m "ci: build and retain Skill Pack artifacts"
```

---

### Task 5: Validate manual ChatGPT and Codex compatibility evidence

**Files:**
- Create: `skill-pack/pilots/pilot-report.schema.json`
- Create: `skill-pack/pilots/report-template.json`
- Create: `skill-pack/scripts/validate_manual_evidence.py`
- Create: `skill-pack/tests/test_manual_evidence.py`
- Create: `skill-pack/tests/fixtures/manual-evidence/valid-chatgpt.json`
- Create: `skill-pack/tests/fixtures/manual-evidence/invalid-missing-evidence.json`

**Interfaces:**
- Produces: `validate_evidence(path: Path) -> dict` and a schema-backed compatibility record.

- [ ] **Step 1: Write failing evidence tests**

```python
# skill-pack/tests/test_manual_evidence.py
from pathlib import Path

import pytest
+from jsonschema import ValidationError

from skill_pack.scripts.validate_manual_evidence import validate_evidence

FIXTURES = Path(__file__).parent / "fixtures" / "manual-evidence"


def test_valid_manual_evidence_passes() -> None:
    payload = validate_evidence(FIXTURES / "valid-chatgpt.json")
    assert payload["result"] == "PASS"
    assert payload["skill"] == "personal-ai-workspace-context-bootstrap"


def test_missing_evidence_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_evidence(FIXTURES / "invalid-missing-evidence.json")
```

Remove the accidental leading `+` before `from jsonschema import ValidationError` when creating the file; the final test file must contain valid Python.

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_manual_evidence.py -v
```

Expected: missing schema or module.

- [ ] **Step 3: Create the evidence schema and template**

```json
// skill-pack/pilots/pilot-report.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["tested_at", "surface", "skill", "skill_version", "framework_version", "scenario", "result", "evidence", "private_data_removed"],
  "properties": {
    "tested_at": {"type": "string", "format": "date-time"},
    "surface": {"enum": ["CHATGPT_WEB", "CHATGPT_DESKTOP", "CHATGPT_MOBILE", "CODEX_DESKTOP", "CODEX_CLI"]},
    "skill": {"enum": ["personal-ai-workspace-installer-upgrader", "personal-ai-workspace-context-bootstrap"]},
    "skill_version": {"const": "0.1.0-beta.1"},
    "framework_version": {"type": "string"},
    "scenario": {"type": "string", "minLength": 3},
    "result": {"enum": ["PASS", "FAIL", "BLOCKED", "PARTIAL"]},
    "evidence": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 3}},
    "notes": {"type": "array", "items": {"type": "string"}},
    "private_data_removed": {"const": true},
    "critical_defect": {"type": "boolean"},
    "rollback_required": {"type": "boolean"}
  }
}
```

```json
// skill-pack/pilots/report-template.json
{
  "tested_at": "2026-07-20T12:00:00Z",
  "surface": "CHATGPT_WEB",
  "skill": "personal-ai-workspace-context-bootstrap",
  "skill_version": "0.1.0-beta.1",
  "framework_version": "1.5.1",
  "scenario": "current operational briefing with active tasks",
  "result": "PASS",
  "evidence": ["Sanitized screenshot attached to the pilot issue"],
  "notes": ["All active tasks were represented"],
  "private_data_removed": true,
  "critical_defect": false,
  "rollback_required": false
}
```

- [ ] **Step 4: Implement validation**

```python
# skill-pack/scripts/validate_manual_evidence.py
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "skill-pack/pilots/pilot-report.schema.json").read_text(encoding="utf-8"))


def validate_evidence(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator(SCHEMA, format_checker=FormatChecker()).validate(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a sanitized Skill Pack compatibility report")
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    payload = validate_evidence(args.report)
    print(f"valid {payload['surface']} {payload['skill']} {payload['result']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Add valid and invalid fixtures**

```json
// skill-pack/tests/fixtures/manual-evidence/valid-chatgpt.json
{
  "tested_at": "2026-07-20T12:00:00Z",
  "surface": "CHATGPT_WEB",
  "skill": "personal-ai-workspace-context-bootstrap",
  "skill_version": "0.1.0-beta.1",
  "framework_version": "1.5.1",
  "scenario": "new-conversation context briefing",
  "result": "PASS",
  "evidence": ["Sanitized transcript reference pilot-001"],
  "notes": ["Coverage header and all active task rows present"],
  "private_data_removed": true,
  "critical_defect": false,
  "rollback_required": false
}
```

```json
// skill-pack/tests/fixtures/manual-evidence/invalid-missing-evidence.json
{
  "tested_at": "2026-07-20T12:00:00Z",
  "surface": "CHATGPT_WEB",
  "skill": "personal-ai-workspace-context-bootstrap",
  "skill_version": "0.1.0-beta.1",
  "framework_version": "1.5.1",
  "scenario": "new-conversation context briefing",
  "result": "PASS",
  "private_data_removed": true,
  "critical_defect": false,
  "rollback_required": false
}
```

- [ ] **Step 6: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_manual_evidence.py -v
git add skill-pack/pilots skill-pack/scripts/validate_manual_evidence.py skill-pack/tests/test_manual_evidence.py skill-pack/tests/fixtures/manual-evidence
git commit -m "test: validate Skill Pack compatibility evidence"
```

---

### Task 6: Create structured pilot intake and pilot guidance

**Files:**
- Create: `skill-pack/pilots/README.md`
- Create: `.github/ISSUE_TEMPLATE/skill-pilot-feedback.yml`
- Extend: `skill-pack/tests/test_docs.py`

**Interfaces:**
- Produces a sanitized, repeatable pilot-report channel for installation, upgrade, bootstrap and Codex scenarios.

- [ ] **Step 1: Extend the failing docs test**

```python
# append to skill-pack/tests/test_docs.py

def test_pilot_template_requires_versions_scenario_and_privacy_confirmation() -> None:
    text = (ROOT / ".github/ISSUE_TEMPLATE/skill-pilot-feedback.yml").read_text(encoding="utf-8")
    for phrase in [
        "Skill Pack pilot feedback",
        "Skill Pack version",
        "Framework version",
        "Scenario",
        "Expected result",
        "Actual result",
        "I removed private data",
    ]:
        assert phrase in text
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_docs.py::test_pilot_template_requires_versions_scenario_and_privacy_confirmation -v
```

Expected: missing file.

- [ ] **Step 3: Create pilot guidance**

```markdown
<!-- skill-pack/pilots/README.md -->
# Skill Pack pilot program

The beta becomes stable only after evidence from fresh installation, partial installation or repair, supported upgrade, Context Bootstrap, Codex user-global installation and every available ChatGPT Skills surface.

## Safety

Use a disposable or sanitized test Workspace. Remove private IDs, account names, contact data, Gmail content, confidential records, tokens and screenshots that reveal personal information.

## Report

Record surface, Skill Pack version, framework version, scenario, expected result, actual result, evidence, critical-defect status and rollback status. Validate machine-readable reports with:

```bash
python skill-pack/scripts/validate_manual_evidence.py report.json
```

A failed pilot is valuable evidence. Never convert `BLOCKED` or `PARTIAL` into `PASS` merely because the limitation is understood.
```

- [ ] **Step 4: Create the GitHub issue form**

```yaml
# .github/ISSUE_TEMPLATE/skill-pilot-feedback.yml
name: Skill Pack pilot feedback
description: Report sanitized evidence from installing or using the Personal AI Workspace Skill Pack beta
title: "[Skill Pilot] "
labels: ["skill-pilot"]
body:
  - type: dropdown
    id: skill
    attributes:
      label: Skill
      options:
        - personal-ai-workspace-installer-upgrader
        - personal-ai-workspace-context-bootstrap
        - combined Skill Pack
    validations:
      required: true
  - type: input
    id: skill_version
    attributes:
      label: Skill Pack version
      placeholder: 0.1.0-beta.1
    validations:
      required: true
  - type: input
    id: framework_version
    attributes:
      label: Framework version
      placeholder: 1.5.1
    validations:
      required: true
  - type: input
    id: surface
    attributes:
      label: Surface
      placeholder: ChatGPT web, ChatGPT desktop, Codex desktop, or Codex CLI
    validations:
      required: true
  - type: textarea
    id: scenario
    attributes:
      label: Scenario
      description: Describe the installation, upgrade, repair, bootstrap, scale, connector, or conflict case.
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected result
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: Actual result
    validations:
      required: true
  - type: textarea
    id: evidence
    attributes:
      label: Sanitized evidence
      description: Add logs, screenshots, transcript excerpts or artifact checksums with private information removed.
    validations:
      required: true
  - type: checkboxes
    id: privacy
    attributes:
      label: Privacy confirmation
      options:
        - label: I removed private data, account identifiers, credentials, email content and confidential Workspace information.
          required: true
```

- [ ] **Step 5: Run test and commit**

```bash
python -m pytest skill-pack/tests/test_docs.py::test_pilot_template_requires_versions_scenario_and_privacy_confirmation -v
git add skill-pack/pilots/README.md .github/ISSUE_TEMPLATE/skill-pilot-feedback.yml skill-pack/tests/test_docs.py
git commit -m "docs: add structured Skill Pack pilot intake"
```

---

### Task 7: Summarize pilot evidence and calculate stable-release readiness

**Files:**
- Create: `skill-pack/scripts/summarize_pilots.py`
- Create: `skill-pack/tests/test_summarize_pilots.py`
- Create: three valid pilot fixture JSON files

**Interfaces:**
- Produces: `summarize(reports: list[dict]) -> dict` with counts, required-scenario coverage, critical defects, and `stable_ready`.

- [ ] **Step 1: Write failing readiness tests**

```python
# skill-pack/tests/test_summarize_pilots.py
import json
from pathlib import Path

from skill_pack.scripts.summarize_pilots import summarize

FIXTURES = Path(__file__).parent / "fixtures" / "pilots"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_three_successful_external_scenarios_without_critical_defects_are_ready() -> None:
    result = summarize([
        load("fresh-install.json"),
        load("supported-upgrade.json"),
        load("context-bootstrap.json"),
    ])
    assert result["stable_ready"] is True
    assert result["critical_defects"] == 0


def test_missing_upgrade_scenario_is_not_ready() -> None:
    result = summarize([
        load("fresh-install.json"),
        load("context-bootstrap.json"),
    ])
    assert result["stable_ready"] is False
    assert "supported-upgrade" in result["missing_scenarios"]
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_summarize_pilots.py -v
```

Expected: missing module and fixtures.

- [ ] **Step 3: Implement readiness summary**

```python
# skill-pack/scripts/summarize_pilots.py
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_SCENARIOS = {"fresh-install", "supported-upgrade", "context-bootstrap"}


def summarize(reports: list[dict[str, Any]]) -> dict[str, Any]:
    passed_scenarios = {
        str(report["scenario_key"])
        for report in reports
        if report.get("result") == "PASS" and not report.get("critical_defect", False)
    }
    critical_defects = sum(bool(report.get("critical_defect", False)) for report in reports)
    missing = sorted(REQUIRED_SCENARIOS - passed_scenarios)
    external_sessions = len({str(report["pilot_id"]) for report in reports})
    return {
        "reports": len(reports),
        "external_sessions": external_sessions,
        "passed_scenarios": sorted(passed_scenarios),
        "missing_scenarios": missing,
        "critical_defects": critical_defects,
        "stable_ready": external_sessions >= 3 and not missing and critical_defects == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize Skill Pack pilot readiness")
    parser.add_argument("reports", nargs="+", type=Path)
    args = parser.parse_args()
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in args.reports]
    print(json.dumps(summarize(payloads), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Add pilot fixtures**

Each fixture uses the same structure; create these exact differences:

```json
// skill-pack/tests/fixtures/pilots/fresh-install.json
{"pilot_id":"pilot-fresh-001","scenario_key":"fresh-install","result":"PASS","critical_defect":false}
```

```json
// skill-pack/tests/fixtures/pilots/supported-upgrade.json
{"pilot_id":"pilot-upgrade-001","scenario_key":"supported-upgrade","result":"PASS","critical_defect":false}
```

```json
// skill-pack/tests/fixtures/pilots/context-bootstrap.json
{"pilot_id":"pilot-bootstrap-001","scenario_key":"context-bootstrap","result":"PASS","critical_defect":false}
```

- [ ] **Step 5: Run and commit**

```bash
python -m pytest skill-pack/tests/test_summarize_pilots.py -v
git add skill-pack/scripts/summarize_pilots.py skill-pack/tests/test_summarize_pilots.py skill-pack/tests/fixtures/pilots
git commit -m "feat: calculate Skill Pack pilot readiness"
```

---

### Task 8: Audit the release candidate before publication

**Files:**
- Create: `skill-pack/scripts/release_candidate_audit.py`
- Create: `skill-pack/tests/test_release_candidate_audit.py`

**Interfaces:**
- Produces: `audit_release_directory(root: Path, version: str) -> list[str]`; empty list means the candidate is internally consistent.

- [ ] **Step 1: Write failing audit tests**

```python
# skill-pack/tests/test_release_candidate_audit.py
from pathlib import Path

from skill_pack.scripts.build_all import build_all
from skill_pack.scripts.release_candidate_audit import audit_release_directory

ROOT = Path(__file__).resolve().parents[2]


def test_built_release_candidate_passes_audit(tmp_path: Path) -> None:
    build_all(ROOT, tmp_path, "0.1.0-beta.1")
    assert audit_release_directory(tmp_path, "0.1.0-beta.1") == []


def test_missing_checksum_is_reported(tmp_path: Path) -> None:
    build_all(ROOT, tmp_path, "0.1.0-beta.1")
    (tmp_path / "SHA256SUMS.txt").unlink()
    assert "missing SHA256SUMS.txt" in audit_release_directory(tmp_path, "0.1.0-beta.1")
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_release_candidate_audit.py -v
```

Expected: missing module.

- [ ] **Step 3: Implement the audit**

```python
# skill-pack/scripts/release_candidate_audit.py
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import zipfile


def audit_release_directory(root: Path, version: str) -> list[str]:
    errors: list[str] = []
    names = [
        f"Personal-AI-Workspace-Installer-Upgrader-{version}.zip",
        f"Personal-AI-Workspace-Context-Bootstrap-{version}.zip",
        f"Personal-AI-Workspace-Skill-Pack-{version}.zip",
    ]
    checksum_path = root / "SHA256SUMS.txt"
    if not checksum_path.is_file():
        return ["missing SHA256SUMS.txt"]
    checksum_lines = {
        line.split(maxsplit=1)[1].strip(): line.split(maxsplit=1)[0]
        for line in checksum_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    for name in names:
        path = root / name
        if not path.is_file():
            errors.append(f"missing {name}")
            continue
        expected = checksum_lines.get(name)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected != actual:
            errors.append(f"checksum mismatch: {name}")
        try:
            with zipfile.ZipFile(path) as archive:
                bad = archive.testzip()
                if bad:
                    errors.append(f"corrupt ZIP member {bad} in {name}")
        except zipfile.BadZipFile:
            errors.append(f"invalid ZIP: {name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Personal AI Workspace Skill Pack release artifacts")
    parser.add_argument("root", type=Path)
    parser.add_argument("--version", default="0.1.0-beta.1")
    args = parser.parse_args()
    errors = audit_release_directory(args.root, args.version)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("release candidate valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run audit tests**

```bash
python -m pytest skill-pack/tests/test_release_candidate_audit.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Run the complete candidate audit**

```bash
python skill-pack/scripts/build_all.py --output skill-pack/dist --version 0.1.0-beta.1
python skill-pack/scripts/release_candidate_audit.py skill-pack/dist --version 0.1.0-beta.1
```

Expected: `release candidate valid`.

- [ ] **Step 6: Commit**

```bash
git add skill-pack/scripts/release_candidate_audit.py skill-pack/tests/test_release_candidate_audit.py
git commit -m "test: audit Skill Pack release candidates"
```

---

### Task 9: Prepare a manually gated GitHub prerelease workflow

**Files:**
- Create: `.github/workflows/publish-skill-pack-prerelease.yml`
- Create: `releases/skill-pack-v0.1.0-beta.1.md`
- Extend: `skill-pack/tests/test_docs.py`

**Interfaces:**
- Produces GitHub prerelease tag `skill-pack-v0.1.0-beta.1` only after manual workflow dispatch with exact confirmation text.

- [ ] **Step 1: Add a failing workflow-gate test**

```python
# append to skill-pack/tests/test_docs.py

def test_prerelease_workflow_requires_exact_manual_confirmation() -> None:
    text = (ROOT / ".github/workflows/publish-skill-pack-prerelease.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch" in text
    assert "PUBLISH skill-pack-v0.1.0-beta.1" in text
    assert "--prerelease" in text
    assert "skill-pack/dist/SHA256SUMS.txt" in text
    assert "environment: skill-pack-prerelease" in text
```

- [ ] **Step 2: Run and observe failure**

+```bash
+python -m pytest skill-pack/tests/test_docs.py::test_prerelease_workflow_requires_exact_manual_confirmation -v
+```
+
+Remove the accidental leading `+` characters when creating the final plan implementation commands.
+
+Expected: missing workflow.
+
+- [ ] **Step 3: Create release notes**
+
+```markdown
+<!-- releases/skill-pack-v0.1.0-beta.1.md -->
+# Personal AI Workspace Skill Pack 0.1.0-beta.1
+
+**Channel:** prerelease  
+**Framework target:** Personal AI Workspace 1.5.1
+
+## Included skills
+
+- `personal-ai-workspace-installer-upgrader`
+- `personal-ai-workspace-context-bootstrap`
+
+## Beta purpose
+
+Validate installation-state detection, approved migrations, idempotency, connector capability reporting, active-task completeness, context budgeting and cross-surface skill installation before a stable release.
+
+## Important boundaries
+
+- The Markdown creator v1.5.1 remains the universal fallback.
+- The beta must not be tested against a production Workspace without a reviewed backup and migration plan.
+- Unknown newer Workspace versions remain read-only.
+- No background execution is implied.
+- Report pilot evidence through the repository issue form after removing private information.
+```
+
+- [ ] **Step 4: Create the manual prerelease workflow**
+
+```yaml
+# .github/workflows/publish-skill-pack-prerelease.yml
+name: Publish Skill Pack prerelease
+
+on:
+  workflow_dispatch:
+    inputs:
+      confirmation:
+        description: Type PUBLISH skill-pack-v0.1.0-beta.1
+        required: true
+        type: string
+
+permissions:
+  contents: write
+
+jobs:
+  publish:
+    if: ${{ inputs.confirmation == 'PUBLISH skill-pack-v0.1.0-beta.1' }}
+    environment: skill-pack-prerelease
+    runs-on: ubuntu-latest
+    steps:
+      - uses: actions/checkout@v5
+      - uses: actions/setup-python@v6
+        with:
+          python-version: "3.11"
+          cache: pip
+      - run: python -m pip install -e '.[dev]'
+      - run: python -m pytest -v
+      - run: python skill-pack/scripts/build_all.py --output skill-pack/dist --version 0.1.0-beta.1
+      - run: python skill-pack/scripts/release_candidate_audit.py skill-pack/dist --version 0.1.0-beta.1
+      - name: Create prerelease
+        env:
+          GH_TOKEN: ${{ github.token }}
+        run: |
+          gh release create skill-pack-v0.1.0-beta.1 \
+            skill-pack/dist/Personal-AI-Workspace-Installer-Upgrader-0.1.0-beta.1.zip \
+            skill-pack/dist/Personal-AI-Workspace-Context-Bootstrap-0.1.0-beta.1.zip \
+            skill-pack/dist/Personal-AI-Workspace-Skill-Pack-0.1.0-beta.1.zip \
+            skill-pack/dist/SHA256SUMS.txt \
+            --title "Personal AI Workspace Skill Pack 0.1.0-beta.1" \
+            --notes-file releases/skill-pack-v0.1.0-beta.1.md \
+            --prerelease
+```
+
+- [ ] **Step 5: Run workflow contract tests**
+
+```bash
+python -m pytest skill-pack/tests/test_docs.py::test_prerelease_workflow_requires_exact_manual_confirmation -v
+```
+
+Expected: pass.
+
+- [ ] **Step 6: Commit without dispatching the workflow**
+
+```bash
+git add .github/workflows/publish-skill-pack-prerelease.yml releases/skill-pack-v0.1.0-beta.1.md skill-pack/tests/test_docs.py
+git commit -m "release: prepare gated Skill Pack beta workflow"
+```
+
+Do not run the publication workflow until Michał explicitly approves publication of `skill-pack-v0.1.0-beta.1`.
+
+---
+
+### Task 10: Run final integration verification and open the implementation PR
+
+**Files:**
+- Modify: `ROADMAP.md` add the Skill Pack beta milestone and pilot gate
+- Modify: `README.md` add the Skill Pack beta section only after all local and CI checks pass
+
+**Interfaces:**
+- Produces one reviewable implementation PR containing source, tests, docs, build workflows and the unpublished prerelease workflow.
+
+- [ ] **Step 1: Run the complete test suite**
+
+```bash
+python -m pytest -v
+```
+
+Expected: all foundation, installer, bootstrap and integration tests pass.
+
+- [ ] **Step 2: Build and audit artifacts twice**
+
+```bash
+rm -rf skill-pack/dist skill-pack/dist-second
+python skill-pack/scripts/build_all.py --output skill-pack/dist --version 0.1.0-beta.1
+python skill-pack/scripts/build_all.py --output skill-pack/dist-second --version 0.1.0-beta.1
+diff -r skill-pack/dist skill-pack/dist-second
+python skill-pack/scripts/release_candidate_audit.py skill-pack/dist --version 0.1.0-beta.1
+```
+
+Expected: `diff` exits with status 0 and audit prints `release candidate valid`.
+
+- [ ] **Step 3: Run public-safety scans**
+
+```bash
+python skill-pack/scripts/scan_private_identifiers.py skills
+python skill-pack/scripts/scan_private_identifiers.py skill-pack/dist
+```
+
+Expected: both report `public-safe`.
+
+- [ ] **Step 4: Validate documentation and Pages locally**
+
+```bash
+python skill-pack/scripts/validate_skill_pack.py --site docs
+python -m http.server 4173 --directory docs
+```
+
+In a separate terminal, verify:
+
+```bash
+curl -fsS http://127.0.0.1:4173/index.html >/dev/null
+curl -fsS http://127.0.0.1:4173/skills.html >/dev/null
+curl -fsS http://127.0.0.1:4173/pilot.html >/dev/null
+```
+
+Expected: all commands exit 0. Then stop the HTTP server.
+
+- [ ] **Step 5: Update roadmap and README**
+
+Add to `ROADMAP.md`:
+
+```markdown
+## Skill Pack beta
+
+- [ ] Merge the two-skill implementation after code review and green CI.
+- [ ] Obtain explicit owner approval before publishing `skill-pack-v0.1.0-beta.1`.
+- [ ] Complete fresh-install, supported-upgrade and Context Bootstrap pilot scenarios.
+- [ ] Record at least three external pilot sessions with no critical defect before stable release.
+```
+
+Add to `README.md` after the latest creator section:
+
+```markdown
+## Skill Pack beta
+
+Personal AI Workspace is also being packaged as two focused Agent Skills: **Installer & Upgrader** and **Context Bootstrap**. The beta is additive and does not replace the Markdown creator. Read the [Skill Pack overview](docs/skills.html), [installation guide](docs/INSTALLATION.md) and [pilot guide](docs/pilot.html).
+```
+
+- [ ] **Step 6: Commit final documentation**
+
+```bash
+git add README.md ROADMAP.md
+git commit -m "docs: document Skill Pack beta and pilot gate"
+```
+
+- [ ] **Step 7: Push and open a draft implementation PR**
+
+```bash
+git push -u origin feature/skill-pack-0.1.0-beta.1
+gh pr create \
+  --draft \
+  --base main \
+  --head feature/skill-pack-0.1.0-beta.1 \
+  --title "Build Personal AI Workspace Skill Pack 0.1.0-beta.1" \
+  --body "Implements the approved two-skill architecture, deterministic packaging, installation docs, compatibility evidence, gated prerelease workflow and pilot infrastructure. Does not publish the prerelease or modify a private Workspace."
+```
+
+- [ ] **Step 8: Review CI and do not publish**
+
+Expected required checks:
+
+```text
+Validate repository
+Build Skill Pack
+Pages build or link validation
+```
+
+Do not merge until code review and all required checks are green. Do not dispatch `Publish Skill Pack prerelease` until a separate explicit owner approval names `skill-pack-v0.1.0-beta.1`.
+
+---
+
+## Self-Review Checklist
+
+- [ ] Foundation interfaces used here exactly match the foundation plan: `build_skill`, `assert_valid_skill`, `assert_public_safe`, `create_deterministic_zip`, and `write_checksums`.
+- [ ] Both skill package names and version strings are consistent across manifest, docs, workflows, tests and release notes.
+- [ ] No task publishes a release without a separate explicit owner action.
+- [ ] Markdown creator v1.5.1 remains documented as the fallback.
+- [ ] No active Google Tasks path appears.
+- [ ] Public/private scans run before artifact publication.
+- [ ] ChatGPT and Codex support claims require evidence records.
+- [ ] Pilot readiness requires three external sessions, required scenario coverage and zero critical defects.
+- [ ] All code blocks contain final names and commands; no implementation placeholder remains.
