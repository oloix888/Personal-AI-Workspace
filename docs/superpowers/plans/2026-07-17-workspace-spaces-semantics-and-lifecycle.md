# Active Workspace Spaces Semantics and Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Journal, Observations, Decisions, Projects, Working Notes and Archive active, discoverable, idempotently installable workspace systems with explicit routing and lifecycle contracts.

**Architecture:** Define generic schemas and deterministic routing/lifecycle functions in shared Skill Pack tooling. Installer & Upgrader uses declarative space/view/template manifests to create or repair selected structures after exact-scope approval. Autonomous Memory Capture routes candidates through the shared contract, while Context Bootstrap reads only active or directly relevant historical records.

**Tech Stack:** Python 3.11+, JSON Schema Draft 2020-12, pytest, Agent Skills Markdown, Notion connector instructions, declarative installation manifests.

## Global Constraints

- Binding source: `docs/superpowers/specs/2026-07-17-personal-context-and-active-workspace-semantics-addendum.md`.
- Public tracking: `Personal-AI-Workspace#16`; private tracking: `Apex#25`.
- Do not create ornamental databases or pages.
- Every enabled space requires purpose, include/exclude rules, read/write triggers, routing, lifecycle, default views/templates and a real workflow.
- Journal never stores hidden chain-of-thought or full transcript dumps.
- Working Notes are explicitly non-canonical and require review/expiry.
- Archive is a lifecycle state, never a dumping ground or silent deletion path.
- Installer structural changes require exact-scope approval and readback.
- Existing equivalent spaces, fields, views and templates must be detected before creation.
- Reruns are idempotent and preserve local customizations.
- Public fixtures are fictional and contain no private Workspace IDs or data.
- No live private migration, publication or adapter activation is authorized.
- Every task uses TDD, a focused commit and separate specification/code-quality review.

---

## File Map

```text
skills/_shared/contract/
└── workspace-spaces.md

skills/_shared/schemas/
├── workspace-space-contract.schema.json
├── journal-entry.schema.json
├── observation-record.schema.json
├── decision-record.schema.json
├── project-record.schema.json
├── working-note.schema.json
└── archive-lifecycle.schema.json

skills/_shared/manifests/
└── core-workspace-spaces.json

skill-pack/src/paiw_skill_pack/
├── workspace_spaces.py
└── lifecycle.py

skill-pack/tests/
├── fixtures/workspace-spaces/
│   ├── empty-installation.json
│   ├── existing-equivalent.json
│   ├── partial-installation.json
│   ├── routing-candidates.json
│   ├── working-note-expiry.json
│   └── archive-history.json
├── test_workspace_space_schemas.py
├── test_workspace_routing.py
├── test_workspace_lifecycle.py
└── test_workspace_manifest.py

skills/personal-ai-workspace-installer-upgrader/
├── references/workspace-spaces.md
├── scripts/render_space_blueprint.py
└── tests/test_workspace_spaces_installation.py

skills/personal-ai-workspace-context-bootstrap/
├── references/workspace-spaces.md
└── tests/test_workspace_space_visibility.py

skill-pack/migrations/1.5.1-to-1.6.0/
└── workspace-spaces.md

docs/WORKSPACE-SPACES.md
```

---

### Task 1: Define the generic workspace-space contract

**Files:**
- Create: `skills/_shared/schemas/workspace-space-contract.schema.json`
- Create: `skills/_shared/contract/workspace-spaces.md`
- Create: `skill-pack/tests/test_workspace_space_schemas.py`

**Interfaces:**
- A space contract is declarative and provider-neutral.
- Installer manifests and runtime routing both consume the same contract.

- [ ] **Step 1: Write failing schema tests**

```python
from paiw_skill_pack.schemas import validate_payload


def test_valid_workspace_space_contract() -> None:
    validate_payload(
        "workspace-space-contract.schema.json",
        {
            "space_key": "journal",
            "display_name": "Journal",
            "purpose": "Chronological material events and user-visible reflections.",
            "canonicality": "SUPPORTING",
            "include_rules": ["material_event", "meaningful_progress"],
            "exclude_rules": ["hidden_chain_of_thought", "routine_small_talk"],
            "read_triggers": ["daily_review", "relevant_person_or_project"],
            "write_triggers": ["material_event"],
            "routing_rules": ["journal_entry"],
            "lifecycle_states": ["ACTIVE", "ARCHIVED"],
            "promotion_rules": [],
            "archive_or_expiry_rules": ["archive_when_closed"],
            "default_views": ["Recent", "High Salience"],
            "templates": ["Material Event"],
            "bootstrap_visibility": "SALIENT_ONLY",
            "retention_and_deletion_boundary": "Preserve provenance; no silent permanent deletion."
        },
    )
```

