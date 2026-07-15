# Skill Pack Foundation and Build Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the shared contracts, deterministic build system, validators, privacy scanner, package generator, and CI foundation required by both Phase 1 Personal AI Workspace skills.

**Architecture:** Keep one versioned source of truth under `skills/_shared`, then vendor the required shared files into each standalone skill package during a deterministic build. Python scripts perform only local deterministic operations: schema validation, fixture normalization, private-data scanning, package validation, ZIP creation, and checksums; connector orchestration remains in skill instructions.

**Tech Stack:** Python 3.11+, standard library, `pytest>=8,<9`, `PyYAML>=6,<7`, `jsonschema>=4,<5`, GitHub Actions, Markdown, JSON Schema Draft 2020-12.

## Global Constraints

- The two public skills must remain independently installable and self-contained.
- The Markdown creator v1.5.1 remains the supported universal fallback during Phase 1.
- No public runtime package may contain private Notion IDs, private Google account or Drive folder IDs, `oloix888/Apex`, private contacts, Gmail content, or the private `emma-workspace-memory` manifest.
- The intentionally public project contact `michal24749@gmail.com`, project name, creator attribution, Apache-2.0 license, and NOTICE are allowed.
- Public scripts must not call personal cloud services or mutate a live Workspace.
- Active Google Tasks paths are prohibited.
- All build output must be deterministic for identical source input.
- Every task follows TDD: failing test, observed failure, minimal implementation, passing test, commit.
- This plan does not authorize publication of a prerelease or modification of Michał's private Workspace.

---

## File Map

```text
pyproject.toml
skills/_shared/
├── contract/
│   ├── attribution.md
│   ├── capability-model.md
│   ├── governance.md
│   ├── privacy-and-sensitive-context.md
│   ├── readback-contract.md
│   ├── versioning-contract.md
│   └── compatibility.json
├── schemas/
│   ├── capability-report.schema.json
│   ├── installation-report.schema.json
│   ├── migration-manifest.schema.json
│   ├── feature-registry.schema.json
│   └── context-briefing.schema.json
└── fixtures/
    └── README.md
skill-pack/
├── README.md
├── src/paiw_skill_pack/
│   ├── __init__.py
│   ├── build.py
│   ├── frontmatter.py
│   ├── models.py
│   ├── package.py
│   ├── scanner.py
│   ├── schemas.py
│   └── validate.py
├── scripts/
│   ├── build_skill_pack.py
│   ├── package_skill_pack.py
│   ├── scan_private_identifiers.py
│   └── validate_skill_pack.py
└── tests/
    ├── fixtures/minimal-skill/
    ├── test_build.py
    ├── test_frontmatter.py
    ├── test_models.py
    ├── test_package.py
    ├── test_repository_layout.py
    ├── test_scanner.py
    ├── test_schemas.py
    └── test_validate.py
.github/workflows/validate-skill-pack.yml
```

---

### Task 1: Establish the Python tooling skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `skill-pack/src/paiw_skill_pack/__init__.py`
- Create: `skill-pack/tests/test_repository_layout.py`
- Create: `skill-pack/README.md`

**Interfaces:**
- Produces: importable package `paiw_skill_pack`; repository layout expected by every later task.

- [ ] **Step 1: Write the failing repository-layout test**

```python
# skill-pack/tests/test_repository_layout.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_skill_pack_roots_exist() -> None:
    expected = [
        ROOT / "skills" / "_shared" / "contract",
        ROOT / "skills" / "_shared" / "schemas",
        ROOT / "skills" / "_shared" / "fixtures",
        ROOT / "skill-pack" / "src" / "paiw_skill_pack",
        ROOT / "skill-pack" / "scripts",
    ]
    assert [str(path.relative_to(ROOT)) for path in expected if not path.is_dir()] == []


def test_python_package_is_importable() -> None:
    import paiw_skill_pack

    assert paiw_skill_pack.__version__ == "0.1.0-beta.1"
```

- [ ] **Step 2: Run the test and observe failure**

Run:

```bash
python -m pytest skill-pack/tests/test_repository_layout.py -v
```

Expected: collection or assertion failure because `paiw_skill_pack` and required directories do not exist.

- [ ] **Step 3: Add the package and project configuration**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=75", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "personal-ai-workspace-skill-pack-tools"
version = "0.1.0b1"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = [
  "pytest>=8,<9",
  "PyYAML>=6,<7",
  "jsonschema>=4,<5",
]

[tool.setuptools]
package-dir = {"" = "skill-pack/src"}

[tool.setuptools.packages.find]
where = ["skill-pack/src"]

