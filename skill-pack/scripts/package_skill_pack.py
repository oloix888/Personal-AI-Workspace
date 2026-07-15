from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from paiw_skill_pack.package import (
    assert_unique_root_artifact_names,
    create_deterministic_zip,
    write_checksums,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Package Personal AI Workspace skills")
    parser.add_argument("roots", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, default=Path("skill-pack/dist"))
    args = parser.parse_args()
    assert_unique_root_artifact_names(args.roots)
    args.output.mkdir(parents=True, exist_ok=True)
    archives = [
        create_deterministic_zip(root, args.output / f"{root.name}.zip")
        for root in args.roots
    ]
    write_checksums(archives, args.output / "SHA256SUMS.txt")
    for archive in archives:
        print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
