# Constitution Truncation Hardening Implementation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` or `superpowers:executing-plans`. Implement task-by-task with RED → GREEN tests, focused commits, specification review and code-quality review.

**Goal:** Make partial Constitution reads a hard, detectable failure across the creator, public Skill Pack, Codex distribution and private adapter, while keeping every canonical document within explicit connector-readable budgets.

## Task 1 — Shared contract and schemas

Create a vendored shared contract defining:

```text
BLOCKED_CONSTITUTION_TRUNCATED
ROOT_BUDGET = 3500
START_HERE_BUDGET = 5000
MODULE_BUDGET = 7000
```

Add a completeness-report schema with fields:

- document role;
- expected URL/title/version;
- observed character count;
- budget;
- expected ending sentinel;
- sentinel observed;
- truncated flag;
- complete flag;
- failure reason.

Tests must fail before implementation and cover missing sentinel, explicit truncation, unexpected ending and uncertain completeness.

## Task 2 — Public creator

Update the Markdown creator so every installation:

1. creates a deliberately short root Constitution;
2. places routing in module `00`;
3. places integration state in Feature Registry / Context Bootstrap;
4. places full changelog in module `11`;
5. writes an ending sentinel or equivalent final marker;
6. reads the root back after creation;
7. blocks completion if the marker is absent or the response is truncated.

Add upgrade instructions for older overlong installations.

## Task 3 — Installer & Upgrader

Add detection and repair for:

- over-budget root;
- over-budget Start Here;
- over-budget detailed modules;
- explicit connector truncation;
- missing ending sentinel;
- partially migrated roots.

Classify the installation as `DAMAGED` or high-severity repair required. Preview the exact migration and obtain structural approval before writing. Preserve canonical URLs and child pages. Rerunning repair must create no duplicates.

## Task 4 — Context Bootstrap

Before any operational briefing:

1. verify owner identity;
2. fully read the root Constitution;
3. require the expected ending sentinel;
4. stop with `BLOCKED_CONSTITUTION_TRUNCATED` if completeness is uncertain;
5. explicitly state that child modules do not override the block.

Do not produce a normal briefing while blocked.

## Task 5 — Validators and CI

Add validators for source templates and generated artifacts:

- root operational-body budget;
- Start Here budget;
- module budget;
- ending sentinel;
- prohibited phrase pattern that treats truncated scope as sufficient;
- package references to the truncation-safety contract.

CI and release gates must reject noncompliant creator and skill packages.

## Task 6 — ChatGPT and Codex documentation

Update installation and troubleshooting guides with:

- exact failure code;
- how to verify complete fetch;
- how to repair an overlong root;
- prohibition on continuing from selected modules alone;
- private adapter requirement to fail closed.

## Task 7 — Private adapter v6

The private `emma-workspace-memory v6.0.0` adapter must:

- expect Constitution `3.1+` or a compatible truncation-safe contract;
- verify root, Start Here and module budgets;
- require the ending sentinel;
- block on incompatible or missing completeness contract;
- reference the live Emma Workspace URLs only in the private manifest;
- retain rollback to private skill `5.6.0`.

## Task 8 — Test matrix

Required fixtures and scenarios:

1. valid short root;
2. overlong root;
3. connector response with explicit `truncated` marker;
4. response without final sentinel;
5. complete root plus truncated child module;
6. truncated root plus complete child modules;
7. migration preserving canonical URLs;
8. repeated migration producing no duplicates;
9. old installation upgraded to truncation-safe layout;
10. public packages scanned for private identifiers.

## Acceptance criteria

- No code path treats a truncated root as sufficient.
- Root, Start Here and module budgets are mechanically enforced.
- The installer repairs an old overlong installation safely and idempotently.
- Context Bootstrap fails closed before briefing.
- Creator installs the safe layout by default.
- Public ChatGPT/Codex packages and private adapter share the same contract version.
- All tests, package validators, privacy scanners and release gates pass.
- Prerelease publication remains separately gated by explicit owner approval.