[tool.pytest.ini_options]
addopts = "-ra"
testpaths = ["skill-pack/tests"]
pythonpath = ["skill-pack/src"]
```

```python
# skill-pack/src/paiw_skill_pack/__init__.py
__version__ = "0.1.0-beta.1"
```

```markdown
<!-- skill-pack/README.md -->
# Personal AI Workspace Skill Pack build tools

Local deterministic tools for validating, building, scanning and packaging the public Phase 1 skills. These scripts never call personal cloud services and never mutate a live Workspace.

## Development

```bash
python -m pip install -e '.[dev]'
python -m pytest
```
```

Create the empty source roots by adding these files:

```markdown
<!-- skills/_shared/contract/README.md -->
# Shared contract

Versioned source rules vendored into every distributed skill.
```

```markdown
<!-- skills/_shared/schemas/README.md -->
# Shared schemas

JSON Schemas used by deterministic local validators.
```

```markdown
<!-- skills/_shared/fixtures/README.md -->
# Public-safe fixtures

Fixtures use fictional people, accounts, URLs and identifiers only.
```

```python
# skill-pack/scripts/__init__.py
"""Command wrappers for the Skill Pack build."""
```

- [ ] **Step 4: Install development dependencies and rerun the test**

Run:

```bash
python -m pip install -e '.[dev]'
python -m pytest skill-pack/tests/test_repository_layout.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml skill-pack skills/_shared
git commit -m "build: scaffold Skill Pack tooling"
```

---

### Task 2: Define compatibility and semantic capability models

**Files:**
- Create: `skills/_shared/contract/compatibility.json`
- Create: `skills/_shared/contract/capability-model.md`
- Create: `skills/_shared/contract/governance.md`
- Create: `skills/_shared/contract/privacy-and-sensitive-context.md`
- Create: `skills/_shared/contract/readback-contract.md`
- Create: `skills/_shared/contract/versioning-contract.md`
- Create: `skills/_shared/contract/attribution.md`
- Create: `skill-pack/src/paiw_skill_pack/models.py`
- Create: `skill-pack/tests/test_models.py`

**Interfaces:**
- Produces: `CapabilityState`, `CapabilityResult`, `CompatibilityManifest`, and `load_compatibility(path)` used by both skills and validators.

- [ ] **Step 1: Write failing model tests**

```python
# skill-pack/tests/test_models.py
from pathlib import Path

from paiw_skill_pack.models import (
    CapabilityResult,
    CapabilityState,
    load_compatibility,
)

ROOT = Path(__file__).resolve().parents[2]


def test_capability_result_is_explicit() -> None:
    result = CapabilityResult(
        capability="notion.content.read",
        state=CapabilityState.AVAILABLE_READ_ONLY,
        detail="Notion content can be read but not changed.",
    )
    assert result.capability == "notion.content.read"
    assert result.state.value == "AVAILABLE_READ_ONLY"


def test_compatibility_manifest_loads() -> None:
    manifest = load_compatibility(
        ROOT / "skills/_shared/contract/compatibility.json"
    )
    assert manifest.skill_pack_version == "0.1.0-beta.1"
    assert manifest.target_framework_version == "1.5.1"
    assert manifest.supported_framework_versions[0] == "1.0"
    assert manifest.supported_framework_versions[-1] == "1.5.1"
```

- [ ] **Step 2: Run the tests and observe failure**

```bash
python -m pytest skill-pack/tests/test_models.py -v
```

Expected: import failure because `paiw_skill_pack.models` does not exist.

- [ ] **Step 3: Implement the typed models**

```python
# skill-pack/src/paiw_skill_pack/models.py
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path


class CapabilityState(StrEnum):
    AVAILABLE_READ_WRITE = "AVAILABLE_READ_WRITE"
    AVAILABLE_READ_ONLY = "AVAILABLE_READ_ONLY"
    UNAVAILABLE = "UNAVAILABLE"
    UNAUTHORIZED = "UNAUTHORIZED"
    ACCOUNT_MISMATCH = "ACCOUNT_MISMATCH"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class CapabilityResult:
    capability: str
    state: CapabilityState
    detail: str


@dataclass(frozen=True, slots=True)
class CompatibilityManifest:
    skill_pack_version: str
    supported_framework_versions: tuple[str, ...]
    target_framework_version: str
    minimum_contract_version: str


def load_compatibility(path: Path) -> CompatibilityManifest:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return CompatibilityManifest(
        skill_pack_version=str(payload["skill_pack_version"]),
        supported_framework_versions=tuple(payload["supported_framework_versions"]),
        target_framework_version=str(payload["target_framework_version"]),
        minimum_contract_version=str(payload["minimum_contract_version"]),
    )
