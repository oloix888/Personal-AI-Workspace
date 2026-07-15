from pathlib import Path
import shutil

import pytest

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


@pytest.mark.parametrize(
    ("tree_name", "target_relative", "is_directory"),
    [
        ("source", "references", True),
        ("source", "SKILL.md", False),
        ("shared", "contract", True),
        ("shared", "contract/README.md", False),
    ],
)
def test_build_rejects_file_and_directory_symlinks_in_input_trees(
    tmp_path: Path, tree_name: str, target_relative: str, is_directory: bool
) -> None:
    repository_root = tmp_path / "repository"
    source_root = repository_root / "source"
    shared_root = repository_root / "skills" / "_shared"
    shutil.copytree(FIXTURES / "minimal-skill", source_root)
    shutil.copytree(ROOT / "skills" / "_shared", shared_root)
    shutil.copy2(ROOT / "LICENSE", repository_root / "LICENSE")
    shutil.copy2(ROOT / "NOTICE", repository_root / "NOTICE")
    target_root = source_root if tree_name == "source" else shared_root
    symlink = target_root / "linked-input"
    try:
        symlink.symlink_to(target_root / target_relative, target_is_directory=is_directory)
    except OSError as exc:
        pytest.skip(f"symlinks are unavailable on this platform: {exc}")

    with pytest.raises(ValueError, match=rf"{tree_name} tree contains symlink: linked-input"):
        build_skill(source_root, shared_root, tmp_path / "build", "0.1.0-beta.1")


@pytest.mark.parametrize("destination_kind", ["source", "shared"])
def test_build_rejects_destination_overlap_before_removing_any_input(
    tmp_path: Path, destination_kind: str
) -> None:
    repository_root = tmp_path / "repository"
    source_root = repository_root / "minimal-skill"
    shared_root = repository_root / "skills" / "_shared"
    shutil.copytree(FIXTURES / "minimal-skill", source_root)
    shutil.copytree(ROOT / "skills" / "_shared", shared_root)
    shutil.copy2(ROOT / "LICENSE", repository_root / "LICENSE")
    shutil.copy2(ROOT / "NOTICE", repository_root / "NOTICE")
    source_marker = source_root / "source-marker.txt"
    shared_marker = shared_root / "shared-marker.txt"
    source_marker.write_text("preserve source", encoding="utf-8")
    shared_marker.write_text("preserve shared", encoding="utf-8")
    destination_root = source_root.parent if destination_kind == "source" else shared_root

    with pytest.raises(ValueError, match="build paths overlap"):
        build_skill(source_root, shared_root, destination_root, "0.1.0-beta.1")

    assert source_marker.read_text(encoding="utf-8") == "preserve source"
    assert shared_marker.read_text(encoding="utf-8") == "preserve shared"


def test_build_rejects_source_and_shared_overlap_before_building(tmp_path: Path) -> None:
    source_root = tmp_path / "minimal-skill"
    shutil.copytree(FIXTURES / "minimal-skill", source_root)
    marker = source_root / "source-marker.txt"
    marker.write_text("preserve source", encoding="utf-8")

    with pytest.raises(ValueError, match="build paths overlap: source and shared"):
        build_skill(source_root, source_root, tmp_path / "build", "0.1.0-beta.1")

    assert marker.read_text(encoding="utf-8") == "preserve source"