- [ ] **Step 2: Run RED**

```bash
python -m pytest skill-pack/tests/test_workspace_space_schemas.py -v
```

Expected: missing schema.

- [ ] **Step 3: Implement schema enums**

Canonicality:

```text
CANONICAL
SUPPORTING
TEMPORARY
LIFECYCLE_VIEW
```

Bootstrap visibility:

```text
NEVER
SALIENT_ONLY
ACTIVE_ONLY
DIRECTLY_RELEVANT
```

Require every field shown above; set `additionalProperties: false`.

- [ ] **Step 4: Write shared contract**

The contract states:

- no ornamental spaces;
- every enabled space has at least one real workflow and discoverable owner view;
- routing ambiguity returns `REVIEW_REQUIRED`;
- local customizations are preserved;
- empty spaces are not treated as active knowledge;
- archive never authorizes deletion.

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_workspace_space_schemas.py -v
git add skills/_shared/contract/workspace-spaces.md skills/_shared/schemas/workspace-space-contract.schema.json skill-pack/tests/test_workspace_space_schemas.py
git commit -m "feat: define active workspace space contract"
```

---

### Task 2: Define Journal and Observations schemas

**Files:**
- Create: `skills/_shared/schemas/journal-entry.schema.json`
- Create: `skills/_shared/schemas/observation-record.schema.json`
- Extend: `skill-pack/tests/test_workspace_space_schemas.py`

**Interfaces:**
- Journal is user-visible supporting chronology.
- Observations contain typed epistemic records and counterevidence.

- [ ] **Step 1: Add failing tests**

```python
def test_journal_rejects_hidden_reasoning_type() -> None: ...
def test_journal_requires_materiality_and_links(): ...
def test_observation_requires_type_source_confidence_and_review(): ...
def test_observation_preserves_counterevidence(): ...
```

- [ ] **Step 2: Implement Journal schema**

Required fields:

```text
entry_id
title
occurred_at
summary
materiality_reason
source
people
projects
decisions
tasks
canonical_links
sensitivity
status
```

Allowed status:

```text
ACTIVE
REVIEW_NEEDED
ARCHIVED
```

The schema has no field for hidden reasoning or private scratchpad content.

- [ ] **Step 3: Implement Observations schema**

Required fields:

```text
observation_id
subject
statement
observation_type
source
observed_at
confidence
sensitivity
supporting_evidence
counterevidence
review_date
status
related_people
related_projects
```

Observation types reuse the psychological/wellbeing epistemic types where applicable plus `OPERATIONAL_OBSERVATION`.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_workspace_space_schemas.py -v
git add skills/_shared/schemas skill-pack/tests/test_workspace_space_schemas.py
git commit -m "feat: define Journal and Observations schemas"
```

---

### Task 3: Define Decisions and Projects schemas

**Files:**
- Create: `skills/_shared/schemas/decision-record.schema.json`
- Create: `skills/_shared/schemas/project-record.schema.json`
- Extend: `skill-pack/tests/test_workspace_space_schemas.py`

**Interfaces:**
- Decision records support lightweight decisions and full Decision Cases.
- Project records are canonical hubs.

- [ ] **Step 1: Add failing tests**

Cover required rationale/review/outcome links and project goal/status/next-action links.

- [ ] **Step 2: Implement Decision schema**

Required fields:

```text
decision_id
title
decision_kind
status
selected_option
rationale_summary
assumptions
constraints
decided_at
review_date
outcome_status
lesson_summary
project_links
task_links
source_links
```

Decision kind:

```text
LIGHTWEIGHT
DECISION_CASE
```

Status:

```text
OPEN
DECIDED
REVIEW_DUE
CLOSED
```

Outcome status:

```text
NOT_REVIEWED
POSITIVE
MIXED
NEGATIVE
SUPERSEDED
```

- [ ] **Step 3: Implement Project schema**

Required fields:

```text
project_id
title
goal
status
owner
people
tasks
decisions
risks
files
sources
latest_update
next_action
last_updated
archive_ready
```

Status:

```text
PROPOSED
ACTIVE
BLOCKED
PAUSED
COMPLETED
CANCELLED
ARCHIVED
```

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_workspace_space_schemas.py -v
git add skills/_shared/schemas skill-pack/tests/test_workspace_space_schemas.py
git commit -m "feat: define discoverable decision and project records"
```

---

### Task 4: Define Working Notes and Archive lifecycle

**Files:**
- Create: `skills/_shared/schemas/working-note.schema.json`
- Create: `skills/_shared/schemas/archive-lifecycle.schema.json`
- Create: `skill-pack/src/paiw_skill_pack/lifecycle.py`
- Create: `skill-pack/tests/test_workspace_lifecycle.py`
- Add fixtures: `working-note-expiry.json`, `archive-history.json`

**Interfaces:**
- Produces `evaluate_working_note(note: dict, *, as_of: date) -> dict`.
- Produces `archive_transition(record: dict, *, reason: str, at: datetime) -> dict`.

- [ ] **Step 1: Write failing tests**

```python
from datetime import date, datetime, timezone
from paiw_skill_pack.lifecycle import archive_transition, evaluate_working_note


def test_expired_working_note_requires_lifecycle_decision() -> None:
    note = {"note_id": "n-1", "title": "Draft analysis", "created_at": "2026-07-01", "review_or_expiry_date": "2026-07-10", "lifecycle_decision": "KEEP_WORKING", "canonicality": "TEMPORARY", "source": "turn:1"}
    result = evaluate_working_note(note, as_of=date(2026, 7, 17))
    assert result["status"] == "REVIEW_DUE"


def test_archive_transition_preserves_provenance() -> None:
    result = archive_transition({"id": "x", "status": "COMPLETED", "source": "workspace:x"}, reason="closed", at=datetime(2026, 7, 17, tzinfo=timezone.utc))
    assert result["archived_from_status"] == "COMPLETED"
    assert result["source"] == "workspace:x"
```

- [ ] **Step 2: Implement Working Note schema**

Required fields:

```text
note_id
title
summary
owner_or_context
created_at
review_or_expiry_date
lifecycle_decision
promotion_destination
canonicality = TEMPORARY
source
status
```

Lifecycle decision enum:

```text
PROMOTE_TO_CANONICAL
KEEP_WORKING
ARCHIVE
EXPIRE
```

- [ ] **Step 3: Implement Archive lifecycle schema**

Required:

```text
record_id
record_type
archived_at
archive_reason
archived_from_status
source
canonical_links
retention_rule
permanent_deletion_authorized = false
```

- [ ] **Step 4: Implement lifecycle functions**

Expired notes return `REVIEW_DUE` until an explicit lifecycle decision is applied. Archive transition preserves original status, source and links and never deletes.

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_workspace_lifecycle.py -v
git add skills/_shared/schemas skill-pack/src/paiw_skill_pack/lifecycle.py skill-pack/tests
git commit -m "feat: add Working Notes and Archive lifecycle"
```

---

### Task 5: Implement deterministic candidate routing

**Files:**
- Create: `skill-pack/src/paiw_skill_pack/workspace_spaces.py`
- Create: `skill-pack/tests/test_workspace_routing.py`
- Add fixture: `routing-candidates.json`

**Interfaces:**
- Produces `route_candidate(candidate: dict) -> dict`.
- Output: `destination`, `operation`, `canonicality`, `reason`, `review_required`.

- [ ] **Step 1: Write failing routing tests**

```python
from paiw_skill_pack.workspace_spaces import route_candidate


def test_routes_material_event_to_journal() -> None:
    result = route_candidate({"candidate_type": "Material Event", "signals": ["material_event", "chronological"]})
    assert result["destination"] == "Journal"


def test_routes_hypothesis_to_observations() -> None:
    result = route_candidate({"candidate_type": "Hypothesis", "signals": ["interpretation"]})
    assert result["destination"] == "Observations"


def test_routes_unfinished_analysis_to_working_notes() -> None:
    result = route_candidate({"candidate_type": "Analysis", "signals": ["unfinished", "non_canonical"]})
    assert result["destination"] == "Working Notes"


def test_ambiguous_candidate_requires_review() -> None:
    result = route_candidate({"candidate_type": "Unknown", "signals": []})
    assert result["review_required"] is True
    assert result["operation"] == "REVIEW_REQUIRED"
```

- [ ] **Step 2: Implement routing map**

```python
ROUTING_RULES = {
    "material_event": "Journal",
    "observation": "Observations",
    "interpretation": "Observations",
    "hypothesis": "Observations",
    "explicit_decision": "Decisions",
    "multi_step_goal": "Projects",
    "unfinished": "Working Notes",
    "closed": "Archive",
    "superseded": "Archive",
    "expired": "Archive",
}
```

When multiple compatible signals exist, prefer the smallest canonical destination. Incompatible top-priority destinations produce `REVIEW_REQUIRED`; never create both automatically.

- [ ] **Step 3: Integrate canonical matching**

Before `CREATE_NEW`, the caller must supply canonical-match evidence or an explicit `no_match_found` result from bounded discovery. Route output includes expected deduplication key.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_workspace_routing.py -v
git add skill-pack/src/paiw_skill_pack/workspace_spaces.py skill-pack/tests
git commit -m "feat: route memory candidates to active workspace spaces"
```

---

### Task 6: Create declarative space/view/template manifest

**Files:**
- Create: `skills/_shared/manifests/core-workspace-spaces.json`
- Create: `skill-pack/tests/test_workspace_manifest.py`

**Interfaces:**
- Manifest contains generic semantic keys, not private Notion IDs.
- Installer resolves semantic fields/views to connector operations.

- [ ] **Step 1: Write failing manifest tests**

Require space keys:

```text
journal
observations
decisions
projects
working_notes
archive
```

For each space assert purpose, required properties, views, templates, routing keys and enabled-by-default/core-optional state.

- [ ] **Step 2: Implement manifest**

Example Journal entry:

```json
{
  "space_key": "journal",
  "display_name": "Journal",
  "required": false,
  "recommended": true,
  "properties": ["Title", "Occurred At", "Summary", "Materiality Reason", "Source", "People", "Projects", "Decisions", "Tasks", "Sensitivity", "Status"],
  "views": ["Recent", "High Salience", "By Person", "By Project", "Review or Follow-up Needed"],
  "templates": ["Material Event"],
  "routing_keys": ["material_event", "meaningful_progress", "significant_setback"]
}
```

Decisions and Projects may be core/recommended according to the existing framework profile; preserve owner configuration on upgrades.

- [ ] **Step 3: Validate no private identifiers**

```bash
python skill-pack/scripts/scan_private_identifiers.py skills/_shared/manifests
```

Expected: `public-safe`.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_workspace_manifest.py -v
git add skills/_shared/manifests/core-workspace-spaces.json skill-pack/tests/test_workspace_manifest.py
git commit -m "feat: declare workspace spaces, views and templates"
```

---

### Task 7: Integrate Installer & Upgrader blueprints and migration

**Files:**
- Create: `skills/personal-ai-workspace-installer-upgrader/references/workspace-spaces.md`
- Create: `skills/personal-ai-workspace-installer-upgrader/scripts/render_space_blueprint.py`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_workspace_spaces_installation.py`
- Create/Modify: `skill-pack/migrations/1.5.1-to-1.6.0/workspace-spaces.md`
- Modify: `skills/personal-ai-workspace-installer-upgrader/SKILL.md`

**Interfaces:**
- Produces `render_space_blueprint(discovery: dict, selection: dict, manifest: dict) -> dict`.

- [ ] **Step 1: Write failing installer tests**

Cover:

```text
fresh install selected spaces
existing equivalent space detected
partial space repaired
view created only when missing
local extra view preserved
rerun produces no operations
owner-disabled optional space remains disabled
unknown newer schema stays read-only
```

- [ ] **Step 2: Implement blueprint operations**

Operations are declarative:

```text
CREATE_SPACE
ADD_PROPERTY
CREATE_VIEW
CREATE_TEMPLATE
UPDATE_ROUTING_INSTRUCTION
MIGRATE_RECORD_LINK
NO_CHANGE
REVIEW_CONFLICT
```

Each operation includes semantic target, current evidence, desired state, idempotency key, risk, rollback and readback requirements.

- [ ] **Step 3: Implement exact-scope preview**

Preview groups operations by space and distinguishes required/core from optional/recommended. It must show that no data deletion is planned.

- [ ] **Step 4: Write migration instructions**

Migration discovers existing Journal/Observations/Decisions/Projects/notes/archive equivalents, maps fields/views, preserves records and custom views, adds only missing approved components, updates routing instructions and verifies readback.

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_workspace_spaces_installation.py -v
git add skills/personal-ai-workspace-installer-upgrader skill-pack/migrations/1.5.1-to-1.6.0/workspace-spaces.md
git commit -m "feat: install and upgrade active workspace spaces"
```

