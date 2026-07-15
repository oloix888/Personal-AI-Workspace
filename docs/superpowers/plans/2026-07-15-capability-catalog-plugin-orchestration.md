# Capability Catalog and Plugin Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a provider-neutral Capability Catalog, goal-based capability packs, surface-aware routing, activation policies, and progressive skill/plugin loading to Personal AI Workspace.

**Architecture:** Keep the public catalog and schemas under `skill-pack/capabilities` and `skills/_shared`. The Installer & Upgrader owns detection, goal-based selection, migration, and exact-scope approval. Context Bootstrap owns the compact startup manifest and minimal task-relevant resolution. Installed third-party skills retain their native invocation rules; Personal AI Workspace orchestrates rather than reimplements them.

**Tech Stack:** Python 3.11+, JSON Schema Draft 2020-12, YAML, pytest, Agent Skills Markdown, GitHub Actions, public Markdown creator.

## Global Constraints

- Notion is the only mandatory external connector.
- All other capabilities are optional, owner-controlled, and provider-neutral.
- Never load every full skill or plugin instruction set at startup.
- Full instructions load only for capabilities that are configured, enabled, available on the current surface, relevant, and permitted by activation policy.
- Preserve `CORE_BOOTSTRAP`, `ON_DEMAND_IMPLICIT`, `EXPLICIT_ONLY`, `EXPLICIT_WITH_CONFIRMATION`, and `DISABLED` exactly.
- Preserve `Enabled`, `Disabled by User`, `Unavailable`, `Pending Setup`, `Paused`, and `Degraded` exactly.
- Preserve plugin-native gates, including explicit-only artifact routers and Data Analytics Work Mode behavior.
- Never invent connector write capabilities.
- Never silently change selected provider or enable a disabled capability during upgrade.
- Public packages contain no private Emma Workspace identifiers, private accounts, contacts, Gmail content, or `oloix888/Apex` runtime references.
- Financial trading, deployment, publication, communication, access grants, paid compute, and sensitive-data cloud uploads retain their existing action confirmations.
- Every task follows TDD and ends with a focused commit.
- This plan does not authorize prerelease publication.

---

## File Map

```text
skill-pack/capabilities/
├── catalog.yaml
├── packs.yaml
└── README.md
skills/_shared/
├── contract/
│   ├── capability-catalog.md
│   └── capability-resolution.md
└── schemas/
    ├── capability-catalog.schema.json
    ├── capability-packs.schema.json
    └── feature-registry.schema.json        # extend
skill-pack/src/paiw_skill_pack/
├── capabilities.py
└── pack_recommendation.py
skill-pack/tests/
├── fixtures/capabilities/
│   ├── valid-catalog.yaml
│   ├── invalid-duplicate-key.yaml
│   ├── runtime-web.json
│   ├── runtime-codex.json
│   └── user-goals.json
├── test_capability_catalog.py
├── test_capability_resolution.py
└── test_pack_recommendation.py
skills/personal-ai-workspace-installer-upgrader/
├── references/capability-catalog-and-packs.md
├── scripts/recommend_capabilities.py
├── scripts/render_capability_blueprint.py
└── tests/
    ├── test_capability_blueprint.py
    └── test_capability_migration.py
skills/personal-ai-workspace-context-bootstrap/
├── references/capability-resolution.md
├── scripts/resolve_capabilities.py
└── tests/
    ├── test_capability_resolution.py
    └── test_capability_budget.py
skill-pack/migrations/1.5.1-to-1.6.0/
├── migration.json
├── operations.md
├── validation.md
└── rollback.md
docs/
├── CAPABILITIES.md
└── INSTALLATION.md                         # update
```

---

### Task 1: Define the machine-readable catalog contract

**Files:**
- Create: `skills/_shared/schemas/capability-catalog.schema.json`
- Create: `skills/_shared/schemas/capability-packs.schema.json`
- Extend: `skills/_shared/schemas/feature-registry.schema.json`
- Create: `skills/_shared/contract/capability-catalog.md`
- Create: `skills/_shared/contract/capability-resolution.md`
- Test: `skill-pack/tests/test_capability_catalog.py`

