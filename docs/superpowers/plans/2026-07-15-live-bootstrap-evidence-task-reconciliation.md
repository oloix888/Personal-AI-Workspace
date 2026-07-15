# Live Bootstrap Evidence and Task Reconciliation — Implementation Plan

> **For Codex:** execute with `superpowers:subagent-driven-development`. Use a fresh implementer per task, then specification review and code-quality review. Fix all Critical and Important findings before advancing.

**Goal:** Make every new conversation prove capability and task coverage from current live sources instead of trusting a persisted Context Bootstrap cache.

**Tracking:** `oloix888/Apex#17`  
**Depends on:** foundation, disclosure, truncation, capability-catalog plans  
**Feeds:** installer/upgrader, context-bootstrap, integration/pilot, private-adapter plans

## Preflight

1. Start from current `main` in a clean worktree/branch.
2. Read:
   - `docs/superpowers/specs/2026-07-15-personal-ai-workspace-skill-pack-phase-1-design.md`
   - `docs/superpowers/specs/2026-07-15-phase-1-release-scope-audit.md`
   - `docs/superpowers/specs/2026-07-15-live-bootstrap-evidence-task-reconciliation-addendum.md`
   - capability, truncation, disclosure, memory, installer, bootstrap and private-adapter plans.
3. Record the workstream in `.superpowers/sdd/progress.md`.
4. Run the existing baseline suite before changes.
5. Do not publish a release or use private fixtures.

---

## Task 1 — Add evidence-report schemas

**Files**

- Create: `skill-pack/shared/schemas/capability-manifest-report.schema.json`
- Create: `skill-pack/shared/schemas/task-reconciliation-report.schema.json`
- Create: `skill-pack/shared/schemas/bootstrap-evidence-report.schema.json`
- Modify: shared schema index/validator registration
- Test: schema validation tests

### RED

Add failing tests that require:

- session ID and verification timestamp;
- owner/account result;
- source identifiers;
- pagination-complete flag;
- observed and expected counts;
- terminal-sentinel result;
- duplicate/missing-field results;
- task reconciliation outcomes;
- `FULL`, `PARTIAL`, `BLOCKED` status enums;
- explicit missing sources and conflicts.

Run only the new schema tests and confirm failure.

### GREEN

Implement the minimum valid schemas and register them with the common validator.

### VERIFY

- valid full/partial/blocked reports pass;
- malformed reports fail with useful paths;
- schemas are vendored into both standalone skill packages;
- public/private scanner passes.

### COMMIT

```text
git commit -m "feat: add live bootstrap evidence schemas"
```

---

## Task 2 — Implement paginated capability-manifest validation

**Files**

- Create: `skill-pack/shared/src/capability_manifest.py`
- Create: `skill-pack/shared/tests/test_capability_manifest.py`
- Add fixtures:
  - `live-full/`
  - `cached-full-live-partial/`
  - `missing-sentinel/`
  - `duplicate-sentinel/`
  - `count-mismatch/`
  - `duplicate-key/`
  - `missing-required-field/`

### Contract

The implementation accepts normalized pages from a connector adapter and MUST:

1. continue until `has_more=false`;
2. require exactly one semantic sentinel;
3. read `manifest_contract_version`, `manifest_revision`, `expected_record_count`, and required fields from the sentinel;
4. compare observed count to expected count;
5. check unique/non-empty keys and required fields;
6. produce a schema-valid report;
7. never use cached status to upgrade live evidence.

### RED

Write tests for all failure modes plus a new-session test where yesterday's cached `FULL` and today's truncated live read produce `PARTIAL`.

### GREEN

Implement a provider-neutral validator. Keep connector calling outside this module; consume normalized page batches.

### VERIFY

- deterministic ordering;
- no deployment-specific IDs or counts;
- disabled and explicit-only records remain represented;
- unknown supported fields are preserved or safely ignored;
- unit tests pass.

### COMMIT

```text
git commit -m "feat: validate paginated capability manifests"
```

---

## Task 3 — Add capability connector adapter contract

**Files**

- Create: `skill-pack/shared/references/capability-manifest-source-contract.md`
- Create/modify: connector capability adapter interfaces
- Test: adapter contract fixtures

### Requirements

Define semantic operations:

```text
capability_manifest.list_page(cursor, page_size)
capability_manifest.identity()
```

The contract MUST expose:

```text
records
has_more
next_cursor
source_id
read_at
truncated_or_partial
```

The skills MUST use page sizes small enough for reliable tool responses and MUST continue despite user-visible response summarization when the underlying tool reports a cursor.

### Tests

- three-page manifest;
- cursor repetition loop detection;
- provider returns `has_more=true` without cursor;
- mid-pagination authorization failure;
- response marked truncated;
- empty manifest;
- unsupported sentinel version.

### COMMIT

```text
git commit -m "feat: define capability manifest source contract"
```

---

## Task 4 — Implement task-ledger normalization and reconciliation

**Files**

- Create: `skill-pack/shared/src/task_reconciliation.py`
- Create: `skill-pack/shared/tests/test_task_reconciliation.py`
- Create fixtures:
  - `tasks/full/`
  - `tasks/unledgered-issue/`
  - `tasks/missing-backend/`
  - `tasks/conflicting-state/`
  - `tasks/multiple-priorities/`
  - `tasks/missing-priority/`
  - `tasks/superseded-open/`
  - `tasks/recurring/`
  - `tasks/many-pages/`

### Normalized task model

At minimum:

```text
deduplication_key
ledger_id
backend
backend_id
backend_url
title
owner
priority
status
due_date
blockers
approval_state
updated_at
source
```

### Reconciliation rules

Implement outcomes:

```text
RECONCILED
UNLEDGERED_TASK
MISSING_BACKEND_RECORD
CONFLICTING_STATE
MISSING_PRIORITY
MULTIPLE_PRIORITIES
OWNER_MISMATCH
SUPERSEDED_BUT_OPEN
STALE_LEDGER
```

Field precedence MUST be configurable. Do not silently collapse conflicting source values.

### RED/GREEN/VERIFY

- tests first;
- implementation second;
- report validates against schema;
- every active task appears once in compact index output;
- large fixtures paginate fully;
- closed/superseded task never appears active;
- public fixture names and identities are fictional.

### COMMIT

```text
git commit -m "feat: reconcile task ledger with execution backend"
```

---

## Task 5 — Add task source adapter contracts

**Files**

- Create: `skill-pack/shared/references/task-source-contract.md`
- Create/modify: semantic connector adapters
- Tests: source pagination and filtering

### Semantic operations

```text
task_ledger.list_page(cursor, page_size)
execution_backend.list_active_page(cursor, page_size, selector)
```

Support:

- task-only issue repositories;
- mixed repositories with configured label/prefix selectors;
- unclassified issue reporting;
- recurring internal tasks without external backend;
- multiple optional execution backends.

The public contract MUST NOT hard-code `Apex`, private labels, or private projects. Example priorities may use generic `priority:A/B/C` mappings, configurable per deployment.

### COMMIT

```text
git commit -m "feat: define paginated task source adapters"
```

---

## Task 6 — Integrate live evidence into Context Bootstrap skill

**Files**

- Modify: `skills/personal-ai-workspace-context-bootstrap/SKILL.md`
- Modify: context-bootstrap references/scripts
- Modify: `agents/openai.yaml`
- Tests: skill contract and end-to-end bootstrap fixtures

### Required startup sequence

1. verify account identity;
2. read complete root Constitution;
3. collect and validate live capability manifest;
4. collect task ledger and execution-backend state;
5. reconcile tasks;
6. check due reviews;
7. assemble bounded briefing;
8. persist optional cache only after the evidence report is complete;
9. load full instructions only for the minimal relevant verified capability set.

### Status behavior

- all required evidence full → `BOOTSTRAP_FULL`;
- optional gap → `BOOTSTRAP_PARTIAL` with exact limitation;
- identity/root/sentinel/security conflict → `BOOTSTRAP_BLOCKED`;
- cached full + live partial → `BOOTSTRAP_PARTIAL`;
- unverified optional capability → suppress implicit invocation.

### Context budget

Maintain `TASK_INDEX_MODE` and guarantee one compact row per active task. The capability manifest stays metadata-only; full skill bodies are loaded after routing.

### Tests

- new conversation revalidates;
- same-session bounded reuse if configured;
- live partial cannot be upgraded by cache;
- 500+ tasks and 100+ capabilities;
- explicit-only artifact routers remain explicit;
- disabled capability cannot route;
- current-session evidence metadata appears in output.

