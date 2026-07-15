from __future__ import annotations

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile

from .scanner import PUBLIC_PROJECT_EMAIL, assert_public_file_safe, assert_public_safe
from .validate import assert_valid_skill

FIXED_TIMESTAMP = (2026, 7, 15, 0, 0, 0)


def _write_deterministic_zip(skill_root: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in skill_root.rglob("*") if item.is_file()):
            relative = Path(skill_root.name) / path.relative_to(skill_root)
            info = zipfile.ZipInfo(relative.as_posix(), FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(
                info,
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )


def create_deterministic_zip(
    skill_root: Path,
    destination: Path,
    public_email: str = PUBLIC_PROJECT_EMAIL,
) -> Path:
    """Validate and privacy-scan a skill before atomically publishing its ZIP.

    The library API enforces the same source, generated-output, and final-package
    gates as the CLI, so callers cannot accidentally bypass package safety.
    """
    assert_valid_skill(skill_root)
    assert_public_safe(skill_root, public_email)

    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".skill-pack-package-", dir=destination.parent) as staging:
        staged_archive = Path(staging) / destination.name
        _write_deterministic_zip(skill_root, staged_archive)
        # Scan the generated output archive and every ZIP member before it can
        # replace the requested destination.
        assert_public_file_safe(staged_archive, public_email)
        staged_archive.replace(destination)

    # Re-scan the published package to make the output contract explicit even
    # when callers invoke this API directly instead of the package CLI.
    assert_public_file_safe(destination, public_email)
    return destination


def write_checksums(files: list[Path], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for path in sorted(files, key=lambda item: item.name):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination
