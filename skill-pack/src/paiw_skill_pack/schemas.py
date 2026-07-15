from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "skills" / "_shared" / "schemas"
RFC3339_DATE_TIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
FORMAT_CHECKER = FormatChecker()


@FORMAT_CHECKER.checks("date-time")
def _is_rfc3339_date_time(value: object) -> bool:
    """Validate the schema's timestamp contract without optional checker extras."""
    if not isinstance(value, str) or RFC3339_DATE_TIME_RE.fullmatch(value) is None:
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return False
    return True


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / f"{name}.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def validate_payload(name: str, payload: dict[str, Any]) -> None:
    Draft202012Validator(load_schema(name), format_checker=FORMAT_CHECKER).validate(payload)
