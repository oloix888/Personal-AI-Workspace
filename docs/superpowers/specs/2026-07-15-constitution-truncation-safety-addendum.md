# Constitution Truncation Safety Addendum

**Status:** Approved binding scope amendment  
**Date:** 2026-07-15  
**Applies to:** public creator, Installer & Upgrader, Context Bootstrap, shared Skill Pack contracts, ChatGPT/Codex installation guidance, validators, migrations, tests, release gates, and private `emma-workspace-memory v6.0.0` adapter.

## Problem

A canonical Workspace Constitution that is truncated in a connector read is not loaded. Reading selected child modules separately does not establish that every binding rule from the canonical index was seen.

## Binding rule

The assistant must never state that the available scope is sufficient after the root Constitution was truncated, ended unexpectedly, omitted an expected section, or has uncertain completeness.

Such a read produces:

```text
BLOCKED_CONSTITUTION_TRUNCATED
```

Dependent work stops until the root is shortened or split and a complete readback succeeds.

## Readability budgets

- Root Constitution operational body: approximately 3,500 characters maximum before technical child-page references.
- `Start Here`: approximately 5,000 characters maximum.
- Detailed module: approximately 7,000 characters maximum.

The root contains only status, mandatory startup order, hard completeness condition, a compact set of non-negotiable boundaries, navigation links, and a short pointer to history.

Full routing belongs in module `00`; integration status belongs in Feature & Integration Registry and Context Bootstrap; complete version history belongs in module `11`.

## Required completeness evidence

A complete read must include an expected ending sentinel or equivalent final section defined by the installation manifest. Absence of that marker fails closed.

## Installer & Upgrader behavior

An over-budget, truncated, or sentinel-missing root is classified as `DAMAGED` or a high-severity repair condition. Repair must:

1. preserve the canonical URL and child pages;
2. move duplicated detail to the correct modules;
3. shorten the root and `Start Here` to their budgets;
4. update module `00`, module `11`, version and changelog;
5. perform a complete connector readback;
6. remain idempotent and create no duplicate pages.

## Context Bootstrap behavior

Context Bootstrap must not produce an owner briefing from an unverifiable Constitution contract. It reports the block and the exact missing completeness evidence.

## Test contract

Required tests include:

- overlong root fixture fails validation;
- truncated root response blocks the workflow;
- selected child modules cannot override the block;
- missing ending sentinel fails validation;
- migration shortens the root without losing canonical URLs or child pages;
- root, Start Here and module budgets are enforced;
- repeated repair is idempotent;
- complete readback clears the block.

## Live reference implementation

The private Emma Workspace was repaired to Constitution `3.1`, module `00` `2.1`, module `11` `2.1`, and a shortened `Start Here`. Complete connector readbacks succeeded after repair.