# Personal AI Workspace — Personal Context and Active Workspace Semantics Addendum

**Status:** Approved binding Phase 1 addendum  
**Date:** 2026-07-17  
**Public tracking:** `Personal-AI-Workspace#12`, `#14`, `#15`, `#16`  
**Private execution tracking:** `Apex#23`, `#24`, `#25`  
**Applies to:** framework/creator `1.6.0`, Installer & Upgrader `0.1.0-beta.1`, Context Bootstrap `0.1.0-beta.1`, shared Skill Pack contracts, public documentation/tests and private Emma adapter `6.0.0-rc.1`  
**Publication:** not authorized by this document

## 1. Purpose

This addendum closes four practical gaps:

1. Context Bootstrap can be operationally complete yet still lack the people, events and personal-state context most useful for real advice.
2. Personal AI Workspace does not explicitly define how canonical Workspace data combines with current conversation context and native AI memory/personalization.
3. Psychological, wellbeing, health and supplement information needs a durable, confidential, epistemically typed model rather than either blanket exclusion or indiscriminate capture.
4. Journal, Observations, Decisions, Projects, Working Notes and Archive must be active, discoverable workflows rather than empty ornamental spaces.

The owner approved these changes for Phase 1. The separate naming/rebrand investigation in `Personal-AI-Workspace#13` and `Apex#26` remains Phase 2 and MUST NOT block or rename Phase 1 artifacts.

## 2. Normative language and precedence

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are normative.

This addendum supplements all earlier approved Phase 1 documents. When a conflict exists, the canonical Codex entrypoint applies its document-precedence rules. For behavior addressed here, this addendum supersedes older generic wording.

## 3. Memory Fusion contract

### 3.1 Sources remain complementary

Using Personal AI Workspace MUST NOT disable or ignore:

- the current user message;
- current-conversation context;
- native AI memory or platform personalization when available;
- verified live connector data;
- canonical Notion records;
- cached summaries;
- explicit assistant interpretations or hypotheses.

The system combines those sources while retaining provenance and source type.

### 3.2 Default evidence hierarchy

Use the following precedence when sources conflict:

```text
1. explicit current user statement
2. verified live canonical Workspace record
3. verified live connector source
4. current conversation context
5. native AI memory or platform personalization
6. cached summaries
7. assistant interpretation or hypothesis
```

This is a default conflict-resolution hierarchy, not permission to erase history.

A lower-ranked source MAY add context but MUST NOT silently overwrite a conflicting higher-ranked source. When evidence conflicts, retain both statements, sources and dates and classify the operation as one of:

```text
CORRECT_EXISTING
CONTRADICT_EXISTING
SUPERSEDE_EXISTING
REVIEW_REQUIRED
```

Native AI memory is an auxiliary signal. It MUST NOT act as an invisible source of truth above live canonical Workspace data.

### 3.3 Unavailable source behavior

If a source is unavailable, the assistant MAY proceed with remaining sources but MUST report materially relevant coverage limits. Absence of native memory or personalization is not an installation error. Notion remains the only mandatory external connector.

## 4. Person and relationship capture

Apply this two-stage rule to every person- or relationship-related statement:

```text
ALWAYS_EVALUATE
SAVE_IF_MATERIAL
```

### 4.1 Always evaluate

Every statement about a person, relationship or interaction becomes a bounded memory candidate. Evaluation MUST consider identity resolution, relationship state, commitments, preferences, conflicts, changes, communication context, material events, corrections and repeated patterns.

### 4.2 Save if material

Persist or update the smallest canonical record when the statement is likely to matter later or changes the understanding of:

- identity;
- relationship type or state;
- an important interaction;
- a promise, commitment or follow-up;
- a communication preference or boundary;
- an unresolved conflict;
- a material life event affecting the relationship;
- a repeated pattern supported by evidence;
- a correction, contradiction or supersession.

Do not persist incidental mentions, unchanged duplicates, transient small talk or unsupported speculation presented as fact.

## 5. Psychological and wellbeing context

### 5.1 Record types

Psychological and wellbeing records MUST use one of:

```text
SELF_REPORTED_STATE
OBSERVED_SIGNAL
REPEATED_PATTERN
INTERPRETATION
HYPOTHESIS
COUNTEREVIDENCE
RISK_SIGNAL
```

### 5.2 Required fields

Each record includes:

```text
subject
statement
record_type
source
source_context
observed_at
valid_from
valid_until_or_review_after
perspective
epistemic_status
confidence
sensitivity
supporting_evidence
counterevidence
owner_correction_history
related_people_projects_or_events
```