```

```json
// skills/_shared/contract/compatibility.json
{
  "skill_pack_version": "0.1.0-beta.1",
  "supported_framework_versions": ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.5.1"],
  "target_framework_version": "1.5.1",
  "minimum_contract_version": "1.0.0"
}
```

- [ ] **Step 4: Add the shared human-readable contracts**

```markdown
<!-- skills/_shared/contract/capability-model.md -->
# Capability model

Skills audit semantic capabilities instead of assuming connector function names. Required states are `AVAILABLE_READ_WRITE`, `AVAILABLE_READ_ONLY`, `UNAVAILABLE`, `UNAUTHORIZED`, `ACCOUNT_MISMATCH`, `DEGRADED`, and `UNKNOWN`. Missing capabilities are reported and never invented.
```

```markdown
<!-- skills/_shared/contract/governance.md -->
# Governance

Structural writes require explicit owner approval for the exact displayed scope. Approval does not extend to newly discovered scope. Normal record updates inside an approved schema are not structural changes. No skill claims background execution without a real automation.
```

```markdown
<!-- skills/_shared/contract/privacy-and-sensitive-context.md -->
# Privacy and sensitive context

Material sensitive context may be retained with purpose, provenance, epistemic status, confidence and confidentiality. Internal retention does not authorize external disclosure. Passwords, tokens, one-time codes, reset links and authentication secrets are excluded.
```

```markdown
<!-- skills/_shared/contract/readback-contract.md -->
# Readback contract

A connector-backed write is successful only after the resulting object is read back and its identity, parent, critical properties and links are verified. Partial or truncated reads are reported as incomplete.
```

```markdown
<!-- skills/_shared/contract/versioning-contract.md -->
# Versioning contract

Framework, Skill Pack, individual skill and installed Workspace schema versions are tracked independently. Unknown newer Workspace versions are read-only and are never automatically downgraded.
```

```markdown
<!-- skills/_shared/contract/attribution.md -->
# Attribution

Personal AI Workspace was originally created by Michał Poliński and Emma ✨. Public packages retain the Apache-2.0 license and project NOTICE. The public contact is `michal24749@gmail.com`.
```

- [ ] **Step 5: Rerun tests**

```bash
python -m pytest skill-pack/tests/test_models.py -v
```

Expected: `2 passed`.

- [ ] **Step 6: Commit**

```bash
git add skills/_shared/contract skill-pack/src/paiw_skill_pack/models.py skill-pack/tests/test_models.py
git commit -m "feat: define shared compatibility and capability contracts"
```

---

### Task 3: Add machine-readable schemas and validation

**Files:**
- Create: `skills/_shared/schemas/capability-report.schema.json`
- Create: `skills/_shared/schemas/installation-report.schema.json`
- Create: `skills/_shared/schemas/migration-manifest.schema.json`
- Create: `skills/_shared/schemas/feature-registry.schema.json`
- Create: `skills/_shared/schemas/context-briefing.schema.json`
- Create: `skill-pack/src/paiw_skill_pack/schemas.py`
- Create: `skill-pack/tests/test_schemas.py`

**Interfaces:**
- Produces: `load_schema(name) -> dict` and `validate_payload(schema_name, payload) -> None`.

- [ ] **Step 1: Write failing schema tests**

```python
# skill-pack/tests/test_schemas.py
import pytest
from jsonschema import ValidationError

from paiw_skill_pack.schemas import validate_payload


def test_capability_report_accepts_explicit_state() -> None:
    validate_payload(
        "capability-report",
        {
            "generated_at": "2026-07-15T09:00:00Z",
            "capabilities": [
                {
                    "capability": "notion.content.read",
                    "state": "AVAILABLE_READ_ONLY",
                    "detail": "Read-only connector",
                }
            ],
        },
    )


def test_capability_report_rejects_invented_state() -> None:
    with pytest.raises(ValidationError):
        validate_payload(
            "capability-report",
            {
                "generated_at": "2026-07-15T09:00:00Z",
                "capabilities": [
                    {
                        "capability": "notion.content.read",
                        "state": "PROBABLY_AVAILABLE",
                        "detail": "Unsupported state",
                    }
                ],
            },
        )


