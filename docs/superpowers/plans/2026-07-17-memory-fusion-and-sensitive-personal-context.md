# Memory Fusion and Sensitive Personal Context Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explicit source-precedence contract and safe, confidential, time-aware psychological, wellbeing, health and supplement memory profiles integrated with Autonomous Memory Capture, Installer & Upgrader, Context Bootstrap and the private adapter.

**Architecture:** Extend the shared Autonomous Memory contract with source evidence, conflict preservation and specialized personal-context schemas. Deterministic Python functions merge normalized evidence, evaluate person/relationship materiality, validate typed psychological/health records and select current-state summaries. Connector-backed reads and writes remain instruction-led; public fixtures remain entirely fictional.

**Tech Stack:** Python 3.11+, JSON Schema Draft 2020-12, pytest, Agent Skills Markdown, shared `paiw_skill_pack` tooling.

## Global Constraints

- Binding source: `docs/superpowers/specs/2026-07-17-personal-context-and-active-workspace-semantics-addendum.md`.
- Public tracking: `Personal-AI-Workspace#15`; private tracking: `Apex#24`.
- Use `ALWAYS_EVALUATE / SAVE_IF_MATERIAL` for person and relationship statements.
- Native AI memory is auxiliary and cannot silently override verified canonical Workspace data.
- Transient mood is not a stable trait; one behavior is not a repeated pattern.
- Interpretation and hypothesis remain typed and never silently become facts.
- Health and supplement entries are time-aware; stopped/historical entries do not appear as current.
- Sensitive records are Confidential and owner-only by default.
- Explicit no-save instructions, owner corrections and source restrictions are mandatory.
- Never store hidden chain-of-thought or authentication secrets.
- Public fixtures use fictional people and synthetic health data only.
- No live private migration, publication or adapter activation is authorized.
- Every task uses TDD, a focused commit and separate specification/code-quality reviews.

---

## File Map

```text
skills/_shared/contract/
├── memory-fusion.md
└── sensitive-personal-context.md

skills/_shared/schemas/
├── memory-source-evidence.schema.json
├── memory-conflict.schema.json
├── psychological-context.schema.json
└── health-context.schema.json

skill-pack/src/paiw_skill_pack/
├── memory_fusion.py
├── relationship_capture.py
├── psychological_context.py
└── health_context.py

skill-pack/tests/
├── fixtures/personal-context/
│   ├── source-precedence.json
│   ├── native-memory-conflict.json
│   ├── relationship-material.json
│   ├── relationship-incidental.json
│   ├── transient-mood.json
│   ├── repeated-pattern.json
│   ├── hypothesis-counterevidence.json
│   ├── active-supplement.json
│   ├── stopped-supplement.json
│   └── owner-correction.json
├── test_memory_fusion.py
├── test_relationship_capture.py
├── test_psychological_context.py
└── test_health_context.py

skills/personal-ai-workspace-context-bootstrap/
├── references/memory-fusion.md
├── references/sensitive-personal-context.md
└── tests/test_sensitive_personal_context_contract.py

skills/personal-ai-workspace-installer-upgrader/
├── references/memory-fusion.md
├── references/sensitive-personal-context.md
└── tests/test_sensitive_personal_context_installation.py

skill-pack/migrations/1.5.1-to-1.6.0/
└── sensitive-personal-context.md

docs/MEMORY.md
```

---

### Task 1: Define source-evidence and conflict schemas

**Files:**
- Create: `skills/_shared/schemas/memory-source-evidence.schema.json`
- Create: `skills/_shared/schemas/memory-conflict.schema.json`
- Create: `skill-pack/tests/test_memory_fusion.py`

**Interfaces:**
- `memory-source-evidence` represents one normalized claim plus its source rank.
- `memory-conflict` preserves all conflicting evidence and the chosen operation.

- [ ] **Step 1: Write failing schema tests**

