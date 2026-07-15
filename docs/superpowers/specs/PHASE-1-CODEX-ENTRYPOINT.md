# Personal AI Workspace Phase 1 — Canonical Codex Entrypoint

**Status:** Binding implementation entrypoint  
**Date:** 2026-07-15  
**Base:** latest `main` only  
**Execution:** `superpowers:subagent-driven-development`  
**Publication:** not authorized

## Purpose

This file is the single starting point for Codex implementation. It resolves the order of the original Phase 1 plans and all subsequently approved binding addenda.

Do not implement from the obsolete `feat/skill-pack-phase-1` branch or closed PR #4.

## Preflight

1. Create a clean worktree/branch from the latest `main`.
2. Read the architecture and scope documents below.
3. Run the preflight conflict scan required by Subagent-Driven Development.
4. Create and maintain `.superpowers/sdd/progress.md`.
5. Use a fresh implementer for each task, followed by specification review and code-quality review.
6. Fix all Critical and Important findings before advancing.
7. Never publish a prerelease or activate the live private adapter without a later explicit approval naming the exact version.

## Binding specifications

Read all of these before implementation:

1. `docs/superpowers/specs/2026-07-15-personal-ai-workspace-skill-pack-phase-1-design.md`
2. `docs/superpowers/specs/2026-07-15-phase-1-release-scope-audit.md`
3. `docs/superpowers/specs/2026-07-15-one-time-disclosure-consent-addendum.md`
4. `docs/superpowers/specs/2026-07-15-constitution-truncation-safety-addendum.md`
5. `docs/superpowers/specs/2026-07-15-capability-catalog-plugin-orchestration-design.md`
6. `docs/superpowers/specs/2026-07-15-autonomous-memory-capture-design.md`
7. `docs/superpowers/specs/2026-07-15-live-bootstrap-evidence-task-reconciliation-addendum.md`

If a filename differs slightly in the repository, locate the matching approved document by title and record the resolved path in the progress ledger before implementation.

## Document precedence

When two approved documents differ, apply this precedence from highest to lowest:

1. this canonical entrypoint;
2. the newest binding addendum that addresses the disputed behavior;
3. the final Phase 1 release scope audit;
4. the focused implementation plan for the affected workstream;
5. the original Phase 1 architecture specification;
6. older issue text, historical PR descriptions, cached reports, or obsolete implementation branches.

Do not silently choose between conflicts. Record the conflict and the applied precedence in `.superpowers/sdd/progress.md`.

## Version targets

```text
Framework / Markdown creator: 1.6.0
Public Skill Pack: 0.1.0-beta.1
Installer & Upgrader: 0.1.0-beta.1
Context Bootstrap: 0.1.0-beta.1
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

The earlier locally built `6.0.0-rc.1` candidate is historical build evidence only and is not activation-ready. Rebuild the candidate after the public skills exist so it includes Constitution 3.3, Context Bootstrap 1.3, the deployment-specific capability-manifest sentinel, current-session evidence leases, Bootstrap Task Ledger reconciliation, owner-only disclosure, and Autonomous Memory Capture.

Only public-safe adapter templates, schemas, loaders, tests, and build tooling may be committed to this public repository. The real private manifest, private IDs, private artifacts, and live installation reports stay outside public source and public release assets.

## Implementation order

Execute the plans in this exact order:

1. `docs/superpowers/plans/2026-07-15-skill-pack-foundation-build-pipeline.md`
2. `docs/superpowers/plans/2026-07-15-one-time-disclosure-consent-integration.md`
3. `docs/superpowers/plans/2026-07-15-constitution-truncation-hardening.md`
4. `docs/superpowers/plans/2026-07-15-capability-catalog-plugin-orchestration.md`
5. `docs/superpowers/plans/2026-07-15-live-bootstrap-evidence-task-reconciliation.md`
6. `docs/superpowers/plans/2026-07-15-installer-upgrader-skill.md`
7. `docs/superpowers/plans/2026-07-15-autonomous-memory-capture.md`
8. `docs/superpowers/plans/2026-07-15-context-bootstrap-skill.md`
9. `docs/superpowers/plans/2026-07-15-skill-pack-integration-prerelease-pilot.md`
10. `docs/superpowers/plans/2026-07-15-private-emma-workspace-adapter-v6.md`
11. Final whole-branch review against Apex #6–#18 and every binding specification above.

## Cross-cutting invariants

### Current-session source evidence

- Cached Context Bootstrap content is orientation only.
- Every new conversation revalidates live capability and task sources.
- A configured-capability manifest is full only after pagination reaches `has_more=false`, one terminal sentinel is present, observed count matches the deployment-specific expected count, keys are unique, and required fields are populated.
- Active task coverage is full only after the canonical task ledger and configured execution backend are exhausted and reconciled.
- A cached `FULL` can never upgrade a live `PARTIAL` or `BLOCKED` result.
- Public fixtures and schemas MUST use deployment-neutral counts; the private count `44` is configuration, not a public constant.

### Constitution

- Complete root readback is mandatory.
- Truncated or uncertain root means `BLOCKED_CONSTITUTION_TRUNCATED`.
- Child modules do not clear that block.
- Enforce the approved readability budgets and repair path.

### Privacy and disclosure

- All direct and derived Workspace information is owner-only by default.
- Every external disclosure requires fresh, exact, single-use approval for recipients/destination, channel/action, purpose, scope, final content/version, attachments, links, visibility, and permissions.
- Prior or standing consent is invalid.

### Autonomous Memory

- Bounded post-turn capture may update ordinary canonical records in approved schemas.
- Do not store hidden reasoning or authentication secrets.
- Structural changes, permanent deletion, external disclosure, publication, deployment, trading, and other consequential actions retain their approval gates.
- Failed writes report `MEMORY_CAPTURE_DEGRADED`; no background retry claim.

### Capabilities

- Notion is the only mandatory external connector.
- Every other capability is optional and owner-controlled.
- Respect activation policy, current surface, provider choice, risk tier, authorization, and live health.
- Metadata-first progressive loading; full instructions only for the minimal relevant verified set.
- Explicit-only artifact routers remain explicit-only.
- Disabled/high-risk specialist capabilities remain disabled unless correctly enabled.

### Tasks

- No silent task omission.
- Every active task must appear at least as a compact index row.
- Use pagination and `TASK_INDEX_MODE` for large sets.
- Detect unledgered tasks, missing backend records, status/owner conflicts, missing or multiple priorities, stale ledger records, and superseded-but-open records.
- Recording a task never means executing it.

### Public/private boundary

Public packages, tests, docs, logs, and examples must contain no private:

- Notion page/database/view IDs;
- account identities;
- Drive folders or file IDs;
- repositories or task content;
- Gmail/contact/relationship data;
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
ChatGPT installation guide
Codex user-global installers and verification
AGENTS.md template/fragment
compatibility manifest
versioned migration manifests
pilot and release notes
private adapter build and rollback evidence outside public release assets
```

## Completion gate

Codex may open a draft PR only after:

- all task-scoped tests pass;
- final whole-branch tests pass;
- deterministic builds reproduce hashes;
- package integrity and checksums pass;
- public/private scanner passes;
- no cached self-certification remains;
- no active task can be silently omitted;
- all Apex #6–#18 requirements are traceable to code/tests/docs;
- no release publication workflow has been dispatched.

The final response must include the draft PR URL, test summary, known limitations, artifact paths, and a clear statement that publication and private live activation remain unapproved.
