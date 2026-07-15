# Personal AI Workspace — One-Time External Disclosure Consent Addendum

**Status:** Approved binding scope amendment  
**Date:** 2026-07-15  
**Applies to:** public creator, Installer & Upgrader skill, Context Bootstrap skill, public ChatGPT/Codex Skill Pack, Codex installers and AGENTS.md guidance, future specialist skills, public documentation and tests, plus the private `emma-workspace-memory v6.0.0` adapter.

## 1. Non-disclosure default

No information contained in a Personal AI Workspace may be disclosed, transmitted, summarized, quoted, attached, published, invited, forwarded, copied, or otherwise made available to anyone other than the Workspace owner.

This boundary covers:

- direct records, files, messages, tasks, contacts, calendar data, sources and attachments;
- sensitive and non-sensitive information alike;
- summaries, inferences, classifications, derived facts, embeddings, reports and generated artifacts based on Workspace data;
- information about the owner and information about third parties stored in the Workspace;
- disclosure through email, reply, reply-all, forwarding, Calendar invitations, contact sharing, GitHub issues, pull requests, comments, public repositories, shared Drive folders or links, documents, presentations, spreadsheets, PDFs, images, chat messages, APIs, connectors, automations and any future channel.

Private storage in the verified owner's own Notion or private Google Drive is not an external disclosure. Publishing, link-sharing, moving to a third-party-owned location, or granting access is external disclosure.

## 2. Only exception: exact one-time consent

External disclosure is permitted only when the owner gives clear, informed approval for one specific disclosure event.

The approval must identify:

1. exact recipient or recipients;
2. exact channel and action;
3. exact information scope, including exclusions when relevant;
4. purpose;
5. final content or artifact version;
6. attachments, links and access permissions;
7. whether the action is send, reply, reply-all, forward, invite, publish, share, upload, comment or another explicit operation.

Approval expires immediately after the one successful execution or after the approved action is abandoned. It cannot be reused.

## 3. No standing, implied or inherited consent

The following never count as permission:

- an earlier approval, even for the same recipient;
- a general statement that a trusted person may receive information;
- a relationship, role, employment or family connection;
- the recipient already knowing some or all of the information;
- permission to read, store, analyze or summarize Workspace data;
- permission to draft a message;
- permission to use a connector;
- a recurring automation, template, task or standing workflow;
- silence, lack of objection or prior disclosure by another person;
- an approval granted in another conversation or for another version of content.

Even if the owner asks for a permanent or blanket disclosure permission, the system records it only as a preference to streamline future confirmation; each disclosure still requires a fresh one-time approval.

## 4. Material changes require fresh approval

After approval, any material change requires re-confirmation, including changes to:

- recipients;
- channel or action mode;
- body, summary, quoted details or conclusions;
- attachments or links;
- access permissions;
- information scope;
- purpose;
- reply versus reply-all versus forward;
- public versus private visibility;
- final artifact checksum or version.

## 5. Consent evidence record

Before execution, retain a reviewable consent record containing:

```text
consent_id
owner_identity
approved_at
disclosure_action
channel
recipients
purpose
information_scope
explicit_exclusions
final_content_hash_or_version
attachments_and_permissions
single_use = true
status = APPROVED | EXECUTED | ABANDONED | FAILED
executed_at
result_url_or_message_id
```

A failed or partially completed action does not authorize a different retry. A technically identical retry after a transient failure may occur only while the approved action remains clearly pending and no content, recipient, permission or channel changed; otherwise ask again.

## 6. Third-party requests

If anyone other than the owner requests Workspace information, the assistant must not disclose it. It should direct the request to the owner or prepare a draft request for the owner's review. Identity uncertainty is treated as no authorization.

## 7. Skill-specific requirements

### Installer & Upgrader

- install this policy into the Constitution and all relevant modules;
- preserve it during upgrades and repairs;
- treat its removal or weakening as a structural and security-sensitive change requiring exact-scope approval;
- detect missing or contradictory disclosure rules as `DAMAGED` or a high-severity repair finding;
- never migrate a standing disclosure permission as valid consent.

### Context Bootstrap

- briefing output is for the verified owner only;
- do not generate a briefing for another person or a shared/public destination;
- minimize sensitive detail and use pointers where possible;
- do not place Workspace context into collaboration channels without a separate one-time consent event;
- report account mismatch or uncertain recipient identity and stop.

### Public ChatGPT/Codex Skill Pack

- vendor this contract into every standalone skill package;
- include positive and negative routing examples;
- include deterministic tests for one-time scope, recipient changes, attachment changes, recurring workflows and public/private destinations;
- public fixtures use fictional data only.

### Codex distribution and AGENTS.md

- the global/project instruction snippet must state that Workspace information is owner-only by default;
- code generation, logs, issues, PRs and comments must not contain private Workspace context unless the owner approves the exact disclosure;
- local repository access does not imply permission to publish or commit Workspace data.

### Private Emma adapter v6.0.0

- contain the owner's verified identities and private source map;
- enforce this contract across Gmail, Calendar, Contacts, Drive, GitHub, Notion, generated artifacts and automations;
- maintain compatibility with the public shared disclosure-contract version;
- fail closed on missing or incompatible contract versions.

## 8. Required tests

At minimum, test:

- exact recipient + exact scope + exact final content succeeds once;
- the same action cannot run a second time from the same approval;
- adding a recipient requires fresh approval;
- changing reply to reply-all requires fresh approval;
- adding or replacing an attachment requires fresh approval;
- changing a Drive link from private to public requires fresh approval;
- recurring automation cannot reuse consent;
- prior consent in another conversation is rejected;
- recipient already knowing the information does not bypass consent;
- owner-only briefing remains allowed;
- account mismatch and identity uncertainty stop disclosure;
- private Workspace data scanner catches accidental inclusion in public packages and repositories.

## 9. Release scope

This addendum is a binding Global Constraint for every Phase 1 implementation plan. Where an older plan conflicts with it, this addendum governs. Implementation must update the shared privacy contract, schemas, both skills, installer/migrations, documentation, Codex guidance, tests, release validation and the private adapter plan before prerelease readiness can be claimed.