### 5.3 Non-negotiable interpretation rules

- A transient mood MUST NOT become a stable personality trait.
- One behavior MUST NOT become a repeated pattern.
- An interpretation or hypothesis MUST NOT become a fact without supporting evidence or direct owner confirmation.
- A durable repeated pattern SHOULD require multiple materially separate observations or explicit owner confirmation.
- Counterevidence MUST remain visible and linked.
- The system MUST NOT infer a clinical diagnosis from ordinary conversation.
- Records are `Confidential` and owner-only by default.
- Explicit owner correction MUST be preserved and reflected in current summaries.

### 5.4 Risk signals

High-stakes risk signals require careful, source-grounded handling. The memory system stores the minimum useful context and does not use a risk label as a substitute for professional assessment or emergency procedures.

## 6. Health, medication and supplement context

### 6.1 Entry types

Support at least:

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

### 6.2 Lifecycle states

Each entry uses one of:

```text
ACTIVE
PAUSED
STOPPED
HISTORICAL
UNCONFIRMED
```

### 6.3 Required fields

```text
item_or_subject
entry_type
status
dose_or_value
frequency
purpose
started_at
paused_or_stopped_at
source
reported_effect
possible_adverse_effect
confidence
sensitivity
review_date
related_records
```

Old, paused, stopped or historical items MUST NOT appear as currently active. Unknown dose or schedule remains unknown; the system MUST NOT invent it.

Health-related guidance remains evidence-aware and MUST NOT present the Workspace as a substitute for qualified medical care.

## 7. Context Bootstrap 1.4 enrichment

### 7.1 Required sections

The rendered briefing contains these ordered sections when relevant:

```text
1. Current Focus
2. People in Focus
3. Active Tasks A/B/C
4. Active Projects and Commitments
5. Recent and Salient Events
6. Wellbeing and Health Snapshot
7. Decisions and Pending Reviews
8. Risks, Conflicts and Blockers
9. Capability Health
10. Recently Changed Memory
```

Empty optional sections MAY be omitted with an explicit zero-count indicator in structured output. Active tasks MUST never be omitted merely to make room for optional personal-context sections.

### 7.2 Salience model

Every included non-task item MUST include a source and at least one explicit salience reason from an extensible enum including:

```text
explicitly_emphasized
unresolved_commitment
active_relationship_impact
active_project_impact
recurring_pattern
high_emotional_impact
health_or_wellbeing_relevance
blocks_current_decision
recent_material_change
review_due
```

An opaque model score alone is insufficient. Deterministic rules and visible reasons are required.

### 7.3 People in Focus

Default maximum: 5 people.

Each entry includes:

```text
person_id
name
current_relationship_context
salience_reason
latest_material_interaction
open_commitment_or_unresolved_state
next_step
last_verified
canonical_url
```

People in Focus is an operational current set, not a permanent ranking of the most important people in the owner's life.

### 7.4 Recent and Salient Events

Default maximum: 10 events, mixing recent events with older unresolved or still-impactful events.

Each event includes:

```text
event_id
occurred_at
summary
people
projects
impact
salience_reason
source
canonical_url
review_after_or_valid_until
```

### 7.5 Wellbeing and Health Snapshot

The briefing includes only the minimum operationally useful summary:

- direct self-reported current state;
- material recent changes;
- active constraints or follow-ups;
- relevant active health, medication or supplement changes;
- links to confidential canonical records.

It MUST NOT duplicate a full confidential profile, expose it outside the verified owner conversation or convert hypotheses into facts.

### 7.6 Recently Changed Memory

Show material canonical records created, corrected, contradicted or superseded within the configured freshness window. Every entry includes operation type, timestamp, source and canonical link. Do not list cosmetic edits.

### 7.7 Budget and current-session evidence

- Preserve the existing overall briefing budget unless an approved configuration changes it.
- Use per-section budgets and deterministic prioritization.
- Every active task remains at least a compact index row.
- Use continuation or index mode rather than silent omission.
- `FULL` remains a current-session evidence result and still requires live capability/task/review validation.
- Cached personal-context sections cannot certify their source.

## 8. Active workspace-space semantics

### 8.1 General contract

Do not create ornamental databases or pages.

Every enabled space MUST define:

```text
purpose
include_rules
exclude_rules
read_triggers
write_triggers
canonicality
routing_rules
lifecycle_states
promotion_rules
archive_or_expiry_rules
default_views
templates
bootstrap_visibility
retention_and_deletion_boundary
```

Every enabled space must support at least one real workflow and an owner-visible view that makes its records discoverable.

