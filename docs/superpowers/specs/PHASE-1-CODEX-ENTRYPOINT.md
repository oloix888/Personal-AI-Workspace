# Personal AI Workspace Phase 1 — Canonical Codex Entrypoint

**Status:** Binding implementation entrypoint  
**Date:** 2026-07-17  
**Base:** latest `main` only  
**Execution:** `superpowers:subagent-driven-development`  
**Publication:** not authorized

## Purpose

This file is the single starting point for Codex implementation. It resolves the order of the original Phase 1 plans and all subsequently approved binding addenda.

Do not implement from the obsolete `feat/skill-pack-phase-1` branch or closed PR #4.

The active implementation is Draft PR #11 on branch `codex/zacznij-implementacje-fazy-1-personal-ai-workspace`. When resuming that branch, fetch current `main`, merge it without force-pushing, preserve completed reviewed work and update the same Draft PR.

## Preflight

1. Create or resume a clean worktree/branch from the latest `main`.
2. Read the architecture and scope documents below.
3. Run the preflight conflict scan required by Subagent-Driven Development.
4. Create and maintain `.superpowers/sdd/progress.md`.
5. Use a fresh implementer for each task, followed by specification review and code-quality review.
6. Fix all Critical and Important findings before advancing.
7. Never publish a prerelease or activate the live private adapter without a later explicit approval naming the exact version.
8. Preserve completed reviewed work; do not restart a completed workstream without a concrete defect or new binding requirement.

## Binding specifications

Read all of these before implementation:

1. `docs/superpowers/specs/2026-07-15-personal-ai-workspace-skill-pack-phase-1-design.md`
2. `docs/superpowers/specs/2026-07-15-phase-1-release-scope-audit.md`
3. `docs/superpowers/specs/2026-07-15-one-time-disclosure-consent-addendum.md`
4. `docs/superpowers/specs/2026-07-15-constitution-truncation-safety-addendum.md`
5. `docs/superpowers/specs/2026-07-15-capability-catalog-plugin-orchestration-design.md`
6. `docs/superpowers/specs/2026-07-15-autonomous-memory-capture-design.md`
7. `docs/superpowers/specs/2026-07-15-live-bootstrap-evidence-task-reconciliation-addendum.md`
8. `docs/superpowers/specs/2026-07-17-personal-context-and-active-workspace-semantics-addendum.md`

If a filename differs slightly in the repository, locate the matching approved document by title and record the resolved path in the progress ledger before implementation.

## Document precedence

When two approved documents differ, apply this precedence from highest to lowest:

1. this canonical entrypoint;
2. the newest binding addendum that addresses the disputed behavior;
3. the final Phase 1 release scope audit;
4. the focused implementation plan for the affected workstream;
5. the original Phase 1 architecture specification;
6. older issue text, historical PR descriptions, cached reports or obsolete implementation branches.

Do not silently choose between conflicts. Record the conflict and applied precedence in `.superpowers/sdd/progress.md`.

## Version targets

```text
Framework / Markdown creator: 1.6.0
Public Skill Pack: 0.1.0-beta.1
Installer & Upgrader: 0.1.0-beta.1
Context Bootstrap: 0.1.0-beta.1 with personal-focus contract
Private Emma adapter: 6.0.0-rc.1
Private rollback skill: 5.6.0
```

## Binding private-adapter errata

The older private-adapter plan contains historical references to migration from `5.5.0` and artifact names for a stable `6.0.0`. Those references are superseded.

The implementation MUST use:

```text
migration baseline: emma-workspace-memory 5.6.0
rollback target: emma-workspace-memory 5.6.0
build target: emma-workspace-memory 6.0.0-rc.1
activation state: blocked until public skills and all private checks pass
```

The earlier locally built `6.0.0-rc.1` candidate is historical build evidence only and is not activation-ready. Rebuild the candidate after the public skills exist so it includes:

- Constitution 3.3 and current-session live-evidence bootstrap;
- deployment-specific capability-manifest sentinel and Task Ledger reconciliation;
- owner-only disclosure;
- Autonomous Memory Capture;
- Memory Fusion source precedence;
- confidential psychological/wellbeing and health/supplement contracts;
- active workspace-space routing and lifecycle;
- enriched Context Bootstrap personal-focus sections.