**Interfaces:**
- Produces JSON Schemas consumed by local validators and both public skills.
- Produces exact enum values used in every later task.

- [ ] **Step 1: Write failing schema tests**

```python
# skill-pack/tests/test_capability_catalog.py
from pathlib import Path
import yaml
import pytest
from jsonschema import ValidationError

from paiw_skill_pack.schemas import validate_payload

ROOT = Path(__file__).resolve().parents[2]


def test_public_catalog_matches_schema() -> None:
    payload = yaml.safe_load(
        (ROOT / "skill-pack/capabilities/catalog.yaml").read_text(encoding="utf-8")
    )
    validate_payload("capability-catalog.schema.json", payload)


def test_duplicate_capability_keys_are_rejected() -> None:
    payload = {
        "catalog_version": "1.0.0",
        "capabilities": [
            _capability("plugin.linkedin"),
            _capability("plugin.linkedin"),
        ],
    }
    with pytest.raises(ValueError, match="duplicate capability key"):
        from paiw_skill_pack.capabilities import validate_catalog_semantics
        validate_catalog_semantics(payload)


def test_invalid_activation_policy_is_rejected() -> None:
    payload = _capability("example")
    payload["activation_policy"] = "AUTOMAGIC"
    with pytest.raises(ValidationError):
        validate_payload(
            "capability-catalog.schema.json",
            {"catalog_version": "1.0.0", "capabilities": [payload]},
        )


def _capability(key: str) -> dict:
    return {
        "key": key,
        "display_name": "Example",
        "kind": "Data Source",
        "default_state": "Pending Setup",
        "activation_policy": "EXPLICIT_ONLY",
        "surface_availability": ["ChatGPT Web"],
        "risk_tier": "Low",
        "provider_role": "example_source",
        "default_provider": "Example",
        "skill_or_plugin_reference": "example/plugin",
        "required_capabilities": ["example.read"],
        "account_required": False,
        "dependencies": [],
        "read_scope": "Bounded example data",
        "write_scope": "None",
        "external_disclosure_behavior": "Owner-only",
        "output_destination": "Chat",
        "persistence_policy": "Store source-backed durable decisions only.",
        "health_probe": "Bounded read",
        "missed_sync_behavior": "Report unavailable",
        "recommended_packs": [],
        "version": "1.0",
    }
```

- [ ] **Step 2: Run and verify RED**

```bash
python -m pytest skill-pack/tests/test_capability_catalog.py -v
```

Expected: failures because schemas, catalog, and semantic validator do not exist.

- [ ] **Step 3: Create the catalog schema**

Implement Draft 2020-12 schemas with `additionalProperties: false`. Use these exact enums:

```json
{
  "kind": ["Core System", "Data Source", "Domain Workflow", "Artifact Output", "Action System", "Developer System", "Creative System"],
  "state": ["Enabled", "Disabled by User", "Unavailable", "Pending Setup", "Paused", "Degraded"],
  "activation_policy": ["CORE_BOOTSTRAP", "ON_DEMAND_IMPLICIT", "EXPLICIT_ONLY", "EXPLICIT_WITH_CONFIRMATION", "DISABLED"],
  "surface": ["ChatGPT Web", "Work Mode", "ChatGPT Desktop", "Codex CLI", "Codex Desktop", "API"],
  "risk": ["Low", "Moderate", "High", "Critical"]
}
```

The feature-registry schema must add:

```text
capability_kind
activation_policy
surface_availability
risk_tier
skill_or_plugin_reference
selected_provider
output_destination
capability_packs
health_probe
persistence_policy
```

- [ ] **Step 4: Write shared contracts**

`capability-catalog.md` states:

- Notion is the only mandatory external connector.
- Installed is not equivalent to enabled, authorized, healthy, or available.
- Provider selection is explicit.
- Disabled history is retained.

`capability-resolution.md` defines manifest-first progressive loading and the exact activation behavior.

- [ ] **Step 5: Rerun tests**

```bash
python -m pytest skill-pack/tests/test_capability_catalog.py -v
```

Expected: schema-valid tests pass; duplicate test remains failing until Task 2.

- [ ] **Step 6: Commit**

```bash
git add skills/_shared skill-pack/tests/test_capability_catalog.py
git commit -m "feat: define capability catalog contracts"
```

