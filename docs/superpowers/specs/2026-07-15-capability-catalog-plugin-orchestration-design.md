# Capability Catalog and Plugin Orchestration Design

**Status:** Approved binding scope amendment  
**Date:** 2026-07-15  
**Owners:** Michał Poliński and Emma ✨  
**Tracks:** `oloix888/Apex#15`, Phase 1 Skill Pack, public creator, private Emma adapter

## 1. Purpose

Personal AI Workspace must know which skills, plugins, connectors, artifact surfaces, and action systems are configured without loading every full instruction set into every conversation.

The system therefore introduces a provider-neutral **Capability Catalog**, stored operationally in the Feature & Integration Registry and distributed publicly as a machine-readable manifest. At conversation start, the assistant loads a compact capability manifest. It loads full skill or plugin instructions only when the capability is:

1. configured and enabled;
2. available on the current product surface;
3. relevant to the active request;
4. permitted by its activation policy;
5. healthy enough for the required read or write operation.

This is progressive disclosure for capabilities: **manifest first, task-relevant instructions second**.

## 2. Goals

- Make Notion the only mandatory external connector.
- Let users enable, disable, pause, configure, or replace every non-Notion capability.
- Support ChatGPT Web, Work Mode, ChatGPT Desktop, Codex CLI, Codex Desktop, and API surfaces without pretending that every capability exists everywhere.
- Prevent context overflow caused by loading all installed skills and plugins.
- Preserve each plugin's own invocation contract, including explicit-only routers and confirmation gates.
- Add goal-based capability packs to the installer without hiding the underlying choices.
- Keep provider selection explicit and stable across upgrades.
- Record capability health, source coverage, output destination, persistence policy, and risk.
- Allow a private Workspace to have a different enabled set from the public default.

## 3. Non-goals

Phase 1 does not:

- reimplement the internals of installed third-party plugins;
- guarantee that an installed plugin is authorized or callable;
- load every full `SKILL.md` at startup;
- grant background execution;
- enable Discord or any other provider without an available and verified route;
- create a universal standing authorization for external actions;
- enable financial trading, cloud upload of sensitive research data, deployment, publication, or communication by default;
- silently switch from one provider to another.

## 4. Core model

### 4.1 Capability state

The existing operational states remain:

```text
Enabled
Disabled by User
Unavailable
Pending Setup
Paused
Degraded
```

State answers whether the configured capability may currently participate in routing. It does not describe how it may be invoked.

### 4.2 Activation policy

```text
CORE_BOOTSTRAP
ON_DEMAND_IMPLICIT
EXPLICIT_ONLY
EXPLICIT_WITH_CONFIRMATION
DISABLED
```

- `CORE_BOOTSTRAP`: load the compact startup contract every significant conversation. Only Notion identity, Constitution, module 00, Feature Registry, Context Bootstrap, Capability Catalog, and Autonomous Memory Capture belong here.
- `ON_DEMAND_IMPLICIT`: the assistant may select the capability automatically when the request clearly matches.
- `EXPLICIT_ONLY`: the user must explicitly select, at-mention, or request the capability before its full instructions are loaded.
- `EXPLICIT_WITH_CONFIRMATION`: discovery and planning may occur when relevant, but every consequential action requires its own domain-specific confirmation.
- `DISABLED`: do not read, route, or act through the capability.

### 4.3 Capability kind

```text
Core System
Data Source
Domain Workflow
Artifact Output
Action System
Developer System
Creative System
```

The kind determines expected behavior. A Data Source may expose read-only evidence. An Artifact Output creates a file. An Action System changes an external system. A Domain Workflow orchestrates evidence and artifacts but may depend on other capabilities.

### 4.4 Surface availability

```text
ChatGPT Web
Work Mode
ChatGPT Desktop
Codex CLI
Codex Desktop
API
```

A capability may be installed but absent on the active surface. Runtime availability must be verified from positive product or tool signals; it must not be inferred from prior sessions or catalog metadata alone.

### 4.5 Risk tier

```text
Low
Moderate
High
Critical
```

Risk influences routing, required confirmation, source verification, and audit depth. It never overrides a plugin's stricter native rules.

### 4.6 Required fields

Every public catalog entry and private Feature Registry record must carry:

```text
key
display_name
kind
state
activation_policy
surface_availability
risk_tier
selected_provider
skill_or_plugin_reference
required_capabilities
account_required
dependencies
read_scope
write_scope
external_disclosure_behavior
output_destination
persistence_policy
health_probe
missed_sync_behavior
recommended_packs
version
```

## 5. Startup resolution algorithm

1. Verify the Notion account and load the complete truncation-safe Constitution root.
2. Load Start Here, module 00, Feature Registry, Capability Catalog, and Context Bootstrap.
3. Build a compact manifest for every configured capability containing only:
   - key and display name;
   - state;
   - activation policy;
   - current surface support;
   - risk tier;
   - selected provider;
   - health summary;
   - skill/plugin reference location.
