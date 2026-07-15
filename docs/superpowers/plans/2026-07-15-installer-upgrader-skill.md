# Personal AI Workspace Installer & Upgrader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Agent Skill that safely detects, installs, repairs, or upgrades Personal AI Workspace through available connectors while preserving user data, feature choices, attribution, and exact-scope owner control.

**Architecture:** The skill is instruction-led and connector-orchestrating. Deterministic Python scripts classify supplied discovery reports, resolve migration paths, calculate idempotency keys, render approval previews, and generate handover text; scripts never call cloud services directly. Installation and migration instructions use semantic capabilities, evidence-linked state detection, sequential migration manifests, connector readback, and rollback checkpoints.

**Tech Stack:** Agent Skills (`SKILL.md`, `agents/openai.yaml`), Markdown references, Python 3.11+, JSON, JSON Schema, pytest, shared Skill Pack tooling from the foundation plan.

## Global Constraints

- Implement only after the foundation plan is merged and passing.
- Skill directory name and frontmatter name are exactly `personal-ai-workspace-installer-upgrader`.
- `allow_implicit_invocation` is `false`.
- No structural write occurs before exact-scope owner approval.
- Unknown newer framework versions remain read-only and are never downgraded automatically.
- Reruns are idempotent and must not create duplicate canonical pages, databases, tasks, migrations, or feature records.
- Active Google Tasks recommendations and connector branches are prohibited.
- GitHub Issues are the recommended external task backend; Notion Task Outbox is the canonical ledger and fallback.
- Final persistent artifacts follow the verified Google Drive upload policy when enabled and available; upload failure leaves the workflow visibly incomplete.
- No public package contains private Emma Workspace identifiers, private account data, personal contacts, private repositories, or secrets.
- The skill does not modify Michał's private live Workspace during public development or testing.
- Every task uses TDD and ends with a focused commit.

---

## File Map

```text
skills/personal-ai-workspace-installer-upgrader/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── capability-audit.md
│   ├── discovery-and-classification.md
│   ├── fresh-install.md
│   ├── migration-and-repair.md
│   ├── approval-and-readback.md
│   ├── feature-registry.md
│   ├── artifact-and-handover.md
│   └── installation-signatures.json
├── scripts/
│   ├── classify_installation.py
│   ├── generate_anchor_text.py
│   ├── idempotency_key.py
│   ├── render_blueprint.py
│   └── resolve_migration_path.py
└── tests/
    ├── fixtures/
    │   ├── not-installed.json
    │   ├── partial.json
    │   ├── installed-supported.json
    │   ├── installed-unknown.json
    │   ├── damaged.json
    │   └── capability-report.json
    ├── test_anchor_text.py
    ├── test_blueprint.py
    ├── test_classifier.py
    ├── test_idempotency.py
    ├── test_migration_path.py
    ├── test_routing_contract.py
    └── test_skill_contract.py
skill-pack/migrations/
├── index.json
├── 1.0-to-1.1/
├── 1.1-to-1.2/
├── 1.2-to-1.3/
├── 1.3-to-1.4/
├── 1.4-to-1.5/
└── 1.5-to-1.5.1/
```

---

### Task 1: Create the skill skeleton and routing contract

**Files:**
- Create: `skills/personal-ai-workspace-installer-upgrader/SKILL.md`
- Create: `skills/personal-ai-workspace-installer-upgrader/agents/openai.yaml`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_routing_contract.py`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py`

**Interfaces:**
- Produces: exact skill identity, activation boundaries, and package-level contract used by the build validator.

- [ ] **Step 1: Write failing routing tests**

```python
# skills/personal-ai-workspace-installer-upgrader/tests/test_routing_contract.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_frontmatter_has_precise_positive_and_negative_boundaries() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "name: personal-ai-workspace-installer-upgrader" in text
    assert "Use when installing, detecting, repairing, migrating, or upgrading Personal AI Workspace" in text
    assert "Do not use for normal daily Workspace updates or conversation startup briefings" in text


def test_installer_requires_explicit_invocation() -> None:
    text = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
    assert "allow_implicit_invocation: false" in text
```

```python
# skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_reference_names_are_declared() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for name in [
        "capability-audit.md",
        "discovery-and-classification.md",
        "fresh-install.md",
        "migration-and-repair.md",
        "approval-and-readback.md",
        "feature-registry.md",
        "artifact-and-handover.md",
    ]:
        assert name in text


def test_safety_boundaries_are_explicit() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
    for phrase in [
        "exact-scope owner approval",
        "readback",
        "unknown newer version",
        "do not downgrade",
        "no background execution",
        "do not use google tasks",
    ]:
        assert phrase in text
```

- [ ] **Step 2: Run tests and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_routing_contract.py skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py -v
```

Expected: failure because skill files do not exist.

- [ ] **Step 3: Create the skill entry files**

```markdown
<!-- skills/personal-ai-workspace-installer-upgrader/SKILL.md -->
---
name: personal-ai-workspace-installer-upgrader
description: Use when installing, detecting, repairing, migrating, or upgrading Personal AI Workspace. Trigger for fresh setup, existing-workspace discovery, version checks, partial installations, damaged installations, migration plans, and creator upgrades. Do not use for normal daily Workspace updates or conversation startup briefings.
---

