# Personal AI Workspace Phase 1 — Final Release Scope Audit

**Status:** Final pre-development scope review  
**Date:** 2026-07-15  
**Target framework:** Personal AI Workspace `1.6.0`  
**Target public Skill Pack:** `0.1.0-beta.1` prerelease  
**Target private adapter:** `emma-workspace-memory 6.0.0-rc.1`  
**Publication:** Not authorized by this document

## 1. Audit conclusion

The Phase 1 scope is complete enough for Codex implementation after the plan documents in this branch are merged to `main` and the misleading incomplete implementation PR #4 is closed as superseded.

No material approved requirement is missing from the design/plan set after adding:

- Capability Catalog and progressive skill/plugin loading;
- capability packs, provider choice, surface awareness, activation policies, risk tiers, and health probes;
- Autonomous Memory Capture;
- Constitution truncation hardening;
- owner-only one-time disclosure controls;
- public ChatGPT/Codex distribution and private Emma adapter.

Several items are intentionally deferred and are listed explicitly in Section 12. They are not silent omissions.

## 2. Binding version model

The implementation must track these versions independently:

```text
Framework / Markdown creator: 1.6.0
Public Skill Pack: 0.1.0-beta.1
Installer & Upgrader skill: 0.1.0-beta.1
Context Bootstrap skill: 0.1.0-beta.1
Private Emma adapter: 6.0.0-rc.1
Private rollback skill: 5.6.0
Installed Workspace schema/Constitution: deployment-specific
Capability Catalog contract: 1.0.0
Autonomous Memory Capture contract: 1.0.0
```

A newer unknown Workspace version is read-only and never automatically downgraded.

## 3. Workstream coverage matrix

| Requirement | Tracking | Design / Plan owner | Required deliverable |
|---|---|---|---|
| Public Installation / Getting Started | Apex #6 | Integration and pilot plan | `INSTALLATION.md`, GitHub Pages guide, ChatGPT and Codex steps |
| Version-aware install, repair, migration, rollback | Apex #7 | Installer & Upgrader plan | state classification, sequential migrations, idempotency, readback |
| Context Bootstrap and active task completeness | Apex #8 | Context Bootstrap plan | all active A/B/C/recurring tasks, projects, commitments, reviews, risks, coverage |
| Remove Google Tasks | Apex #9 | Installer, task contract, migration | no active Google Tasks branch; GitHub Issues + Task Outbox |
| Artifact archive and Drive readback | Apex #10 | Foundation/integration/installer | enabled-Drive archive gate, checksum/readback, honest incomplete state |
| Enable/disable features and integrations | Apex #11 | Capability Catalog plan | registry state, dependencies, provider, surfaces, activation, health |
| Public ChatGPT + Codex Skill Pack | Apex #12 | Original four Phase 1 plans | two standalone skills, combined pack, CI, packages, checksums, docs |
| Owner-only one-time external disclosure | Apex #13 | disclosure addendum and plan | exact recipient/channel/scope/version approval; second-use rejection |
| Complete Constitution read and length budgets | Apex #14 | truncation addendum and plan | 3500/5000/7000 budgets, sentinel/readback, fail-closed, repair |
| Capability Catalog and plugin orchestration | Apex #15 | capability design and plan | public catalog, packs, progressive loading, provider/surface/risk contracts |
| Autonomous Memory Capture | Apex #16 | memory design and plan | bounded post-turn capture, canonical update, provenance, failure states |
| Private Emma adapter | Apex #5 plus adapter plan | private-adapter plan | thin private profile over public skills, rollback and compatibility |

## 4. Mandatory product architecture

### 4.1 Core

Notion is the only mandatory external connector. Core Workspace includes:

```text
Notion identity
Workspace Constitution
Start Here
module 00
Feature & Integration Registry
Capability Catalog
Context Bootstrap
Knowledge
Relations
Autonomous Memory Capture
```

A deployment without Notion is not Personal AI Workspace.

### 4.2 Optional integrations

Every other connector, skill, provider, or plugin is optional and represented in the Capability Catalog with:

```text
state
activation policy
supported surfaces
risk tier
selected provider
required capabilities
read/write scope
output destination
persistence policy
health probe
```

No upgrade may silently enable a disabled capability or switch provider.

### 4.3 Progressive loading

Startup loads a compact manifest of all configured capabilities. Full instructions load only for the minimal enabled, available, relevant set.

This resolves the earlier request to make AI aware of all configured skills and plugins without overflowing Context Bootstrap or violating native explicit-only skill contracts.

## 5. Cross-cutting safety requirements

### 5.1 Owner-only disclosure

