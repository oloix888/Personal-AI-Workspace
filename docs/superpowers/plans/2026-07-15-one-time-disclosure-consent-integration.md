# One-Time External Disclosure Consent Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce owner-only Workspace information by default across the creator, public Skill Pack, Codex guidance, tests and release validation, allowing external disclosure only after fresh, exact, single-use owner approval.

**Architecture:** Add one shared `external-disclosure-consent.md` contract plus a machine-readable consent-event schema. Vendor the contract into both public skills, make installer detection and migration verify it, make Context Bootstrap owner-only, and add deterministic consent-validation plus privacy-scanning tests. The private Emma adapter consumes the same contract version in its separate plan.

**Tech Stack:** Agent Skills, Markdown, JSON Schema Draft 2020-12, Python 3.11+, pytest, shared Skill Pack build tooling.

## Global Constraints

- The approved addendum `docs/superpowers/specs/2026-07-15-one-time-disclosure-consent-addendum.md` governs any conflict with older plans.
- No Workspace information—direct or derived—may be disclosed to anyone other than the verified owner without fresh one-time approval for the exact disclosure event.
- Consent is never standing, inherited, implied, recurring or reusable.
- Material changes to recipients, action, channel, content, scope, attachments, permissions, purpose or final version require re-confirmation.
- Private storage in the verified owner's Notion or private Drive is internal; public/shared access is external disclosure.
- Unknown recipient identity or account mismatch fails closed.
- This plan does not publish a prerelease or modify Michał's private Workspace.
- Every task follows TDD and ends with a focused commit.

---

### Task 1: Add the shared disclosure contract and consent-event schema

**Files:**
- Create: `skills/_shared/contract/external-disclosure-consent.md`
- Create: `skills/_shared/schemas/disclosure-consent-event.schema.json`
- Modify: `skills/_shared/contract/compatibility.json`
- Create: `skill-pack/tests/test_disclosure_contract.py`
- Modify: `skill-pack/tests/test_schemas.py`

**Interfaces:**
- Produces contract version `1.0.0` and schema `disclosure-consent-event.schema.json`.
- Later tasks consume consent records with `single_use: true` and explicit recipient/content scope.

- [ ] **Step 1: Write failing contract tests**

```python
# skill-pack/tests/test_disclosure_contract.py
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "skills/_shared/contract/external-disclosure-consent.md"
SCHEMA = ROOT / "skills/_shared/schemas/disclosure-consent-event.schema.json"


def test_contract_is_default_deny_and_single_use() -> None:
    text = CONTRACT.read_text(encoding="utf-8").lower()
    for phrase in [
        "no external disclosure by default",
        "verified workspace owner",
        "one-time approval",
        "cannot be reused",
        "material change requires fresh approval",
        "third-party request",
    ]:
        assert phrase in text


def test_consent_schema_requires_exact_scope() -> None:
    payload = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = set(payload["required"])
    assert {
        "consent_id", "owner_identity", "approved_at", "action", "channel",
        "recipients", "purpose", "information_scope", "final_content_version",
        "attachments_and_permissions", "single_use", "status"
    } <= required
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_disclosure_contract.py -v
```

Expected: failure because the contract and schema do not exist.

- [ ] **Step 3: Create the contract**

```markdown
# External Disclosure Consent

## No external disclosure by default

Information contained in Personal AI Workspace is for the verified Workspace owner only. This includes direct records and derived summaries, inferences, reports, classifications and generated artifacts.

## One-time approval

External disclosure requires fresh, informed, one-time approval identifying exact recipients, channel, action, purpose, information scope, exclusions, final content or artifact version, attachments, links and permissions. Approval expires after one successful execution or abandonment and cannot be reused.

## No implied or standing consent

Prior approval, trusted-recipient status, relationship, recipient prior knowledge, connector access, draft approval, recurring workflow, silence or approval from another conversation never authorize a new disclosure.

## Re-confirmation

Any material change to recipients, channel, action mode, body, summary, scope, purpose, attachments, links, access permissions or final version requires fresh approval.

## Identity and third-party requests

Identity uncertainty and account mismatch fail closed. A third-party request is refused or redirected to the owner.

## Internal storage versus disclosure

Private storage in the verified owner's Notion or private Drive is internal. Publishing, sharing a link, granting access or moving data to a third-party-controlled location is external disclosure.
```