```python
from paiw_skill_pack.schemas import validate_payload


def test_valid_memory_source_evidence() -> None:
    validate_payload(
        "memory-source-evidence.schema.json",
        {
            "evidence_id": "e-1",
            "statement": "The user prefers morning meetings.",
            "source_type": "CURRENT_USER_STATEMENT",
            "source_reference": "conversation:turn-42",
            "observed_at": "2026-07-17T08:00:00Z",
            "confidence": "High",
            "epistemic_status": "Fact",
            "sensitivity": "Private",
        },
    )


def test_conflict_preserves_both_sources() -> None:
    validate_payload(
        "memory-conflict.schema.json",
        {
            "conflict_id": "c-1",
            "canonical_key": "preference.meeting-time",
            "evidence": [
                {"evidence_id": "e-1", "statement": "morning", "source_type": "CANONICAL_WORKSPACE", "source_reference": "workspace:1", "observed_at": "2026-07-01T08:00:00Z", "confidence": "High", "epistemic_status": "Fact", "sensitivity": "Private"},
                {"evidence_id": "e-2", "statement": "afternoon", "source_type": "CURRENT_USER_STATEMENT", "source_reference": "turn:42", "observed_at": "2026-07-17T08:00:00Z", "confidence": "High", "epistemic_status": "Fact", "sensitivity": "Private"},
            ],
            "operation": "SUPERSEDE_EXISTING",
            "resolution_reason": "Current explicit user statement supersedes older preference.",
        },
    )
```

- [ ] **Step 2: Run RED**

```bash
python -m pytest skill-pack/tests/test_memory_fusion.py -v
```

Expected: missing schemas.

- [ ] **Step 3: Implement exact enums**

`source_type` enum:

```text
CURRENT_USER_STATEMENT
CANONICAL_WORKSPACE
LIVE_CONNECTOR
CURRENT_CONVERSATION
NATIVE_AI_MEMORY
CACHED_SUMMARY
ASSISTANT_INTERPRETATION
ASSISTANT_HYPOTHESIS
```

`operation` enum:

```text
NO_CHANGE
AUGMENT_EXISTING
CORRECT_EXISTING
CONTRADICT_EXISTING
SUPERSEDE_EXISTING
REVIEW_REQUIRED
```

Set `additionalProperties: false`; require at least two evidence entries in conflicts.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_memory_fusion.py -v
git add skills/_shared/schemas skill-pack/tests/test_memory_fusion.py
git commit -m "feat: define Memory Fusion evidence schemas"
```

---

### Task 2: Implement deterministic Memory Fusion precedence

**Files:**
- Create: `skill-pack/src/paiw_skill_pack/memory_fusion.py`
- Extend: `skill-pack/tests/test_memory_fusion.py`
- Create: `skills/_shared/contract/memory-fusion.md`

**Interfaces:**
- Produces `merge_evidence(evidence: list[dict]) -> dict`.
- Produces `SOURCE_RANK: dict[str, int]`.

- [ ] **Step 1: Write failing behavior tests**

```python
from paiw_skill_pack.memory_fusion import merge_evidence


def test_current_user_statement_can_supersede_older_workspace_fact() -> None:
    result = merge_evidence([
        {"evidence_id": "w", "statement": "morning", "source_type": "CANONICAL_WORKSPACE", "source_reference": "workspace:1", "observed_at": "2026-06-01T08:00:00Z", "confidence": "High", "epistemic_status": "Fact", "sensitivity": "Private"},
        {"evidence_id": "u", "statement": "afternoon", "source_type": "CURRENT_USER_STATEMENT", "source_reference": "turn:1", "observed_at": "2026-07-17T08:00:00Z", "confidence": "High", "epistemic_status": "Fact", "sensitivity": "Private"},
    ])
    assert result["operation"] == "SUPERSEDE_EXISTING"
    assert len(result["evidence"]) == 2
    assert result["selected_evidence_id"] == "u"


