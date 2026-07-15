from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from paiw_skill_pack.scanner import assert_public_safe


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan public Skill Pack files for private data")
    parser.add_argument("roots", type=Path, nargs="+")
    parser.add_argument("--public-email", default="michal24749@gmail.com")
    args = parser.parse_args()
    for root in args.roots:
        assert_public_safe(root, args.public_email)
        print(f"public-safe: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
