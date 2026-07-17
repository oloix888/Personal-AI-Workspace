# Context Bootstrap Salience and Personal Focus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the public Context Bootstrap skill with bounded People in Focus, salient events, wellbeing/health snapshot and recently changed memory sections without weakening live-evidence validation or complete active-task coverage.

**Architecture:** Add shared deployment-neutral schemas and deterministic normalization/salience functions, then compose them into the existing Context Bootstrap budgeting and rendering pipeline. Optional personal-context sections receive per-section budgets; active tasks retain hard completeness priority. Connector access remains instruction-led and scripts consume normalized fixture payloads only.

**Tech Stack:** Agent Skills, Python 3.11+, JSON/JSON Schema, pytest, shared `paiw_skill_pack` tooling, Markdown references.

## Global Constraints

- Binding source: `docs/superpowers/specs/2026-07-17-personal-context-and-active-workspace-semantics-addendum.md`.
- Public tracking: `Personal-AI-Workspace#14`; private tracking: `Apex#23`.
- Context Bootstrap remains read-only at startup.
- `FULL` remains current-session live evidence; cached personal context cannot certify its source.
- Every active task remains represented at least as a compact row.
- Default People in Focus maximum is 5; default salient-event maximum is 10.
- Every non-task item requires source and explicit salience reason.
- Wellbeing/health content is minimum necessary detail and owner-only.
- Public fixtures contain fictional data only.
- No release publication or live private-adapter activation is authorized.
- Every task uses TDD, a focused commit, specification review and code-quality review.

---

## File Map

```text
skills/_shared/schemas/
├── bootstrap-person-focus.schema.json
├── bootstrap-salient-event.schema.json
├── bootstrap-wellbeing-snapshot.schema.json
├── bootstrap-memory-change.schema.json
└── bootstrap-salience-reason.schema.json

skills/personal-ai-workspace-context-bootstrap/
├── SKILL.md
├── references/
│   ├── briefing-format.md
│   ├── context-budget.md
│   ├── personal-focus.md
│   ├── salient-events.md
│   ├── wellbeing-health-snapshot.md
│   └── recently-changed-memory.md
├── scripts/
│   ├── select_salient_items.py
│   ├── normalize_people_focus.py
│   ├── normalize_salient_events.py
│   ├── normalize_wellbeing_snapshot.py
│   ├── normalize_memory_changes.py
│   ├── apply_budget.py
│   └── render_briefing.py
└── tests/
    ├── fixtures/
    │   ├── personal-context-empty.json
    │   ├── personal-context-normal.json
    │   ├── personal-context-overloaded.json
    │   ├── personal-context-conflicting.json
    │   ├── personal-context-stale.json
    │   ├── personal-context-sensitive.json
    │   └── personal-context-partial.json
    ├── test_salience.py
    ├── test_people_focus.py
    ├── test_salient_events.py
    ├── test_wellbeing_snapshot.py
    ├── test_memory_changes.py
    ├── test_budget.py
    ├── test_render_briefing.py
    └── test_personal_context_end_to_end.py

docs/CONTEXT-BOOTSTRAP.md
```

---

### Task 1: Define shared personal-context schemas

**Files:**
- Create: `skills/_shared/schemas/bootstrap-salience-reason.schema.json`
- Create: `skills/_shared/schemas/bootstrap-person-focus.schema.json`
- Create: `skills/_shared/schemas/bootstrap-salient-event.schema.json`
- Create: `skills/_shared/schemas/bootstrap-wellbeing-snapshot.schema.json`
- Create: `skills/_shared/schemas/bootstrap-memory-change.schema.json`
- Test: `skill-pack/tests/test_schemas.py`

**Interfaces:**
- Produces JSON Schemas loaded through the existing schema loader.
- All URLs and identifiers are generic strings; no deployment-specific count or private ID is embedded.

- [ ] **Step 1: Add failing schema-registration tests**