Only public-safe adapter templates, schemas, loaders, tests and build tooling may be committed to this public repository. The real private manifest, private IDs, private artifacts and live installation reports stay outside public source and public release assets.

## Approved roadmap boundary

Public issue `#13` and private `Apex#26` track a possible unique product name. Rebranding is Phase 2 and MUST NOT rename Phase 1 repository paths, skill identities, package names, release files or historical attribution.

Public issues `#14–#16` and private `Apex#23–#25` are binding Phase 1 additions.

## Implementation order

Execute the plans in this exact order:

1. `docs/superpowers/plans/2026-07-15-skill-pack-foundation-build-pipeline.md`
2. `docs/superpowers/plans/2026-07-15-one-time-disclosure-consent-integration.md`
3. `docs/superpowers/plans/2026-07-15-constitution-truncation-hardening.md`
4. `docs/superpowers/plans/2026-07-15-capability-catalog-plugin-orchestration.md`
5. `docs/superpowers/plans/2026-07-15-live-bootstrap-evidence-task-reconciliation.md`
6. `docs/superpowers/plans/2026-07-15-installer-upgrader-skill.md`
7. `docs/superpowers/plans/2026-07-15-autonomous-memory-capture.md`
8. `docs/superpowers/plans/2026-07-17-memory-fusion-and-sensitive-personal-context.md`
9. `docs/superpowers/plans/2026-07-15-context-bootstrap-skill.md`
10. `docs/superpowers/plans/2026-07-17-workspace-spaces-semantics-and-lifecycle.md`
11. `docs/superpowers/plans/2026-07-17-context-bootstrap-salience-and-focus.md`
12. `docs/superpowers/plans/2026-07-15-skill-pack-integration-prerelease-pilot.md`
13. `docs/superpowers/plans/2026-07-15-private-emma-workspace-adapter-v6.md`
14. Final whole-branch review against existing Phase 1 requirements, public issues `#14–#16`, private `Apex#23–#25` and every binding specification above.

### Resume rule for Draft PR #11

Workstream 1 foundation is already reviewed and complete in Draft PR #11. Workstream 2 began before this addendum. When resuming:

1. fetch and merge current `main` into the existing PR branch;
2. resolve conflicts without force-push;
3. verify completed foundation tests still pass;
4. continue the current disclosure workstream;
5. add the new workstreams at positions 8, 10 and 11 above;
6. update `.superpowers/sdd/progress.md` from the old 11-workstream list to this 14-step order;
7. keep PR #11 as Draft until all completion gates pass.

## Cross-cutting invariants

### Current-session source evidence

- Cached Context Bootstrap content is orientation only.
- Every new conversation revalidates live capability and task sources.
- A configured-capability manifest is full only after pagination reaches `has_more=false`, one terminal sentinel is present, observed count matches the deployment-specific expected count, keys are unique and required fields are populated.
- Active task coverage is full only after the canonical task ledger and configured execution backend are exhausted and reconciled.
- A cached `FULL` can never upgrade a live `PARTIAL` or `BLOCKED` result.
- Public fixtures and schemas MUST use deployment-neutral counts; private counts are configuration, not public constants.

### Constitution

- Complete root readback is mandatory.
- Truncated or uncertain root means `BLOCKED_CONSTITUTION_TRUNCATED`.
- Child modules do not clear that block.
- Enforce approved readability budgets and repair path.

### Privacy and disclosure

- All direct and derived Workspace information is owner-only by default.
- Every external disclosure requires fresh, exact, single-use approval for recipients/destination, channel/action, purpose, scope, final content/version, attachments, links, visibility and permissions.
- Prior or standing consent is invalid.
- Confidential psychological, wellbeing, health and relationship records never receive weaker disclosure rules.

### Autonomous Memory

- Bounded post-turn capture may update ordinary canonical records in approved schemas.
- Do not store hidden reasoning or authentication secrets.
- Structural changes, permanent deletion, external disclosure, publication, deployment, trading and other consequential actions retain approval gates.
- Failed writes report `MEMORY_CAPTURE_DEGRADED`; no background retry claim.
- Every person/relationship statement is evaluated; material durable information is saved or updated, while incidental and duplicate content is not persisted.

### Memory Fusion and sensitive personal context

