# Personal AI Workspace — Live Bootstrap Evidence and Task Reconciliation Addendum

**Status:** Approved binding addendum for Phase 1 development  
**Date:** 2026-07-15  
**Tracking:** `oloix888/Apex#17`  
**Applies to:** framework/creator `1.6.0`, public Skill Pack `0.1.0-beta.1`, private adapter `6.0.0-rc.1`  
**Publication:** Not authorized by this document

## 1. Why this addendum exists

A bootstrap cache reported that the capability registry was complete, while the live registry response available in that conversation was truncated. The conversation accepted the cached assertion as proof of current completeness. A separate audit also found open execution issues that were missing from the canonical task ledger and an obsolete issue that remained open.

The underlying design was directionally correct but lacked a mechanical source-evidence contract.

This addendum makes the following rule binding:

> A cached briefing may orient the assistant, but it can never certify the live source that it summarizes.

`FULL` is a current-session evidence result, not a durable property copied from an earlier conversation.

## 2. Normative language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

This document supplements the approved Phase 1 architecture and scope audit. Where an older document permits a cached status to be treated as current evidence, this addendum controls.

## 3. Source-of-truth hierarchy

For startup and operational briefing, use this hierarchy:

1. current authenticated account identity;
2. complete root Workspace Constitution readback;
3. current paginated capability-manifest source;
4. current paginated task ledger;
5. current execution-backend state;
6. current due-review sources;
7. cached Context Bootstrap content;
8. narrative summaries or old reports.

A lower source can add orientation but MUST NOT override a conflicting or incomplete higher source.

## 4. Current-session evidence lease

### 4.1 Session scope

Every new conversation or isolated agent run MUST revalidate bootstrap sources.

A status such as:

```text
CAPABILITY_MANIFEST_FULL
TASK_COVERAGE_FULL
BOOTSTRAP_FULL
```

expires at the end of the conversation or execution session that produced it.

It MUST NOT be inherited merely because:

- Context Bootstrap says the previous run was full;
- the database was full yesterday;
- another conversation validated the same workspace;
- a stored health-check timestamp is recent;
- the provider or account is usually available.

### 4.2 Freshness

Each evidence report MUST contain:

```text
verified_at
surface
owner_identity
source_ids_or_urls
pagination_complete
record_count
expected_record_count
sentinel_or_terminal_marker
conflicts
missing_sources
status
```

The public product MAY define a configurable freshness window for repeated checks inside one uninterrupted session. It MUST NOT silently carry that window into a new conversation.

## 5. Capability manifest completeness contract

### 5.1 Dedicated configured-capabilities view

The installer MUST create or identify a canonical view containing every configured capability record, including enabled, disabled, pending, unavailable, paused, and degraded entries.

The bootstrap skill MUST query this view with pagination until:

```text
has_more = false
```

A single database-schema fetch or a truncated tool response is not a manifest read.

### 5.2 Terminal sentinel

Every installed manifest MUST contain exactly one terminal control record with a stable semantic key, for example:

```text
zz.system.capability-manifest-sentinel
```

The sentinel stores at least:

```text
manifest_contract_version
manifest_revision
expected_record_count
required_fields
last_reconciled_at
```

A public implementation MUST NOT hard-code a private deployment's record count. It reads the expected count from the installed sentinel or migration manifest.

### 5.3 Required validation

`CAPABILITY_MANIFEST_FULL` requires all of the following:

1. the owner/account identity is verified;
2. pagination reached `has_more=false`;
3. the terminal sentinel is present exactly once;
4. the observed record count equals the sentinel's expected count;
5. every `Feature Key` is non-empty and unique;
6. every record has non-empty:
   - `State`;
   - `Activation Policy`;
   - `Capability Kind`;
   - `Risk Tier`;
   - `Selected Provider`;
7. the sentinel contract version is supported;
8. no manifest revision conflict is present.

Recommended additional validation:

- stable sort or canonical-key ordering;
- optional manifest digest;
- provider/state dependency checks;
- explicit-only and disabled-capability invariants;
- surface compatibility checks.

### 5.4 Failure states

Use explicit states:

```text
CAPABILITY_MANIFEST_FULL
CAPABILITY_MANIFEST_PARTIAL
CAPABILITY_MANIFEST_CONFLICT
CAPABILITY_MANIFEST_BLOCKED
```

Examples:

- pagination stopped early → `PARTIAL`;
- sentinel missing or duplicated → `CONFLICT`;
- observed count differs from expected → `CONFLICT`;
- account mismatch → `BLOCKED`;
- provider temporarily unavailable after some pages → `PARTIAL`;
- root Constitution truncated → `BLOCKED`.

When the manifest is not full, the assistant MUST NOT implicitly invoke an optional capability whose current state was not verified. Explicit user requests may proceed only after the capability's own live availability, authorization, activation policy, and risk gate are verified.

## 6. Task-ledger and execution-backend reconciliation

### 6.1 Canonical task ledger

An installation with task management enabled MUST expose a bootstrap-oriented task-ledger view. It MUST be queryable with pagination and include at least:

```text
task_id_or_deduplication_key
title
owner
priority_list
status
due_date
blockers
approval_state
backend
backend_record_id
backend_url
last_sync_attempt
source
```

### 6.2 Execution backend

For every configured task backend, the bootstrap MUST obtain a complete current list of active execution records.

For GitHub Issues:

- paginate all matching open issues;
- use the deployment's task selection policy;
- in a task-only repository, every open issue is in scope;
- in a mixed repository, configured task labels/prefixes define scope, while unclassified open issues are reported rather than silently ignored;
- verify issue state, title, owner/assignee, labels, and update time.

### 6.3 Reconciliation outcomes

Each active backend record MUST resolve to one of:

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

The assistant MUST NOT silently choose a winner when source values conflict, except where the installed source-precedence contract explicitly owns a field.

### 6.4 Full task coverage

`TASK_COVERAGE_FULL` requires:

1. task-ledger pagination reached `has_more=false`;
2. backend pagination reached its terminal state;
3. every active backend task has a ledger record or an explicitly accepted exception;
4. every active ledger task with an external backend has a resolvable backend record;
5. every task has one allowed priority/list classification;
6. ownership and status conflicts are resolved or explicitly surfaced;
7. superseded or closed records are not presented as active;
8. all recurring tasks are represented;
9. the report states counts and reconciliation results.

A static hand-written list of "important tasks" is never a substitute for complete active-task coverage.

## 7. Bootstrap status model

The Context Bootstrap skill MUST produce one of:

```text
BOOTSTRAP_FULL
BOOTSTRAP_PARTIAL
BOOTSTRAP_BLOCKED
```

### `BOOTSTRAP_FULL`

Requires:

- verified owner/account;
- complete root Constitution readback;
- `CAPABILITY_MANIFEST_FULL`;
- `TASK_COVERAGE_FULL` when task management is enabled;
- due Decision/System Evolution review checks;
- source freshness and conflict report;
- a bounded briefing or `TASK_INDEX_MODE` representation.

### `BOOTSTRAP_PARTIAL`

Used when material work can safely continue with clearly listed gaps, such as an optional source being unavailable. It MUST list:

- unavailable source;
- affected sections;
- what is omitted or stale;
- whether optional capability routing is restricted;
- the strongest safe next action.

### `BOOTSTRAP_BLOCKED`

Used for hard failures, including:

- wrong owner/account;
- truncated or unverifiable root Constitution;
- unsupported manifest contract;
- missing or conflicting terminal sentinel;
- security-policy conflict;
- another installed hard block.

## 8. Context Bootstrap cache semantics

The persisted Context Bootstrap page is a bounded cache and navigation surface. It MAY contain:

- last successful evidence report;
- current counts;
- material conflicts;
- high-value active-state index;
- links to live views and sources;
- known degraded integrations.

It MUST include a statement equivalent to:

> This cache is not proof of current source completeness. Revalidate live sources in every new conversation.

The cache MUST NOT:

- self-certify its own freshness;
- turn a partial live read into full;
- copy the entire workspace;
- copy every full skill body;
- silently omit active tasks because of context limits.

## 9. Installer and migration requirements