---

### Task 2: Implement catalog loading and semantic validation

**Files:**
- Create: `skill-pack/src/paiw_skill_pack/capabilities.py`
- Create: `skill-pack/capabilities/catalog.yaml`
- Create: `skill-pack/capabilities/README.md`
- Extend: `skill-pack/tests/test_capability_catalog.py`

**Interfaces:**

```python
load_catalog(path: Path) -> CapabilityCatalog
validate_catalog_semantics(payload: dict) -> None
compact_manifest(catalog, configured, surface) -> list[dict]
```

- [ ] **Step 1: Add failing model tests**

```python
from paiw_skill_pack.capabilities import load_catalog, compact_manifest


def test_compact_manifest_excludes_full_instruction_bodies() -> None:
    catalog = load_catalog(ROOT / "skill-pack/capabilities/catalog.yaml")
    manifest = compact_manifest(
        catalog,
        configured={"plugin.linkedin": {"state": "Enabled"}},
        surface="ChatGPT Web",
    )
    item = next(row for row in manifest if row["key"] == "plugin.linkedin")
    assert set(item) == {
        "key", "display_name", "state", "activation_policy", "surface_supported",
        "risk_tier", "selected_provider", "health", "skill_or_plugin_reference",
    }
    assert "instructions" not in item
```

- [ ] **Step 2: Run and verify RED**

```bash
python -m pytest skill-pack/tests/test_capability_catalog.py -v
```

- [ ] **Step 3: Implement immutable models and validation**

Use `dataclass(frozen=True, slots=True)` for `Capability` and `CapabilityCatalog`. Reject:

- duplicate keys;
- `CORE_BOOTSTRAP` on non-core capabilities;
- `DISABLED` activation with default state `Enabled`;
- `Critical` action capability with implicit activation;
- provider role without a default or selectable provider declaration;
- missing Notion core capability;
- any other capability marked mandatory external connector.

- [ ] **Step 4: Create public catalog entries**

At minimum include:

```text
workspace.notion-core
workspace.constitution
workspace.context-bootstrap
workspace.autonomous-memory-capture
plugin.linkedin
plugin.linkedin-ads
plugin.sales
plugin.data-analytics
artifact.document
artifact.pdf
artifact.spreadsheet
artifact.presentation
plugin.creative-production
plugin.adobe
plugin.meetup
plugin.spotify
plugin.apple-music
plugin.hugging-face
plugin.openai-developers
plugin.build-web-apps
plugin.product-design
plugin.render
plugin.booking
plugin.public-equity-investing
plugin.investment-banking
plugin.life-science-research
plugin.ngs-analysis
plugin.revolut-x.read
plugin.revolut-x.alerts
plugin.revolut-x.trading
```

Use fictional/public-safe provider examples only. The public catalog must not include private account names, Notion IDs, folder IDs, contacts, or private repository names.

- [ ] **Step 5: Rerun tests and scanner**

```bash
python -m pytest skill-pack/tests/test_capability_catalog.py -v
python skill-pack/scripts/scan_private_identifiers.py skill-pack/capabilities
```

Expected: all pass and `public-safe`.

- [ ] **Step 6: Commit**

```bash
git add skill-pack/src/paiw_skill_pack/capabilities.py skill-pack/capabilities skill-pack/tests/test_capability_catalog.py
git commit -m "feat: add public capability catalog"
```

---

### Task 3: Define goal-based capability packs

**Files:**
- Create: `skill-pack/capabilities/packs.yaml`
- Create: `skill-pack/src/paiw_skill_pack/pack_recommendation.py`
- Create: `skill-pack/tests/test_pack_recommendation.py`

**Interfaces:**

```python
recommend_packs(goals: set[str]) -> list[PackRecommendation]
resolve_pack_capabilities(pack_keys, catalog) -> list[str]
```

- [ ] **Step 1: Write failing recommendation tests**