- [ ] **Step 4: Create the schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://personal-ai-workspace.example/schemas/disclosure-consent-event.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "consent_id", "owner_identity", "approved_at", "action", "channel",
    "recipients", "purpose", "information_scope", "explicit_exclusions",
    "final_content_version", "attachments_and_permissions", "single_use", "status"
  ],
  "properties": {
    "consent_id": {"type": "string", "minLength": 1},
    "owner_identity": {"type": "string", "minLength": 1},
    "approved_at": {"type": "string", "format": "date-time"},
    "action": {"type": "string", "minLength": 1},
    "channel": {"type": "string", "minLength": 1},
    "recipients": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
    "purpose": {"type": "string", "minLength": 1},
    "information_scope": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
    "explicit_exclusions": {"type": "array", "items": {"type": "string"}},
    "final_content_version": {"type": "string", "minLength": 1},
    "attachments_and_permissions": {"type": "array", "items": {"type": "string"}},
    "single_use": {"const": true},
    "status": {"enum": ["APPROVED", "EXECUTED", "ABANDONED", "FAILED"]},
    "executed_at": {"type": ["string", "null"], "format": "date-time"},
    "result_url_or_id": {"type": ["string", "null"]}
  }
}
```

- [ ] **Step 5: Add contract compatibility metadata**

Add to `compatibility.json`:

```json
"external_disclosure_contract_version": "1.0.0"
```

Update the compatibility loader and tests to expose the field.

- [ ] **Step 6: Validate schema and contract**

```bash
python -m pytest skill-pack/tests/test_disclosure_contract.py skill-pack/tests/test_schemas.py -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add skills/_shared skill-pack/tests skill-pack/src/paiw_skill_pack/models.py
git commit -m "feat: define one-time external disclosure contract"
```

---

### Task 2: Add deterministic consent validation

**Files:**
- Create: `skill-pack/src/paiw_skill_pack/consent.py`
- Create: `skill-pack/tests/test_consent.py`
- Create: `skill-pack/tests/fixtures/consent/approved.json`

**Interfaces:**
- Produces `DisclosureAttempt`, `ConsentDecision`, and `validate_disclosure(consent, attempt) -> ConsentDecision`.
- A decision includes `allowed: bool` and machine-readable reasons.

- [ ] **Step 1: Write failing tests**

```python
# skill-pack/tests/test_consent.py
from paiw_skill_pack.consent import validate_disclosure

BASE = {
    "consent_id": "consent-1",
    "owner_identity": "owner-1",
    "approved_at": "2026-07-15T10:00:00Z",
    "action": "send-email",
    "channel": "gmail",
    "recipients": ["recipient-1"],
    "purpose": "share approved update",
    "information_scope": ["release-summary"],
    "explicit_exclusions": ["private-notes"],
    "final_content_version": "sha256:abc",
    "attachments_and_permissions": ["guide.md:private-attachment"],
    "single_use": True,
    "status": "APPROVED"
}


def test_exact_approved_attempt_is_allowed_once() -> None:
    decision = validate_disclosure(BASE, {
        "action": "send-email", "channel": "gmail",
        "recipients": ["recipient-1"], "purpose": "share approved update",
        "information_scope": ["release-summary"],
        "final_content_version": "sha256:abc",
        "attachments_and_permissions": ["guide.md:private-attachment"]
    })
    assert decision.allowed is True


def test_recipient_change_is_rejected() -> None:
    attempt = {**BASE, "recipients": ["recipient-1", "recipient-2"]}
    decision = validate_disclosure(BASE, attempt)
    assert decision.allowed is False
    assert "recipients_changed" in decision.reasons


def test_executed_consent_cannot_be_reused() -> None:
    consent = {**BASE, "status": "EXECUTED"}
    decision = validate_disclosure(consent, BASE)
    assert decision.allowed is False
    assert "consent_not_active" in decision.reasons
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest skill-pack/tests/test_consent.py -v
```

Expected: import failure.

- [ ] **Step 3: Implement exact-match validation**

```python
# skill-pack/src/paiw_skill_pack/consent.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ConsentDecision:
    allowed: bool
    reasons: tuple[str, ...]


FIELDS = (
    "action", "channel", "recipients", "purpose", "information_scope",
    "final_content_version", "attachments_and_permissions"
)