```python
from paiw_skill_pack.schemas import load_shared_schema


def test_personal_context_schemas_are_registered() -> None:
    for name in [
        "bootstrap-salience-reason",
        "bootstrap-person-focus",
        "bootstrap-salient-event",
        "bootstrap-wellbeing-snapshot",
        "bootstrap-memory-change",
    ]:
        schema = load_shared_schema(name)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
```

- [ ] **Step 2: Run the focused test**

Run:

```bash
python -m pytest skill-pack/tests/test_schemas.py -v
```

Expected: FAIL because the schemas are missing.

- [ ] **Step 3: Create the salience-reason schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://personal-ai-workspace.example/schemas/bootstrap-salience-reason.schema.json",
  "title": "Bootstrap Salience Reason",
  "type": "string",
  "enum": [
    "explicitly_emphasized",
    "unresolved_commitment",
    "active_relationship_impact",
    "active_project_impact",
    "recurring_pattern",
    "high_emotional_impact",
    "health_or_wellbeing_relevance",
    "blocks_current_decision",
    "recent_material_change",
    "review_due"
  ]
}
```

- [ ] **Step 4: Create person-focus schema**

Required properties:

```json
{
  "person_id": "person-1",
  "name": "Example Person",
  "current_relationship_context": "Close collaborator",
  "salience_reasons": ["unresolved_commitment"],
  "latest_material_interaction": "Discussed launch plan",
  "open_commitment_or_unresolved_state": "Confirm delivery date",
  "next_step": "Follow up",
  "last_verified": "2026-07-17T08:00:00Z",
  "canonical_url": "https://notion.example/person-1",
  "source": {"system": "notion", "url": "https://notion.example/person-1"}
}
```

Set `additionalProperties` to `false` and require every listed property except `next_step`.

- [ ] **Step 5: Create event, wellbeing and memory-change schemas**

Use these required contracts:

```text
salient event:
  event_id, occurred_at, summary, people, projects, impact,
  salience_reasons, source, canonical_url, review_after_or_valid_until

wellbeing snapshot:
  as_of, self_reported_state, observed_changes, active_constraints,
  active_health_changes, follow_ups, canonical_links, source_coverage,
  sensitivity

memory change:
  record_id, operation, changed_at, summary, source, canonical_url
```

Allowed memory-change operations:

```text
CREATE_NEW
AUGMENT_EXISTING
CORRECT_EXISTING
CONTRADICT_EXISTING
SUPERSEDE_EXISTING
```

- [ ] **Step 6: Run schema tests and shared validator tests**

```bash
python -m pytest skill-pack/tests/test_schemas.py skill-pack/tests/test_schema_validation.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add skills/_shared/schemas skill-pack/tests/test_schemas.py
git commit -m "feat: define bootstrap personal-context schemas"
```

---

### Task 2: Implement explicit salience selection

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/select_salient_items.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_salience.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/references/personal-focus.md`

**Interfaces:**
- Produces `select_salient(items: list[dict], *, limit: int, now: datetime) -> list[dict]`.
- Each selected item must already include `salience_reasons`; opaque scores cannot create eligibility.

- [ ] **Step 1: Write failing tests**

```python
from datetime import datetime, timezone

from select_salient_items import select_salient


def test_rejects_item_without_visible_salience_reason() -> None:
    items = [{"id": "x", "updated_at": "2026-07-17T08:00:00Z"}]
    assert select_salient(items, limit=5, now=datetime.now(timezone.utc)) == []


def test_prioritizes_unresolved_and_recent_material_change() -> None:
    items = [
        {"id": "old", "salience_reasons": ["recurring_pattern"], "updated_at": "2026-06-01T08:00:00Z"},
        {"id": "commitment", "salience_reasons": ["unresolved_commitment"], "updated_at": "2026-07-01T08:00:00Z"},
        {"id": "recent", "salience_reasons": ["recent_material_change"], "updated_at": "2026-07-17T08:00:00Z"},
    ]
    selected = select_salient(items, limit=2, now=datetime(2026, 7, 17, tzinfo=timezone.utc))
    assert [item["id"] for item in selected] == ["commitment", "recent"]
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_salience.py -v
```

