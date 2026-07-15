# Autonomous Memory Capture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Personal AI Workspace autonomously save or update material durable information during active conversations without requiring per-record permission, while preserving canonical records, provenance, user control, structural governance, and owner-only disclosure.

**Architecture:** Add a shared capture contract and machine-readable candidate/write schemas. Context Bootstrap performs a bounded post-turn capture pass and routes candidates to generic destination adapters. Installer & Upgrader creates or migrates the feature and Constitution rules. Deterministic local scripts classify candidates and render write plans; connector-backed discovery, writes, and readback remain instruction-led. The public package contains no private records or identifiers.

**Tech Stack:** Python 3.11+, JSON Schema Draft 2020-12, pytest, Agent Skills Markdown, Notion connector workflows, public-safe fixtures.

## Global Constraints

- Ordinary create/update operations inside approved schemas may be autonomous.
- Structural changes, new databases/properties, permanent protected-record deletion, external disclosure, communication, publication, invitations, financial trades, deployment, paid compute, and sensitive-data cloud upload remain approval-gated.
- Never persist hidden chain-of-thought, private scratchpads, passwords, tokens, API keys, one-time codes, reset links, cookies, or other authentication secrets.
- Respect explicit `do not save this`, source restrictions, correction, archive, merge, and deletion instructions.
- Sensitive context may be retained when materially relevant, with purpose, provenance, epistemic status, perspective, confidence, validity, and Confidential classification.
- Deduplicate and update canonical records; do not create parallel copies when a safe match exists.
- Preserve contradiction, correction, and supersession history.
- Do not promise background retry. A failed capture reports `MEMORY_CAPTURE_DEGRADED` in the active session.
- Do not announce every tiny successful write; report material changes or failures when useful.
- Public fixtures and packages contain no private Emma Workspace data.
- Every task follows TDD and ends with a focused commit.
- This plan does not authorize prerelease publication.

---

## File Map

```text
skills/_shared/
├── contract/autonomous-memory-capture.md
└── schemas/
    ├── memory-candidate.schema.json
    ├── memory-capture-plan.schema.json
    └── memory-capture-result.schema.json
skill-pack/src/paiw_skill_pack/
├── memory.py
└── redaction.py                         # extend if present
skill-pack/tests/
├── fixtures/memory/
│   ├── durable-fact.json
│   ├── transient-small-talk.json
│   ├── correction.json
│   ├── reported-claim.json
│   ├── secret-adjacent.json
│   ├── do-not-save.json
│   └── large-turn.json
├── test_memory_candidates.py
├── test_memory_plans.py
└── test_memory_safety.py
skills/personal-ai-workspace-context-bootstrap/
├── references/autonomous-memory-capture.md
├── scripts/classify_memory_candidates.py
├── scripts/render_capture_plan.py
└── tests/
    ├── test_memory_capture.py
    ├── test_memory_budget.py
    └── test_memory_failure_modes.py
skills/personal-ai-workspace-installer-upgrader/
├── references/autonomous-memory-capture.md
└── tests/test_autonomous_memory_installation.py
skill-pack/migrations/1.5.1-to-1.6.0/
└── autonomous-memory.md
docs/
└── MEMORY.md
```

---

### Task 1: Define capture schemas and shared contract

**Files:**
- Create: `skills/_shared/contract/autonomous-memory-capture.md`
- Create: `skills/_shared/schemas/memory-candidate.schema.json`
- Create: `skills/_shared/schemas/memory-capture-plan.schema.json`
- Create: `skills/_shared/schemas/memory-capture-result.schema.json`
- Create: `skill-pack/tests/test_memory_candidates.py`

**Interfaces:**

A candidate uses:

```text
candidate_id
candidate_type
proposed_destination
statement_or_summary
source_context
occurred_at_or_validity
perspective
epistemic_status
confidence
sensitivity
materiality_reason
requested_action
explicit_save_instruction
explicit_no_save
```

A capture plan uses:

```text
capture_id
candidates
writes
skipped
review_required
coverage
```