# Personal AI Workspace Installer & Upgrader

## Required references

Read the vendored shared contracts, then read:

- `references/capability-audit.md`
- `references/discovery-and-classification.md`
- `references/fresh-install.md`
- `references/migration-and-repair.md`
- `references/approval-and-readback.md`
- `references/feature-registry.md`
- `references/artifact-and-handover.md`

## Non-negotiable boundaries

- Audit semantic connector capabilities and account identity before assuming access.
- Classify the installation from evidence, never from one title alone.
- Obtain exact-scope owner approval before every structural write.
- Verify every connector-backed write by readback.
- Treat an unknown newer version as read-only; do not downgrade it.
- Do not use Google Tasks as an active backend.
- Do not claim background execution without a real automation.
- Do not store hidden chain-of-thought, credentials, tokens, passwords, reset links, or one-time codes.
- Keep the Markdown creator available as the universal fallback.

## Workflow

1. Capability and account audit.
2. Evidence-linked discovery.
3. Installation-state classification.
4. Fresh-install, repair, upgrade, or read-only recommendation.
5. Full blueprint or migration preview.
6. Exact-scope owner approval.
7. Connector-backed operations in dependency order.
8. Readback, verification, and rollback when required.
9. Handover, personalization text, project instructions, and artifact archive status.
```

```yaml
# skills/personal-ai-workspace-installer-upgrader/agents/openai.yaml
interface:
  display_name: "Personal AI Workspace Installer & Upgrader"
  short_description: "Install, detect, repair, or upgrade Personal AI Workspace safely"
  brand_color: "#EA580C"
  default_prompt: "Inspect my environment and prepare a safe Personal AI Workspace installation or upgrade plan."
policy:
  allow_implicit_invocation: false
```

Create each required reference as a one-line placeholder-free scope declaration so package validation can proceed before later tasks fill it:

```markdown
# Capability Audit

Defines semantic capability and account checks performed before discovery.
```

Use the matching title and one-sentence purpose for every listed reference file.

- [ ] **Step 4: Rerun routing tests**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_routing_contract.py skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Validate package source**

```bash
python skill-pack/scripts/scan_private_identifiers.py skills/personal-ai-workspace-installer-upgrader
```

Expected: `public-safe`.

- [ ] **Step 6: Commit**

```bash
git add skills/personal-ai-workspace-installer-upgrader
git commit -m "feat: scaffold installer-upgrader skill"
```

---

### Task 2: Implement evidence-based installation classification

**Files:**
- Create: `skills/personal-ai-workspace-installer-upgrader/scripts/classify_installation.py`
- Create: `skills/personal-ai-workspace-installer-upgrader/references/installation-signatures.json`
- Replace: `skills/personal-ai-workspace-installer-upgrader/references/discovery-and-classification.md`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_classifier.py`
- Create: five installation-state fixture JSON files

**Interfaces:**
- Consumes: normalized discovery JSON.
- Produces: installation report matching `installation-report.schema.json`.
- Function: `classify_installation(discovery: dict, supported_versions: set[str]) -> dict`.

- [ ] **Step 1: Write failing classifier tests**

```python
# skills/personal-ai-workspace-installer-upgrader/tests/test_classifier.py
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/classify_installation.py"
FIXTURES = Path(__file__).parent / "fixtures"


def load_module():
    spec = importlib.util.spec_from_file_location("classify_installation", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("not-installed.json", "NOT_INSTALLED"),
        ("partial.json", "PARTIAL"),
        ("installed-supported.json", "INSTALLED_SUPPORTED"),
        ("installed-unknown.json", "INSTALLED_UNKNOWN"),
        ("damaged.json", "DAMAGED"),
    ],
)
def test_classifies_installation_states(fixture: str, expected: str) -> None:
    module = load_module()
    discovery = json.loads((FIXTURES / fixture).read_text(encoding="utf-8"))
    report = module.classify_installation(
        discovery,
        {"1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.5.1"},
    )
    assert report["state"] == expected
    assert report["reason"]
    assert report["coverage"] in {"FULL", "PARTIAL", "DEGRADED"}
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_classifier.py -v
```

Expected: file-not-found or import failure.

- [ ] **Step 3: Implement the classifier**

