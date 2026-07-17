from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from paiw_skill_pack.validate import assert_valid_skill


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate built Personal AI Workspace skills")
    parser.add_argument("roots", type=Path, nargs="+")
    args = parser.parse_args()
    for root in args.roots:
        assert_valid_skill(root)
        print(f"valid: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
