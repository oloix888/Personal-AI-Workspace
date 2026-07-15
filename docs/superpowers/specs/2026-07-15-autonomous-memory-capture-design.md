# Autonomous Memory Capture Design

**Status:** Approved binding scope amendment  
**Date:** 2026-07-15  
**Owners:** Michał Poliński and Emma ✨  
**Tracks:** `oloix888/Apex#16`, Phase 1 Skill Pack, public creator, private Emma adapter

## 1. Purpose

Personal AI Workspace should not depend on the user repeatedly saying “remember this” or “save this.” During an active conversation, the assistant should autonomously identify material durable information and create or update the smallest appropriate canonical record.

This capability is named **Autonomous Memory Capture**.

Autonomy applies to ordinary data operations inside an already approved Workspace structure. It does not authorize the assistant to change schemas, disclose information, perform external communication, spend money, deploy systems, trade, invite people, publish, or permanently delete protected records.

## 2. Goals

- Capture useful durable context without requiring per-record confirmation.
- Update canonical records instead of accumulating duplicate notes.
- Preserve provenance, epistemic status, confidence, sensitivity, and history.
- Respect explicit restrictions such as “do not save this.”
- Keep transient conversation and hidden reasoning out of durable memory.
- Route facts, people, commitments, decisions, tasks, sources, and operational observations to the correct subsystem.
- Report capture failures truthfully without promising a background retry.
- Keep the capture pass bounded so it does not dominate the response.
- Support both ChatGPT and Codex through the public Skill Pack and private adapter.

## 3. Non-goals

Autonomous Memory Capture is not:

- a full transcript archive;
- hidden chain-of-thought storage;
- a private scratchpad;
- a reason to save every sentence, joke, greeting, or temporary mood;
- permission to create new databases or properties;
- permission to delete, publish, share, email, invite, trade, deploy, or purchase;
- a background daemon;
- permission to bypass a capability's disabled state or activation policy;
- a substitute for source verification;
- a guarantee that every candidate can be safely written on every surface.

## 4. Materiality model

A candidate should be captured when one or more of the following are true:

- it is likely to matter in a future conversation;
- it changes the understanding of the user, a person, a relationship, a project, or a system;
- it creates or changes a commitment, task, deadline, dependency, risk, or decision;
- it corrects or contradicts an existing record;
- it defines a stable preference, goal, value, constraint, boundary, provider choice, or operating rule;
- it identifies a reusable source, artifact, model, metric, process, or strategy;
- it is a high-value observation about system behavior;
- the user explicitly asks for retention.

A candidate should normally not be captured when it is:

- ordinary greeting or small talk;
- a transient conversational filler;
- a duplicate of an unchanged canonical fact;
- hidden reasoning or internal scratch work;
- a password, token, one-time code, reset link, session cookie, or authentication secret;
- a long raw payload whose durable value is adequately represented by a source link and summary;
- a generated intermediate file, cache, or rejected variation;
- explicitly marked “do not save,” “off the record,” or equivalent by the owner or source.

## 5. Candidate types and destinations

### 5.1 Knowledge

Capture:

- durable facts;
- preferences;
- goals and values;
- constraints and boundaries;
- strategies and operating principles;
- source-backed observations;
- definitions and reusable domain knowledge;
- corrections and supersessions.

Destination: Knowledge Nodes, Knowledge Relations, Sources & Evidence, Topic Maps, or Review Queue.

### 5.2 Relations

Capture:

- people and identity resolution;
- relationship type and state;
- interaction context;
- communication preferences;
- commitments and follow-ups;
- material relationship observations;
- reported claims, interpretations, and hypotheses with proper status.

Destination: People & Agents, Relationships, Interactions & Notes, Commitments & Follow-ups, or Relationship Review Queue.

### 5.3 Decisions

Capture:

- explicit decisions;
- selected option and rationale summary;
- assumptions and constraints;
- review date;
- lessons and outcomes.

A full Decision Case is opened only when the existing material-decision trigger applies. Small explicit choices may be recorded as ordinary decision notes without creating an oversized case.

### 5.4 Tasks

Capture:

- an actionable obligation;
- a promised follow-up;
- a requested deliverable;
- a deadline or blocker;
- a system repair or improvement that has a clear expected result.

Generic public installations should stage the task in the canonical Task Outbox. Creating an external GitHub Issue automatically is allowed only when the configured task-backend policy, privacy, repository visibility, and owner rules permit it. A task record is not proof that the work was executed.