A write uses:

```text
operation
canonical_key
destination
match_evidence
content_patch
provenance
readback_requirements
```

- [ ] **Step 1: Write failing schema tests**

```python
# skill-pack/tests/test_memory_candidates.py
import pytest
from jsonschema import ValidationError
from paiw_skill_pack.schemas import validate_payload


def test_valid_memory_candidate() -> None:
    validate_payload(
        "memory-candidate.schema.json",
        {
            "candidate_id": "cand-1",
            "candidate_type": "Preference",
            "proposed_destination": "Knowledge",
            "statement_or_summary": "The user prefers concise weekly reviews.",
            "source_context": {"type": "conversation", "reference": "turn-1"},
            "occurred_at_or_validity": None,
            "perspective": "User",
            "epistemic_status": "Fact",
            "confidence": "High",
            "sensitivity": "Private",
            "materiality_reason": "Stable operating preference",
            "requested_action": "AUGMENT_EXISTING",
            "explicit_save_instruction": False,
            "explicit_no_save": False,
        },
    )


def test_secret_candidate_type_is_not_available() -> None:
    payload = {
        "candidate_id": "cand-secret",
        "candidate_type": "Password",
        "proposed_destination": "Knowledge",
        "statement_or_summary": "secret",
        "source_context": {"type": "conversation", "reference": "turn-2"},
        "occurred_at_or_validity": None,
        "perspective": "User",
        "epistemic_status": "Fact",
        "confidence": "High",
        "sensitivity": "Confidential",
        "materiality_reason": "Authentication",
        "requested_action": "CREATE_NEW",
        "explicit_save_instruction": True,
        "explicit_no_save": False,
    }
    with pytest.raises(ValidationError):
        validate_payload("memory-candidate.schema.json", payload)
```

- [ ] **Step 2: Run and verify RED**

```bash
python -m pytest skill-pack/tests/test_memory_candidates.py -v
```

- [ ] **Step 3: Implement strict schemas**

Use exact enums:

```text
candidate_type:
  Fact, Reported Claim, Observation, Interpretation, Hypothesis,
  Preference, Goal, Value, Constraint, Correction, Decision, Strategy,
  Commitment, Task, Source, Artifact, Operational Observation

proposed_destination:
  Knowledge, Relations, Decisions, Tasks, Sources, Artifacts, Evolution

requested_action:
  CREATE_NEW, AUGMENT_EXISTING, CORRECT_EXISTING, CONTRADICT_EXISTING,
  SUPERSEDE_EXISTING, NO_CHANGE, REVIEW_REQUIRED

epistemic_status:
  Fact, Reported Claim, Observation, Interpretation, Hypothesis

confidence:
  High, Medium, Low, Unknown

sensitivity:
  Public, Private, Confidential
```

Schemas must use `additionalProperties: false` and reject empty summaries.

- [ ] **Step 4: Write shared contract**

The contract includes materiality, exclusions, autonomy boundary, canonical matching, readback, selective refresh, capture budgets, user control, and failure states exactly as the approved design.

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_memory_candidates.py -v
git add skills/_shared skill-pack/tests/test_memory_candidates.py
git commit -m "feat: define autonomous memory capture contract"
```

---

### Task 2: Implement deterministic candidate filtering and classification

**Files:**
- Create: `skill-pack/src/paiw_skill_pack/memory.py`
- Create: `skill-pack/tests/test_memory_candidates.py`
- Add fixtures under `skill-pack/tests/fixtures/memory/`

**Interfaces:**

```python
classify_candidate(candidate: dict) -> CandidateDecision
filter_candidates(candidates: list[dict], limits: CaptureLimits) -> CaptureSelection
```

- [ ] **Step 1: Add failing classification tests**

Cover:

```python
def test_durable_preference_is_selected(): ...
def test_transient_small_talk_is_skipped(): ...
def test_explicit_save_instruction_increases_priority_but_does_not_allow_secret(): ...
def test_explicit_no_save_is_skipped(): ...
def test_reported_claim_keeps_reported_claim_status(): ...
def test_secret_is_removed_while_adjacent_useful_context_remains(): ...
def test_candidates_are_clustered_and_bounded(): ...
```

- [ ] **Step 2: Run RED**

```bash
python -m pytest skill-pack/tests/test_memory_candidates.py -v
```

- [ ] **Step 3: Implement models**

Use:

```python
from dataclasses import dataclass
from enum import StrEnum

class CandidateDisposition(StrEnum):
    SELECT = "SELECT"
    SKIP_TRANSIENT = "SKIP_TRANSIENT"
    SKIP_DUPLICATE = "SKIP_DUPLICATE"
    SKIP_SECRET = "SKIP_SECRET"
    SKIP_EXPLICIT_NO_SAVE = "SKIP_EXPLICIT_NO_SAVE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"

@dataclass(frozen=True, slots=True)
class CaptureLimits:
    max_candidates: int = 12
    max_direct_writes: int = 5
```

Classification is deterministic over normalized candidate metadata. It does not infer hidden content from free-form conversation in local scripts.

Priority order:

1. explicit correction;
2. commitment/deadline/task;
3. explicit decision;
4. stable preference/goal/constraint;
5. high-impact relationship context;
6. reusable source/artifact;
7. other durable facts;
8. operational observations.

- [ ] **Step 4: Add secret redaction**

Recognize password, API key, access token, one-time code, reset link, session cookie, and private key patterns. Return a skipped finding without logging the full secret. Keep adjacent non-secret summary only when it stands independently.

- [ ] **Step 5: Test and commit**

```bash
python -m pytest skill-pack/tests/test_memory_candidates.py -v
git add skill-pack/src/paiw_skill_pack/memory.py skill-pack/tests/test_memory_candidates.py skill-pack/tests/fixtures/memory
git commit -m "feat: classify bounded memory candidates"
```

---

### Task 3: Build canonical write plans

**Files:**
- Extend: `skill-pack/src/paiw_skill_pack/memory.py`
- Create: `skill-pack/tests/test_memory_plans.py`

**Interfaces:**

```python
build_capture_plan(
    candidates: list[dict],
    canonical_matches: dict[str, list[dict]],
    limits: CaptureLimits,
) -> dict
```

- [ ] **Step 1: Write failing plan tests**

Verify:

- one exact match -> augment existing;
- correction -> correct existing and preserve prior version metadata;
- conflicting sources -> contradict existing;
- several plausible people -> review required, not guessed merge;
- no match -> create new;
- unchanged canonical content -> no change;
- repeated run -> no duplicate write;
- at most five direct writes by default.

- [ ] **Step 2: Implement canonical matching contract**

Local planning consumes connector-normalized candidate matches with fields:

```text
record_id
canonical_key
destination
match_score
match_reasons
current_version
current_summary
source_links
```

Rules:

- exact stable ID or dedup key controls;
- unique high-confidence match may update;
- ambiguous match becomes `REVIEW_REQUIRED`;
- semantic similarity alone must not merge people or legal/financial records;
- content patch contains only changed fields or bounded appended content;
- plan carries readback requirements.

- [ ] **Step 3: Test**

```bash
python -m pytest skill-pack/tests/test_memory_plans.py -v
```

- [ ] **Step 4: Commit**

```bash
git add skill-pack/src/paiw_skill_pack/memory.py skill-pack/tests/test_memory_plans.py
git commit -m "feat: build canonical memory write plans"
```

---

### Task 4: Add Context Bootstrap capture workflow

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/references/autonomous-memory-capture.md`
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/classify_memory_candidates.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/render_capture_plan.py`
- Extend: `skills/personal-ai-workspace-context-bootstrap/SKILL.md`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_memory_capture.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_memory_budget.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_memory_failure_modes.py`

- [ ] **Step 1: Write failing skill-contract tests**

Assert `SKILL.md` contains:

```text
Autonomous Memory Capture
material durable information
canonical record
explicit do not save
MEMORY_CAPTURE_DEGRADED
no background retry
structural changes still require approval
external disclosure still requires one-time approval
```

