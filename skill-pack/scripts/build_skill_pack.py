from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from paiw_skill_pack.build import build_skill


def main() -> int:
    parser = argparse.ArgumentParser(description="Build standalone Personal AI Workspace skills")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--shared", type=Path, default=Path("skills/_shared"))
    parser.add_argument("--output", type=Path, default=Path("skill-pack/build"))
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    built = build_skill(args.source, args.shared, args.output, args.version)
    print(built)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
