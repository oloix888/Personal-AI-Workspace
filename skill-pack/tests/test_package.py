from pathlib import Path
import zipfile

import pytest

from paiw_skill_pack.build import build_skill
from paiw_skill_pack.package import create_deterministic_zip, write_checksums
from paiw_skill_pack.scanner import PublicSafetyError
from paiw_skill_pack.validate import validate_skill_root

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"


def test_zip_is_reproducible(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    first = create_deterministic_zip(built, tmp_path / "first.zip")
    second = create_deterministic_zip(built, tmp_path / "second.zip")
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert archive.testzip() is None
        assert "minimal-skill/SKILL.md" in archive.namelist()


def test_checksum_manifest_is_sorted(tmp_path: Path) -> None:
    a = tmp_path / "a.zip"
    b = tmp_path / "b.zip"
    a.write_bytes(b"a")
    b.write_bytes(b"b")
    output = write_checksums([b, a], tmp_path / "SHA256SUMS.txt")
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0].endswith("  a.zip")
    assert lines[1].endswith("  b.zip")


def test_packaging_rejects_an_invalid_skill_tree_before_creating_an_archive(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    (built / "NOTICE").unlink()
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(ValueError, match="missing NOTICE"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


def test_packaging_rejects_private_input_in_an_otherwise_valid_skill_tree(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    private_email = "private.user" + "@example.com"
    (built / "private-input.md").write_text(private_email, encoding="utf-8")
    assert validate_skill_root(built) == []
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(PublicSafetyError, match="private-input.md:1"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


def test_packaging_rejects_private_content_in_the_generated_archive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    destination = tmp_path / "minimal-skill.zip"

    def write_unsafe_archive(skill_root: Path, archive_path: Path) -> None:
        private_email = "private.user" + "@example.com"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr(f"{skill_root.name}/private.md", private_email)

    monkeypatch.setattr(
        "paiw_skill_pack.package._write_deterministic_zip", write_unsafe_archive
    )

    with pytest.raises(PublicSafetyError, match="private.md:1"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()