def test_native_memory_cannot_silently_override_live_workspace() -> None:
    result = merge_evidence([
        {"evidence_id": "w", "statement": "active project A", "source_type": "CANONICAL_WORKSPACE", "source_reference": "workspace:project-a", "observed_at": "2026-07-17T08:00:00Z", "confidence": "High", "epistemic_status": "Fact", "sensitivity": "Private"},
        {"evidence_id": "m", "statement": "active project B", "source_type": "NATIVE_AI_MEMORY", "source_reference": "native-memory", "observed_at": "2026-07-10T08:00:00Z", "confidence": "Unknown", "epistemic_status": "Reported Claim", "sensitivity": "Private"},
    ])
    assert result["selected_evidence_id"] == "w"
    assert result["operation"] in {"CONTRADICT_EXISTING", "REVIEW_REQUIRED"}
```

- [ ] **Step 2: Implement ranking**

```python
SOURCE_RANK = {
    "CURRENT_USER_STATEMENT": 700,
    "CANONICAL_WORKSPACE": 600,
    "LIVE_CONNECTOR": 500,
    "CURRENT_CONVERSATION": 400,
    "NATIVE_AI_MEMORY": 300,
    "CACHED_SUMMARY": 200,
    "ASSISTANT_INTERPRETATION": 100,
    "ASSISTANT_HYPOTHESIS": 50,
}
```

Sort by rank, then observed timestamp, then stable evidence ID. Never drop non-selected conflicting evidence.

Operations:

- identical statements -> `NO_CHANGE`;
- current statement adds compatible detail -> `AUGMENT_EXISTING`;
- explicit correction of erroneous record -> `CORRECT_EXISTING`;
- unresolved incompatible claims -> `CONTRADICT_EXISTING` or `REVIEW_REQUIRED`;
- explicit changed preference/current state -> `SUPERSEDE_EXISTING`.

- [ ] **Step 3: Write shared contract**

Document source hierarchy, unavailable-source behavior, visible conflicts, no silent native-memory override and provenance retention.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_memory_fusion.py -v
git add skill-pack/src/paiw_skill_pack/memory_fusion.py skills/_shared/contract/memory-fusion.md skill-pack/tests/test_memory_fusion.py
git commit -m "feat: merge memory evidence by explicit precedence"
```

---

### Task 3: Implement person and relationship materiality evaluation

**Files:**
- Create: `skill-pack/src/paiw_skill_pack/relationship_capture.py`
- Create: `skill-pack/tests/test_relationship_capture.py`
- Add fixtures: `relationship-material.json`, `relationship-incidental.json`

**Interfaces:**
- Produces `evaluate_relationship_candidate(candidate: dict) -> dict`.
- Output includes `evaluated: true`, `save: bool`, `materiality_reasons`, `destination`, `requested_action`.

- [ ] **Step 1: Write failing tests**

```python
from paiw_skill_pack.relationship_capture import evaluate_relationship_candidate


def test_every_relationship_statement_is_evaluated() -> None:
    result = evaluate_relationship_candidate({"statement": "I saw Alex in the elevator.", "source": "turn:1"})
    assert result["evaluated"] is True


def test_material_commitment_is_saved() -> None:
    result = evaluate_relationship_candidate({"statement": "Alex promised to send the contract Friday.", "source": "turn:2", "signals": ["commitment", "deadline"]})
    assert result["save"] is True
    assert result["destination"] in {"Relations", "Commitments"}


def test_incidental_unchanged_mention_is_not_persisted() -> None:
    result = evaluate_relationship_candidate({"statement": "Alex was mentioned in passing.", "source": "turn:3", "signals": ["incidental"]})
    assert result["evaluated"] is True
    assert result["save"] is False
```

- [ ] **Step 2: Implement explicit materiality signals**

Save when signals include:

```text
identity_change
relationship_state_change
material_interaction
commitment
follow_up
communication_preference
boundary
conflict
material_life_event
supported_repeated_pattern
correction
contradiction
supersession
```

Reject save for `incidental`, `small_talk`, `unchanged_duplicate` unless another material signal exists.

- [ ] **Step 3: Map destinations**