def _normalized(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(value)
    return value


def validate_disclosure(consent: dict[str, Any], attempt: dict[str, Any]) -> ConsentDecision:
    reasons: list[str] = []
    if consent.get("status") != "APPROVED" or consent.get("single_use") is not True:
        reasons.append("consent_not_active")
    for field in FIELDS:
        if _normalized(consent.get(field)) != _normalized(attempt.get(field)):
            reasons.append(f"{field}_changed")
    return ConsentDecision(allowed=not reasons, reasons=tuple(reasons))
```

- [ ] **Step 4: Add attachment, reply-all, public-link and recurring-workflow cases**

Add tests rejecting:

```text
new attachment
reply → reply-all
private Drive permission → public link
approval from prior action reused by recurring automation
approval from another conversation with changed final version
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_consent.py -v
git add skill-pack/src/paiw_skill_pack/consent.py skill-pack/tests/test_consent.py skill-pack/tests/fixtures/consent
git commit -m "feat: validate exact single-use disclosure consent"
```

---

### Task 3: Integrate disclosure policy into Installer & Upgrader

**Files:**
- Modify: `skills/personal-ai-workspace-installer-upgrader/SKILL.md`
- Modify: `skills/personal-ai-workspace-installer-upgrader/references/discovery-and-classification.md`
- Modify: `skills/personal-ai-workspace-installer-upgrader/references/fresh-install.md`
- Modify: `skills/personal-ai-workspace-installer-upgrader/references/migration-and-repair.md`
- Modify: `skills/personal-ai-workspace-installer-upgrader/references/approval-and-readback.md`
- Modify: `skills/personal-ai-workspace-installer-upgrader/tests/test_skill_contract.py`
- Modify: installation fixtures and migration manifests

**Interfaces:**
- Installer reads the shared disclosure contract version.
- Discovery report exposes `external_disclosure_contract_version` and policy health.

- [ ] **Step 1: Add failing contract tests**

Require installer instructions to contain:

```text
owner-only by default
one-time consent
no standing consent
identity uncertainty fails closed
policy weakening is structural
missing policy is high-severity
```

- [ ] **Step 2: Add detection rules**

Extend installation signatures and classification:

```text
missing disclosure policy on current target version → PARTIAL or DAMAGED depending on contradictions
standing-consent rule present → DAMAGED security finding
newer incompatible contract version → INSTALLED_UNKNOWN read-only
```

- [ ] **Step 3: Add fresh-install blueprint behavior**

The blueprint must install the policy in:

```text
Constitution index
module 00
identity/privacy module
Relations module
Gmail module
Calendar/Contacts module
Drive/files module
Notion audit module
change-management module
Start Here
```

- [ ] **Step 4: Add migration rules**

Each supported migration preserves or strengthens the policy. Never convert historical generic permissions into executable consent events.

- [ ] **Step 5: Add tests and commit**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests -v
git add skills/personal-ai-workspace-installer-upgrader skill-pack/migrations
git commit -m "feat: enforce disclosure policy during install and upgrade"
```

---

### Task 4: Make Context Bootstrap owner-only

**Files:**
- Modify: `skills/personal-ai-workspace-context-bootstrap/SKILL.md`
- Modify: `skills/personal-ai-workspace-context-bootstrap/references/constitution-loading.md`
- Modify: `skills/personal-ai-workspace-context-bootstrap/references/sensitive-context.md`
- Modify: `skills/personal-ai-workspace-context-bootstrap/references/briefing-format.md`
- Modify: `skills/personal-ai-workspace-context-bootstrap/tests/test_skill_contract.py`
- Modify: `skills/personal-ai-workspace-context-bootstrap/tests/test_end_to_end.py`

**Interfaces:**
- Bootstrap produces a briefing only for the verified owner.
- Any shared/public destination requires a separate disclosure workflow and consent event.

- [ ] **Step 1: Add failing owner-only tests**

Test that the skill:

```text
stops on account mismatch
rejects "brief my colleague"
rejects shared/public destination without consent
allows owner-only briefing
uses minimum sensitive detail and canonical pointers
```

- [ ] **Step 2: Update instructions**

State explicitly:

```text
A briefing is an owner-only response. Do not send, post, attach, publish or share it to another recipient or channel from this skill. Route external sharing through an exact one-time consent workflow.
```

- [ ] **Step 3: Add end-to-end fixtures and commit**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests -v
git add skills/personal-ai-workspace-context-bootstrap
git commit -m "feat: make context briefing owner-only"
```

---

### Task 5: Extend public privacy scans and package validation

**Files:**
- Modify: `skill-pack/src/paiw_skill_pack/scanner.py`
- Modify: `skill-pack/tests/test_scanner.py`
- Modify: `skill-pack/src/paiw_skill_pack/validate.py`
- Modify: `skill-pack/tests/test_validate.py`

**Interfaces:**
- Scanner finds private Workspace identifiers and suspicious copied data.
- Validator requires the disclosure contract in each final skill.

- [ ] **Step 1: Add failing scanner tests**

Add unsafe fixtures containing:

```text
private Notion URL
private Drive ID
private task repository
real Gmail subject/body excerpt
private contact name/email
serialized connector response
```

- [ ] **Step 2: Extend scanner rules**

Return path, line, rule and redacted excerpt. Allow only documented public creator attribution and project contact.

- [ ] **Step 3: Require vendored disclosure contract**

`validate_skill_root()` must fail when `references/shared/contract/external-disclosure-consent.md` is missing or its contract version differs from compatibility metadata.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest skill-pack/tests/test_scanner.py skill-pack/tests/test_validate.py -v
git add skill-pack/src skill-pack/tests
git commit -m "test: block private Workspace disclosure in public packages"
```

---

### Task 6: Update creator, public documentation and Codex guidance

**Files:**
- Modify next-version creator source under `source/creator/`
- Modify: `INSTALLATION.md`
- Modify: public Skill Pack documentation and GitHub Pages content
- Create: `skill-pack/templates/AGENTS.personal-ai-workspace.md`
- Create: `skill-pack/tests/test_agents_template.py`

**Interfaces:**
- Creator installs the policy into new Workspaces.
- AGENTS snippet protects local code, commits, issues, PRs and logs.

- [ ] **Step 1: Write failing documentation tests**

Require exact concepts:

```text
owner-only by default
one-time approval
exact recipient and information scope
no standing consent
local repository access does not authorize publication
```

- [ ] **Step 2: Add the Codex template**

```markdown
## Personal AI Workspace confidentiality

Workspace information is for the verified owner only by default. Do not place it in source files, logs, commits, issues, pull requests, comments, public artifacts or third-party messages without fresh one-time owner approval for the exact recipients, channel, information scope and final content version. Prior approval never becomes standing consent.
```

- [ ] **Step 3: Update the creator**

The creator must install and test the disclosure rule, including one-time consent and no standing permissions.

- [ ] **Step 4: Run docs tests and commit**

```bash
python -m pytest skill-pack/tests/test_agents_template.py skill-pack/tests/test_documentation.py -v
git add source skill-pack/templates docs INSTALLATION.md
git commit -m "docs: add one-time disclosure controls"
```

---

### Task 7: Add release-gate coverage

**Files:**
- Modify: release security audit
- Modify: prerelease workflow
- Modify: compatibility report schema and example
- Modify: pilot report template

**Interfaces:**
- Release candidate cannot pass without disclosure-contract evidence.

- [ ] **Step 1: Add failing release-gate tests**

Require:

```text
contract version matches
both skills vendor contract
creator contains policy
Codex template contains policy
all one-time-consent tests pass
public privacy scan clean
```

- [ ] **Step 2: Add pilot scenarios**

Pilot report records:

```text
owner-only briefing
approved one-time email/share
second-use rejection
recipient-change rejection
public-link rejection
account-mismatch stop
```

- [ ] **Step 3: Run the full suite**

```bash
python -m pytest -v
python skill-pack/scripts/validate_skill_pack.py
python skill-pack/scripts/scan_private_identifiers.py skills
```

Expected: all tests pass and scanner reports `public-safe`.

- [ ] **Step 4: Commit**

```bash
git add .github skill-pack docs
 git commit -m "ci: gate releases on one-time disclosure policy"
```

---

## Completion checklist

- [ ] Shared contract and schema exist and are versioned.
- [ ] Installer detects, installs, preserves and migrates the policy.
- [ ] Context Bootstrap is owner-only.
- [ ] Public packages contain no private Workspace data.
- [ ] Creator and Codex guidance contain the rule.
- [ ] No standing consent can authorize an action.
- [ ] Release gate and pilot evidence cover the policy.
- [ ] Private adapter implementation is completed under its separate plan.