```python
from paiw_skill_pack.pack_recommendation import recommend_packs


def test_business_goals_recommend_business_growth_without_financial_trading() -> None:
    recs = recommend_packs({"business", "sales", "marketing"})
    keys = [item.key for item in recs]
    assert "business-growth" in keys
    capabilities = {key for item in recs for key in item.capabilities}
    assert "plugin.sales" in capabilities
    assert "plugin.linkedin" in capabilities
    assert "plugin.revolut-x.trading" not in capabilities


def test_notion_core_is_always_present() -> None:
    recs = recommend_packs(set())
    core = next(item for item in recs if item.key == "core-workspace")
    assert "workspace.notion-core" in core.capabilities
```

- [ ] **Step 2: Implement pack data and recommendation logic**

Use the exact nine packs from the design. Recommendations return:

```python
@dataclass(frozen=True, slots=True)
class PackRecommendation:
    key: str
    reason: str
    capabilities: tuple[str, ...]
    recommended: bool
```

The recommender never enables capabilities. It prepares a blueprint for user review.

- [ ] **Step 3: Test**

```bash
python -m pytest skill-pack/tests/test_pack_recommendation.py -v
```

- [ ] **Step 4: Commit**

```bash
git add skill-pack/capabilities/packs.yaml skill-pack/src/paiw_skill_pack/pack_recommendation.py skill-pack/tests/test_pack_recommendation.py
git commit -m "feat: add goal-based capability packs"
```

---

### Task 4: Add surface-aware capability resolution

**Files:**
- Extend: `skill-pack/src/paiw_skill_pack/capabilities.py`
- Create: `skill-pack/tests/test_capability_resolution.py`
- Create fixtures under `skill-pack/tests/fixtures/capabilities/`

**Interfaces:**

```python
resolve_for_request(
    manifest: list[dict],
    request_intents: set[str],
    surface: str,
    explicit_mentions: set[str],
) -> ResolutionResult
```

`ResolutionResult` contains:

```text
selected
requires_explicit_invocation
requires_action_confirmation
unavailable
surface_mismatches
state_conflicts
```

- [ ] **Step 1: Write failing routing tests**

Cover:

- LinkedIn selected implicitly for professional-person research.
- Investment Banking not selected while disabled.
- PDF not selected without explicit `@pdf`.
- Data Analytics selected but carries the Work Mode gate on ChatGPT Web Chat.
- Build Web Apps produces surface mismatch on unsupported ChatGPT Web context.
- Revolut Trading cannot be implicit, even if mistakenly configured `Enabled`.
- unrelated enabled skills are not selected.

- [ ] **Step 2: Implement deterministic resolution**

Rules execute in this order:

1. state;
2. surface;
3. intent relevance;
4. activation policy;
5. native plugin gate metadata;
6. risk floor.

Never turn a catalog entry into proof that a tool is callable. Resolution returns a candidate; runtime health confirmation occurs later.

- [ ] **Step 3: Test**

```bash
python -m pytest skill-pack/tests/test_capability_resolution.py -v
```

- [ ] **Step 4: Commit**

```bash
git add skill-pack/src/paiw_skill_pack/capabilities.py skill-pack/tests/test_capability_resolution.py skill-pack/tests/fixtures/capabilities
git commit -m "feat: resolve capabilities by state surface and activation"
```

---

### Task 5: Extend Installer & Upgrader with pack selection and migration

