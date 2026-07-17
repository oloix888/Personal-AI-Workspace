from pathlib import Path

from paiw_skill_pack.models import (
    CapabilityResult,
    CapabilityState,
    load_compatibility,
)

ROOT = Path(__file__).resolve().parents[2]


def test_capability_result_is_explicit() -> None:
    result = CapabilityResult(
        capability="notion.content.read",
        state=CapabilityState.AVAILABLE_READ_ONLY,
        detail="Notion content can be read but not changed.",
    )
    assert result.capability == "notion.content.read"
    assert result.state.value == "AVAILABLE_READ_ONLY"


def test_compatibility_manifest_loads() -> None:
    manifest = load_compatibility(
        ROOT / "skills/_shared/contract/compatibility.json"
    )
    assert manifest.skill_pack_version == "0.1.0-beta.1"
    assert manifest.target_framework_version == "1.6.0"
    assert manifest.supported_framework_versions[0] == "1.0"
    assert manifest.supported_framework_versions[-1] == "1.6.0"