```python
# skills/personal-ai-workspace-installer-upgrader/scripts/classify_installation.py
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CORE_KEYS = {"constitution", "start_here", "module_00", "workspace_index"}


def classify_installation(discovery: dict[str, Any], supported_versions: set[str]) -> dict[str, Any]:
    matched = sorted(key for key, value in discovery.get("artifacts", {}).items() if value.get("present"))
    missing = sorted(CORE_KEYS - set(matched))
    conflicts = sorted(discovery.get("conflicts", []))
    coverage = discovery.get("coverage", "PARTIAL")
    version = discovery.get("framework_version")

    severe_conflict_prefixes = (
        "duplicate-canonical-constitution",
        "incompatible-property-type",
        "identity-conflict",
        "interrupted-migration-ambiguous",
    )
    if any(conflict.startswith(severe_conflict_prefixes) for conflict in conflicts):
        state = "DAMAGED"
        reason = "Canonical structure is contradictory or unsafe to mutate."
        confidence = "HIGH"
    elif not matched:
        state = "NOT_INSTALLED"
        reason = "No convincing Personal AI Workspace artifacts were found."
        confidence = "HIGH" if coverage == "FULL" else "MEDIUM"
    elif missing:
        state = "PARTIAL"
        reason = "Some Workspace artifacts exist, but required core components are missing."
        confidence = "HIGH" if coverage != "DEGRADED" else "MEDIUM"
    elif version in supported_versions:
        state = "INSTALLED_SUPPORTED"
        reason = "Required core components and a supported framework version were detected."
        confidence = "HIGH"
    else:
        state = "INSTALLED_UNKNOWN"
        reason = "A complete Workspace appears present, but its version is unsupported or unknown."
        confidence = "MEDIUM"

    return {
        "state": state,
        "confidence": confidence,
        "framework_version": version,
        "matched": matched,
        "missing": missing,
        "conflicts": conflicts,
        "coverage": coverage,
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify a Personal AI Workspace discovery report")
    parser.add_argument("discovery", type=Path)
    parser.add_argument("--supported", nargs="+", required=True)
    args = parser.parse_args()
    payload = json.loads(args.discovery.read_text(encoding="utf-8"))
    print(json.dumps(classify_installation(payload, set(args.supported)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Add public-safe fixtures**

```json
// tests/fixtures/not-installed.json
{"coverage":"FULL","framework_version":null,"artifacts":{},"conflicts":[]}
```

```json
// tests/fixtures/partial.json
{
  "coverage":"FULL",
  "framework_version":null,
  "artifacts":{"constitution":{"present":true,"url":"https://notion.example/constitution"}},
  "conflicts":[]
}
```

```json
// tests/fixtures/installed-supported.json
{
  "coverage":"FULL",
  "framework_version":"1.5.1",
  "artifacts":{
    "constitution":{"present":true,"url":"https://notion.example/constitution"},
    "start_here":{"present":true,"url":"https://notion.example/start"},
    "module_00":{"present":true,"url":"https://notion.example/module-00"},
    "workspace_index":{"present":true,"url":"https://notion.example/index"}
  },
  "conflicts":[]
}
```

Use the same complete artifact set with version `2.0` for `installed-unknown.json`. Use the same complete set plus conflict `duplicate-canonical-constitution:2` for `damaged.json`.

- [ ] **Step 5: Add discovery signatures**

```json
// references/installation-signatures.json
{
  "constitution": {
    "title_patterns": ["Workspace Constitution", "modular Constitution"],
    "required_markers": ["Start Here", "module 00", "owner approval"]
  },
  "start_here": {
    "title_patterns": ["Start Here"],
    "required_markers": ["Workspace Constitution", "required modules"]
  },
  "module_00": {
    "title_patterns": ["00 —", "00 -"],
    "required_markers": ["reading protocol", "module selection"]
  },
  "workspace_index": {
    "title_patterns": ["Workspace Index"],
    "required_properties": ["Name", "Page URL", "Index Status"]
  }
}
```

- [ ] **Step 6: Replace discovery documentation**

```markdown
# Discovery and classification

Discover by account identity, content markers and schema signatures—never by private IDs or one title alone. Search Constitution candidates, Start Here, module 00, version metadata, core databases, Feature & Integration Registry, Task Outbox, System Evolution Lab, duplicates and customizations. Produce an evidence-linked normalized discovery JSON, then run `scripts/classify_installation.py`. `INSTALLED_UNKNOWN` and `DAMAGED` are read-only until a separately approved migration or recovery plan exists.
```

- [ ] **Step 7: Rerun tests and validate report schema**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_classifier.py -v
python skills/personal-ai-workspace-installer-upgrader/scripts/classify_installation.py \
  skills/personal-ai-workspace-installer-upgrader/tests/fixtures/installed-supported.json \
  --supported 1.0 1.1 1.2 1.3 1.4 1.5 1.5.1 \
  > /tmp/installation-report.json
python - <<'PY'
import json
from paiw_skill_pack.schemas import validate_payload
validate_payload("installation-report", json.load(open("/tmp/installation-report.json", encoding="utf-8")))
print("valid installation report")
PY
```

Expected: tests pass and schema validation prints `valid installation report`.

- [ ] **Step 8: Commit**

```bash
git add skills/personal-ai-workspace-installer-upgrader/scripts/classify_installation.py skills/personal-ai-workspace-installer-upgrader/references skills/personal-ai-workspace-installer-upgrader/tests
git commit -m "feat: classify existing Workspace installations"
```

---

### Task 3: Define capability and account audit behavior

**Files:**
- Replace: `skills/personal-ai-workspace-installer-upgrader/references/capability-audit.md`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/fixtures/capability-report.json`
- Extend: `skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py`

**Interfaces:**
- Produces normalized capability report consumed before discovery.

- [ ] **Step 1: Add failing contract assertions**

```python
# append to test_skill_contract.py
def test_capability_audit_blocks_wrong_account_and_never_invents_tools() -> None:
    text = (ROOT / "references/capability-audit.md").read_text(encoding="utf-8").lower()
    for phrase in [
        "semantic capability",
        "account_mismatch",
        "stop operations",
        "do not invent",
        "read-only",
        "reduced scope",
    ]:
        assert phrase in text
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py::test_capability_audit_blocks_wrong_account_and_never_invents_tools -v
```

Expected: assertion failure against the short scaffold text.

- [ ] **Step 3: Write the capability audit reference**

```markdown
# Capability and account audit