All direct and derived Workspace information is owner-only by default. One external disclosure requires one fresh, exact, single-use approval for:

- recipients/destination;
- channel/action;
- purpose;
- information scope and exclusions;
- final content/artifact version;
- attachments, links, visibility, and permissions.

Prior, general, relational, inherited, recurring, or cross-conversation consent is invalid.

### 5.2 Structure governance

Ordinary data writes in approved schemas may be autonomous. Schema, database, property, module, provider, activation, retention, integration, automation, or required-workflow changes require exact-scope owner approval.

### 5.3 Constitution completeness

A truncated root is a hard block:

```text
BLOCKED_CONSTITUTION_TRUNCATED
```

Child modules do not clear the block. Target budgets:

```text
root Constitution operational body: ~3500 characters
Start Here: ~5000 characters
detailed module: ~7000 characters
```

### 5.4 Secrets

Never store or publish passwords, tokens, API keys, one-time codes, reset links, private keys, cookies, or other authentication secrets.

### 5.5 No background claims

A skill or Notion record does not create background execution. Session-triggered work is described as session-triggered. Scheduled Tasks, hooks, Jobs, or external agents require real configured mechanisms and their own verification.

## 6. Resolved scope conflicts

### 6.1 Drive mandatory versus optional

**Resolution:**

- Public product: Drive is optional because only Notion is mandatory.
- If Drive is `Disabled by User`, artifact completion may use another explicitly selected local/native handoff and records `ARCHIVE_DISABLED_BY_USER`; this is not an upload failure.
- If Drive is enabled and selected as the artifact archive, completion requires exact-file upload and readback; failure is `ARTIFACT_ARCHIVE_INCOMPLETE`.
- Private Emma profile may configure Drive as required. Its current connector limitations remain a private degraded state.

### 6.2 Read-only Context Bootstrap versus memory writes

**Resolution:**

- Startup briefing generation is read-only by default.
- Autonomous Memory Capture is a separate bounded post-turn phase.
- A write-heavy startup is prohibited.
- Optional persistent bootstrap caching remains separately governed.

### 6.3 Load all skills versus explicit-only routers

**Resolution:**

- Load metadata/manifest for all configured capabilities.
- Load full instructions only when selected by activation policy.
- `@document`, `@pdf`, `@spreadsheet`, and `@presentation` remain explicit-only where required by their routers.

### 6.4 Autonomously save everything versus data minimization

**Resolution:**

- Capture all *material durable* information the assistant judges useful under the approved contract.
- Do not archive the entire conversation, small talk, duplicates, transient details, hidden reasoning, or secrets.
- Explicit no-save instructions control.
- Sensitive context is retained when materially relevant with full provenance and classification.

### 6.5 Autonomous task creation versus external disclosure

**Resolution:**

- Internal Task Outbox staging may be autonomous under configured task rules.
- External/public GitHub Issue creation requires a configured backend policy that confirms the destination is acceptable; otherwise stage internally or require approval.
- Task creation never means task execution.

### 6.6 Installed versus callable

**Resolution:**

Catalog metadata represents configured intent. The current runtime must still verify actual callability, authorization, account identity, and health before using a provider.

## 7. Capability integration coverage

### Deeply integrated in Phase 1

```text
LinkedIn
LinkedIn Ads
Sales
Data Analytics
Documents
PDF
Spreadsheets
Presentations / Google Slides
Creative Production
Adobe
Meetup
```

### Cataloged optional

```text
Spotify / Apple Music provider choice
Hugging Face
OpenAI Developers
Build Web Apps
Product Design
Render
Booking.com
Public Equity Investing
```

### Installed but default-disabled specialist capabilities

```text
Investment Banking
Life Science Research
NGS Analysis
Revolut X Read
Revolut X Alerts
Revolut X Trading
```

The public catalog may include other providers later without changing the core data model.

## 8. Public deliverables

The release candidate must contain:

```text
Personal-AI-Workspace-Creator-v1.6.0.md
Personal-AI-Workspace-Installer-Upgrader-0.1.0-beta.1.zip
Personal-AI-Workspace-Context-Bootstrap-0.1.0-beta.1.zip
Personal-AI-Workspace-Skill-Pack-0.1.0-beta.1.zip
SHA256SUMS.txt
INSTALLATION.md
docs/CAPABILITIES.md
docs/MEMORY.md
ChatGPT installation guide
Codex user-global installation scripts and verification
AGENTS.md template/fragment
compatibility manifest
migration manifests 1.0 -> 1.6.0
release notes and pilot instructions
```

The Markdown creator `1.5.1` remains the fallback until `1.6.0` passes pilot acceptance.