---

### Task 8: Integrate Autonomous Memory and Context Bootstrap visibility

**Files:**
- Modify: `skills/_shared/contract/autonomous-memory-capture.md`
- Modify: `skill-pack/src/paiw_skill_pack/memory.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/references/workspace-spaces.md`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_workspace_space_visibility.py`
- Modify: relevant memory tests

**Interfaces:**
- Memory planning calls `route_candidate` before constructing writes.
- Bootstrap visibility respects each space's contract.

- [ ] **Step 1: Add failing integration tests**

Cover:

- material event routes to Journal;
- hypothesis routes to Observations with type preserved;
- explicit choice routes to Decisions;
- multi-step goal routes to Projects;
- unfinished analysis routes to Working Notes with expiry;
- archived record excluded from normal briefing;
- archived record included when directly relevant to current request;
- empty space not reported as active knowledge;
- ambiguous routing does not create duplicates.

- [ ] **Step 2: Integrate routing**

Memory plan records destination, canonicality, deduplication key, lifecycle state and readback. `REVIEW_REQUIRED` candidates remain in active conversation or approved review queue; they do not create a new structural queue.

- [ ] **Step 3: Implement Bootstrap visibility**

```text
Journal -> salient/recent only
Observations -> active/review-due and task-relevant
Decisions -> open/review-due/recent outcomes
Projects -> active/blocked/recently updated
Working Notes -> only directly relevant or review-due
Archive -> directly relevant only
```

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_workspace_routing.py skill-pack/tests/test_workspace_lifecycle.py skills/personal-ai-workspace-context-bootstrap/tests/test_workspace_space_visibility.py -v
git add skills/_shared skill-pack/src/paiw_skill_pack skills/personal-ai-workspace-context-bootstrap
git commit -m "feat: use active workspace spaces in memory and bootstrap"
```

---

### Task 9: Add owner-visible documentation and end-to-end tests

**Files:**
- Create: `docs/WORKSPACE-SPACES.md`
- Create: `skill-pack/tests/test_workspace_spaces_end_to_end.py`
- Modify: creator/installation documentation paths defined by the integration plan
- Modify: private-adapter public-safe compatibility tests

**Interfaces:**
- Documentation explains what each space does, how records become visible and how lifecycle works.

- [ ] **Step 1: Write end-to-end tests**

Use fixtures for fresh, existing, partial and rerun installations. Assert:

- expected spaces only;
- required views/templates;
- idempotent second run;
- preserved custom view;
- correct routing and promotion;
- expired Working Note review;
- archived record exclusion;
- no private identifiers.

- [ ] **Step 2: Write `docs/WORKSPACE-SPACES.md`**

For each space include:

```text
Purpose
What belongs here
What does not belong here
When AI reads it
When AI writes it
Views
Lifecycle
Examples
```

Explicitly explain where a user clicks to find decisions, active projects, observations and notes.

- [ ] **Step 3: Update creator and installer documentation**

Installation choices explain optional/recommended spaces and show final links/views in handover. Do not claim a space is active when it has no records.

- [ ] **Step 4: Run root tests and scanner**

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider
python skill-pack/scripts/scan_private_identifiers.py .
```

Expected: all PASS and `public-safe: .`.

- [ ] **Step 5: Commit**

```bash
git add docs/WORKSPACE-SPACES.md skill-pack/tests creator skills private
git commit -m "feat: document and verify active workspace spaces"
```

---

## Plan self-review checklist

- [ ] Every space has purpose, include/exclude, routing, lifecycle, views and a real workflow.
- [ ] Journal excludes hidden reasoning and transcript dumping.
- [ ] Observations preserve evidence and counterevidence.
- [ ] Decisions and Projects are owner-discoverable through required views.
- [ ] Working Notes cannot remain indefinitely without review.
- [ ] Archive preserves provenance and does not authorize deletion.
- [ ] Routing is deterministic, deduplicated and review-gated when ambiguous.
- [ ] Installer is idempotent and preserves local customizations.
- [ ] Empty spaces are not misreported as active knowledge.
- [ ] Public/private scan covers schemas, manifests, fixtures and docs.
- [ ] Traceability covers public issue #16 and Apex #25.