Expected: missing module.

- [ ] **Step 3: Implement deterministic reason weights**

```python
REASON_WEIGHT = {
    "unresolved_commitment": 100,
    "blocks_current_decision": 95,
    "review_due": 90,
    "health_or_wellbeing_relevance": 85,
    "active_relationship_impact": 80,
    "active_project_impact": 75,
    "explicitly_emphasized": 70,
    "high_emotional_impact": 65,
    "recent_material_change": 60,
    "recurring_pattern": 55,
}
```

Rank by maximum visible reason weight, then newest `updated_at`, then stable `id`. Reject unknown-only or empty reasons with `ValueError` in strict mode and omission in normal rendering mode.

- [ ] **Step 4: Document the rule**

`personal-focus.md` must state:

- transparent reasons are required;
- People in Focus is not a permanent importance ranking;
- sources and last-verified timestamps are mandatory;
- default limit is 5;
- sensitive detail remains in canonical records.

- [ ] **Step 5: Run tests**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_salience.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/personal-ai-workspace-context-bootstrap/scripts/select_salient_items.py skills/personal-ai-workspace-context-bootstrap/tests/test_salience.py skills/personal-ai-workspace-context-bootstrap/references/personal-focus.md
git commit -m "feat: select bootstrap items by explicit salience"
```

---

### Task 3: Normalize People in Focus

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/normalize_people_focus.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_people_focus.py`
- Add fixture data to `personal-context-normal.json` and `personal-context-conflicting.json`

**Interfaces:**
- Produces `normalize_person_focus(record: dict) -> dict`.
- Uses shared person-focus schema.

- [ ] **Step 1: Write failing tests**

```python
from normalize_people_focus import normalize_person_focus


def test_normalizes_person_with_canonical_link() -> None:
    result = normalize_person_focus({
        "id": "p-1",
        "name": "Alex Example",
        "relationship_context": "Client sponsor",
        "reasons": ["active_project_impact"],
        "last_interaction": "Approved scope",
        "open_state": "Waiting for signature",
        "last_verified": "2026-07-17T08:00:00Z",
        "url": "https://notion.example/p-1",
    })
    assert result["person_id"] == "p-1"
    assert result["salience_reasons"] == ["active_project_impact"]


def test_requires_canonical_link_and_source() -> None:
    try:
        normalize_person_focus({"id": "p-1", "name": "Alex", "reasons": ["active_project_impact"]})
    except ValueError as exc:
        assert "canonical" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError")
```

- [ ] **Step 2: Implement minimal normalization**

Normalize aliases without inventing missing values. Preserve unknown optional values as `None`; require identity, name, reasons, last verified and canonical URL.

- [ ] **Step 3: Add conflict fixture**

The fixture includes two relationship-state values with sources and timestamps. The normalized output must mark the entry `CONFLICTING_STATE` and retain both values in `conflicts` rather than selecting silently.

- [ ] **Step 4: Run tests**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_people_focus.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/personal-ai-workspace-context-bootstrap/scripts/normalize_people_focus.py skills/personal-ai-workspace-context-bootstrap/tests/test_people_focus.py skills/personal-ai-workspace-context-bootstrap/tests/fixtures
git commit -m "feat: normalize people in focus"
```

---

### Task 4: Normalize salient events and review expiry

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/normalize_salient_events.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_salient_events.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/references/salient-events.md`

**Interfaces:**
- Produces `normalize_event(record: dict) -> dict` and `is_event_current(event: dict, now: datetime) -> bool`.

- [ ] **Step 1: Write failing tests**

Cover:

