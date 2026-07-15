from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_validation_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "skill-pack/scripts/validate_skill_pack.py", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Validate built Personal AI Workspace skills" in result.stdout