## 9. Private deliverables

Outside public source and release assets:

```text
emma-workspace-memory 6.0.0-rc.1
private manifest
private source map
private account identities
private feature/provider states
private Drive and task-backend configuration
migration from 5.6.0
rollback to 5.6.0
private compatibility and privacy tests
```

The private adapter composes the public contracts and must not fork or weaken them.

## 10. Required verification matrix

### Installation and migration

- NOT_INSTALLED, PARTIAL, INSTALLED_SUPPORTED, INSTALLED_UNKNOWN, DAMAGED
- upgrade chain and rollback
- idempotent rerun
- duplicate prevention
- unknown newer version read-only
- old overlong Constitution repair
- old explicit-save-only memory migration
- capability provider/state preservation

### Context Bootstrap

- complete root required
- Feature Registry version equality
- all active tasks represented
- task index mode
- compact capability manifest
- minimal relevant full-skill loading
- source coverage, staleness, truncation, and conflict reporting

### Autonomous Memory

- durable fact captured
- transient content skipped
- canonical update rather than duplicate
- correction and contradiction history
- reported claim/hypothesis status preserved
- secret excluded
- explicit no-save honored
- structural/external actions remain gated
- bounded capture
- degraded failure without background promise

### Plugins

- explicit-only artifact routers
- Data Analytics surface gate
- LinkedIn/Ads read-only assumptions
- disabled specialist routing
- provider switching
- surface mismatch
- high-risk confirmation
- NGS cloud-upload boundary
- Revolut no-autonomous-trade boundary

### Security and packaging

- public/private scanner
- no private IDs or contacts
- deterministic builds
- ZIP integrity
- checksums
- license/NOTICE/attribution
- one-time disclosure second-use rejection
- no automatic release publication

## 11. Codex execution order

Codex must execute from a clean branch created from the latest `main`, not from PR #4.

Use this order:

1. `2026-07-15-skill-pack-foundation-build-pipeline.md`
2. `2026-07-15-one-time-disclosure-consent-integration.md`
3. `2026-07-15-constitution-truncation-hardening.md`
4. `2026-07-15-capability-catalog-plugin-orchestration.md`
5. `2026-07-15-installer-upgrader-skill.md`
6. `2026-07-15-autonomous-memory-capture.md`
7. `2026-07-15-context-bootstrap-skill.md`
8. `2026-07-15-skill-pack-integration-prerelease-pilot.md`
9. `2026-07-15-private-emma-workspace-adapter-v6.md`
10. final whole-branch review against this audit

Use `superpowers:subagent-driven-development`, a fresh implementer per task, task-scoped review, durable ledger, and final whole-branch review.

## 12. Explicitly deferred items

### Heartbeat / autonomous scheduling

Not in the Phase 1 core runtime. Phase 1 may expose extension points and documentation for:

- ChatGPT Scheduled Tasks;
- Codex `SessionStart` hook;
- external schedulers;
- Hugging Face Scheduled Jobs;
- future agent or MCP orchestration.

No heartbeat is claimed without a real trigger and connector access. Full heartbeat implementation is Phase 2.

### Discord community connector

Deferred. No verified connector is currently part of the product contract. GitHub Issues/PRs remain the operational community surfaces.

### Automatic public prerelease publication

Deferred until a separate explicit approval naming the exact version. CI may build candidate artifacts but must not publish automatically.

### Private adapter activation

Blocked until both public skills are built, installed, and compatibility-tested. Private `5.6.0` remains rollback.

### Google Drive binary upload reliability

The generic contract and tests are in scope. The current private connector limitation remains a tracked degraded condition and cannot be hidden.

### GitHub Project assignment

Still unsupported by the current connector. Issues and Task Outbox remain authoritative.

## 13. Repository cleanup before development

- Merge all approved design/plan PRs to `main`.
- Close PR #4 as superseded/incomplete; it contains only `pyproject.toml` despite claiming full implementation.
- Create a new implementation branch from the resulting latest `main`.
- Do not reuse `feat/skill-pack-phase-1` as implementation base.
- Do not publish a release or migrate the live private adapter during public development.

## 14. Final readiness gate

Codex development may begin when:

- all approved plan documents are on `main`;
- PR #4 is closed as superseded;
- the implementation prompt references this audit and all ordered plans;
- a clean implementation branch/worktree is created;
- baseline tests are recorded;
- the durable subagent progress ledger is initialized;
- the prerelease and private-migration prohibitions are repeated in the prompt.

**Audit verdict:** `READY_FOR_CODEX_AFTER_PLAN_MERGE_AND_PR4_CLEANUP`.