```python
def test_keeps_old_unresolved_event_with_review_date(): ...
def test_excludes_expired_event_without_active_impact(): ...
def test_requires_source_and_salience_reason(): ...
def test_preserves_people_and_project_links(): ...
```

Use fictional events only.

- [ ] **Step 2: Implement normalization**

Rules:

- recent events are eligible when they have a material reason;
- old events remain eligible when unresolved or still affecting an active person/project/decision;
- expired events are excluded unless a current source reasserts impact;
- event date, source, canonical URL and reason are mandatory.

- [ ] **Step 3: Document event lifecycle**

`salient-events.md` defines default maximum 10, review/expiry behavior and the difference between recent and salient.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_salient_events.py -v
git add skills/personal-ai-workspace-context-bootstrap
git commit -m "feat: normalize recent and salient events"
```

---

### Task 5: Build minimal wellbeing and health snapshot

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/normalize_wellbeing_snapshot.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_wellbeing_snapshot.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/references/wellbeing-health-snapshot.md`

**Interfaces:**
- Produces `build_wellbeing_snapshot(records: list[dict], *, as_of: datetime) -> dict`.
- Consumes typed records from the Memory Fusion/personal-context workstream.

- [ ] **Step 1: Write failing tests**

```python
def test_includes_direct_self_report_and_active_constraint(): ...
def test_excludes_stopped_supplement_from_active_changes(): ...
def test_does_not_render_hypothesis_as_fact(): ...
def test_returns_canonical_links_not_full_confidential_payload(): ...
def test_marks_partial_source_coverage(): ...
```

- [ ] **Step 2: Implement allowed summary fields**

Return only:

```text
as_of
self_reported_state
observed_changes
active_constraints
active_health_changes
follow_ups
canonical_links
source_coverage
sensitivity = Confidential
```

For hypotheses, render `Possible pattern (hypothesis): ...` or omit from the snapshot when not operationally necessary.

- [ ] **Step 3: Document confidentiality and minimization**

The reference must prohibit copying full medical, sexual, psychological or substance-use details into Bootstrap when a bounded summary and canonical link suffice.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_wellbeing_snapshot.py -v
git add skills/personal-ai-workspace-context-bootstrap
git commit -m "feat: render minimal wellbeing and health snapshot"
```

---

### Task 6: Normalize recently changed memory

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/normalize_memory_changes.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_memory_changes.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/references/recently-changed-memory.md`

**Interfaces:**
- Produces `select_memory_changes(records: list[dict], *, since: datetime, limit: int) -> list[dict]`.

- [ ] **Step 1: Write failing tests**

Cover material create/correct/contradict/supersede, cosmetic edit exclusion, stable ordering and missing canonical link rejection.

- [ ] **Step 2: Implement selection**

Allowed operations are the shared enum. Sort newest first, then stable record ID. Default limit: 8. Exclude metadata-only timestamp changes.

