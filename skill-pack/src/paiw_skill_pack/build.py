from __future__ import annotations

import hashlib
from pathlib import Path
import shutil


def _copy_tree(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())


def _find_legal_root(shared_root: Path) -> Path:
    resolved_shared_root = shared_root.resolve()
    for candidate in (resolved_shared_root, *resolved_shared_root.parents):
        if (candidate / "LICENSE").is_file() and (candidate / "NOTICE").is_file():
            return candidate
    raise FileNotFoundError(
        "unable to locate canonical LICENSE and NOTICE above the shared skill root"
    )


def build_skill(source_root: Path, shared_root: Path, destination_root: Path, version: str) -> Path:
    skill_name = source_root.name
    destination = destination_root / skill_name
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    _copy_tree(source_root, destination)
    _copy_tree(shared_root / "contract", destination / "references" / "shared" / "contract")
    _copy_tree(shared_root / "schemas", destination / "references" / "shared" / "schemas")
    legal_root = _find_legal_root(shared_root)
    for filename in ("LICENSE", "NOTICE"):
        (destination / filename).write_bytes((legal_root / filename).read_bytes())
    (destination / "VERSION").write_text(version + "\n", encoding="utf-8")
    return destination


def hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