Before discovery, map available connector tools to the vendored semantic capability model. Record each capability as `AVAILABLE_READ_WRITE`, `AVAILABLE_READ_ONLY`, `UNAVAILABLE`, `UNAUTHORIZED`, `ACCOUNT_MISMATCH`, `DEGRADED`, or `UNKNOWN`.

For each service:

1. read the connected identity when the tool supports it;
2. compare observed and user-approved expected identity;
3. on `ACCOUNT_MISMATCH`, stop operations for that service and report both identities;
4. do not invent unavailable tools, permissions, connector writes, or background execution;
5. continue with reduced scope only when the resulting classification or operation remains truthful and safe;
6. a read-only connector may support discovery but cannot authorize an installation or migration that requires writes;
7. schema-changing work requires the separate `notion.schema.modify` capability;
8. Drive completion requires both `drive.file.upload` and `drive.file.readback`.

Minimum discovery capability: `notion.content.read`. Minimum fresh-install capability: `notion.content.read`, `notion.content.write`, and the creation/schema capabilities required by the approved blueprint.
```

- [ ] **Step 4: Add a valid fixture and schema test**

```json
// tests/fixtures/capability-report.json
{
  "generated_at": "2026-07-15T09:00:00Z",
  "capabilities": [
    {"capability":"notion.content.read","state":"AVAILABLE_READ_WRITE","detail":"Fictional connector"},
    {"capability":"notion.content.write","state":"AVAILABLE_READ_WRITE","detail":"Fictional connector"},
    {"capability":"drive.file.upload","state":"UNAVAILABLE","detail":"No upload tool"}
  ]
}
```

Add:

```python
# append to test_skill_contract.py
import json
from paiw_skill_pack.schemas import validate_payload


def test_capability_fixture_matches_shared_schema() -> None:
    payload = json.loads((ROOT / "tests/fixtures/capability-report.json").read_text(encoding="utf-8"))
    validate_payload("capability-report", payload)
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add skills/personal-ai-workspace-installer-upgrader/references/capability-audit.md skills/personal-ai-workspace-installer-upgrader/tests
git commit -m "docs: define installer capability audit"
```

---

### Task 4: Implement migration manifests and path resolution

**Files:**
- Create: `skill-pack/migrations/index.json`
- Create: six migration directories with `migration.json`, `preconditions.md`, `operations.md`, `validation.md`, `rollback.md`
- Create: `skills/personal-ai-workspace-installer-upgrader/scripts/resolve_migration_path.py`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_migration_path.py`
- Replace: `skills/personal-ai-workspace-installer-upgrader/references/migration-and-repair.md`

**Interfaces:**
- Produces: `resolve_path(index, source, target) -> list[str]` and validated migration manifests.

- [ ] **Step 1: Write failing path tests**

```python
# skills/personal-ai-workspace-installer-upgrader/tests/test_migration_path.py
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills/personal-ai-workspace-installer-upgrader/scripts/resolve_migration_path.py"
INDEX = ROOT / "skill-pack/migrations/index.json"


def load_module():
    spec = importlib.util.spec_from_file_location("resolve_migration_path", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_resolves_sequential_path() -> None:
    module = load_module()
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    assert module.resolve_path(index, "1.2", "1.5.1") == [
        "1.2-to-1.3",
        "1.3-to-1.4",
        "1.4-to-1.5",
        "1.5-to-1.5.1",
    ]


def test_refuses_unknown_target() -> None:
    module = load_module()
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="no migration path"):
        module.resolve_path(index, "1.5.1", "2.0")
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_migration_path.py -v
```

Expected: missing script or index.

- [ ] **Step 3: Add the migration index**

```json
// skill-pack/migrations/index.json
{
  "target": "1.5.1",
  "migrations": [
    {"id":"1.0-to-1.1","from":"1.0","to":"1.1","path":"1.0-to-1.1/migration.json"},
    {"id":"1.1-to-1.2","from":"1.1","to":"1.2","path":"1.1-to-1.2/migration.json"},
    {"id":"1.2-to-1.3","from":"1.2","to":"1.3","path":"1.2-to-1.3/migration.json"},
    {"id":"1.3-to-1.4","from":"1.3","to":"1.4","path":"1.3-to-1.4/migration.json"},
    {"id":"1.4-to-1.5","from":"1.4","to":"1.5","path":"1.4-to-1.5/migration.json"},
    {"id":"1.5-to-1.5.1","from":"1.5","to":"1.5.1","path":"1.5-to-1.5.1/migration.json"}
  ]
}
```

- [ ] **Step 4: Implement path resolution**

