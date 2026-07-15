# Private Emma Workspace Adapter v6.0.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the private `emma-workspace-memory` skill from v5.5.0 to a thin v6.0.0 adapter that composes the public Personal AI Workspace Skill Pack with Michał's private identities, source map, Constitution, task backend and one-time disclosure controls.

**Architecture:** Public skills own generic installer/upgrade and context-bootstrap logic. The private adapter contains only private configuration, Emma-specific policy, compatibility checks, routing and verified references. It fails closed when public skill or disclosure-contract versions are missing or incompatible and never copies private values into public packages.

**Tech Stack:** Agent Skills, Markdown, YAML, Python 3.11+, pytest, deterministic ZIP packaging, SHA-256, Codex user-global installation under `$HOME/.agents/skills`.

## Global Constraints

- Public skills and private adapter remain separate packages and repositories/archives.
- v6.0.0 depends on the approved public Skill Pack compatibility contract.
- One-time external disclosure consent is mandatory across every connector and generated artifact.
- No information from the private Workspace may enter public skill sources, fixtures, logs, issues, PRs, release artifacts or test output.
- The adapter must preserve private Notion IDs, Drive folders and Apex configuration only inside private package scope.
- Migration from v5.5.0 requires exact-scope owner approval, backup, verification and rollback.
- No prerelease publication or live migration occurs merely by merging this plan.
- Every task follows TDD and ends with a focused commit.

---

### Task 1: Define adapter compatibility and private manifest boundaries

**Files:**
- Create: `private/emma-workspace-memory-v6/SKILL.md`
- Create: `private/emma-workspace-memory-v6/agents/openai.yaml`
- Create: `private/emma-workspace-memory-v6/references/private-workspace-manifest.example.md`
- Create: `private/emma-workspace-memory-v6/references/public-skill-compatibility.json`
- Create: `private/emma-workspace-memory-v6/tests/test_adapter_contract.py`

**Interfaces:**
- Adapter requires public skills `personal-ai-workspace-installer-upgrader` and `personal-ai-workspace-context-bootstrap`.
- Compatibility fields: public Skill Pack version, shared contract version and disclosure contract version.

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_adapter_requires_public_skills_and_disclosure_contract() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for value in [
        "personal-ai-workspace-installer-upgrader",
        "personal-ai-workspace-context-bootstrap",
        "external disclosure contract",
        "fail closed",
    ]:
        assert value in text.lower()


def test_compatibility_manifest_is_explicit() -> None:
    payload = json.loads((ROOT / "references/public-skill-compatibility.json").read_text())
    assert payload["minimum_skill_pack_version"] == "0.1.0-beta.1"
    assert payload["external_disclosure_contract_version"] == "1.0.0"
```

- [ ] **Step 2: Run and observe failure**

```bash
python -m pytest private/emma-workspace-memory-v6/tests/test_adapter_contract.py -v
```

- [ ] **Step 3: Create the adapter entry files**

`SKILL.md` must:

```text
load private manifest
verify public skill compatibility
route install/upgrade explicitly to installer-upgrader
load context through context-bootstrap
apply Emma-specific private policies
fail closed on missing disclosure contract
never copy private data into public outputs
```

Use:

```yaml
policy:
  allow_implicit_invocation: true
```

The adapter itself may activate implicitly for Michał's Workspace, while structural installer operations remain explicitly invoked through the public installer skill.

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest private/emma-workspace-memory-v6/tests/test_adapter_contract.py -v
git add private/emma-workspace-memory-v6
git commit -m "feat: scaffold private Emma Workspace adapter v6"
```

---

### Task 2: Add private manifest loading and validation

**Files:**
- Create: `private/emma-workspace-memory-v6/scripts/load_private_manifest.py`
- Create: `private/emma-workspace-memory-v6/references/private-manifest.schema.json`
- Create: `private/emma-workspace-memory-v6/tests/test_private_manifest.py`
- Create private deployment manifest outside the public repository or in an encrypted/private artifact workflow.

**Interfaces:**
- `load_private_manifest(path) -> PrivateManifest`
- Manifest includes expected account identities, Constitution URL, Start Here URL, module registry, Drive folders, task repository, public skill versions and private policy flags.