- [ ] **Step 3: Document behavior and run tests**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_memory_changes.py -v
```

- [ ] **Step 4: Commit**

```bash
git add skills/personal-ai-workspace-context-bootstrap
git commit -m "feat: surface recently changed canonical memory"
```

---

### Task 7: Integrate per-section budget and renderer

**Files:**
- Modify: `skills/personal-ai-workspace-context-bootstrap/scripts/apply_budget.py`
- Modify: `skills/personal-ai-workspace-context-bootstrap/scripts/render_briefing.py`
- Modify: `skills/personal-ai-workspace-context-bootstrap/references/context-budget.md`
- Modify: `skills/personal-ai-workspace-context-bootstrap/references/briefing-format.md`
- Modify: `skills/personal-ai-workspace-context-bootstrap/tests/test_budget.py`
- Modify: `skills/personal-ai-workspace-context-bootstrap/tests/test_render_briefing.py`

**Interfaces:**
- Existing task budget remains hard-priority.
- New function: `allocate_section_budget(payload: dict, total_tokens: int) -> dict[str, int]`.

- [ ] **Step 1: Add failing budget tests**

```python
def test_active_tasks_survive_personal_context_overload(): ...
def test_people_are_capped_at_five(): ...
def test_events_are_capped_at_ten(): ...
def test_optional_sections_use_continuation_instead_of_silent_drop(): ...
def test_rendered_item_shows_source_and_salience_reason(): ...
```

- [ ] **Step 2: Implement budget tiers**

Use deterministic tiers:

```text
Tier 0: coverage/status and all active tasks
Tier 1: blockers, reviews, current focus, active commitments
Tier 2: people in focus, active projects, wellbeing constraints
Tier 3: salient events, recently changed memory, capability details
```

Within each tier, apply section caps and stable order. When content exceeds budget, include continuation metadata:

```json
{"section": "recent_and_salient_events", "shown": 10, "remaining": 4, "continuation_required": true}
```

- [ ] **Step 3: Update renderer headings in exact order**

```text
Current Focus
People in Focus
Active Tasks
Active Projects and Commitments
Recent and Salient Events
Wellbeing and Health Snapshot
Decisions and Pending Reviews
Risks, Conflicts and Blockers
Capability Health
Recently Changed Memory
```

- [ ] **Step 4: Run focused tests**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_budget.py skills/personal-ai-workspace-context-bootstrap/tests/test_render_briefing.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/personal-ai-workspace-context-bootstrap
git commit -m "feat: budget and render enriched context briefing"
```

---

### Task 8: Update skill routing, fixtures, end-to-end tests and docs

**Files:**
- Modify: `skills/personal-ai-workspace-context-bootstrap/SKILL.md`
- Create/complete: all `personal-context-*.json` fixtures
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_personal_context_end_to_end.py`
- Modify: `docs/CONTEXT-BOOTSTRAP.md`
- Modify: `docs/superpowers/specs/PHASE-1-CODEX-ENTRYPOINT.md` only if the canonical branch has not already incorporated this plan

**Interfaces:**
- End-to-end command consumes one normalized JSON fixture and produces structured JSON plus human-readable Markdown.

- [ ] **Step 1: Add failing contract tests**

Require the skill to name all new references and state:

```text
People in Focus is bounded
salience reasons are visible
wellbeing is minimum necessary detail
all active tasks remain represented
cached sections do not certify live sources
```

- [ ] **Step 2: Create fixtures**

Each fixture uses fictional names and URLs. The sensitive fixture contains synthetic confidential data and validates redaction/minimization.

- [ ] **Step 3: Add end-to-end tests**

Test empty, normal, overloaded, conflicting, stale, sensitive and partial payloads. Assert section order, coverage status, task completeness, item limits, canonical links and no secrets.

- [ ] **Step 4: Update documentation**

`docs/CONTEXT-BOOTSTRAP.md` explains the ten-section model, current-session evidence, salience reasons, per-section budgets, confidentiality and deeper-record lookup.

- [ ] **Step 5: Run all Context Bootstrap and root tests**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests -v
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider
python skill-pack/scripts/scan_private_identifiers.py .
```

Expected: all PASS and `public-safe: .`.

- [ ] **Step 6: Commit**

```bash
git add skills/personal-ai-workspace-context-bootstrap docs/CONTEXT-BOOTSTRAP.md
git commit -m "feat: complete Context Bootstrap personal focus enrichment"
```

---

## Plan self-review checklist

- [ ] Every non-task personal-context item requires source and visible salience reason.
- [ ] Task completeness remains higher priority than optional sections.
- [ ] People and event caps are deterministic and configurable.
- [ ] Wellbeing/health summary is minimal, confidential and linked.
- [ ] Cached content cannot self-certify `FULL`.
- [ ] All fixtures are fictional and public-safe.
- [ ] Public/private scanner and full test suite are part of completion.
- [ ] Traceability covers public issue #14 and Apex #23.