```python
# scripts/resolve_migration_path.py
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def resolve_path(index: dict[str, Any], source: str, target: str) -> list[str]:
    by_source = {item["from"]: item for item in index["migrations"]}
    current = source
    path: list[str] = []
    visited: set[str] = set()
    while current != target:
        if current in visited or current not in by_source:
            raise ValueError(f"no migration path from {source} to {target}")
        visited.add(current)
        migration = by_source[current]
        path.append(migration["id"])
        current = migration["to"]
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve a sequential Personal AI Workspace migration path")
    parser.add_argument("index", type=Path)
    parser.add_argument("source")
    parser.add_argument("target")
    args = parser.parse_args()
    payload = json.loads(args.index.read_text(encoding="utf-8"))
    print("\n".join(resolve_path(payload, args.source, args.target)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Create all six migration packages**

For each directory, use a concrete manifest matching the shared schema. Example for `1.4-to-1.5`:

```json
{
  "id": "1.4-to-1.5",
  "from": "1.4",
  "to": "1.5",
  "destructive": false,
  "requires": ["notion.content.read", "notion.content.write", "notion.database.create"],
  "preconditions": ["single-canonical-constitution", "version-is-1.4"],
  "operations": ["add-sensitive-context-policy", "create-system-evolution-lab"],
  "validations": ["constitution-readback", "lab-schema-valid", "workspace-index-updated"],
  "rollback": "archive-created-lab-and-restore-constitution-snapshot"
}
```

Use these operation sets for the remaining manifests:

```text
1.0-to-1.1: create-creators-page, add-attribution-links
1.1-to-1.2: create-about-page, add-first-response-manifest
1.2-to-1.3: create-modular-constitution, migrate-rules-to-modules, verify-no-truncation
1.3-to-1.4: add-structure-governance, add-personalization-and-project-snippets
1.5-to-1.5.1: add-evolution-review-due-check
```

Each directory receives explicit `preconditions.md`, `operations.md`, `validation.md`, and `rollback.md` that name every operation from its manifest and state that unknown local customizations are preserved unless the approved plan says otherwise.

- [ ] **Step 6: Add migration-manifest validation to the test**

Append:

```python
from paiw_skill_pack.schemas import validate_payload


def test_all_migration_manifests_are_valid() -> None:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    for item in index["migrations"]:
        manifest = json.loads((INDEX.parent / item["path"]).read_text(encoding="utf-8"))
        validate_payload("migration-manifest", manifest)
```

- [ ] **Step 7: Write the migration and repair reference**

```markdown
# Migration and repair

Resolve only declared sequential migration paths. Before execution, read each manifest, confirm preconditions, show the combined operation list, identify preserved customizations, create a rollback checkpoint, and obtain exact-scope approval. Execute one migration at a time, write an implementation result after each step, and stop on readback failure. `INSTALLED_UNKNOWN` is read-only. `DAMAGED` requires a recovery plan that preserves evidence and does not silently choose among duplicate canonical records.
```

- [ ] **Step 8: Run tests**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_migration_path.py -v
```

Expected: all tests pass.

- [ ] **Step 9: Commit**

```bash
git add skill-pack/migrations skills/personal-ai-workspace-installer-upgrader/scripts/resolve_migration_path.py skills/personal-ai-workspace-installer-upgrader/references/migration-and-repair.md skills/personal-ai-workspace-installer-upgrader/tests/test_migration_path.py
git commit -m "feat: add versioned migration manifests"
```

---

### Task 5: Render exact-scope blueprint and approval previews

**Files:**
- Create: `skills/personal-ai-workspace-installer-upgrader/scripts/render_blueprint.py`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_blueprint.py`
- Replace: `skills/personal-ai-workspace-installer-upgrader/references/approval-and-readback.md`

**Interfaces:**
- Consumes: JSON with current state, target state, operations, preserved items, risks, rollback, verification.
- Produces: Markdown approval preview.

- [ ] **Step 1: Write failing blueprint test**

```python
# tests/test_blueprint.py
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/render_blueprint.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_blueprint", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_blueprint_contains_exact_scope_and_approval_boundary() -> None:
    module = load_module()
    text = module.render_blueprint(
        {
            "current_state": "PARTIAL",
            "target_state": "1.5.1",
            "operations": ["Create module 00", "Repair Workspace Index"],
            "preserved": ["Existing Knowledge records"],
            "risks": ["Broken local links"],
            "rollback": ["Archive newly created pages", "Restore Constitution snapshot"],
            "verification": ["Fetch module 00", "Query Workspace Index"],
        }
    )
    assert "## Exact structural scope" in text
    assert "Create module 00" in text
    assert "Existing Knowledge records" in text
    assert "Approval covers only the scope shown above" in text
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_blueprint.py -v
```

Expected: missing script.

- [ ] **Step 3: Implement renderer**

```python
# scripts/render_blueprint.py
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) or "- None"