4. Classify the user's current request into one or more capability intents.
5. Remove candidates that are disabled, paused, unavailable, unsupported on the current surface, or irrelevant.
6. Apply invocation gates:
   - implicit capabilities may be selected;
   - explicit-only capabilities require explicit selection;
   - action capabilities require their confirmation contract before execution.
7. Load the full instructions only for the minimal useful selected set.
8. Run the smallest safe health probe needed for this task; do not probe every provider on every turn.
9. Preserve source provenance and route durable outcomes through Autonomous Memory Capture.
10. Report unavailable or degraded material capabilities when the gap affects the result.

## 6. Capability packs

The installer asks about user goals, then recommends packs. Packs are templates, not hidden forced bundles.

### Core Workspace — mandatory

- Notion connector
- Workspace Constitution
- Feature & Integration Registry
- Capability Catalog
- Context Bootstrap
- Knowledge
- Relations
- Autonomous Memory Capture

### Productivity

- Gmail
- Google Calendar
- Google Contacts
- Google Drive
- GitHub Issues
- Documents
- PDF
- Spreadsheets
- Presentations / Google Slides

### Business Growth

- LinkedIn
- LinkedIn Ads
- Sales
- Data Analytics
- Creative Production
- Adobe
- Product Design
- artifact outputs

### Social & Networking

- LinkedIn
- Meetup
- Calendar
- Contacts
- Relations

### Developer & AI

- GitHub
- Hugging Face
- OpenAI Developers
- Build Web Apps
- Product Design
- Render
- Data Analytics

### Finance & Markets

- Public Equity Investing
- Revolut X Read
- Revolut X Alerts
- Revolut X Trading as a separate Critical capability

### Deal & Finance Professional

- Investment Banking
- Data Analytics
- Documents
- Spreadsheets
- PDF
- Presentations

### Life Sciences

- Life Science Research
- NGS Analysis
- Hugging Face
- Data Analytics
- Documents
- Spreadsheets

### Lifestyle

- Spotify or Apple Music
- Meetup
- Booking.com
- Calendar

## 7. Initial integration policy

### 7.1 Deeply integrated in Phase 1

#### LinkedIn

- Kind: Data Source
- Default: recommended and enabled when available
- Activation: `ON_DEMAND_IMPLICIT`
- Use: professional-person lookup, meeting preparation, Sales enrichment, Relations provenance
- Constraint: no messaging, posting, profile editing, or connection actions are invented

#### LinkedIn Ads

- Kind: Data Source
- Default: `Pending Setup`
- Activation: `ON_DEMAND_IMPLICIT` after account selection
- Use: campaign, creative, spend, impression, click, CTR, CPM, CPC, and budget analysis
- Constraint: treat as analytics unless a verified write API is actually exposed

#### Sales

- Kind: Domain Workflow
- Default: enabled
- Activation: `ON_DEMAND_IMPLICIT` for clear seller/account/opportunity intent
- Use: account research, prioritization, meeting prep, follow-up, deal strategy, pipeline, business cases, competition, customer evidence
- Persistence: durable account facts, decisions, commitments, objections, and next actions

#### Data Analytics

- Kind: Domain Workflow
- Default: enabled
- Activation: `ON_DEMAND_IMPLICIT`
- Constraint: preserve the ChatGPT Web Chat-mode recommendation/override gate and source-of-truth requirements
- Use: metrics, KPI design, diagnostics, dashboards, notebooks, reports, market sizing, and cross-plugin analysis

#### Documents, PDF, Spreadsheets, Presentations

- Kind: Artifact Output
- Default: enabled
- Activation: `EXPLICIT_ONLY` where the installed router requires `@document`, `@pdf`, `@spreadsheet`, or `@presentation`
- Constraint: never trigger those routers merely because an artifact seems useful
- Persistence: final artifact and source manifest; not temporary rendering files

#### Creative Production and Adobe

- Kind: Creative System
- Default: enabled for business and Metaf use
- Activation: `ON_DEMAND_IMPLICIT` after required brief/source gates
- Use: positioning, mood boards, scenes, offers, ads, shots, logos, social variations, mockups, retouching, and quick-cut workflows

#### Meetup

- Kind: Data Source
- Default: enabled
- Activation: `ON_DEMAND_IMPLICIT`
- Use: networking and social event discovery
- Constraint: do not assume RSVP; Calendar writes remain separately confirmed

### 7.2 Cataloged optional capabilities

- Spotify selected as the default music provider; playlist changes require explicit intent.
- Apple Music remains a disabled provider alternative unless the owner switches.
- Hugging Face remains `Pending Setup` and `EXPLICIT_ONLY` for auth, cost, upload, Jobs, Endpoints, training, or publication.
- OpenAI Developers, Build Web Apps, and Product Design may route implicitly for clear developer/product work.
- Render remains `Pending Setup` and `EXPLICIT_WITH_CONFIRMATION` for deployment changes.
- Booking.com may route implicitly for travel search, not assumed booking execution.
- Public Equity Investing is enabled but `EXPLICIT_ONLY` and does not authorize trading.