- [ ] **Step 1: Write failing schema and loader tests**

Test required fields without using real values in repository fixtures:

```text
owner_identity
expected_notion_identity
expected_google_identity
constitution_url
start_here_url
private_task_repository
drive_folders
public_skill_pack_version
external_disclosure_contract_version
```

- [ ] **Step 2: Implement typed validation**

Reject:

```text
missing identity
invalid URL
unsupported public skill version
missing disclosure contract
public repository used as private task backend without explicit configuration
```

- [ ] **Step 3: Add private-data boundary test**

The public repository scanner must reject any committed file containing the real private manifest. The private build process accepts the manifest only from an external path supplied at build time.

- [ ] **Step 4: Run tests and commit public-safe loader code**

```bash
python -m pytest private/emma-workspace-memory-v6/tests/test_private_manifest.py -v
git add private/emma-workspace-memory-v6/scripts private/emma-workspace-memory-v6/references/private-manifest.schema.json private/emma-workspace-memory-v6/tests
git commit -m "feat: validate private Emma adapter manifest"
```

---

### Task 3: Enforce one-time disclosure across private connector routing

**Files:**
- Create: `private/emma-workspace-memory-v6/references/external-disclosure-routing.md`
- Create: `private/emma-workspace-memory-v6/scripts/validate_private_disclosure.py`
- Create: `private/emma-workspace-memory-v6/tests/test_private_disclosure.py`

**Interfaces:**
- Reuse the public consent schema and exact-match validator.
- Private routing maps Gmail, Calendar, Contacts, Drive, GitHub, Notion share actions and generated artifacts to disclosure events.

- [ ] **Step 1: Write failing routing tests**

Cover:

```text
email send
reply-all
Calendar invite
contact export
public Drive link
GitHub issue/comment/PR
shared Notion page
generated report sent to third party
recurring automation
```

Every external action requires fresh single-use approval. Owner-only storage and owner-only briefing remain allowed.

- [ ] **Step 2: Implement channel mapping**

Return a canonical attempt containing:

```text
action
channel
recipients
purpose
information_scope
final_content_version
attachments_and_permissions
```

- [ ] **Step 3: Add fail-closed identity behavior**

Reject when:

```text
owner identity mismatch
recipient unresolved
shared-link visibility unknown
content version missing
consent already executed
```

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest private/emma-workspace-memory-v6/tests/test_private_disclosure.py -v
git add private/emma-workspace-memory-v6
git commit -m "feat: enforce one-time disclosure in private adapter"
```

---

### Task 4: Compose public Context Bootstrap with private Workspace routing

**Files:**
- Create: `private/emma-workspace-memory-v6/references/context-routing.md`
- Create: `private/emma-workspace-memory-v6/tests/test_context_routing.py`
- Modify: `private/emma-workspace-memory-v6/SKILL.md`

**Interfaces:**
- Adapter invokes the public bootstrap contract using private Constitution and source map.
- Briefing destination is the verified owner conversation only.

- [ ] **Step 1: Add failing routing tests**

Require:

```text
Constitution index + Start Here + module 00
private Feature Registry
Task Outbox + GitHub task status
active projects, commitments, reviews and risks
owner-only destination
partial coverage reporting
```

- [ ] **Step 2: Add routing instructions**

Do not duplicate public normalization logic. The private adapter supplies configuration and required source locations, then defers to the public context-bootstrap skill.

- [ ] **Step 3: Run and commit**

```bash
python -m pytest private/emma-workspace-memory-v6/tests/test_context_routing.py -v
git add private/emma-workspace-memory-v6
git commit -m "feat: compose public bootstrap with Emma private context"
```

---

### Task 5: Add v5.5.0 → v6.0.0 migration and rollback

**Files:**
- Create: `private/emma-workspace-memory-v6/migrations/5.5.0-to-6.0.0/migration.json`
- Create: `private/emma-workspace-memory-v6/migrations/5.5.0-to-6.0.0/preconditions.md`
- Create: `private/emma-workspace-memory-v6/migrations/5.5.0-to-6.0.0/operations.md`
- Create: `private/emma-workspace-memory-v6/migrations/5.5.0-to-6.0.0/validation.md`
- Create: `private/emma-workspace-memory-v6/migrations/5.5.0-to-6.0.0/rollback.md`
- Create: `private/emma-workspace-memory-v6/tests/test_migration.py`

**Interfaces:**
- Migration transforms the private skill package, not live Notion data unless separately approved.
- Live Constitution compatibility is validated but live structure changes remain separately gated.

- [ ] **Step 1: Write failing migration tests**

Test:

```text
backup v5.5.0 package
public skills installed or explicitly blocked
private manifest externalized
v6 adapter installed
AGENTS section previewed
compatibility verified
rollback restores v5.5.0
```

- [ ] **Step 2: Define migration operations**

```text
archive v5.5.0 package
install two public skills user-globally
install private adapter
write private manifest outside public source
merge approved AGENTS.md section after backup
run verification
create handover artifact
```

- [ ] **Step 3: Define rollback**

Rollback removes v6 adapter, restores v5.5.0 and restores the prior AGENTS.md backup. It does not delete public skills unless the user approves that separate action.

- [ ] **Step 4: Run and commit**

```bash
python -m pytest private/emma-workspace-memory-v6/tests/test_migration.py -v
git add private/emma-workspace-memory-v6/migrations private/emma-workspace-memory-v6/tests/test_migration.py
git commit -m "feat: add Emma adapter v6 migration and rollback"
```

---

### Task 6: Build, scan and package the private adapter

**Files:**
- Create: private build script outside public release workflow
- Create: `private/emma-workspace-memory-v6/tests/test_packaging.py`
- Create private release notes and verification report templates

**Interfaces:**
- Produces dated private ZIP, instruction Markdown and SHA-256 manifest.
- Public GitHub release workflow must never upload these files.

- [ ] **Step 1: Add packaging tests**

Verify:

```text
private manifest included only in private artifact
public package scanner would reject private artifact
private package contains disclosure contract version
ZIP is valid
checksum matches
no credentials or authentication secrets
```

- [ ] **Step 2: Build private artifacts**

Naming:

```text
DD.MM.YYYY Emma Workspace Memory - global Codex skill v6.0.0.zip
DD.MM.YYYY Emma Workspace - working instructions v6.0.0.md
DD.MM.YYYY Emma Workspace Memory v6.0.0 SHA-256.txt
```

- [ ] **Step 3: Verify Drive archive policy**

Upload the exact final artifacts to the configured private `Skill Packages` folder when capability is available. Verify file IDs, names, parents, URLs and checksums. If binary upload fails, mark the handover incomplete and do not claim Drive archival.

- [ ] **Step 4: Commit only public-safe templates and code**

Do not commit the built private ZIP or real manifest to the public repository.

---

### Task 7: Private installation verification and handover

**Files:**
- Create private verification checklist and report outside public source
- Update private Task Outbox and System Evolution Lab only after explicit live-migration approval

**Interfaces:**
- Verification covers Codex user-global discovery and owner-only disclosure behavior.

- [ ] **Step 1: Verify skills**

```text
public installer skill visible
public bootstrap skill visible
private Emma adapter visible
explicit installer invocation works
implicit bootstrap route works
private adapter loads correct manifest
```

- [ ] **Step 2: Verify disclosure boundary**

Run safe tests:

```text
owner-only briefing succeeds
unapproved third-party share is blocked
approved exact test disclosure succeeds once
second use is blocked
recipient change is blocked
public-link change is blocked
```

Do not send real private data during verification; use synthetic Confidential records in a disposable private test area.

- [ ] **Step 3: Produce handover**

Handover includes installed versions, compatibility hashes, backup/rollback locations, Drive archive status and known limitations.

- [ ] **Step 4: Record implementation result**

Only after separate approval to migrate the live environment, update private Task Outbox and System Evolution Lab with readback.

---

## Completion checklist

- [ ] Private adapter v6 is thin and composes public skills.
- [ ] Real private manifest never enters public source or releases.
- [ ] Disclosure contract is enforced across all private channels.
- [ ] Migration and rollback from v5.5.0 are tested.
- [ ] Codex global installation is verified.
- [ ] Final private artifacts are checksum-verified and Drive-archived or visibly incomplete.
- [ ] No live migration occurs without a later exact-scope approval.
