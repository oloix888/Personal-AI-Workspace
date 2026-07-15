# Personal AI Workspace Context Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Agent Skill that loads Personal AI Workspace at conversation start and produces a compact, truthful, source-linked briefing covering all active tasks and the highest-value current operational state.

**Architecture:** The skill is read-only by default. Connector instructions load Constitution, feature state, canonical active records, and relevant source detail; deterministic Python scripts normalize records, reconcile conflicts, calculate freshness, enforce a context budget, redact unnecessary sensitive detail, and render human-readable or JSON briefings. Every active task appears at least as a compact index row, while archival detail is fetched on demand.

**Tech Stack:** Agent Skills, Markdown references, Python 3.11+, JSON, pytest, shared Skill Pack schemas and build tooling.

## Global Constraints

- Implement after the foundation plan is merged and before integration/release work.
- Skill directory and frontmatter name are exactly `personal-ai-workspace-context-bootstrap`.
- `allow_implicit_invocation` is `true`, but Personalization and project instructions remain the reliable new-conversation trigger.
- The skill never installs, migrates, repairs, or structurally changes a Workspace.
- Default behavior is read-only; optional cache writes require a separately approved workflow and readback.
- Every active A/B/C and recurring task must appear at least as a compact index row.
- No silent omission when context limits are reached.
- Default briefing target is 8,000 tokens or fewer; use `TASK_INDEX_MODE` and numbered continuations when required.
- Connector coverage, staleness, truncation, conflicts, and unavailable sources are reported explicitly.
- Feature & Integration Registry states are respected.
- Sensitive context is included only when operationally necessary and at minimum detail; authentication secrets are never included.
- Active Google Tasks paths are prohibited.
- No public package may contain private identifiers or personal data.
- Every task follows TDD and ends with a focused commit.

---

## File Map

```text
skills/personal-ai-workspace-context-bootstrap/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── constitution-loading.md
│   ├── source-and-precedence.md
│   ├── task-normalization.md
│   ├── freshness-and-coverage.md
│   ├── context-budget.md
│   ├── sensitive-context.md
│   └── briefing-format.md
├── scripts/
│   ├── apply_budget.py
│   ├── classify_freshness.py
│   ├── normalize_tasks.py
│   ├── reconcile_tasks.py
│   ├── redact_sensitive.py
│   └── render_briefing.py
└── tests/
    ├── fixtures/
    │   ├── empty.json
    │   ├── normal.json
    │   ├── many-tasks.json
    │   ├── conflicts.json
    │   ├── stale.json
    │   ├── partial.json
    │   ├── disabled-features.json
    │   ├── reviews-and-risks.json
    │   └── sensitive.json
    ├── test_budget.py
    ├── test_freshness.py
    ├── test_normalize_tasks.py
    ├── test_reconcile_tasks.py
    ├── test_redaction.py
    ├── test_render_briefing.py
    ├── test_routing_contract.py
    ├── test_skill_contract.py
    └── test_end_to_end.py
```

---

### Task 1: Create the skill skeleton and activation boundaries

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/SKILL.md`
- Create: `skills/personal-ai-workspace-context-bootstrap/agents/openai.yaml`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_routing_contract.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_skill_contract.py`

**Interfaces:**
- Produces the exact skill identity and read-only workflow contract.

- [ ] **Step 1: Write failing routing tests**

```python
# tests/test_routing_contract.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_frontmatter_has_positive_and_negative_boundaries() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "name: personal-ai-workspace-context-bootstrap" in text
    assert "Use at the beginning of a new conversation" in text
    assert "Do not use for installation, migration, repair, or structural changes" in text


def test_bootstrap_allows_implicit_invocation() -> None:
    text = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
    assert "allow_implicit_invocation: true" in text
```

```python
# tests/test_skill_contract.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_references_are_declared() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for name in [
        "constitution-loading.md",
        "source-and-precedence.md",
        "task-normalization.md",
        "freshness-and-coverage.md",
        "context-budget.md",
        "sensitive-context.md",
        "briefing-format.md",
    ]:
        assert name in text


def test_bootstrap_is_read_only_and_truthful() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
    for phrase in [
        "read-only by default",
        "all active tasks",
        "no silent omission",
        "partial coverage",
        "truncation",
        "do not use google tasks",
    ]:
        assert phrase in text
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_routing_contract.py skills/personal-ai-workspace-context-bootstrap/tests/test_skill_contract.py -v
```

Expected: failure because the skill files do not exist.

- [ ] **Step 3: Create the skill entry files**