**Files:**
- Create: `skills/personal-ai-workspace-installer-upgrader/references/capability-catalog-and-packs.md`
- Create: `skills/personal-ai-workspace-installer-upgrader/scripts/recommend_capabilities.py`
- Create: `skills/personal-ai-workspace-installer-upgrader/scripts/render_capability_blueprint.py`
- Extend: `skills/personal-ai-workspace-installer-upgrader/SKILL.md`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_capability_blueprint.py`
- Create: `skills/personal-ai-workspace-installer-upgrader/tests/test_capability_migration.py`
- Create migration files: `skill-pack/migrations/1.5.1-to-1.6.0/`

**Interfaces:**

```python
render_capability_blueprint(current, recommendations, decisions) -> str
migrate_registry(current_records, target_catalog) -> MigrationPlan
```

- [ ] **Step 1: Write failing blueprint tests**

Verify the preview includes:

- selected goals and packs;
- exact capability states;
- activation policy;
- supported surfaces;
- risk tier;
- selected provider;
- account/setup needs;
- data preservation;
- structural operations;
- rollback.

- [ ] **Step 2: Write failing migration tests**

Verify:

- `Disabled by User` stays disabled;
- provider choice is preserved;
- existing history is retained;
- repeated migration produces no duplicate feature keys;
- Notion core is repaired if missing;
- Drive disabled by user is not marked upload failure;
- old installations without the catalog are classified for migration rather than fresh-install duplication.

- [ ] **Step 3: Implement the scripts and reference workflow**

The installer must ask goal-based questions, show recommendations, let the user edit every optional choice, and obtain exact-scope approval before adding the schema or records.

- [ ] **Step 4: Add migration manifest**

`migration.json` includes:

```json
{
  "id": "1.5.1-to-1.6.0",
  "from": "1.5.1",
  "to": "1.6.0",
  "destructive": false,
  "requires": ["notion.content.read", "notion.content.write"],
  "preconditions": ["complete truncation-safe Constitution read", "owner-approved capability blueprint"],
  "operations": [
    "extend Feature Registry schema",
    "create Capability Catalog page",
    "upsert catalog records by stable feature key",
    "update Constitution and Context Bootstrap contracts"
  ],
  "validations": [
    "no duplicate feature keys",
    "configured providers preserved",
    "disabled capabilities remain disabled",
    "complete readback"
  ],
  "rollback": "restore previous properties and archive new catalog records without deleting historical data"
}
```

- [ ] **Step 5: Test**

```bash
python -m pytest skills/personal-ai-workspace-installer-upgrader/tests/test_capability_blueprint.py skills/personal-ai-workspace-installer-upgrader/tests/test_capability_migration.py -v
```

- [ ] **Step 6: Commit**

```bash
git add skills/personal-ai-workspace-installer-upgrader skill-pack/migrations/1.5.1-to-1.6.0
git commit -m "feat: add capability-aware installation and migration"
```

---

### Task 6: Extend Context Bootstrap with progressive capability loading

**Files:**
- Create: `skills/personal-ai-workspace-context-bootstrap/references/capability-resolution.md`
- Create: `skills/personal-ai-workspace-context-bootstrap/scripts/resolve_capabilities.py`
- Extend: `skills/personal-ai-workspace-context-bootstrap/SKILL.md`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_capability_resolution.py`
- Create: `skills/personal-ai-workspace-context-bootstrap/tests/test_capability_budget.py`

- [ ] **Step 1: Write failing bootstrap tests**

Verify:

- compact manifest includes all configured capability keys;
- no full instruction bodies are embedded;
- only selected skill references are returned for loading;
- disabled/unavailable items appear only when materially relevant;
- 100 configured capabilities remain under a fixed manifest budget;
- surface and provider conflicts are reported;
- active task completeness is unaffected.

- [ ] **Step 2: Implement the resolver wrapper**

The script accepts:

```json
{
  "surface": "ChatGPT Web",
  "mode": "chat",
  "request_intents": ["sales", "professional-person"],
  "explicit_mentions": [],
  "configured_capabilities": []
}
```

It returns selected references plus compact status, never connector credentials or full instructions.

- [ ] **Step 3: Update briefing reference**

Document:

- compact startup manifest;
- minimal selected skill set;
- runtime health check;
- no silent provider fallback;
- native explicit-selection gates;
- interaction with task index mode and Autonomous Memory Capture.

- [ ] **Step 4: Test**

```bash
python -m pytest skills/personal-ai-workspace-context-bootstrap/tests/test_capability_resolution.py skills/personal-ai-workspace-context-bootstrap/tests/test_capability_budget.py -v
```

- [ ] **Step 5: Commit**

```bash
git add skills/personal-ai-workspace-context-bootstrap
git commit -m "feat: add progressive capability loading to bootstrap"
```

---

### Task 7: Add plugin-specific contract tests

**Files:**
- Create: `skill-pack/tests/test_plugin_contracts.py`
- Add public-safe fixture entries under `skill-pack/tests/fixtures/capabilities/`

- [ ] **Step 1: Write the contract matrix**

Tests must assert:

- LinkedIn is read-only professional search.
- LinkedIn Ads defaults to analytics/read and requires account setup.
- Sales may route implicitly only for clear seller intent.
- Data Analytics preserves its Work Mode/Chat-mode contract metadata.
- Document/PDF/Spreadsheet/Presentation are explicit-only.
- Creative Production and Adobe require the appropriate brief/source gate.
- Meetup cannot claim RSVP.
- Spotify playlist writes require explicit intent and no silent Apple Music fallback.
- Hugging Face Jobs/Endpoints/uploads are explicit and High risk.
- Render is confirmation-gated.
- Public Equity is research-only, not trade execution.
- Investment Banking, Life Science Research, NGS, and all Revolut X capabilities default disabled.
- NGS stores no sequence data by default.
- Revolut Trading is Critical and can never use implicit activation.

- [ ] **Step 2: Run tests and fix catalog mismatches**

```bash
python -m pytest skill-pack/tests/test_plugin_contracts.py -v
```

- [ ] **Step 3: Commit**

```bash
git add skill-pack/tests/test_plugin_contracts.py skill-pack/tests/fixtures/capabilities skill-pack/capabilities/catalog.yaml
git commit -m "test: enforce plugin orchestration contracts"
```

---

### Task 8: Update creator, documentation, packaging, and private-adapter contract

**Files:**
- Update the public Markdown creator source used to build the next framework release.
- Create: `docs/CAPABILITIES.md`
- Update: `docs/INSTALLATION.md` or `INSTALLATION.md`
- Update: `README.md`
- Update private-adapter plan/spec references without adding private values to public source.
- Extend: `.github/workflows/validate-skill-pack.yml`

- [ ] **Step 1: Add creator tests**

Verify the creator:

- states Notion is mandatory and all others optional;
- asks goal-based pack questions;
- shows provider and risk choices;
- installs progressive loading instructions;
- does not enable disabled capabilities during upgrade;
- preserves explicit artifact invocation rules;
- generates Personalization/project text that loads manifest first.

- [ ] **Step 2: Write user documentation**

`docs/CAPABILITIES.md` explains:

- states vs activation policies;
- capability kinds;
- surfaces;
- packs;
- provider choice;
- enabling/disabling;
- health and degraded states;
- why full instructions are not all loaded at startup.

- [ ] **Step 3: Extend CI**

CI validates:

```bash
python -m pytest skill-pack/tests/test_capability_catalog.py skill-pack/tests/test_capability_resolution.py skill-pack/tests/test_pack_recommendation.py skill-pack/tests/test_plugin_contracts.py -v
python skill-pack/scripts/validate_skill_pack.py
python skill-pack/scripts/scan_private_identifiers.py skill-pack/capabilities skills
```

- [ ] **Step 4: Commit**

```bash
git add README.md docs skill-pack .github skills
git commit -m "docs: publish capability catalog and pack guidance"
```

---

### Task 9: Whole-feature verification

- [ ] **Step 1: Run the complete test suite**

```bash
python -m pytest -v
```

- [ ] **Step 2: Build twice and compare hashes**

```bash
rm -rf build/skill-pack-a build/skill-pack-b
python skill-pack/scripts/build_skill_pack.py --output build/skill-pack-a
python skill-pack/scripts/build_skill_pack.py --output build/skill-pack-b
python - <<'PY'
from pathlib import Path
from paiw_skill_pack.build import hash_tree
assert hash_tree(Path('build/skill-pack-a')) == hash_tree(Path('build/skill-pack-b'))
print('deterministic')
PY
```

- [ ] **Step 3: Scan public artifacts**

```bash
python skill-pack/scripts/scan_private_identifiers.py build/skill-pack-a
```

- [ ] **Step 4: Run explicit routing scenarios**

Test at least:

```text
professional person lookup -> LinkedIn selected
sales account prep -> Sales + relevant sources
campaign analysis -> LinkedIn Ads + Data Analytics
PDF request without @pdf -> explicit invocation required
@pdf request -> PDF selected
NGS request while disabled -> disabled response
Revolut trade request while disabled -> disabled response
web-app request on Codex -> Build Web Apps selected
```

- [ ] **Step 5: Commit verification evidence**

```bash
git add docs/test-results skill-pack/test-results 2>/dev/null || true
git commit -m "test: verify capability orchestration end to end"
```

Do not publish a release in this task.