- identity/relationship state -> `Relations`;
- interaction -> `Interactions`;
- promise/follow-up -> `Commitments`;
- supported pattern/interpretation -> `Observations`;
- correction -> matched canonical destination.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_relationship_capture.py -v
git add skill-pack/src/paiw_skill_pack/relationship_capture.py skill-pack/tests/test_relationship_capture.py skill-pack/tests/fixtures/personal-context
git commit -m "feat: evaluate material relationship memory candidates"
```

---

### Task 4: Define and validate psychological/wellbeing records

**Files:**
- Create: `skills/_shared/schemas/psychological-context.schema.json`
- Create: `skill-pack/src/paiw_skill_pack/psychological_context.py`
- Create: `skill-pack/tests/test_psychological_context.py`
- Add fixtures: `transient-mood.json`, `repeated-pattern.json`, `hypothesis-counterevidence.json`, `owner-correction.json`

**Interfaces:**
- Produces `validate_psychological_record(record: dict) -> dict`.
- Produces `can_promote_to_pattern(records: list[dict], *, owner_confirmed: bool = False) -> bool`.

- [ ] **Step 1: Add failing schema and behavior tests**

```python
from paiw_skill_pack.psychological_context import can_promote_to_pattern, validate_psychological_record


def test_transient_state_is_not_a_stable_pattern() -> None:
    record = validate_psychological_record({
        "record_id": "psy-1",
        "subject": "owner",
        "statement": "Low motivation this morning",
        "record_type": "SELF_REPORTED_STATE",
        "source": {"type": "CURRENT_USER_STATEMENT", "reference": "turn:1"},
        "observed_at": "2026-07-17T08:00:00Z",
        "valid_from": "2026-07-17",
        "valid_until_or_review_after": "2026-07-18",
        "perspective": "User",
        "epistemic_status": "Fact",
        "confidence": "High",
        "sensitivity": "Confidential",
        "supporting_evidence": [],
        "counterevidence": [],
        "owner_correction_history": [],
        "related_people_projects_or_events": [],
    })
    assert record["record_type"] == "SELF_REPORTED_STATE"
    assert can_promote_to_pattern([record]) is False


def test_pattern_requires_multiple_observations_or_owner_confirmation() -> None:
    records = [{"record_id": "a", "record_type": "OBSERVED_SIGNAL", "observed_at": "2026-07-01T08:00:00Z"}, {"record_id": "b", "record_type": "OBSERVED_SIGNAL", "observed_at": "2026-07-10T08:00:00Z"}]
    assert can_promote_to_pattern(records) is True
```

- [ ] **Step 2: Implement exact record types**

```text
SELF_REPORTED_STATE
OBSERVED_SIGNAL
REPEATED_PATTERN
INTERPRETATION
HYPOTHESIS
COUNTEREVIDENCE
RISK_SIGNAL
```

Schema requires all fields from the addendum and `sensitivity: Confidential`.

- [ ] **Step 3: Implement promotion rules**

- owner confirmation can promote directly with provenance;
- otherwise require at least two materially separate observations;
- same timestamp/source duplication counts once;
- hypothesis remains hypothesis even with multiple supporting items until explicitly reviewed;
- counterevidence is preserved and lowers confidence but is never deleted.

- [ ] **Step 4: Implement owner correction**

A correction appends to `owner_correction_history`, supersedes the current summary and preserves old statement/provenance.

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_psychological_context.py -v
git add skills/_shared/schemas/psychological-context.schema.json skill-pack/src/paiw_skill_pack/psychological_context.py skill-pack/tests
git commit -m "feat: model confidential psychological and wellbeing context"
```

---

### Task 5: Define health, medication and supplement lifecycle

**Files:**
- Create: `skills/_shared/schemas/health-context.schema.json`
- Create: `skill-pack/src/paiw_skill_pack/health_context.py`
- Create: `skill-pack/tests/test_health_context.py`
- Add fixtures: `active-supplement.json`, `stopped-supplement.json`

**Interfaces:**
- Produces `validate_health_record(record: dict) -> dict`.
- Produces `select_current_health(records: list[dict], *, as_of: date) -> list[dict]`.

- [ ] **Step 1: Write failing tests**

