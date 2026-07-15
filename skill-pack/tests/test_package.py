from pathlib import Path
import zipfile

from paiw_skill_pack.build import build_skill
from paiw_skill_pack.package import create_deterministic_zip, write_checksums

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