- Current conversation, native AI memory/personalization, live connectors and canonical Workspace records are complementary sources.
- Apply explicit source precedence; native memory cannot silently override verified canonical Workspace data.
- Preserve corrections, contradictions, supersessions, source dates and counterevidence.
- A transient mood is not a stable trait; one behavior is not a repeated pattern; hypothesis is not fact.
- Health, medication and supplement records are time-aware; stopped and historical items do not appear as current.
- Explicit `do not save` and owner corrections are mandatory.

### Active workspace spaces

- Do not create ornamental databases or pages.
- Every enabled Journal, Observations, Decisions, Projects, Working Notes and Archive space has purpose, include/exclude rules, read/write triggers, routing, lifecycle, views/templates and a real workflow.
- Journal never stores hidden chain-of-thought or transcript dumps.
- Working Notes are temporary and review/expiry aware.
- Archive preserves provenance and never authorizes silent deletion.
- Ambiguous routing returns `REVIEW_REQUIRED` rather than duplicate records.

### Context Bootstrap personal focus

- Required model: Current Focus, People in Focus, Active Tasks, Projects/Commitments, Recent and Salient Events, Wellbeing/Health Snapshot, Decisions/Reviews, Risks/Conflicts, Capability Health and Recently Changed Memory.
- Every non-task item has a source and visible salience reason.
- People in Focus and salient events are bounded current operational sets, not permanent rankings.
- Sensitive summaries contain minimum necessary detail and canonical links.
- All active tasks remain represented even under personal-context overload.
- Cached personal-context sections do not certify live sources.

### Capabilities

- Notion is the only mandatory external connector.
- Every other capability is optional and owner-controlled.
- Respect activation policy, current surface, provider choice, risk tier, authorization and live health.
- Metadata-first progressive loading; full instructions only for the minimal relevant verified set.
- Explicit-only artifact routers remain explicit-only.
- Disabled/high-risk specialist capabilities remain disabled unless correctly enabled.

### Tasks

- No silent task omission.
- Every active task appears at least as a compact index row.
- Use pagination and `TASK_INDEX_MODE` for large sets.
- Detect unledgered tasks, missing backend records, status/owner conflicts, missing or multiple priorities, stale ledger records and superseded-but-open records.
- Recording a task never means executing it.

### Public/private boundary

Public packages, tests, docs, logs and examples contain no private:

- Notion page/database/view IDs;
- account identities;
- Drive folders or file IDs;
- repositories or task content;
- Gmail/contact/relationship data;
- psychological, wellbeing or health observations;
- private manifest or adapter configuration;
- credentials or secrets.

Use fictional fixtures and deployment-neutral sentinel counts.

## Required final deliverables

```text
Personal-AI-Workspace-Creator-v1.6.0.md
Personal-AI-Workspace-Installer-Upgrader-0.1.0-beta.1.zip
Personal-AI-Workspace-Context-Bootstrap-0.1.0-beta.1.zip
Personal-AI-Workspace-Skill-Pack-0.1.0-beta.1.zip
SHA256SUMS.txt
INSTALLATION.md
docs/CAPABILITIES.md
docs/MEMORY.md
docs/CONTEXT-BOOTSTRAP.md
docs/WORKSPACE-SPACES.md
ChatGPT installation guide
Codex user-global installers and verification
AGENTS.md template/fragment
compatibility manifest
versioned migration manifests
pilot and release notes
private adapter build and rollback evidence outside public release assets
```

## Completion gate

Codex may declare the Draft PR implementation complete only after:

- all task-scoped tests pass;
- final whole-branch tests pass;
- deterministic builds reproduce hashes;
- package integrity and checksums pass;
- public/private scanner passes;
- no cached self-certification remains;
- no active task can be silently omitted;
- source precedence, sensitive-context typing and lifecycle tests pass;
- every enabled workspace space is owner-discoverable and non-ornamental;
- Context Bootstrap personal-focus limits, salience reasons and task priority pass;
- existing Phase 1 requirements plus public issues `#14–#16` and private `Apex#23–#25` are traceable to code/tests/docs;
- public issue `#13` / `Apex#26` remains explicitly deferred and no rebrand occurs;
- no release publication workflow has been dispatched.

The final response must include the Draft PR URL, test summary, known limitations, artifact paths and clear statements that publication and private live activation remain unapproved.