```markdown
<!-- SKILL.md -->
---
name: personal-ai-workspace-context-bootstrap
description: Use at the beginning of a new conversation, or when the user asks for current Workspace context, active tasks, priorities, commitments, project state, pending reviews, risks, or a briefing. Load Personal AI Workspace Constitution first, then build a compact source-linked operational briefing. Do not use for installation, migration, repair, or structural changes.
---

# Personal AI Workspace Context Bootstrap

## Required references

Read the vendored shared contracts, then read:

- `references/constitution-loading.md`
- `references/source-and-precedence.md`
- `references/task-normalization.md`
- `references/freshness-and-coverage.md`
- `references/context-budget.md`
- `references/sensitive-context.md`
- `references/briefing-format.md`

## Boundaries

- Verify the Notion identity before reading personal Workspace data.
- Load Constitution, Start Here, module 00, Feature & Integration Registry, and relevant modules.
- The skill is read-only by default.
- Include all active tasks at least as compact index rows.
- Use no silent omission; report partial coverage, unavailable sources and truncation.
- Do not use Google Tasks as an active source or backend.
- Do not install, repair, migrate, or change structure.
- Do not include authentication secrets or unnecessary sensitive detail.
- Do not claim background execution.

## Workflow

1. Verify identity and Constitution loading.
2. Read feature state and determine enabled sources.
3. Query canonical active-state sources.
4. Normalize records and reconcile conflicts.
5. Calculate freshness and source coverage.
6. Apply context budget without silently dropping active tasks.
7. Render a source-linked briefing.
8. Fetch deeper records only when relevant to the opening request.
```

```yaml
# agents/openai.yaml
interface:
  display_name: "Personal AI Workspace Context Bootstrap"
  short_description: "Load current tasks, projects, commitments, reviews, risks, and feature state"
  brand_color: "#F59E0B"
  default_prompt: "Load my Personal AI Workspace and brief me on the current operational state."
policy:
  allow_implicit_invocation: true
```

Create each reference file with its exact heading and a one-sentence scope statement.

- [ ] **Step 4: Rerun tests**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_routing_contract.py skills/personal-ai-workspace-context-bootstrap/tests/test_skill_contract.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Scan and commit**

```bash
python skill-pack/scripts/scan_private_identifiers.py skills/personal-ai-workspace-context-bootstrap
git add skills/personal-ai-workspace-context-bootstrap
git commit -m "feat: scaffold context-bootstrap skill"
```

---

### Task 2: Normalize task records from canonical source payloads

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/normalize_tasks.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_normalize_tasks.py`
- Replace: `skills/personal-ai-workspace-context-bootstrap/references/task-normalization.md`

**Interfaces:**
- Consumes normalized connector-export rows, not live connectors.
- Produces task dictionaries with fields: `id`, `title`, `priority`, `status`, `execution_owner`, `outcome_or_description`, `due_date`, `blocked_by`, `waiting_for_confirmation`, `source`, `backend_url`, `last_updated`, `freshness`, `recurring`.
- Function: `normalize_task(record: dict, source_name: str) -> dict`.

- [ ] **Step 1: Write failing normalization tests**

```python
# tests/test_normalize_tasks.py
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/normalize_tasks.py"


