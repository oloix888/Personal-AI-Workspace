from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil


def _paths_overlap(first: Path, second: Path) -> bool:
    """Return whether either resolved path is contained by the other."""
    try:
        second.relative_to(first)
        return True
    except ValueError:
        pass
    try:
        first.relative_to(second)
        return True
    except ValueError:
        return False


def _assert_build_paths_do_not_overlap(
    source_root: Path, shared_root: Path, destination: Path
) -> None:
    """Protect inputs before a rebuild removes an existing destination tree."""
    try:
        resolved_paths = {
            "source": source_root.resolve(),
            "shared": shared_root.resolve(),
            "destination": destination.resolve(),
        }
    except OSError as exc:
        raise ValueError("unable to resolve build paths") from exc

    names = tuple(resolved_paths)
    for index, first_name in enumerate(names):
        for second_name in names[index + 1 :]:
            if _paths_overlap(resolved_paths[first_name], resolved_paths[second_name]):
                raise ValueError(
                    f"build paths overlap: {first_name} and {second_name}"
                )


def _assert_tree_has_no_symlinks(source: Path, tree_name: str) -> None:
    """Reject links before a build can copy or dereference an input tree."""
    if source.is_symlink():
        raise ValueError(f"{tree_name} tree contains symlink: .")
    try:
        for directory, directory_names, filenames in os.walk(source, followlinks=False):
            directory_path = Path(directory)
            for name in (*directory_names, *filenames):
                path = directory_path / name
                if path.is_symlink():
                    relative = path.relative_to(source).as_posix()
                    raise ValueError(f"{tree_name} tree contains symlink: {relative}")
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError(f"unable to inspect {tree_name} tree for symlinks") from exc


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
    # Validate both inputs before deleting an existing destination.  A public
    # build must never silently dereference a source/shared symlink.
    skill_name = source_root.name
    destination = destination_root / skill_name
    _assert_build_paths_do_not_overlap(source_root, shared_root, destination)
    _assert_tree_has_no_symlinks(source_root, "source")
    _assert_tree_has_no_symlinks(shared_root, "shared")
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
