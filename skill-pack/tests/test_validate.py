from pathlib import Path

from paiw_skill_pack.build import build_skill
from paiw_skill_pack.validate import validate_skill_root

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"


def test_built_fixture_is_valid(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    assert validate_skill_root(built) == []


def test_external_parent_reference_is_rejected(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "SKILL.md").write_text(
        (built / "SKILL.md").read_text(encoding="utf-8") + "\nRead [outside](../secret.md).\n",
        encoding="utf-8",
    )
    assert any("escapes skill root" in error for error in validate_skill_root(built))