def load_module():
    spec = importlib.util.spec_from_file_location("normalize_tasks", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_normalizes_notion_task_outbox_record() -> None:
    module = load_module()
    task = module.normalize_task(
        {
            "task_id": "TOB-42",
            "title": "[SHARED][B][DOCS] Publish guide",
            "priority": "B",
            "status": "Synced",
            "owner": "Shared",
            "reason": "Publish a stable installation guide.",
            "due_date": "2026-07-20",
            "blocked_by": [],
            "needs_confirmation": False,
            "url": "https://notion.example/task-42",
            "backend_url": "https://github.example/issues/42",
            "last_edited": "2026-07-15T08:00:00Z",
            "recurrence_rule": "",
        },
        "notion-task-outbox",
    )
    assert task["id"] == "TOB-42"
    assert task["priority"] == "B"
    assert task["execution_owner"] == "Shared"
    assert task["source"]["system"] == "notion-task-outbox"
    assert task["recurring"] is False


def test_rejects_unknown_priority() -> None:
    module = load_module()
    with pytest.raises(ValueError, match="priority"):
        module.normalize_task(
            {
                "task_id": "x",
                "title": "Invalid",
                "priority": "URGENTISH",
                "status": "Open",
                "owner": "User",
                "last_edited": "2026-07-15T08:00:00Z",
            },
            "fixture",
        )
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_normalize_tasks.py -v
```

Expected: missing script.

- [ ] **Step 3: Implement task normalization**

```python
# scripts/normalize_tasks.py
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VALID_PRIORITIES = {"A", "B", "C"}


def normalize_task(record: dict[str, Any], source_name: str) -> dict[str, Any]:
    priority = str(record.get("priority", "")).upper()
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"invalid task priority: {priority}")
    title = str(record.get("title", "")).strip()
    if not title:
        raise ValueError("task title is required")
    identifier = str(record.get("task_id") or record.get("id") or record.get("url") or title)
    recurrence_rule = str(record.get("recurrence_rule", "")).strip()
    return {
        "id": identifier,
        "title": title,
        "priority": priority,
        "status": str(record.get("status", "Unknown")),
        "execution_owner": str(record.get("owner", "Unknown")),
        "outcome_or_description": str(record.get("reason") or record.get("description") or ""),
        "due_date": record.get("due_date"),
        "blocked_by": list(record.get("blocked_by", [])),
        "waiting_for_confirmation": bool(record.get("needs_confirmation", False)),
        "source": {"system": source_name, "url": record.get("url")},
        "backend_url": record.get("backend_url"),
        "last_updated": record.get("last_edited") or record.get("updated_at"),
        "freshness": "UNKNOWN",
        "recurring": bool(recurrence_rule),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Personal AI Workspace task records")
    parser.add_argument("input", type=Path)
    parser.add_argument("--source", required=True)
    args = parser.parse_args()
    records = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps([normalize_task(item, args.source) for item in records], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Write normalization reference**

```markdown
# Task normalization

Represent every active A/B/C and recurring task with stable ID, title, priority, status, execution owner, outcome or description, due date, blockers, confirmation state, source URL, backend URL, last update and freshness. GitHub labels and title prefixes may help discover priority and ownership, but canonical field mappings come from the configured Feature & Integration Registry. Historical closed tasks are included only when recently completed or relevant.
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_normalize_tasks.py -v
git add skills/personal-ai-workspace-context-bootstrap/scripts/normalize_tasks.py skills/personal-ai-workspace-context-bootstrap/tests/test_normalize_tasks.py skills/personal-ai-workspace-context-bootstrap/references/task-normalization.md
git commit -m "feat: normalize active task records"
```

---

### Task 3: Reconcile task states without silently choosing a winner

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/reconcile_tasks.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_reconcile_tasks.py`
- Replace: `skills/personal-ai-workspace-context-bootstrap/references/source-and-precedence.md`

**Interfaces:**
- Consumes normalized task records plus field-level precedence configuration.
- Produces reconciled records and conflict objects.
- Function: `reconcile_task(records: list[dict], precedence: dict[str, list[str]]) -> tuple[dict, list[dict]]`.

- [ ] **Step 1: Write failing reconciliation tests**

```python
# tests/test_reconcile_tasks.py
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/reconcile_tasks.py"


def load_module():
    spec = importlib.util.spec_from_file_location("reconcile_tasks", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def record(system: str, status: str, updated: str) -> dict:
    return {
        "id": "task-42",
        "title": "Publish guide",
        "priority": "B",
        "status": status,
        "execution_owner": "Shared",
        "outcome_or_description": "Publish a guide",
        "due_date": None,
        "blocked_by": [],
        "waiting_for_confirmation": False,
        "source": {"system": system, "url": f"https://{system}.example/42"},
        "backend_url": None,
        "last_updated": updated,
        "freshness": "FRESH",
        "recurring": False,
    }


def test_configured_status_precedence_resolves_status_only() -> None:
    module = load_module()
    merged, conflicts = module.reconcile_task(
        [record("notion-task-outbox", "Synced", "2026-07-15T08:00:00Z"), record("github-issues", "Closed", "2026-07-15T08:05:00Z")],
        {"status": ["github-issues", "notion-task-outbox"]},
    )
    assert merged["status"] == "Closed"
    assert conflicts == []


def test_missing_precedence_surfaces_conflict() -> None:
    module = load_module()
    merged, conflicts = module.reconcile_task(
        [record("notion-task-outbox", "Synced", "2026-07-15T08:00:00Z"), record("github-issues", "Open", "2026-07-15T08:05:00Z")],
        {},
    )
    assert merged["status"] == "CONFLICTING_STATE"
    assert conflicts[0]["field"] == "status"
    assert len(conflicts[0]["values"]) == 2
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_reconcile_tasks.py -v
```

Expected: missing script.

- [ ] **Step 3: Implement field-level reconciliation**

```python
# scripts/reconcile_tasks.py
from __future__ import annotations

from copy import deepcopy
from typing import Any

RECONCILED_FIELDS = [
    "title",
    "priority",
    "status",
    "execution_owner",
    "outcome_or_description",
    "due_date",
    "blocked_by",
    "waiting_for_confirmation",
    "backend_url",
    "last_updated",
    "recurring",
]


def _source_rank(system: str, order: list[str]) -> int:
    try:
        return order.index(system)
    except ValueError:
        return len(order)


def reconcile_task(records: list[dict[str, Any]], precedence: dict[str, list[str]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not records:
        raise ValueError("at least one task record is required")
    merged = deepcopy(records[0])
    merged["sources"] = [record["source"] for record in records]
    conflicts: list[dict[str, Any]] = []

    for field in RECONCILED_FIELDS:
        unique = []
        for record in records:
            value = record.get(field)
            if value not in unique:
                unique.append(value)
        if len(unique) <= 1:
            merged[field] = unique[0] if unique else None
            continue
        order = precedence.get(field, [])
        if order:
            selected = min(records, key=lambda item: _source_rank(item["source"]["system"], order))
            merged[field] = selected.get(field)
            continue
        merged[field] = "CONFLICTING_STATE" if field == "status" else records[0].get(field)
        conflicts.append(
            {
                "task_id": merged["id"],
                "field": field,
                "values": [
                    {
                        "value": record.get(field),
                        "source": record["source"],
                        "last_updated": record.get("last_updated"),
                    }
                    for record in records
                ],
            }
        )
    return merged, conflicts
```

- [ ] **Step 4: Write source and precedence reference**

```markdown
# Source and precedence

Source priority is configured per field in the Feature & Integration Registry; it is not globally hard-coded. A common task mapping is: Task Outbox for definition and provenance, GitHub Issue for execution state and closure, Calendar for a real time block only. When sources disagree and no field-level precedence resolves the difference, preserve all values, timestamps and source URLs, mark `CONFLICTING_STATE`, and surface high-impact conflicts. Never silently choose a winner.
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_reconcile_tasks.py -v
git add skills/personal-ai-workspace-context-bootstrap/scripts/reconcile_tasks.py skills/personal-ai-workspace-context-bootstrap/tests/test_reconcile_tasks.py skills/personal-ai-workspace-context-bootstrap/references/source-and-precedence.md
git commit -m "feat: reconcile conflicting task sources"
```

---

### Task 4: Calculate freshness and source coverage

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/classify_freshness.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_freshness.py`
- Replace: `skills/personal-ai-workspace-context-bootstrap/references/freshness-and-coverage.md`

**Interfaces:**
- Produces: `classify_freshness(last_updated, now, fresh_hours, stale_hours) -> str` and coverage header rules.

- [ ] **Step 1: Write failing freshness tests**

```python
# tests/test_freshness.py
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/classify_freshness.py"


def load_module():
    spec = importlib.util.spec_from_file_location("classify_freshness", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_freshness_thresholds() -> None:
    module = load_module()
    now = datetime(2026, 7, 15, 12, tzinfo=timezone.utc)
    assert module.classify_freshness("2026-07-15T10:00:00Z", now, 24, 72) == "FRESH"
    assert module.classify_freshness("2026-07-13T12:00:00Z", now, 24, 72) == "AGING"
    assert module.classify_freshness("2026-07-10T12:00:00Z", now, 24, 72) == "STALE"
    assert module.classify_freshness(None, now, 24, 72) == "UNKNOWN"
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_freshness.py -v
```

Expected: missing script.

- [ ] **Step 3: Implement freshness classification**

```python
# scripts/classify_freshness.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def classify_freshness(last_updated: Optional[str], now: datetime, fresh_hours: int, stale_hours: int) -> str:
    if not last_updated:
        return "UNKNOWN"
    age_hours = (now.astimezone(timezone.utc) - _parse(last_updated)).total_seconds() / 3600
    if age_hours <= fresh_hours:
        return "FRESH"
    if age_hours <= stale_hours:
        return "AGING"
    return "STALE"
```

- [ ] **Step 4: Write freshness and coverage reference**

```markdown
# Freshness and coverage

Each source and normalized record is `FRESH`, `AGING`, `STALE`, or `UNKNOWN` using configurable thresholds. `last refreshed` is the time of the actual successful source read, never merely response-generation time. Coverage is `FULL`, `PARTIAL`, or `DEGRADED` and lists checked, unavailable and truncated sources. A stale record may be displayed only with its stale marker and source date. Never claim a complete Workspace or mailbox scan when pagination, authorization or connector coverage is partial.
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_freshness.py -v
git add skills/personal-ai-workspace-context-bootstrap/scripts/classify_freshness.py skills/personal-ai-workspace-context-bootstrap/tests/test_freshness.py skills/personal-ai-workspace-context-bootstrap/references/freshness-and-coverage.md
git commit -m "feat: classify briefing freshness and coverage"
```

---

### Task 5: Enforce context budget and TASK_INDEX_MODE

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/apply_budget.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_budget.py`
- Replace: `skills/personal-ai-workspace-context-bootstrap/references/context-budget.md`

**Interfaces:**
- Produces: `apply_budget(briefing, max_tokens, estimator) -> dict` with mode `FULL_DETAIL`, `TASK_INDEX_MODE`, or `CONTINUATION_REQUIRED`.

- [ ] **Step 1: Write failing budget tests**

```python
# tests/test_budget.py
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/apply_budget.py"


def load_module():
    spec = importlib.util.spec_from_file_location("apply_budget", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def tasks(count: int) -> list[dict]:
    return [
        {
            "id": f"T-{index}",
            "title": f"Task {index}",
            "priority": "B",
            "status": "Open",
            "execution_owner": "Shared",
            "outcome_or_description": "x" * 500,
            "due_date": None,
            "blocked_by": [],
            "waiting_for_confirmation": False,
            "source": {"system": "fixture", "url": None},
            "backend_url": None,
            "last_updated": "2026-07-15T08:00:00Z",
            "freshness": "FRESH",
            "recurring": False,
        }
        for index in range(count)
    ]


def test_switches_to_task_index_without_dropping_tasks() -> None:
    module = load_module()
    result = module.apply_budget({"tasks": tasks(20), "projects": [], "commitments": [], "reviews": [], "risks": [], "contradictions": [], "recent_material_changes": [], "high_value_facts": []}, 800, lambda text: len(text) // 4)
    assert result["mode"] == "TASK_INDEX_MODE"
    assert len(result["briefing"]["tasks"]) == 20
    assert all("outcome_or_description" not in task for task in result["briefing"]["tasks"])


def test_marks_continuation_when_even_index_exceeds_budget() -> None:
    module = load_module()
    result = module.apply_budget({"tasks": tasks(200), "projects": [], "commitments": [], "reviews": [], "risks": [], "contradictions": [], "recent_material_changes": [], "high_value_facts": []}, 100, lambda text: len(text) // 4)
    assert result["mode"] == "CONTINUATION_REQUIRED"
    assert result["total_task_count"] == 200
    assert result["included_task_count"] < 200
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_budget.py -v
```

Expected: missing script.

- [ ] **Step 3: Implement budget logic**

```python
# scripts/apply_budget.py
from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Callable

INDEX_FIELDS = ["id", "title", "priority", "status", "execution_owner", "due_date", "blocked_by", "waiting_for_confirmation", "backend_url", "freshness", "recurring"]


def _tokens(payload: dict[str, Any], estimator: Callable[[str], int]) -> int:
    return estimator(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def apply_budget(briefing: dict[str, Any], max_tokens: int, estimator: Callable[[str], int]) -> dict[str, Any]:
    full = deepcopy(briefing)
    if _tokens(full, estimator) <= max_tokens:
        return {"mode": "FULL_DETAIL", "briefing": full, "total_task_count": len(full.get("tasks", [])), "included_task_count": len(full.get("tasks", []))}

    indexed = deepcopy(briefing)
    indexed["tasks"] = [{key: task.get(key) for key in INDEX_FIELDS} for task in briefing.get("tasks", [])]
    if _tokens(indexed, estimator) <= max_tokens:
        return {"mode": "TASK_INDEX_MODE", "briefing": indexed, "total_task_count": len(indexed["tasks"]), "included_task_count": len(indexed["tasks"])}

    base = deepcopy(indexed)
    base["tasks"] = []
    for task in indexed["tasks"]:
        candidate = deepcopy(base)
        candidate["tasks"] = base["tasks"] + [task]
        if _tokens(candidate, estimator) > max_tokens:
            break
        base["tasks"].append(task)
    return {"mode": "CONTINUATION_REQUIRED", "briefing": base, "total_task_count": len(indexed["tasks"]), "included_task_count": len(base["tasks"])}
```

- [ ] **Step 4: Write budget reference**

```markdown
# Context budget

Target 8,000 tokens or fewer. Reserve up to 75% for tasks when volume is high. Every active task must appear at least as a compact index row. When full descriptions exceed the budget, use `TASK_INDEX_MODE`; load detail on demand. If the compact index still exceeds the available context, use numbered continuations, state total and included counts, and never silently omit tasks. The briefing optimizes for current operational awareness, not archival completeness.
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_budget.py -v
git add skills/personal-ai-workspace-context-bootstrap/scripts/apply_budget.py skills/personal-ai-workspace-context-bootstrap/tests/test_budget.py skills/personal-ai-workspace-context-bootstrap/references/context-budget.md
git commit -m "feat: enforce bootstrap context budget"
```

---

### Task 6: Redact unnecessary sensitive detail while preserving operational pointers

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/redact_sensitive.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_redaction.py`
- Replace: `skills/personal-ai-workspace-context-bootstrap/references/sensitive-context.md`

**Interfaces:**
- Produces: `minimize_sensitive_record(record, include_detail) -> dict`.

- [ ] **Step 1: Write failing redaction tests**

```python
# tests/test_redaction.py
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/redact_sensitive.py"


def load_module():
    spec = importlib.util.spec_from_file_location("redact_sensitive", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_default_returns_pointer_not_private_detail() -> None:
    module = load_module()
    result = module.minimize_sensitive_record(
        {
            "title": "Confidential relationship context",
            "detail": "Private operational detail",
            "sensitivity": "Confidential",
            "epistemic_status": "Reported Claim",
            "confidence": "Medium",
            "source_url": "https://notion.example/confidential-record",
        },
        include_detail=False,
    )
    assert "detail" not in result
    assert result["pointer"] == "https://notion.example/confidential-record"
    assert result["epistemic_status"] == "Reported Claim"


def test_detail_is_allowed_only_when_explicitly_needed() -> None:
    module = load_module()
    result = module.minimize_sensitive_record(
        {
            "title": "Confidential context",
            "detail": "Minimum detail needed for action",
            "sensitivity": "Confidential",
            "epistemic_status": "Fact",
            "confidence": "High",
            "source_url": "https://notion.example/confidential-record",
        },
        include_detail=True,
    )
    assert result["detail"] == "Minimum detail needed for action"
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_redaction.py -v
```

Expected: missing script.

- [ ] **Step 3: Implement minimization**

```python
# scripts/redact_sensitive.py
from __future__ import annotations

from typing import Any

SECRET_FIELDS = {"password", "token", "one_time_code", "reset_link", "api_key", "session_cookie"}


def minimize_sensitive_record(record: dict[str, Any], include_detail: bool) -> dict[str, Any]:
    if SECRET_FIELDS.intersection(record):
        raise ValueError("authentication secrets must not enter the briefing")
    result = {
        "title": record.get("title"),
        "sensitivity": record.get("sensitivity"),
        "epistemic_status": record.get("epistemic_status"),
        "confidence": record.get("confidence"),
        "pointer": record.get("source_url"),
    }
    if include_detail:
        result["detail"] = record.get("detail")
    return result
```

- [ ] **Step 4: Write sensitive-context reference**

```markdown
# Sensitive context

Include sensitive context only when necessary for the current operational state or opening request. Never include authentication secrets. Prefer a redacted pointer to the canonical Confidential record, preserve epistemic status and confidence, and include only the minimum detail required for action. Respect user-disabled sensitive-context loading. Do not externalize private context into shared tasks, public outputs, email or Calendar through this read-only briefing.
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_redaction.py -v
git add skills/personal-ai-workspace-context-bootstrap/scripts/redact_sensitive.py skills/personal-ai-workspace-context-bootstrap/tests/test_redaction.py skills/personal-ai-workspace-context-bootstrap/references/sensitive-context.md
git commit -m "feat: minimize sensitive briefing context"
```

---

### Task 7: Render the human-readable briefing

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/render_briefing.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_render_briefing.py`
- Replace: `skills/personal-ai-workspace-context-bootstrap/references/briefing-format.md`

**Interfaces:**
- Produces: `render_briefing(payload, mode, counts) -> str`.

- [ ] **Step 1: Write failing render tests**

```python
# tests/test_render_briefing.py
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/render_briefing.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_briefing", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_briefing_starts_with_coverage_and_urgent_items() -> None:
    module = load_module()
    text = module.render_briefing(
        {
            "generated_at": "2026-07-15T09:00:00Z",
            "coverage": {"status":"PARTIAL","sources_checked":["Notion"],"sources_unavailable":["GitHub"],"truncated":False,"notes":["GitHub unavailable"]},
            "tasks": [
                {"id":"T-1","title":"Fix blocker","priority":"A","status":"Blocked","execution_owner":"Shared","due_date":"2026-07-14","blocked_by":["Connector"],"waiting_for_confirmation":False,"backend_url":None,"freshness":"FRESH","recurring":False}
            ],
            "projects": [], "commitments": [], "reviews": [], "risks": [], "contradictions": [], "recent_material_changes": [], "high_value_facts": [], "features": []
        },
        "FULL_DETAIL",
        1,
        1,
    )
    assert text.startswith("# Workspace briefing")
    assert "Coverage: PARTIAL" in text
    assert "## Urgent, overdue, and blocked" in text
    assert "Fix blocker" in text
    assert "GitHub unavailable" in text
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_render_briefing.py -v
```

Expected: missing script.

- [ ] **Step 3: Implement Markdown rendering**

```python
# scripts/render_briefing.py
from __future__ import annotations

from datetime import date
from typing import Any


def _task_line(task: dict[str, Any]) -> str:
    due = f" · due {task['due_date']}" if task.get("due_date") else ""
    blocked = f" · blocked by {', '.join(task.get('blocked_by', []))}" if task.get("blocked_by") else ""
    confirmation = " · awaiting confirmation" if task.get("waiting_for_confirmation") else ""
    link = f" · {task['backend_url']}" if task.get("backend_url") else ""
    return f"- **[{task['priority']}] {task['title']}** — {task['status']} · {task['execution_owner']}{due}{blocked}{confirmation} · {task.get('freshness', 'UNKNOWN')}{link}"


def render_briefing(payload: dict[str, Any], mode: str, total_task_count: int, included_task_count: int) -> str:
    coverage = payload["coverage"]
    lines = [
        "# Workspace briefing",
        "",
        f"Generated: {payload['generated_at']}",
        f"Coverage: {coverage['status']} · Mode: {mode} · Tasks: {included_task_count}/{total_task_count}",
        f"Sources checked: {', '.join(coverage['sources_checked']) or 'none'}",
        f"Sources unavailable: {', '.join(coverage['sources_unavailable']) or 'none'}",
    ]
    if coverage.get("notes"):
        lines.extend(["", "Coverage notes:", *[f"- {note}" for note in coverage["notes"]]])

    tasks = payload.get("tasks", [])
    urgent = [task for task in tasks if task.get("priority") == "A" or task.get("status") in {"Blocked", "CONFLICTING_STATE"} or task.get("waiting_for_confirmation")]
    lines.extend(["", "## Urgent, overdue, and blocked", *([_task_line(task) for task in urgent] or ["- None"] )])

    lines.extend(["", "## Active tasks by priority"])
    for priority in ["A", "B", "C"]:
        selected = [task for task in tasks if task.get("priority") == priority]
        lines.append(f"### {priority}")
        lines.extend([_task_line(task) for task in selected] or ["- None"])

    section_map = [
        ("Active projects", "projects"),
        ("Commitments and follow-ups", "commitments"),
        ("Pending reviews", "reviews"),
        ("Critical risks", "risks"),
        ("Unresolved contradictions", "contradictions"),
        ("Recent material changes", "recent_material_changes"),
        ("High-value current facts", "high_value_facts"),
        ("Feature state", "features"),
    ]
    for title, key in section_map:
        lines.extend(["", f"## {title}"])
        values = payload.get(key, [])
        lines.extend([f"- {value if isinstance(value, str) else value.get('title', value.get('key', str(value)))}" for value in values] or ["- None"])

    if mode == "CONTINUATION_REQUIRED":
        lines.extend(["", f"> The task index continues. This part includes {included_task_count} of {total_task_count} active tasks; no omitted task is implied complete or irrelevant."])
    return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Write briefing-format reference**

```markdown
# Briefing format

Default order: coverage and freshness; urgent, overdue and blocked items; A tasks; remaining tasks by priority; blocked and waiting items; active projects; commitments; pending reviews; critical risks and contradictions; recent material changes; disabled or degraded features; source links and deeper-fetch options. Human output remains concise and source-linked. Machine-readable JSON may be emitted when useful and must match the shared context-briefing schema.
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_render_briefing.py -v
git add skills/personal-ai-workspace-context-bootstrap/scripts/render_briefing.py skills/personal-ai-workspace-context-bootstrap/tests/test_render_briefing.py skills/personal-ai-workspace-context-bootstrap/references/briefing-format.md
git commit -m "feat: render operational Workspace briefings"
```

---

### Task 8: Define Constitution loading, enabled-source routing, and read-only behavior

**Files:**
- Replace: `skills/personal-ai-workspace-context-bootstrap/references/constitution-loading.md`
- Extend: `skills/personal-ai-workspace-context-bootstrap/tests/test_skill_contract.py`

**Interfaces:**
- Produces the connector-orchestration instructions around the deterministic scripts.

- [ ] **Step 1: Add failing contract tests**

```python
# append to test_skill_contract.py
def test_constitution_loading_and_feature_routing_are_mandatory() -> None:
    text = (ROOT / "references/constitution-loading.md").read_text(encoding="utf-8").lower()
    for phrase in [
        "constitution index",
        "start here",
        "module 00",
        "feature & integration registry",
        "enabled",
        "disabled by user",
        "truncated",
        "read-only",
    ]:
        assert phrase in text
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_skill_contract.py::test_constitution_loading_and_feature_routing_are_mandatory -v
```

Expected: assertion failure.

- [ ] **Step 3: Write Constitution-loading reference**

```markdown
# Constitution loading and enabled-source routing

1. Verify the expected Notion identity.
2. Load the Constitution index, Start Here and module 00 through the Notion connector.
3. If any required page is unavailable or truncated, report incomplete coverage and do not pretend the read succeeded.
4. Read the Feature & Integration Registry.
5. Query only features in `Enabled` or explicitly approved `Degraded` read mode.
6. Respect `Disabled by User`, `Unavailable`, `Pending Setup`, and `Paused` states.
7. Load domain modules relevant to the opening request and active operational sources.
8. The bootstrap is read-only. A persistent cache refresh or inconsistency record requires a separate approved workflow and readback.
9. Run the due-check for pending Decision Reviews and System Evolution Weekly Reviews without claiming background execution.
```

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_skill_contract.py -v
git add skills/personal-ai-workspace-context-bootstrap/references/constitution-loading.md skills/personal-ai-workspace-context-bootstrap/tests/test_skill_contract.py
git commit -m "docs: define bootstrap source-loading workflow"
```

---

### Task 9: Build end-to-end fixture matrix and canonical JSON output

**Files:**
- Create all fixture JSON files listed in the file map
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_end_to_end.py`
- Modify: `skills/personal-ai-workspace-context-bootstrap/SKILL.md`

**Interfaces:**
- Demonstrates normalization, reconciliation, freshness, redaction, budgeting, schema validation, and rendering together.

- [ ] **Step 1: Create a failing end-to-end test**

```python
# tests/test_end_to_end.py
import importlib.util
import json
from datetime import datetime, timezone
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


def test_normal_fixture_produces_valid_briefing() -> None:
    normalize = load_script("normalize_tasks")
    freshness = load_script("classify_freshness")
    budget = load_script("apply_budget")
    render = load_script("render_briefing")

    fixture = json.loads((FIXTURES / "normal.json").read_text(encoding="utf-8"))
    tasks = [normalize.normalize_task(record, record["source_name"]) for record in fixture["task_records"]]
    now = datetime(2026, 7, 15, 9, tzinfo=timezone.utc)
    for task in tasks:
        task["freshness"] = freshness.classify_freshness(task["last_updated"], now, 24, 72)

    briefing = {
        "generated_at": "2026-07-15T09:00:00Z",
        "workspace": fixture["workspace"],
        "coverage": fixture["coverage"],
        "features": fixture["features"],
        "tasks": tasks,
        "projects": fixture["projects"],
        "commitments": fixture["commitments"],
        "reviews": fixture["reviews"],
        "risks": fixture["risks"],
        "contradictions": fixture["contradictions"],
        "recent_material_changes": fixture["recent_material_changes"],
        "high_value_facts": fixture["high_value_facts"],
    }
    validate_payload("context-briefing", briefing)
    bounded = budget.apply_budget(briefing, 8000, lambda text: len(text) // 4)
    output = render.render_briefing(bounded["briefing"], bounded["mode"], bounded["total_task_count"], bounded["included_task_count"])
    assert "Workspace briefing" in output
    assert "Install public guide" in output
    assert "Coverage: FULL" in output
```

- [ ] **Step 2: Run and observe missing fixture failure**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_end_to_end.py -v
```

Expected: missing `normal.json`.

- [ ] **Step 3: Add `normal.json`**

```json
{
  "workspace": {"title":"Fictional Workspace","framework_version":"1.5.1","constitution_url":"https://notion.example/constitution"},
  "coverage": {"status":"FULL","sources_checked":["Notion","GitHub"],"sources_unavailable":[],"truncated":false,"notes":[]},
  "features": [{"key":"tasks","state":"Enabled"}],
  "task_records": [
    {
      "source_name":"notion-task-outbox",
      "task_id":"TOB-1",
      "title":"[SHARED][B][DOCS] Install public guide",
      "priority":"B",
      "status":"Synced",
      "owner":"Shared",
      "reason":"Publish the installation guide.",
      "due_date":"2026-07-20",
      "blocked_by":[],
      "needs_confirmation":false,
      "url":"https://notion.example/task-1",
      "backend_url":"https://github.example/issues/1",
      "last_edited":"2026-07-15T08:00:00Z",
      "recurrence_rule":""
    }
  ],
  "projects":["Public Skill Pack"],
  "commitments":[],
  "reviews":["Review installer pilot after prerelease"],
  "risks":[],
  "contradictions":[],
  "recent_material_changes":["Architecture specification approved"],
  "high_value_facts":["Markdown creator remains the fallback"]
}
```

- [ ] **Step 4: Add the remaining fixtures**

Use public-safe fictional data and these exact purposes:

```text
empty.json: zero active tasks and full coverage
many-tasks.json: 75 active tasks to trigger TASK_INDEX_MODE
conflicts.json: GitHub Open vs Notion Completed without precedence
stale.json: records older than stale threshold
partial.json: Notion available, GitHub unavailable
 disabled-features.json: Gmail and Calendar disabled by user
reviews-and-risks.json: due Decision Review, Weekly Review, one critical risk
sensitive.json: Confidential pointer with Reported Claim and no authentication secrets
```

- [ ] **Step 5: Add parameterized fixture tests**

Extend `test_end_to_end.py` to assert:

```python
import pytest


@pytest.mark.parametrize("fixture", ["empty.json", "many-tasks.json", "conflicts.json", "stale.json", "partial.json", "disabled-features.json", "reviews-and-risks.json", "sensitive.json"])
def test_fixture_is_public_safe_json(fixture: str) -> None:
    payload = json.loads((FIXTURES / fixture).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    assert "private" not in json.dumps(payload).lower()
```

Add behavior-specific assertions in the existing unit tests rather than duplicating the whole pipeline.

- [ ] **Step 6: Expand SKILL.md output rules**

Add:

```markdown
## Output order

1. Coverage and freshness.
2. Urgent, overdue, blocked, conflicting, and waiting-for-confirmation items.
3. Active A tasks.
4. Remaining active tasks by priority.
5. Projects and commitments.
6. Pending Decision and System Evolution reviews.
7. Critical risks, contradictions, and recent material changes.
8. Disabled or degraded features.
9. Source links and on-demand deeper reads.
```

- [ ] **Step 7: Run all bootstrap tests**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests -v
```

Expected: all tests pass.

- [ ] **Step 8: Build and validate standalone skill**

```bash
python skill-pack/scripts/build_skill_pack.py \
  --source skills/personal-ai-workspace-context-bootstrap \
  --version 0.1.0-beta.1
python skill-pack/scripts/validate_skill_pack.py \
  skill-pack/build/personal-ai-workspace-context-bootstrap
python skill-pack/scripts/scan_private_identifiers.py \
  skill-pack/build/personal-ai-workspace-context-bootstrap
```

Expected: valid and public-safe.

- [ ] **Step 9: Commit**

```bash
git add skills/personal-ai-workspace-context-bootstrap
git commit -m "test: complete context-bootstrap fixture matrix"
```

---

## Final Context Bootstrap Verification

- [ ] Run all Skill Pack and bootstrap tests:

```bash
python -m pytest skill-pack/tests skills/personal-ai-workspace-context-bootstrap/tests -v
```

- [ ] Verify all active tasks appear in normal and index modes.
- [ ] Verify `CONTINUATION_REQUIRED` includes explicit total and included counts.
- [ ] Verify conflicting states preserve source values and URLs.
- [ ] Verify stale records show freshness markers.
- [ ] Verify disabled features are not queried by instruction contract.
- [ ] Verify sensitive fixtures emit pointers and no secret fields.
- [ ] Verify package validation and privacy scan pass.
- [ ] Confirm no active Google Tasks reference exists:

```bash
if grep -Rni --exclude='*.patch' 'Google Tasks' skills/personal-ai-workspace-context-bootstrap; then
  echo 'Active Google Tasks path found' >&2
  exit 1
fi
```

- [ ] Confirm final ZIP contains only the skill root and vendored internal references.