def render_blueprint(payload: dict[str, Any]) -> str:
    return f"""# Personal AI Workspace change preview

## Current and target state

- Current state: `{payload['current_state']}`
- Target framework version: `{payload['target_state']}`

## Exact structural scope

{_bullets(payload['operations'])}

## Preserved data and customizations

{_bullets(payload['preserved'])}

## Risks and counterarguments

{_bullets(payload['risks'])}

## Rollback checkpoint

{_bullets(payload['rollback'])}

## Verification plan

{_bullets(payload['verification'])}

> Approval covers only the scope shown above. Any newly discovered page, database, property, integration, automation, migration, or materially different consequence requires re-confirmation.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render an exact-scope Workspace blueprint")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    print(render_blueprint(json.loads(args.input.read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Replace approval and readback reference**

```markdown
# Approval and readback

Before a structural write, present the rendered blueprint with current state, target state, exact operations, preserved data, risks, rollback and verification. Ask for explicit approval of that exact scope. Silence, general trust, prior unrelated approval, or permission to maintain data is not structural approval. Stop and request re-confirmation on scope expansion. After every write, read the created or changed object and verify identity, parent, critical properties, links and expected content before continuing dependent operations.
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_blueprint.py -v
```

Expected: `1 passed`.

- [ ] **Step 6: Commit**

```bash
git add skills/personal-ai-workspace-installer-upgrader/scripts/render_blueprint.py skills/personal-ai-workspace-installer-upgrader/tests/test_blueprint.py skills/personal-ai-workspace-installer-upgrader/references/approval-and-readback.md
git commit -m "feat: render exact-scope installation previews"
```

---

### Task 6: Add stable idempotency keys and operation ledger rules

**Files:**
- Create: `skills/personal-ai-workspace-installer-upgrader/scripts/idempotency_key.py`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_idempotency.py`
- Extend: `skills/personal-ai-workspace-installer-upgrader/references/migration-and-repair.md`

**Interfaces:**
- Produces: `idempotency_key(workspace_identity, migration_id, operation_key) -> str`.

- [ ] **Step 1: Write failing key tests**

```python
# tests/test_idempotency.py
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/idempotency_key.py"


def load_module():
    spec = importlib.util.spec_from_file_location("idempotency_key", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_key_is_stable_and_does_not_expose_identity() -> None:
    module = load_module()
    first = module.idempotency_key("fictional-workspace", "1.4-to-1.5", "create-system-evolution-lab")
    second = module.idempotency_key("fictional-workspace", "1.4-to-1.5", "create-system-evolution-lab")
    assert first == second
    assert first.startswith("paiw:")
    assert "fictional-workspace" not in first


def test_different_operation_has_different_key() -> None:
    module = load_module()
    assert module.idempotency_key("w", "m", "a") != module.idempotency_key("w", "m", "b")
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_idempotency.py -v
```

Expected: missing script.

- [ ] **Step 3: Implement stable keys**

```python
# scripts/idempotency_key.py
from __future__ import annotations

import argparse
import hashlib


def idempotency_key(workspace_identity: str, migration_id: str, operation_key: str) -> str:
    material = "\x1f".join([workspace_identity.strip(), migration_id.strip(), operation_key.strip()])
    return "paiw:" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a stable Workspace migration idempotency key")
    parser.add_argument("workspace_identity")
    parser.add_argument("migration_id")
    parser.add_argument("operation_key")
    args = parser.parse_args()
    print(idempotency_key(args.workspace_identity, args.migration_id, args.operation_key))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Add operation-ledger instructions**

Append to `migration-and-repair.md`:

```markdown
## Operation ledger

Before creating an object, compute the stable idempotency key from Workspace identity, migration ID and operation key. Search the migration ledger and canonical destination for that key. If a verified completed operation exists, reuse it. If an incomplete operation exists, resume from its last verified step. Never create a second canonical artifact merely because the first run was interrupted.
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_idempotency.py -v
git add skills/personal-ai-workspace-installer-upgrader/scripts/idempotency_key.py skills/personal-ai-workspace-installer-upgrader/tests/test_idempotency.py skills/personal-ai-workspace-installer-upgrader/references/migration-and-repair.md
git commit -m "feat: add migration idempotency keys"
```

---

### Task 7: Implement Feature Registry and fresh-install instructions

**Files:**
- Replace: `skills/personal-ai-workspace-installer-upgrader/references/feature-registry.md`
- Replace: `skills/personal-ai-workspace-installer-upgrader/references/fresh-install.md`
- Extend: `skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py`

**Interfaces:**
- Produces instruction contract for optional modules and approved fresh installation order.

- [ ] **Step 1: Add failing assertions**

```python
# append to test_skill_contract.py
def test_feature_registry_never_silently_enables_optional_features() -> None:
    text = (ROOT / "references/feature-registry.md").read_text(encoding="utf-8").lower()
    for phrase in [
        "disabled by user",
        "pending setup",
        "paused",
        "degraded",
        "never silently enable",
        "does not delete historical data",
    ]:
        assert phrase in text


def test_fresh_install_requires_blueprint_before_first_write() -> None:
    text = (ROOT / "references/fresh-install.md").read_text(encoding="utf-8").lower()
    for phrase in [
        "before the first structural write",
        "complete blueprint",
        "exact-scope approval",
        "dependency order",
        "readback",
        "cleanup test data",
    ]:
        assert phrase in text
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py -v
```

Expected: the new assertions fail.

- [ ] **Step 3: Write Feature Registry instructions**

```markdown
# Feature & Integration Registry

Required states are `Enabled`, `Disabled by User`, `Unavailable`, `Pending Setup`, `Paused`, and `Degraded`. Record a stable key, core/optional class, owner decision, capabilities, dependencies, read/write scope, activation, deactivation, retention while disabled, missed-sync behavior, affected modules and health state.

Never silently enable an optional feature during installation or upgrade. Disabling stops future feature reads, writes and automations but does not delete historical data. Re-enabling verifies identity, capabilities, dependencies and missed synchronization scope before activity resumes. Core requirements and optional features are shown separately in the blueprint.
```

- [ ] **Step 4: Write fresh-install instructions**

```markdown
# Fresh installation

1. Audit capabilities and accounts.
2. Ask which optional modules and integrations the owner wants.
3. Render the complete blueprint before the first structural write.
4. Obtain exact-scope approval.
5. Create the root, modular Constitution, Start Here and module registry.
6. Create approved databases in dependency order.
7. Create the Feature & Integration Registry.
8. Create About and creator-attribution pages.
9. Configure only enabled integrations.
10. Create clearly marked disposable test data only when required by verification.
11. Verify every object by readback and remove disposable test data.
12. Generate personalization and project instructions using the actual Constitution title and URL.
13. Generate handover and archive artifacts.
14. Record an implementation result and review date.

If the user declines the blueprint, stop without writes. If the approved blueprint changes during implementation, stop and obtain re-confirmation.
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py -v
git add skills/personal-ai-workspace-installer-upgrader/references skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py
git commit -m "docs: define fresh install and feature configuration"
```

---

### Task 8: Generate personalization and project-instruction anchors

**Files:**
- Create: `skills/personal-ai-workspace-installer-upgrader/scripts/generate_anchor_text.py`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_anchor_text.py`

**Interfaces:**
- Produces: `personalization_text(title, url)` and `project_text(title, url)`.

- [ ] **Step 1: Write failing anchor tests**

```python
# tests/test_anchor_text.py
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/generate_anchor_text.py"


def load_module():
    spec = importlib.util.spec_from_file_location("generate_anchor_text", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_personalization_text_uses_real_title_url_and_connector_name() -> None:
    module = load_module()
    text = module.personalization_text("Example Constitution", "https://notion.example/constitution")
    assert "through the Notion connector" in text
    assert "Example Constitution" in text
    assert "https://notion.example/constitution" in text
    assert "[" not in text


def test_project_text_requires_every_new_conversation() -> None:
    module = load_module()
    text = module.project_text("Example Constitution", "https://notion.example/constitution")
    assert "At the start of every new conversation in this project" in text
    assert "without exception" in text
    assert "through the Notion connector" in text
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_anchor_text.py -v
```

Expected: missing script.

- [ ] **Step 3: Implement anchor generation**

```python
# scripts/generate_anchor_text.py
from __future__ import annotations

import argparse


def personalization_text(title: str, url: str) -> str:
    return f'''Before every significant task concerning me, my projects, decisions, relationships, tasks, or files, load the document “{title}” through the Notion connector:\n\n{url}\n\nThen load Start Here, module 00, and every Constitution module relevant to the task. If the Notion connector is unavailable, the wrong account is connected, or any document is incomplete or truncated, tell me explicitly and do not pretend the read was complete.'''


def project_text(title: str, url: str) -> str:
    return f'''At the start of every new conversation in this project—without exception, always as the first action—load the document “{title}” through the Notion connector:\n\n{url}\n\nThen load Start Here, module 00, and every Constitution module relevant to the expected conversation scope. Do not begin substantive work before attempting this read. If the connector is unavailable, the wrong account is connected, or any document is incomplete or truncated, say so explicitly.'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Personal AI Workspace anchor text")
    parser.add_argument("title")
    parser.add_argument("url")
    parser.add_argument("--mode", choices=["personalization", "project"], required=True)
    args = parser.parse_args()
    function = personalization_text if args.mode == "personalization" else project_text
    print(function(args.title, args.url))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_anchor_text.py -v
git add skills/personal-ai-workspace-installer-upgrader/scripts/generate_anchor_text.py skills/personal-ai-workspace-installer-upgrader/tests/test_anchor_text.py
git commit -m "feat: generate installation anchor instructions"
```

---

### Task 9: Define handover and mandatory Drive artifact status

**Files:**
- Replace: `skills/personal-ai-workspace-installer-upgrader/references/artifact-and-handover.md`
- Extend: `skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py`

**Interfaces:**
- Produces explicit completion statuses and handover fields.

- [ ] **Step 1: Add failing handover assertions**

```python
# append to test_skill_contract.py
def test_handover_distinguishes_technical_success_from_archive_completion() -> None:
    text = (ROOT / "references/artifact-and-handover.md").read_text(encoding="utf-8")
    for phrase in [
        "COMPLETE",
        "ARTIFACT_ARCHIVE_INCOMPLETE",
        "BLOCKED",
        "file ID",
        "parent folder",
        "do not substitute",
    ]:
        assert phrase in text
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py::test_handover_distinguishes_technical_success_from_archive_completion -v
```

Expected: assertion failure.

- [ ] **Step 3: Write artifact and handover instructions**

```markdown
# Artifact and handover

Generate a dated handover report containing installation state, versions, verified account identities, enabled and unavailable features, canonical links, migration operations, readback results, personalization text, project text, rollback instructions, unresolved blockers and support path.

When Drive artifact archival is enabled, a final persistent artifact is complete only after upload and readback verify the exact final file, file ID, final name, MIME type, parent folder, accessible URL and checksum or size when available.

Completion statuses:

- `COMPLETE` — connector work and required artifact archive verified;
- `ARTIFACT_ARCHIVE_INCOMPLETE` — Workspace work verified, but exact final artifact could not be uploaded or read back;
- `BLOCKED` — required connector operation or verification failed.

On archive failure, provide the local artifact, state the exact limitation, create a follow-up task, and never claim it is on Drive. Do not substitute a Google Doc for a ZIP, PDF, XLSX, PPTX or another exact artifact unless the owner approves that alternative.
```

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py -v
git add skills/personal-ai-workspace-installer-upgrader/references/artifact-and-handover.md skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py
git commit -m "docs: define installer handover completion gate"
```

---

### Task 10: Add full fixture matrix and dry-run contract test

**Files:**
- Extend all installer fixtures with artifact maps, versions, conflicts, feature states and capability coverage
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_dry_run_contract.py`
- Modify: `skills/personal-ai-workspace-installer-upgrader/SKILL.md`

**Interfaces:**
- Produces complete dry-run evidence that routing, classification, migration selection, approval, and output contracts agree.

- [ ] **Step 1: Write failing dry-run test**

```python
# tests/test_dry_run_contract.py
import importlib.util
import json
from pathlib import Path

from paiw_skill_pack.schemas import validate_payload

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_supported_upgrade_dry_run() -> None:
    classifier = load_script("classify_installation")
    resolver = load_script("resolve_migration_path")
    renderer = load_script("render_blueprint")

    discovery = json.loads((FIXTURES / "installed-supported.json").read_text(encoding="utf-8"))
    report = classifier.classify_installation(discovery, {"1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.5.1"})
    validate_payload("installation-report", report)
    assert report["state"] == "INSTALLED_SUPPORTED"

    index = json.loads((Path(__file__).resolve().parents[3] / "skill-pack/migrations/index.json").read_text(encoding="utf-8"))
    path = resolver.resolve_path(index, "1.4", "1.5.1")
    assert path == ["1.4-to-1.5", "1.5-to-1.5.1"]

    preview = renderer.render_blueprint(
        {
            "current_state": "1.4",
            "target_state": "1.5.1",
            "operations": path,
            "preserved": ["Existing records", "Disabled feature states"],
            "risks": ["Local customization conflict"],
            "rollback": ["Restore checkpoint"],
            "verification": ["Read Constitution", "Validate Evolution Lab", "Verify due-check"],
        }
    )
    assert "Approval covers only" in preview
    assert "1.4-to-1.5" in preview
```

- [ ] **Step 2: Run and observe the intended fixture mismatch**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_dry_run_contract.py -v
```

Expected: failure because the supported fixture currently reports version `1.5.1`, not `1.4`.

- [ ] **Step 3: Change the supported-upgrade fixture to version 1.4**

Keep a second fixture `installed-current.json` at `1.5.1` and add it to the classifier parameter matrix with expected state `INSTALLED_SUPPORTED`.

- [ ] **Step 4: Expand SKILL.md workflow detail**

Add explicit branches:

```markdown
## State handling

- `NOT_INSTALLED`: prepare a fresh-install blueprint.
- `PARTIAL`: map existing artifacts, preserve valid work, and prepare a repair plan.
- `INSTALLED_SUPPORTED`: report current status or resolve sequential migrations to the target.
- `INSTALLED_UNKNOWN`: remain read-only and prepare a compatibility report.
- `DAMAGED`: preserve conflicting evidence and prepare a recovery plan; do not choose a canonical winner silently.
```

- [ ] **Step 5: Run all installer tests**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests -v
```

Expected: all tests pass.

- [ ] **Step 6: Build and validate the standalone skill**

```bash
python skill-pack/scripts/build_skill_pack.py \
  --source skills/personal-ai-workspace-installer-upgrader \
  --version 0.1.0-beta.1
python skill-pack/scripts/validate_skill_pack.py \
  skill-pack/build/personal-ai-workspace-installer-upgrader
python skill-pack/scripts/scan_private_identifiers.py \
  skill-pack/build/personal-ai-workspace-installer-upgrader
```

Expected: valid and public-safe.

- [ ] **Step 7: Commit**

```bash
git add skills/personal-ai-workspace-installer-upgrader
git commit -m "test: complete installer-upgrader dry-run matrix"
```

---

## Final Installer Verification

- [ ] Run all Skill Pack and installer tests:

```bash
python -m pytest skill-pack/tests skills/personal-ai-workspace-installer-upgrader/tests -v
```

- [ ] Build twice and verify deterministic tree hashes.
- [ ] Validate all migration manifests.
- [ ] Confirm no active Google Tasks path:

```bash
if grep -Rni --exclude='*.patch' 'Google Tasks' skills/personal-ai-workspace-installer-upgrader skill-pack/migrations; then
  echo 'Active Google Tasks path found' >&2
  exit 1
fi
```

- [ ] Confirm package scan returns no private identifier finding.
- [ ] Confirm `INSTALLED_UNKNOWN` and `DAMAGED` paths never reach execution without a new approved plan.
- [ ] Confirm final ZIP contains only the skill root and internal references.