The Installer & Upgrader MUST:

1. create or locate the configured-capabilities view;
2. create or locate one terminal sentinel;
3. write the expected count transactionally with manifest changes;
4. create or locate the bootstrap task-ledger view when task management is enabled;
5. migrate older caches from authoritative status to cache-only semantics;
6. detect duplicate/missing capability keys and task records;
7. detect superseded-but-open tasks where the migration can establish the relationship;
8. preserve owner choices, providers, states, history, and links;
9. execute idempotently;
10. read back every created/updated control record;
11. expose rollback and repair evidence.

An installation lacking these controls is `PARTIAL` or `DAMAGED`, depending on risk and whether safe operation is possible.

## 10. Autonomous Memory interaction

Autonomous Memory Capture remains a separate bounded post-turn phase.

It MAY update:

- durable task facts;
- canonical task-ledger records;
- source links;
- material conflicts;
- affected Context Bootstrap cache sections.

It MUST NOT:

- mark a live source full without reading it;
- invent backend status;
- change the sentinel count without a reviewed manifest change;
- create a new schema or view without structural approval;
- hide a reconciliation conflict;
- claim a background retry.

## 11. Public/private boundary

Public source, tests, and examples MUST use fictional identifiers and generic provider names. They MUST NOT contain:

- private Notion IDs or view IDs;
- private repositories or task content;
- private account identities;
- private contacts, email, projects, or relationships;
- a private manifest count as a universal constant.

The private adapter MAY store deployment-specific IDs and expected counts outside public source.

## 12. Required schemas and artifacts

Phase 1 SHOULD add:

```text
bootstrap-evidence-report.schema.json
capability-manifest-report.schema.json
task-reconciliation-report.schema.json
fixtures/bootstrap/live-full/
fixtures/bootstrap/cached-full-live-partial/
fixtures/bootstrap/missing-sentinel/
fixtures/bootstrap/count-mismatch/
fixtures/tasks/unledgered-issue/
fixtures/tasks/superseded-open/
fixtures/tasks/conflicting-state/
```

The public documentation MUST explain the difference between:

- configured;
- callable;
- current-session verified;
- cached;
- full;
- partial;
- blocked.

## 13. Mandatory tests

### Capability manifest

- cached `FULL` plus truncated live source returns `PARTIAL`;
- pagination continues until `has_more=false`;
- missing terminal sentinel fails;
- duplicate terminal sentinel fails;
- expected-count mismatch fails;
- duplicate `Feature Key` fails;
- missing required field fails;
- disabled capability stays disabled;
- provider and surface constraints are preserved;
- new conversation requires new verification.

### Tasks

- active backend issue missing from ledger yields `UNLEDGERED_TASK`;
- active ledger task missing from backend yields `MISSING_BACKEND_RECORD`;
- closed or superseded backend record is not active;
- multiple priority labels fail;
- missing priority fails;
- status and owner conflicts are surfaced;
- recurring tasks are included;
- large ledgers and issue sets paginate fully;
- `TASK_INDEX_MODE` preserves one row per active task.

### Bootstrap

- all full prerequisites produce `BOOTSTRAP_FULL`;
- optional source gap produces truthful `BOOTSTRAP_PARTIAL`;
- wrong account/root truncation/sentinel conflict produces `BOOTSTRAP_BLOCKED`;
- cache cannot upgrade live evidence;
- optional implicit routing is suppressed when capability state is unverified;
- persisted cache records source coverage and verification time.

### Migration

- old installation without sentinel upgrades idempotently;
- old static task list migrates to live-ledger semantics;
- expected counts update with manifest records;
- rollback restores prior controls without deleting user data;
- rerun creates no duplicate views, sentinels, tasks, or migrations.

## 14. Release gate

The Skill Pack prerelease MUST NOT be published until:

1. this addendum is implemented in creator, both public skills, shared contracts, docs, and private adapter;
2. all mandatory tests pass;
3. a clean-install fixture and supported-upgrade fixture produce full evidence reports;
4. a deliberately partial fixture remains partial;
5. public/private scanning passes;
6. whole-branch review confirms no cached self-certification remains.