### 5.5 Sources and artifacts

Capture:

- source identity, URL, provider, date, reliability, and evidence status;
- final artifact ID, version, checksum, location, and source manifest;
- important limitations and coverage.

Do not copy complete copyrighted or sensitive payloads when a bounded summary and source reference are sufficient.

### 5.6 System Evolution Lab

Capture user-visible operational observations when there is:

- a user correction;
- connector failure;
- stale or conflicting configuration;
- duplicated work;
- ambiguous policy;
- recurring friction;
- high-value improvement opportunity;
- unexpected implementation result.

This remains reviewable operational evidence, not hidden reasoning.

## 6. Capture pass lifecycle

A capture pass runs near the end of a material active turn, before the assistant claims that durable context is updated.

### Step 1: detect candidates

Extract a bounded list of candidate information units. Do not treat the full conversation as one payload.

Each candidate includes:

```text
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
```

### Step 2: apply exclusions

Remove:

- secrets;
- hidden chain-of-thought;
- explicit no-save content;
- transient low-value content;
- unchanged duplicates;
- unsupported inferences presented as facts.

Useful context adjacent to an excluded secret may still be captured after the secret is removed.

### Step 3: resolve canonical record

Search the task-relevant destination using name, aliases, identifiers, semantic summary, source, relationship, deduplication key, or existing links.

Outcomes:

```text
CREATE_NEW
AUGMENT_EXISTING
CORRECT_EXISTING
CONTRADICT_EXISTING
SUPERSEDE_EXISTING
NO_CHANGE
REVIEW_REQUIRED
```

### Step 4: build the smallest write

Write only the fields or content required to preserve the new information. Avoid rewriting entire pages when targeted updates are possible.

### Step 5: preserve evidence and history

- Fact: source or direct user statement.
- Reported Claim: who said it, to whom, when, and context.
- Observation: what was directly observed.
- Interpretation: an explicit analytical view.
- Hypothesis: possible explanation requiring validation.

Corrections, contradictions, and supersessions preserve the prior record and provenance rather than silently erasing history.

### Step 6: execute and read back

Verify identity, target, parent, critical properties, links, and resulting content. Do not report success without readback.

### Step 7: refresh dependent indexes selectively

Refresh only affected Workspace Index, Topic Map, Relations view, Feature Registry, Context Bootstrap section, task index, or review queue. Do not rebuild the whole Workspace after every turn.

### Step 8: report only when useful

Do not interrupt ordinary conversation with a verbose log after every small successful capture. Report:

- material records created or corrected when useful to the user;
- ambiguity requiring a decision;
- a failed or degraded capture;
- an action that still needs confirmation.

## 7. Autonomy and approval boundaries

### 7.1 Autonomous ordinary writes

No per-record confirmation is required for:

- creating or updating ordinary Knowledge records;
- updating Relations, Interactions, or Commitments;
- adding source provenance;
- recording an explicit decision or correction;
- staging an internal task under the configured task policy;
- recording a System Evolution observation;
- updating a bounded Context Bootstrap section after a material state change.

### 7.2 Still approval-gated

The capture pass must not autonomously:

- add or remove databases, columns, relations, views, modules, automations, providers, or integrations;
- change a feature state, activation policy, selected provider, or retention policy;
- permanently delete a protected record;
- publish or disclose Workspace information;
- send email or messages;
- invite attendees;
- create public/shared links or access permissions;
- place, replace, or cancel financial orders;
- deploy services or start paid compute;
- upload human or sensitive research data to an external cloud;
- override a domain-specific confirmation rule.

### 7.3 User control

The owner may:

- pause or disable Autonomous Memory Capture;
- say “do not save this” for a specific item;
- restrict a category or destination;
- request a correction, archive, merge, or deletion review;
- inspect what was captured;
- change materiality thresholds through an approved configuration change.

## 8. Sensitive information

Sensitive context is not excluded solely because it is sensitive. It may be captured when materially relevant, with:

- purpose;
- source and date;
- people and relationship context;
- epistemic status and perspective;
- confidence;
- `Confidential` classification;
- validity period where time-bound.

Internal retention never grants external-disclosure permission.

## 9. Capture budget

The implementation must be bounded.

Default constraints:

- maximum 12 candidates per ordinary turn before clustering;
- maximum 5 direct writes in one turn without a dedicated bulk-capture request;
- cluster duplicate candidates;
- prioritize corrections, commitments, decisions, deadlines, and high-impact relationship context;
- overflow candidates become a reviewable capture queue only if an approved queue exists;
- do not create a new structural queue merely because overflow occurred.

The exact defaults may be configurable, but upgrades must preserve user choices.

## 10. Failure behavior

Use:

```text
MEMORY_CAPTURE_FULL
MEMORY_CAPTURE_PARTIAL
MEMORY_CAPTURE_DEGRADED
MEMORY_CAPTURE_BLOCKED_IDENTITY
MEMORY_CAPTURE_BLOCKED_STRUCTURE
MEMORY_CAPTURE_REVIEW_REQUIRED
```

When a connector is unavailable, identity mismatches, the source is truncated, the record is ambiguous, or readback fails:

- do not claim the information was saved;
- preserve the candidate only in the active conversation unless an approved internal queue is available;
- state the material limitation when useful;
- do not promise an automatic background retry.

## 11. Interaction with Capability Catalog

Autonomous Memory Capture is `CORE_BOOTSTRAP` and uses Notion as its selected provider. Domain capabilities pass durable candidate outputs to it through a common capture contract.

Examples:

- LinkedIn -> professional facts with source and last-verified date.
- Sales -> account facts, objections, decisions, commitments, next actions.
- Data Analytics -> metric definitions, controlling source, dated findings, caveats, decisions.
- Creative Production -> selected brief, approved direction, final asset references and outcomes.
- Meetup -> shortlisted or attended events, decisions, contacts, outcomes.
- Hugging Face -> project IDs, revisions, evaluations and job outcomes, never tokens.
- Public Equity -> source-backed thesis, assumptions, catalysts, risks and reviews.
- Disabled capabilities produce no capture candidates from live reads because they are not invoked.

## 12. Installer and upgrade behavior

The Installer & Upgrader must:

- create Autonomous Memory Capture as a Core enabled feature by default;
- explain the behavior and boundaries before first structural write;
- let the user pause or disable it;
- create the necessary rules in Constitution modules 00, 02, 03, 09, and 11;
- map existing Knowledge, Relations, Decision, Task, Source, and Evolution structures;
- migrate older “save only when explicitly asked” installations without duplicating records;
- preserve explicit no-save restrictions and retention rules;
- write Personalization and project instructions that run the bounded capture pass during active conversations;
- verify the feature and readback after installation.

## 13. Context Bootstrap behavior

Context Bootstrap:

- declares Autonomous Memory Capture state in the capability manifest;
- does not become write-heavy during startup;
- runs the capture pass after material interaction, not before reading the user's request;
- refreshes only affected briefing sections;
- reports stale configuration or capture degradation;
- never copies the full conversation into the briefing.

## 14. Public/private boundary

Public packages contain the generic rules, schemas, classifiers, and fixtures. They contain no private identifiers, source URLs, contacts, or actual captured data.

The private Emma adapter supplies:

- expected account identities;
- private Notion source map;
- private task backend;
- exact private feature states and provider choices;
- private retention and Drive configuration.

## 15. Tests

The release must verify:

- a durable fact is stored with provenance;
- a stable preference updates the canonical user profile;
- transient small talk is ignored;
- an existing canonical record is updated, not duplicated;
- a correction preserves prior history;
- a reported claim remains a reported claim;
- a hypothesis does not become fact;
- a secret is excluded while adjacent useful context can be retained;
- explicit “do not save this” is honored;
- sensitive material receives purpose, provenance, status, confidence, and classification;
- a task is staged only under the configured task policy;
- structural changes remain blocked;
- external disclosure remains blocked without one-time approval;
- disabled capability outputs are not captured because they are not invoked;
- write/readback failure returns `MEMORY_CAPTURE_DEGRADED`;
- no background retry is promised;
- repeated execution is idempotent;
- large conversations remain within the capture budget;
- public package scans contain no private data.

## 16. Live private reference

The private Emma Workspace implements the approved behavior through:

- Constitution 3.2;
- Autonomous Memory Capture feature record;
- modules 00 v2.2, 02 v1.2, 03 v1.3, 09 v2.1, and 11 v2.2;
- Context Bootstrap 1.2;
- canonical Knowledge, Relations, Decision Engine, Task Outbox, Sources & Evidence, and System Evolution structures.

These live identifiers and records are private references and must not enter public runtime packages or fixtures.