- [ ] **Step 2: Write end-to-end fixture tests**

Input fixture:

```json
{
  "normalized_candidates": [],
  "canonical_matches": {},
  "connector_state": {
    "identity_verified": true,
    "notion_read": true,
    "notion_write": true
  }
}
```

Expected output includes selected writes, skipped reasons, coverage, and readback checklist. Scripts never call live connectors.

- [ ] **Step 3: Implement CLI wrappers**

```bash
python scripts/classify_memory_candidates.py input.json --output candidates.json
python scripts/render_capture_plan.py candidates.json matches.json --output capture-plan.json
```

Both commands write deterministic sorted JSON and return nonzero on invalid input.

- [ ] **Step 4: Write workflow reference**

Instructions must:

1. run after a material active turn;
2. normalize candidates without copying the full conversation;
3. verify identity and enabled feature state;
4. search only task-relevant canonical destinations;
5. execute at most the approved bounded writes;
6. read back each write;
7. refresh only affected bootstrap sections;
8. report capture degradation when material.

- [ ] **Step 5: Test and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_memory_capture.py skills/personal-ai-workspace-context-bootstrap/tests/test_memory_budget.py skills/personal-ai-workspace-context-bootstrap/tests/test_memory_failure_modes.py -v
git add skills/personal-ai-workspace-context-bootstrap
git commit -m "feat: add post-turn autonomous memory capture"
```

---

### Task 5: Define destination adapters and privacy boundaries

**Files:**
- Extend: `skills/personal-ai-workspace-context-bootstrap/references/autonomous-memory-capture.md`
- Create: `skill-pack/tests/test_memory_safety.py`
- Add fixtures for Knowledge, Relations, Decisions, Tasks, Sources, Artifacts, and Evolution.

- [ ] **Step 1: Write failing routing tests**

Verify:

- Preference -> Knowledge.
- Relationship interaction -> Relations.
- Explicit material choice -> Decisions.
- Actionable obligation -> internal Task Outbox plan.
- Source URL and evidence -> Sources.
- Final file checksum -> Artifacts/Source record.
- Connector correction -> Evolution.

- [ ] **Step 2: Write safety tests**

Verify:

- no GitHub Issue is automatically created when backend visibility/privacy is unknown;
- public/shared destination requires one-time disclosure approval;
- private approved Task Outbox staging is allowed;
- external email draft may be prepared but send is not authorized;
- feature/provider state is not changed by capture;
- protected deletion is not performed;
- sensitive context is correctly classified;
- disabled capability produces no live-read candidates.

- [ ] **Step 3: Implement destination mapping as data**

Use a public mapping file or typed constant. Do not hardcode private data source IDs.

- [ ] **Step 4: Test and commit**

```bash
python -m pytest skill-pack/tests/test_memory_safety.py -v
git add skill-pack/tests/test_memory_safety.py skill-pack/tests/fixtures/memory skills/personal-ai-workspace-context-bootstrap/references/autonomous-memory-capture.md
git commit -m "test: enforce memory destination and privacy boundaries"
```

---

### Task 6: Extend Installer & Upgrader and framework migration

**Files:**
- Create: `skills/personal-ai-workspace-installer-upgrader/references/autonomous-memory-capture.md`
- Extend: `skills/personal-ai-workspace-installer-upgrader/SKILL.md`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_autonomous_memory_installation.py`
- Add: `skill-pack/migrations/1.5.1-to-1.6.0/autonomous-memory.md`
- Extend migration manifest validation.

- [ ] **Step 1: Write failing installation tests**

Verify fresh install:

- adds Autonomous Memory Capture as Core Enabled by default;
- shows behavior and boundaries in the exact-scope blueprint;
- lets the owner pause or disable it;
- writes rules to modules 00, 02, 03, 09, and 11;
- preserves Notion-only core functionality;
- validates readback.

Verify upgrade:

- detects older explicit-save-only behavior;
- does not duplicate existing Knowledge/Relations records;
- preserves `do not save` restrictions;
- preserves retention and sensitive-context rules;
- is idempotent;
- rolls back configuration without deleting captured history.

- [ ] **Step 2: Implement installation reference**

The user-facing explanation must say:

> During active conversations, the assistant may save or update material durable information inside the approved Workspace structure without asking for every ordinary record. It still asks before structural changes, permanent protected deletion, disclosure, communication, publication, financial actions, deployment, and other consequential operations.

- [ ] **Step 3: Add migration operations**

The `1.5.1-to-1.6.0` migration adds the feature record and updates the relevant modules, Feature Registry, Context Bootstrap, and Personalization/project snippets. It never copies raw old conversations.

- [ ] **Step 4: Test and commit**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_autonomous_memory_installation.py -v
git add skills/personal-ai-workspace-installer-upgrader skill-pack/migrations/1.5.1-to-1.6.0
git commit -m "feat: install and migrate autonomous memory capture"
```

---

### Task 7: Update public creator and private-adapter contract

**Files:**
- Update the public creator source for framework `1.6.0`.
- Update: private Emma adapter v6 plan/spec references.
- Create: `docs/MEMORY.md`
- Update: `README.md` and installation docs.

- [ ] **Step 1: Add creator contract tests**

Verify the creator:

- explains autonomous ordinary writes before blueprint approval;
- installs the correct module text;
- includes a user-visible enable/disable choice;
- preserves structural and disclosure gates;
- produces Personalization/project instructions containing a bounded active-session capture pass;
- does not promise background capture;
- provides a test prompt and expected result.

- [ ] **Step 2: Add private-adapter requirements**

The private adapter supplies only private configuration and source mappings. It must compose the public capture contract and verify compatibility. It must not duplicate or weaken the generic safety rules.

- [ ] **Step 3: Write user documentation**

`docs/MEMORY.md` explains:

- what is saved;
- what is not saved;
- how canonical updates work;
- how to inspect, pause, restrict, correct, or delete;
- sensitive context;
- failure states;
- why this is not hidden reasoning or background surveillance.

- [ ] **Step 4: Commit**

```bash
git add README.md docs skill-pack skills
git commit -m "docs: explain autonomous memory capture"
```

---

### Task 8: Whole-feature verification

- [ ] **Step 1: Run focused tests**

```bash
python -m pytest skill-pack/tests/test_memory_candidates.py skill-pack/tests/test_memory_plans.py skill-pack/tests/test_memory_safety.py skills/personal-ai-workspace-context-bootstrap/tests/test_memory_capture.py skills/personal-ai-workspace-context-bootstrap/tests/test_memory_budget.py skills/personal-ai-workspace-context-bootstrap/tests/test_memory_failure_modes.py skills/personal-ai-workspace-installer-upgrader/tests/test_autonomous_memory_installation.py -v
```

- [ ] **Step 2: Run full suite**

```bash
python -m pytest -v
```

- [ ] **Step 3: Scan public packages**

```bash
python skill-pack/scripts/scan_private_identifiers.py skills skill-pack docs
```

- [ ] **Step 4: Run scenario matrix**

```text
stable preference -> canonical Knowledge update
person's new role -> Relations update with source
correction -> prior history preserved
small talk -> skipped
reported rumor -> Reported Claim
password plus useful project fact -> password excluded, project fact retained
do not save this -> skipped
new schema needed -> structural approval required
external email -> draft boundary, no send authority
connector unavailable -> MEMORY_CAPTURE_DEGRADED
repeated same turn -> idempotent no duplicate
15 candidates -> bounded selection and review overflow
```

- [ ] **Step 5: Record verification evidence**

Commit a concise public-safe test report containing commands, counts, and limitations. Do not include fixture secrets or private Workspace data.

- [ ] **Step 6: Commit**

```bash
git add docs/test-results skill-pack/test-results 2>/dev/null || true
git commit -m "test: verify autonomous memory capture end to end"
```

Do not publish a release in this task.