### 8.2 Journal

Purpose: chronological, user-visible record of materially important days, events, developments and bounded reflections.

Journal MAY contain:

- significant events;
- meaningful progress or setbacks;
- important changes in priorities;
- material conversation or meeting summaries;
- user-visible reflections explicitly suitable for retention;
- links to canonical people, projects, decisions, tasks and sources.

Journal MUST NOT contain hidden chain-of-thought, full transcript dumps, routine greetings or trivial small talk.

Required views:

```text
Recent
High Salience
By Person
By Project
Review or Follow-up Needed
```

### 8.3 Observations

Purpose: explicit observations, interpretations, hypotheses, patterns and counterevidence.

Each record includes subject, statement, type, source, observed date, confidence, sensitivity, supporting evidence, counterevidence, review date and status.

Required views:

```text
Active Observations
Hypotheses Requiring Review
Repeated Patterns
Counterevidence
By Person
By Project
```

### 8.4 Decisions

Purpose: make lightweight decisions and full Decision Cases visible and reviewable.

Required views:

```text
All Decisions
Open Decision Cases
Recently Decided
Review Due
Outcomes Recorded
By Project
```

Every decision page exposes rationale summary, assumptions, selected option, decision date, review date, outcome/lesson status and links to related project, tasks and sources.

### 8.5 Projects

Purpose: canonical project hub connecting:

```text
goal
status
owner
people
tasks
decisions
risks
files
sources
latest_update
next_action
```

Required views:

```text
Active
Blocked
Recently Updated
By Owner
Archive Ready
```

### 8.6 Working Notes

Purpose: temporary, explicitly non-canonical working material.

Every note has owner/context, created date, review/expiry date and one lifecycle decision:

```text
PROMOTE_TO_CANONICAL
KEEP_WORKING
ARCHIVE
EXPIRE
```

Promotion destinations include Knowledge, Relations, Decision, Project, Source and Task. Working Notes MUST NOT remain indefinitely without review.

### 8.7 Archive

Archive is a lifecycle state or filtered historical view, not a dumping ground.

Archived records preserve provenance and links, remain subject to retention rules and are excluded from active bootstrap unless directly relevant. No silent permanent deletion is authorized.

## 9. Routing and canonicality

Autonomous Memory Capture and domain capabilities route candidates to the smallest appropriate destination:

```text
material day/event summary -> Journal
observation/interpretation/hypothesis -> Observations
explicit choice -> Decisions
multi-step outcome with goal/dependencies -> Projects
unfinished non-canonical analysis -> Working Notes
closed/superseded/expired item -> Archive lifecycle
```

If routing is ambiguous, return `REVIEW_REQUIRED` rather than creating duplicate records.

## 10. Installer and upgrade requirements

Installer & Upgrader MUST:

- explain each space and personal-context profile before structural creation;
- create only owner-selected optional spaces plus approved core requirements;
- detect equivalent existing spaces, properties, views and templates;
- preview exact structural changes and obtain exact-scope approval;
- create required views/templates idempotently;
- migrate existing data without duplication;
- preserve links, provenance and local customizations;
- migrate explicit-save-only behavior to bounded Autonomous Memory without ignoring no-save restrictions;
- map existing person, relationship, health, observation, decision and project data;
- verify every resulting space, view, template and routing instruction by readback;
- keep unknown newer installations read-only;
- preserve owner choices on disabled spaces and thresholds.

## 11. Public/private boundary

Public schemas, fixtures and examples use fictional people, events, health items and relationships. They contain no private Emma Workspace IDs, contacts, psychological observations, health information, task content or source URLs.

The private adapter supplies private source maps, enabled spaces, account identities, provider choices, thresholds and exact URLs outside public source.

## 12. Acceptance and release gate

The release must test:

- Memory Fusion precedence and visible conflict handling;
- native-memory auxiliary behavior;
- relation `ALWAYS_EVALUATE / SAVE_IF_MATERIAL`;
- transient state versus stable pattern;
- hypothesis and counterevidence preservation;
- health lifecycle and exclusion of stopped items from current summaries;
- owner correction and explicit no-save;
- all Bootstrap 1.4 sections, limits, salience reasons and partial-source behavior;
- active-task completeness under context pressure;
- Journal/Observations/Decisions/Projects/Working Notes/Archive routing and lifecycle;
- owner-visible views and templates;
- idempotent install/upgrade;
- no public/private leakage;
- no release publication or private live activation without later approval.

The final Draft PR MUST trace implementation to public issues `#14–#16` and private execution issues `Apex#23–#25` in code, tests and documentation.