```python
from datetime import date
from paiw_skill_pack.health_context import select_current_health


def test_stopped_item_is_not_current() -> None:
    records = [{"record_id": "h-1", "entry_type": "SUPPLEMENT", "status": "STOPPED", "item_or_subject": "Example supplement", "started_at": "2026-01-01", "paused_or_stopped_at": "2026-06-01", "source": {"type": "CURRENT_USER_STATEMENT", "reference": "turn:1"}, "confidence": "High", "sensitivity": "Confidential", "related_records": []}]
    assert select_current_health(records, as_of=date(2026, 7, 17)) == []


def test_unknown_dose_stays_unknown() -> None:
    record = {"record_id": "h-2", "entry_type": "SUPPLEMENT", "status": "ACTIVE", "item_or_subject": "Example supplement", "dose_or_value": None, "frequency": None, "purpose": "Sleep", "started_at": "2026-07-01", "paused_or_stopped_at": None, "source": {"type": "CURRENT_USER_STATEMENT", "reference": "turn:2"}, "reported_effect": None, "possible_adverse_effect": None, "confidence": "High", "sensitivity": "Confidential", "review_date": "2026-08-01", "related_records": []}
    assert select_current_health([record], as_of=date(2026, 7, 17))[0]["dose_or_value"] is None
```

- [ ] **Step 2: Implement exact enums**

Entry types:

```text
SYMPTOM
CONDITION
MEASUREMENT
MEDICATION
SUPPLEMENT
INTERVENTION
MEDICAL_RECOMMENDATION
REPORTED_BENEFIT
POSSIBLE_SIDE_EFFECT
FOLLOW_UP
```

Statuses:

```text
ACTIVE
PAUSED
STOPPED
HISTORICAL
UNCONFIRMED
```

- [ ] **Step 3: Implement current selection**

Only `ACTIVE` entries appear as active. `UNCONFIRMED` may appear in a separate review list. Paused/stopped/historical entries remain linked history.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_health_context.py -v
git add skills/_shared/schemas/health-context.schema.json skill-pack/src/paiw_skill_pack/health_context.py skill-pack/tests
git commit -m "feat: model health and supplement lifecycle"
```

---

### Task 6: Integrate specialized context with Autonomous Memory Capture

**Files:**
- Modify: `skills/_shared/contract/autonomous-memory-capture.md`
- Modify: `skills/_shared/schemas/memory-candidate.schema.json`
- Modify: `skill-pack/src/paiw_skill_pack/memory.py`
- Modify: `skill-pack/tests/test_memory_candidates.py`
- Modify: `skill-pack/tests/test_memory_plans.py`
- Create: `skills/_shared/contract/sensitive-personal-context.md`

**Interfaces:**
- Adds candidate types/destinations without breaking existing generic types.
- Adds `source_type`, `valid_until_or_review_after`, `counterevidence` and `owner_correction` fields where relevant.

- [ ] **Step 1: Add failing integration tests**

Cover:

- person statement always evaluated;
- material relationship statement produces write plan;
- transient mood produces typed short-lived record, not pattern;
- repeated supported pattern routes to Observations;
- active supplement routes to confidential health destination;
- explicit no-save skips all destinations;
- secret adjacent useful context is retained only after secret removal;
- native-memory conflict produces review/conflict plan rather than overwrite.

- [ ] **Step 2: Extend candidate and destination enums**

Add candidate types:

```text
Person Identity
Relationship Event
Psychological State
Psychological Pattern
Health Item
Health Follow-up
```

Add destinations:

```text
Journal
Observations
Projects
Working Notes
Health Context
Psychological Context
```

- [ ] **Step 3: Implement classification routing**

Call `evaluate_relationship_candidate`, `validate_psychological_record`, `validate_health_record` and `merge_evidence` from the shared memory planning pipeline.

- [ ] **Step 4: Run memory tests**

```bash
python -m pytest skill-pack/tests/test_memory_candidates.py skill-pack/tests/test_memory_plans.py skill-pack/tests/test_memory_safety.py skill-pack/tests/test_relationship_capture.py skill-pack/tests/test_psychological_context.py skill-pack/tests/test_health_context.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/_shared skill-pack/src/paiw_skill_pack skill-pack/tests
git commit -m "feat: route sensitive personal context through autonomous memory"
```

---

### Task 7: Update Installer & Upgrader and migration contract

**Files:**
- Create: `skills/personal-ai-workspace-installer-upgrader/references/memory-fusion.md`
- Create: `skills/personal-ai-workspace-installer-upgrader/references/sensitive-personal-context.md`
- Modify: `skills/personal-ai-workspace-installer-upgrader/SKILL.md`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_sensitive_personal_context_installation.py`
- Create/Modify: `skill-pack/migrations/1.5.1-to-1.6.0/sensitive-personal-context.md`