### 7.3 Specialist default-disabled capabilities

- Investment Banking
- Life Science Research
- NGS Analysis
- Revolut X Read
- Revolut X Alerts
- Revolut X Trading

Disabled capabilities remain visible in the manifest so the assistant knows they exist, but it must not load or invoke them. Enabling them is a configuration change requiring owner intent and health checks.

## 8. Provider neutrality

The catalog defines a semantic role separately from a provider. Examples:

```text
music_provider -> Spotify | Apple Music
document_output -> preinstalled Document | Google Docs
spreadsheet_output -> preinstalled Spreadsheet | Google Sheets
presentation_output -> preinstalled Presentation | Google Slides
crm -> Salesforce | HubSpot | another verified CRM
```

An upgrade may preserve or repair the configured provider but must not silently replace it. Fallback to another provider requires an explicit choice when the change affects data, behavior, cost, permissions, or output format.

## 9. Installer behavior

The Installer & Upgrader must:

1. detect the current framework version and existing registry;
2. ask goal-based pack questions;
3. show recommended capabilities with defaults, required accounts, surfaces, risk, and dependencies;
4. allow per-capability edits before structural writes;
5. obtain exact-scope approval for the blueprint;
6. create or migrate the Feature Registry and Capability Catalog idempotently;
7. never enable an existing `Disabled by User` capability during upgrade;
8. never change selected provider silently;
9. validate the Notion core before optional setup;
10. write Personalization and project instructions that use manifest-first progressive loading;
11. report `Pending Setup`, `Unavailable`, and `Degraded` honestly;
12. leave Drive optional in the public product, while allowing private deployments to mark it required.

## 10. Context Bootstrap behavior

Context Bootstrap must include the compact capability manifest but not the full bodies of every capability.

The briefing includes:

- enabled and relevant capabilities;
- disabled/unavailable/degraded capabilities that materially affect the current request;
- surface and provider conflicts;
- health timestamp and source;
- the selected minimal skill set for the current request;
- active tasks and operational context under the existing budget rules.

If capability metadata and runtime evidence disagree, preserve both and report `CAPABILITY_STATE_CONFLICT`. Runtime callability controls the current action; the registry remains the canonical configured intent until reconciled.

## 11. Security and consent

- Owner-only external-disclosure rules remain binding.
- An installed or enabled capability does not grant disclosure consent.
- `EXPLICIT_WITH_CONFIRMATION` does not create standing consent.
- Financial trades, deployment, publication, external communication, access grants, cloud upload of sensitive/human data, and paid compute retain stricter action-specific confirmation.
- Authentication secrets are never stored in the Workspace or public packages.
- Public packages contain no private Emma Workspace identifiers, accounts, contacts, mail content, or private repository references.

## 12. Persistence and Autonomous Memory handoff

Every capability defines a persistence policy. The capability itself returns evidence or an action result; Autonomous Memory Capture decides which durable, reviewable information to promote.

Do not persist:

- raw feeds merely because they were read;
- every search result;
- every rejected creative variant;
- continuous market ticks;
- hidden reasoning;
- secrets.

Prefer canonical facts, decisions, commitments, metrics, selected outputs, source links, versions, and outcomes.

## 13. Failure states

```text
CAPABILITY_UNAVAILABLE
CAPABILITY_UNAUTHORIZED
CAPABILITY_SURFACE_MISMATCH
CAPABILITY_STATE_CONFLICT
CAPABILITY_HEALTH_DEGRADED
PROVIDER_SELECTION_REQUIRED
EXPLICIT_INVOCATION_REQUIRED
ACTION_CONFIRMATION_REQUIRED
```

Failures are reported without silently selecting a weaker provider or claiming completion.

## 14. Tests

The release must verify:

- Notion is the only mandatory external connector.
- Disabled capabilities are never loaded or invoked.
- Unrelated enabled skills are not fully loaded.
- Relevant implicit skills are selected from the compact manifest.
- Explicit-only artifact routers do not trigger without explicit selection.
- Data Analytics preserves its surface/mode gate.
- LinkedIn and LinkedIn Ads do not gain invented write capabilities.
- Provider switching requires an explicit choice.
- Surface mismatch and unauthorized states are reported.
- Context Bootstrap stays within its budget with many catalog entries.
- Revolut X Trading is disabled by default and remains one-action-confirmed when later enabled.
- NGS human-data cloud upload remains separately consent-gated.
- Drive Disabled-by-User is distinct from failed upload.
- Upgrade preserves state, selected provider, data, and history.
- Repeated migration creates no duplicate feature records.
- Private identifiers do not enter public artifacts.

## 15. Live private reference

The private Emma Workspace implements the approved model with:

- Feature Registry data source `collection://deda7bc2-9c00-4c50-b6ad-c5244871a1d1`;
- `Capability Catalog & Packs` page;
- activation-, pack-, and high-risk views;
- initial capability records and provider selections;
- Constitution 3.2 and Context Bootstrap 1.2.

These live identifiers are private reference data and must never be copied into public runtime packages or fixtures.