### COMMIT

```text
git commit -m "feat: make context bootstrap live-evidence based"
```

---

## Task 7 — Integrate repair into Installer & Upgrader

**Files**

- Modify: installer/upgrader `SKILL.md`, migration engine and fixtures
- Add migration manifest for pre-live-evidence installations
- Tests: install, upgrade, repair, rerun, rollback

### Fresh install

Create:

- configured-capabilities source/view;
- one terminal sentinel;
- deployment-specific expected count;
- bootstrap task-ledger view when tasks enabled;
- cache-only Context Bootstrap wording;
- evidence-report metadata.

### Upgrade/repair

Detect:

- no sentinel;
- duplicate sentinel;
- stale expected count;
- cached self-certification;
- missing task-ledger view;
- unledgered active backend task;
- superseded-but-open task;
- missing list/priority mapping.

Preview exact changes and require structural approval before creating or modifying views, schemas, or control records.

### Idempotency

Reruns MUST NOT duplicate:

- sentinel;
- configured views;
- ledger views;
- task records;
- migration records.

### COMMIT

```text
git commit -m "feat: install and repair live bootstrap controls"
```

---

## Task 8 — Integrate Autonomous Memory and cache refresh

**Files**

- Modify: Autonomous Memory references/contracts
- Tests: post-turn task and cache updates

### Rules

Autonomous Memory MAY update canonical data and affected cache sections after successful readback. It MUST NOT:

- mark a source full without reading it;
- change expected manifest count outside reviewed manifest migration;
- resolve source conflicts without contract authority;
- create new structural views;
- promise background repair.

### Tests

- new durable task creates internal ledger record under allowed policy;
- backend creation remains separately governed;
- backend failure records degraded state;
- cache refresh records evidence timestamp without becoming authority;
- no duplicate task on repeated capture.

### COMMIT

```text
git commit -m "feat: align memory capture with live bootstrap evidence"
```

---

## Task 9 — Update creator, docs and Codex guidance

**Files**

- Modify: creator source for `1.6.0`
- Modify: `INSTALLATION.md`
- Modify: `docs/CAPABILITIES.md`
- Modify/create: `docs/CONTEXT-BOOTSTRAP.md`
- Modify: ChatGPT/Codex install guides and `AGENTS.md` fragment
- Add: troubleshooting guide

### Documentation requirements

Explain:

```text
configured != callable
cached != current-session verified
partial != full
installed != authorized
open backend record != reconciled task
```

Provide user-facing repair paths for:

- missing sentinel;
- count mismatch;
- connector pagination failure;
- unledgered task;
- superseded issue;
- surface mismatch;
- optional source degradation.

The public creator MUST instruct AI to paginate live sources, not copy private view IDs or counts.

### COMMIT

```text
git commit -m "docs: document live bootstrap evidence and task reconciliation"
```

---

## Task 10 — Update private Emma adapter plan and compatibility tests

**Files**

- Modify private-adapter build inputs outside public package as appropriate
- Modify public compatibility contract only with generic requirements
- Tests: private adapter references deployment-specific IDs without leaking them

### Requirements

The private adapter MUST supply:

- configured view identifiers;
- task-ledger view identifier;
- private task backend policy;
- manifest revision and expected count;
- private account identities;
- current Workspace versions;
- rollback configuration.

Public builds and logs MUST not contain those private values.

### COMMIT

```text
git commit -m "test: extend private adapter live-bootstrap compatibility"
```

---

## Task 11 — Whole-workstream verification

Run:

1. complete unit/integration suite;
2. creator reconstruction and migration tests;
3. standalone and combined package builds;
4. deterministic rebuild comparison;
5. ZIP integrity and SHA-256 checks;
6. public/private scanner;
7. ChatGPT skill validation;
8. Codex user-global installation verification;
9. large-manifest and large-task stress fixtures;
10. whole-branch specification review against Apex #6–#17.

Required evidence:

```text
all tests pass
no private identifiers
no cached self-certification
no silent task omission
no automatic prerelease publication
```

Create a draft implementation PR. Do not publish `0.1.0-beta.1` or activate the live private adapter without later explicit approval.

### FINAL COMMIT

```text
git commit -m "test: verify live bootstrap and task reconciliation end to end"
```