**Interfaces:**
- Installer preview exposes selected spaces, fields, views, retention, capture thresholds and privacy boundaries.

- [ ] **Step 1: Write failing installer contract tests**

Require:

```text
Memory Fusion is complementary to native memory
ALWAYS_EVALUATE / SAVE_IF_MATERIAL
psychological context is typed and confidential
health items are time-aware
owner can pause/disable capture or restrict categories
exact-scope approval before structural creation
readback after creation/migration
```

- [ ] **Step 2: Write migration steps**

The migration:

1. discovers existing person, relations, observation and health-like structures;
2. maps fields without duplicating records;
3. preserves no-save/retention restrictions;
4. previews missing fields/views/templates;
5. obtains approval;
6. creates only approved structures;
7. links historical records;
8. verifies readback;
9. leaves unknown newer structures read-only.

- [ ] **Step 3: Run tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_sensitive_personal_context_installation.py -v
git add skills/personal-ai-workspace-installer-upgrader skill-pack/migrations/1.5.1-to-1.6.0
git commit -m "feat: install and migrate sensitive personal context safely"
```

---

### Task 8: Integrate Context Bootstrap, private adapter and documentation

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/references/memory-fusion.md`
- Create: `skills/personal-ai-workspace-context-bootstrap/references/sensitive-personal-context.md`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_sensitive_personal_context_contract.py`
- Modify: `private/emma-workspace-memory-v6/references/context-routing.md` if present after its plan executes
- Modify: public-safe private-adapter tests
- Modify: `docs/MEMORY.md`

**Interfaces:**
- Bootstrap consumes only bounded summaries and canonical links.
- Private adapter provides private source locations and enabled-state configuration, never public fixtures.

- [ ] **Step 1: Add failing Bootstrap contract tests**

Assert:

- native memory is auxiliary;
- conflicts remain visible;
- current health excludes stopped/historical items;
- hypotheses are labelled;
- private records remain owner-only;
- full sensitive records are not copied into Bootstrap.

- [ ] **Step 2: Add private-adapter compatibility tests**

Public-safe tests use placeholder source-map values and require the private adapter to declare support for the Memory Fusion contract version and sensitive-context schema version.

- [ ] **Step 3: Update `docs/MEMORY.md`**

Document source precedence, relation materiality, psychological types, health lifecycle, privacy, owner correction, no-save and current-state summaries.

- [ ] **Step 4: Run root tests and scanner**

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider
python skill-pack/scripts/scan_private_identifiers.py .
```

Expected: all PASS and `public-safe: .`.

- [ ] **Step 5: Commit**

```bash
git add skills/personal-ai-workspace-context-bootstrap private/emma-workspace-memory-v6 docs/MEMORY.md
git commit -m "feat: integrate Memory Fusion across bootstrap and private adapter"
```

---

## Plan self-review checklist

- [ ] Source precedence is explicit, tested and non-destructive.
- [ ] Native memory cannot silently override canonical Workspace data.
- [ ] Every relationship statement is evaluated; only material durable data is saved.
- [ ] Transient mood, repeated pattern, interpretation and hypothesis remain distinct.
- [ ] Counterevidence and owner corrections are preserved.
- [ ] Health lifecycle prevents stopped items appearing as active.
- [ ] Explicit no-save, secret exclusion and owner-only disclosure remain enforced.
- [ ] Public fixtures are fictional and scanner-covered.
- [ ] Installer, memory, Bootstrap and private adapter share the same contract.
- [ ] Traceability covers public issue #15 and Apex #24.