def test_context_briefing_requires_coverage() -> None:
    with pytest.raises(ValidationError):
        validate_payload(
            "context-briefing",
            {
                "generated_at": "2026-07-15T09:00:00Z",
                "workspace": {"title": "Example", "framework_version": "1.5.1"},
            },
        )
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_schemas.py -v
```

Expected: import failure for `paiw_skill_pack.schemas`.

- [ ] **Step 3: Implement schema loading and validation**

```python
# skill-pack/src/paiw_skill_pack/schemas.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "skills" / "_shared" / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / f"{name}.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def validate_payload(name: str, payload: dict[str, Any]) -> None:
    Draft202012Validator(load_schema(name)).validate(payload)
```

- [ ] **Step 4: Add exact schemas**

```json
// skills/_shared/schemas/capability-report.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["generated_at", "capabilities"],
  "properties": {
    "generated_at": {"type": "string", "format": "date-time"},
    "capabilities": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["capability", "state", "detail"],
        "properties": {
          "capability": {"type": "string", "minLength": 1},
          "state": {
            "enum": [
              "AVAILABLE_READ_WRITE",
              "AVAILABLE_READ_ONLY",
              "UNAVAILABLE",
              "UNAUTHORIZED",
              "ACCOUNT_MISMATCH",
              "DEGRADED",
              "UNKNOWN"
            ]
          },
          "detail": {"type": "string"}
        }
      }
    }
  }
}
```

```json
// skills/_shared/schemas/installation-report.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["state", "confidence", "matched", "missing", "conflicts", "coverage"],
  "properties": {
    "state": {"enum": ["NOT_INSTALLED", "PARTIAL", "INSTALLED_SUPPORTED", "INSTALLED_UNKNOWN", "DAMAGED"]},
    "confidence": {"enum": ["HIGH", "MEDIUM", "LOW"]},
    "framework_version": {"type": ["string", "null"]},
    "matched": {"type": "array", "items": {"type": "string"}},
    "missing": {"type": "array", "items": {"type": "string"}},
    "conflicts": {"type": "array", "items": {"type": "string"}},
    "coverage": {"enum": ["FULL", "PARTIAL", "DEGRADED"]},
    "reason": {"type": "string"}
  }
}
```

```json
// skills/_shared/schemas/migration-manifest.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "from", "to", "destructive", "requires", "preconditions", "operations", "validations", "rollback"],
  "properties": {
    "id": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+(?:\\.[0-9]+)?-to-[0-9]+\\.[0-9]+(?:\\.[0-9]+)?$"},
    "from": {"type": "string"},
    "to": {"type": "string"},
    "destructive": {"type": "boolean"},
    "requires": {"type": "array", "items": {"type": "string"}, "uniqueItems": true},
    "preconditions": {"type": "array", "items": {"type": "string"}},
    "operations": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    "validations": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    "rollback": {"type": "string", "minLength": 1}
  }
}
```

```json
// skills/_shared/schemas/feature-registry.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["features"],
  "properties": {
    "features": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["key", "display_name", "classification", "state", "required_capabilities", "dependencies"],
        "properties": {
          "key": {"type": "string", "pattern": "^[a-z0-9.-]+$"},
          "display_name": {"type": "string", "minLength": 1},
          "classification": {"enum": ["CORE", "OPTIONAL"]},
          "state": {"enum": ["Enabled", "Disabled by User", "Unavailable", "Pending Setup", "Paused", "Degraded"]},
          "required_capabilities": {"type": "array", "items": {"type": "string"}},
          "dependencies": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

```json
// skills/_shared/schemas/context-briefing.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["generated_at", "workspace", "coverage", "features", "tasks", "projects", "commitments", "reviews", "risks", "contradictions", "recent_material_changes", "high_value_facts"],
  "properties": {
    "generated_at": {"type": "string", "format": "date-time"},
    "workspace": {
      "type": "object",
      "required": ["title", "framework_version"],
      "properties": {
        "title": {"type": "string"},
        "framework_version": {"type": "string"},
        "constitution_url": {"type": ["string", "null"]}
      }
    },
    "coverage": {
      "type": "object",
      "required": ["status", "sources_checked", "sources_unavailable", "truncated", "notes"],
      "properties": {
        "status": {"enum": ["FULL", "PARTIAL", "DEGRADED"]},
        "sources_checked": {"type": "array", "items": {"type": "string"}},
        "sources_unavailable": {"type": "array", "items": {"type": "string"}},
        "truncated": {"type": "boolean"},
        "notes": {"type": "array", "items": {"type": "string"}}
      }
    },
    "features": {"type": "array"},
    "tasks": {"type": "array"},
    "projects": {"type": "array"},
    "commitments": {"type": "array"},
    "reviews": {"type": "array"},
    "risks": {"type": "array"},
    "contradictions": {"type": "array"},
    "recent_material_changes": {"type": "array"},
    "high_value_facts": {"type": "array"}
  }
}
```

- [ ] **Step 5: Rerun schema tests**

```bash
python -m pytest skill-pack/tests/test_schemas.py -v
```

Expected: `3 passed`.

- [ ] **Step 6: Commit**

```bash
git add skills/_shared/schemas skill-pack/src/paiw_skill_pack/schemas.py skill-pack/tests/test_schemas.py
git commit -m "feat: add shared Skill Pack schemas"
```

---

### Task 4: Implement public/private data and secret scanning

**Files:**
- Create: `skill-pack/src/paiw_skill_pack/scanner.py`
- Create: `skill-pack/tests/test_scanner.py`
- Create: `skill-pack/tests/fixtures/scanner/safe.md`
- Create: `skill-pack/tests/fixtures/scanner/unsafe.md`

**Interfaces:**
- Produces: `scan_tree(root, public_email) -> list[Finding]` and `assert_public_safe(root, public_email) -> None`.

- [ ] **Step 1: Write failing scanner tests**

```python
# skill-pack/tests/test_scanner.py
from pathlib import Path

import pytest

from paiw_skill_pack.scanner import PublicSafetyError, scan_tree

FIXTURES = Path(__file__).parent / "fixtures" / "scanner"


def test_safe_tree_allows_public_project_contact() -> None:
    findings = scan_tree(FIXTURES / "safe", "michal24749@gmail.com")
    assert findings == []


def test_scanner_detects_non_allowlisted_email_and_private_repo() -> None:
    findings = scan_tree(FIXTURES / "unsafe", "michal24749@gmail.com")
    rules = {finding.rule for finding in findings}
    assert "non_allowlisted_email" in rules
    assert "private_repo_reference" in rules


def test_public_safety_error_has_paths() -> None:
    with pytest.raises(PublicSafetyError) as exc:
        from paiw_skill_pack.scanner import assert_public_safe

        assert_public_safe(FIXTURES / "unsafe", "michal24749@gmail.com")
    assert "unsafe.md" in str(exc.value)
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_scanner.py -v
```

Expected: import failure for `paiw_skill_pack.scanner`.

- [ ] **Step 3: Implement the scanner**

```python
# skill-pack/src/paiw_skill_pack/scanner.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".html", ".css", ".js"}
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PRIVATE_REPO_RE = re.compile(r"\boloix888/Apex\b", re.IGNORECASE)
AUTH_SECRET_RE = re.compile(
    r"(?i)\b(password|one[- ]time code|reset link|api[_ -]?key|access[_ -]?token|session cookie)\b\s*[:=]"
)


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    line: int
    rule: str
    excerpt: str


class PublicSafetyError(RuntimeError):
    pass


def scan_tree(root: Path, public_email: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for email in EMAIL_RE.findall(line):
                if email.lower() != public_email.lower():
                    findings.append(Finding(relative, line_number, "non_allowlisted_email", line.strip()))
            if PRIVATE_REPO_RE.search(line):
                findings.append(Finding(relative, line_number, "private_repo_reference", line.strip()))
            if AUTH_SECRET_RE.search(line):
                findings.append(Finding(relative, line_number, "authentication_secret_literal", line.strip()))
    return findings


def assert_public_safe(root: Path, public_email: str) -> None:
    findings = scan_tree(root, public_email)
    if findings:
        detail = "\n".join(
            f"{item.path}:{item.line} [{item.rule}] {item.excerpt}" for item in findings
        )
        raise PublicSafetyError(detail)
```

- [ ] **Step 4: Add fixtures**

```markdown
<!-- skill-pack/tests/fixtures/scanner/safe/safe.md -->
Project contact: michal24749@gmail.com

Example connector identity: fictional-owner@example.invalid
```

The `.invalid` address is not accepted by the email regex because the scanner intentionally treats any syntactically email-like address as sensitive. Replace the example with a non-email URI:

```markdown
<!-- final skill-pack/tests/fixtures/scanner/safe/safe.md -->
Project contact: michal24749@gmail.com

Example connector identity: `example-user` at `example.invalid`.
```

```markdown
<!-- skill-pack/tests/fixtures/scanner/unsafe/unsafe.md -->
Private account: private.user@example.com
Private task repository: oloix888/Apex
```

- [ ] **Step 5: Rerun scanner tests**

```bash
python -m pytest skill-pack/tests/test_scanner.py -v
```

Expected: `3 passed`.

- [ ] **Step 6: Commit**

```bash
git add skill-pack/src/paiw_skill_pack/scanner.py skill-pack/tests/test_scanner.py skill-pack/tests/fixtures/scanner
git commit -m "test: add public package privacy scanner"
```

---

### Task 5: Build standalone skills by deterministic vendoring

**Files:**
- Create: `skill-pack/src/paiw_skill_pack/build.py`
- Create: `skill-pack/tests/test_build.py`
- Create: `skill-pack/tests/fixtures/minimal-skill/SKILL.md`
- Create: `skill-pack/tests/fixtures/minimal-skill/agents/openai.yaml`
- Create: `skill-pack/tests/fixtures/minimal-skill/references/local.md`

**Interfaces:**
- Produces: `build_skill(source_root, shared_root, destination_root, version) -> Path`.
- Consumes: source skill directory and `skills/_shared`.

- [ ] **Step 1: Write the failing deterministic-build test**

```python
# skill-pack/tests/test_build.py
from pathlib import Path

from paiw_skill_pack.build import build_skill, hash_tree

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[2]


def test_build_vendors_shared_contract_and_is_deterministic(tmp_path: Path) -> None:
    first = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills" / "_shared",
        tmp_path / "first",
        "0.1.0-beta.1",
    )
    second = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills" / "_shared",
        tmp_path / "second",
        "0.1.0-beta.1",
    )

    assert (first / "references/shared/contract/governance.md").is_file()
    assert (first / "references/shared/schemas/context-briefing.schema.json").is_file()
    assert (first / "VERSION").read_text().strip() == "0.1.0-beta.1"
    assert hash_tree(first) == hash_tree(second)
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_build.py -v
```

Expected: import failure for `paiw_skill_pack.build`.

- [ ] **Step 3: Implement deterministic copying**

```python
# skill-pack/src/paiw_skill_pack/build.py
from __future__ import annotations

import hashlib
from pathlib import Path
import shutil


def _copy_tree(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())


def build_skill(source_root: Path, shared_root: Path, destination_root: Path, version: str) -> Path:
    skill_name = source_root.name
    destination = destination_root / skill_name
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    _copy_tree(source_root, destination)
    _copy_tree(shared_root / "contract", destination / "references" / "shared" / "contract")
    _copy_tree(shared_root / "schemas", destination / "references" / "shared" / "schemas")
    (destination / "VERSION").write_text(version + "\n", encoding="utf-8")
    return destination


def hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
```

- [ ] **Step 4: Add a minimal fixture skill**

```markdown
<!-- skill-pack/tests/fixtures/minimal-skill/SKILL.md -->
---
name: minimal-skill
description: Use when validating the deterministic Skill Pack builder. Do not use for live Workspace operations.
---

# Minimal Skill

Read `references/local.md` and the vendored shared governance contract.
```

```yaml
# skill-pack/tests/fixtures/minimal-skill/agents/openai.yaml
interface:
  display_name: "Minimal Skill"
  short_description: "Builder fixture"
policy:
  allow_implicit_invocation: false
```

```markdown
<!-- skill-pack/tests/fixtures/minimal-skill/references/local.md -->
# Local fixture reference
```

- [ ] **Step 5: Rerun build tests**

```bash
python -m pytest skill-pack/tests/test_build.py -v
```

Expected: `1 passed`.

- [ ] **Step 6: Commit**

```bash
git add skill-pack/src/paiw_skill_pack/build.py skill-pack/tests/test_build.py skill-pack/tests/fixtures/minimal-skill
git commit -m "feat: build standalone skills deterministically"
```

---

### Task 6: Validate frontmatter, package boundaries, and relative links

**Files:**
- Create: `skill-pack/src/paiw_skill_pack/frontmatter.py`
- Create: `skill-pack/src/paiw_skill_pack/validate.py`
- Create: `skill-pack/tests/test_frontmatter.py`
- Create: `skill-pack/tests/test_validate.py`

**Interfaces:**
- Produces: `parse_skill_frontmatter(text)`, `validate_skill_root(root) -> list[str]`, `assert_valid_skill(root) -> None`.

- [ ] **Step 1: Write failing validation tests**

```python
# skill-pack/tests/test_frontmatter.py
import pytest

from paiw_skill_pack.frontmatter import FrontmatterError, parse_skill_frontmatter


def test_parse_valid_frontmatter() -> None:
    result = parse_skill_frontmatter(
        "---\nname: example\ndescription: Use when testing. Do not use for production.\n---\n# Body\n"
    )
    assert result["name"] == "example"


def test_description_requires_positive_and_negative_boundary() -> None:
    with pytest.raises(FrontmatterError):
        parse_skill_frontmatter(
            "---\nname: example\ndescription: A generic helper.\n---\n# Body\n"
        )
```

```python
# skill-pack/tests/test_validate.py
from pathlib import Path

from paiw_skill_pack.build import build_skill
from paiw_skill_pack.validate import validate_skill_root

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"


def test_built_fixture_is_valid(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    assert validate_skill_root(built) == []


def test_external_parent_reference_is_rejected(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "SKILL.md").write_text(
        (built / "SKILL.md").read_text(encoding="utf-8") + "\nRead [outside](../secret.md).\n",
        encoding="utf-8",
    )
    assert any("escapes skill root" in error for error in validate_skill_root(built))
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_frontmatter.py skill-pack/tests/test_validate.py -v
```

Expected: import failures.

- [ ] **Step 3: Implement frontmatter parsing**

```python
# skill-pack/src/paiw_skill_pack/frontmatter.py
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
```

- [ ] **Step 4: Implement package validation**

```python
# skill-pack/src/paiw_skill_pack/validate.py
from __future__ import annotations

from pathlib import Path
import re

from .frontmatter import FrontmatterError, parse_skill_frontmatter

LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def validate_skill_root(root: Path) -> list[str]:
    errors: list[str] = []
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
                resolved.relative_to(root.resolve())
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
```

- [ ] **Step 5: Run validation tests**

```bash
python -m pytest skill-pack/tests/test_frontmatter.py skill-pack/tests/test_validate.py -v
```

Expected: `4 passed`.

- [ ] **Step 6: Commit**

```bash
git add skill-pack/src/paiw_skill_pack/frontmatter.py skill-pack/src/paiw_skill_pack/validate.py skill-pack/tests/test_frontmatter.py skill-pack/tests/test_validate.py
git commit -m "feat: validate standalone skill packages"
```

---

### Task 7: Package ZIP files and SHA-256 manifests deterministically

**Files:**
- Create: `skill-pack/src/paiw_skill_pack/package.py`
- Create: `skill-pack/tests/test_package.py`

**Interfaces:**
- Produces: `create_deterministic_zip(skill_root, destination) -> Path` and `write_checksums(files, destination) -> Path`.

- [ ] **Step 1: Write failing packaging tests**

```python
# skill-pack/tests/test_package.py
from pathlib import Path
import zipfile

from paiw_skill_pack.build import build_skill
from paiw_skill_pack.package import create_deterministic_zip, write_checksums

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"


def test_zip_is_reproducible(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    first = create_deterministic_zip(built, tmp_path / "first.zip")
    second = create_deterministic_zip(built, tmp_path / "second.zip")
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert archive.testzip() is None
        assert "minimal-skill/SKILL.md" in archive.namelist()


def test_checksum_manifest_is_sorted(tmp_path: Path) -> None:
    a = tmp_path / "a.zip"
    b = tmp_path / "b.zip"
    a.write_bytes(b"a")
    b.write_bytes(b"b")
    output = write_checksums([b, a], tmp_path / "SHA256SUMS.txt")
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0].endswith("  a.zip")
    assert lines[1].endswith("  b.zip")
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_package.py -v
```

Expected: import failure.

- [ ] **Step 3: Implement deterministic ZIP and checksums**

```python
# skill-pack/src/paiw_skill_pack/package.py
from __future__ import annotations

import hashlib
from pathlib import Path
import zipfile

FIXED_TIMESTAMP = (2026, 7, 15, 0, 0, 0)


def create_deterministic_zip(skill_root: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in skill_root.rglob("*") if item.is_file()):
            relative = Path(skill_root.name) / path.relative_to(skill_root)
            info = zipfile.ZipInfo(relative.as_posix(), FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return destination


def write_checksums(files: list[Path], destination: Path) -> Path:
    lines = []
    for path in sorted(files, key=lambda item: item.name):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination
```

- [ ] **Step 4: Rerun packaging tests**

```bash
python -m pytest skill-pack/tests/test_package.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add skill-pack/src/paiw_skill_pack/package.py skill-pack/tests/test_package.py
git commit -m "feat: package reproducible Skill Pack archives"
```

---

### Task 8: Add CLI wrappers and CI validation

**Files:**
- Create: `skill-pack/scripts/build_skill_pack.py`
- Create: `skill-pack/scripts/validate_skill_pack.py`
- Create: `skill-pack/scripts/scan_private_identifiers.py`
- Create: `skill-pack/scripts/package_skill_pack.py`
- Create: `.github/workflows/validate-skill-pack.yml`
- Modify: `skill-pack/README.md`

**Interfaces:**
- Produces stable commands used by later implementation plans and GitHub Actions.

- [ ] **Step 1: Add a failing CLI smoke test**

Create:

```python
# skill-pack/tests/test_cli.py
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_validation_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "skill-pack/scripts/validate_skill_pack.py", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Validate built Personal AI Workspace skills" in result.stdout
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_cli.py -v
```

Expected: failure because the CLI files do not exist.

- [ ] **Step 3: Implement the CLI wrappers**

```python
# skill-pack/scripts/build_skill_pack.py
from __future__ import annotations

import argparse
from pathlib import Path

from paiw_skill_pack.build import build_skill


def main() -> int:
    parser = argparse.ArgumentParser(description="Build standalone Personal AI Workspace skills")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--shared", type=Path, default=Path("skills/_shared"))
    parser.add_argument("--output", type=Path, default=Path("skill-pack/build"))
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    built = build_skill(args.source, args.shared, args.output, args.version)
    print(built)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# skill-pack/scripts/validate_skill_pack.py
from __future__ import annotations

import argparse
from pathlib import Path

from paiw_skill_pack.validate import assert_valid_skill


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate built Personal AI Workspace skills")
    parser.add_argument("roots", type=Path, nargs="+")
    args = parser.parse_args()
    for root in args.roots:
        assert_valid_skill(root)
        print(f"valid: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# skill-pack/scripts/scan_private_identifiers.py
from __future__ import annotations

import argparse
from pathlib import Path

from paiw_skill_pack.scanner import assert_public_safe


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan public Skill Pack files for private data")
    parser.add_argument("root", type=Path)
    parser.add_argument("--public-email", default="michal24749@gmail.com")
    args = parser.parse_args()
    assert_public_safe(args.root, args.public_email)
    print(f"public-safe: {args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# skill-pack/scripts/package_skill_pack.py
from __future__ import annotations

import argparse
from pathlib import Path

from paiw_skill_pack.package import create_deterministic_zip, write_checksums


def main() -> int:
    parser = argparse.ArgumentParser(description="Package Personal AI Workspace skills")
    parser.add_argument("roots", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, default=Path("skill-pack/dist"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    archives = [
        create_deterministic_zip(root, args.output / f"{root.name}.zip")
        for root in args.roots
    ]
    write_checksums(archives, args.output / "SHA256SUMS.txt")
    for archive in archives:
        print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Add CI**

```yaml
# .github/workflows/validate-skill-pack.yml
name: Validate Skill Pack

on:
  pull_request:
    paths:
      - "skills/**"
      - "skill-pack/**"
      - "pyproject.toml"
      - ".github/workflows/validate-skill-pack.yml"
  push:
    branches: [main]
    paths:
      - "skills/**"
      - "skill-pack/**"
      - "pyproject.toml"

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: python -m pip install -e '.[dev]'
      - run: python -m pytest -v
      - run: python skill-pack/scripts/scan_private_identifiers.py skills
```

- [ ] **Step 5: Update the tooling README**

Append:

```markdown
## Stable commands

```bash
python skill-pack/scripts/build_skill_pack.py --source skills/personal-ai-workspace-installer-upgrader --version 0.1.0-beta.1
python skill-pack/scripts/validate_skill_pack.py skill-pack/build/personal-ai-workspace-installer-upgrader
python skill-pack/scripts/scan_private_identifiers.py skill-pack/build
python skill-pack/scripts/package_skill_pack.py skill-pack/build/personal-ai-workspace-installer-upgrader
```
```

- [ ] **Step 6: Run the complete foundation suite**

```bash
python -m pytest -v
python skill-pack/scripts/scan_private_identifiers.py skills
```

Expected: every test passes and scanner prints `public-safe: skills`.

- [ ] **Step 7: Commit**

```bash
git add skill-pack/scripts skill-pack/tests/test_cli.py skill-pack/README.md .github/workflows/validate-skill-pack.yml
git commit -m "ci: validate and package public Skill Pack sources"
```

---

## Final Foundation Verification

- [ ] Run all foundation tests:

```bash
python -m pytest skill-pack/tests -v
```

Expected: all tests pass.

- [ ] Run package privacy scan:

```bash
python skill-pack/scripts/scan_private_identifiers.py skills
```

Expected: no findings.

- [ ] Confirm no active Google Tasks reference exists in new Skill Pack source:

```bash
if grep -Rni --exclude-dir=.git --exclude='*.patch' 'Google Tasks' skills skill-pack; then
  echo 'Unexpected active Google Tasks reference' >&2
  exit 1
fi
```

Expected: command exits `0` without matches.

- [ ] Confirm deterministic output by building the minimal fixture twice and comparing hashes through `test_build.py`.

- [ ] Review the foundation against the approved architecture specification, especially Sections 7–10, 27–31, and 36.
