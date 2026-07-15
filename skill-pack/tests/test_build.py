from pathlib import Path

from paiw_skill_pack.build import build_skill, hash_tree

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[2]


def test_build_vendors_shared_contract_and_is_deterministic(tmp_path: Path) -> None:
    first = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills" / "_shared",
        tmp_path / "first",
        "0.1.0-beta.1",
    )
    second = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills" / "_shared",
        tmp_path / "second",
        "0.1.0-beta.1",
    )

    assert (first / "references/shared/contract/governance.md").is_file()
    assert (first / "references/shared/schemas/context-briefing.schema.json").is_file()
    assert (first / "LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes()
    assert (first / "NOTICE").read_bytes() == (ROOT / "NOTICE").read_bytes()
    assert (first / "VERSION").read_text().strip() == "0.1.0-beta.1"
    assert hash_tree(first) == hash_tree(second)
