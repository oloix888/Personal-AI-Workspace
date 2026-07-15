import pytest
from jsonschema import ValidationError

from paiw_skill_pack.schemas import validate_payload


def test_capability_report_accepts_explicit_state() -> None:
    validate_payload(
        "capability-report",
        {
            "generated_at": "2026-07-15T09:00:00Z",
            "capabilities": [
                {
                    "capability": "notion.content.read",
                    "state": "AVAILABLE_READ_ONLY",
                    "detail": "Read-only connector",
                }
            ],
        },
    )


def test_capability_report_rejects_invented_state() -> None:
    with pytest.raises(ValidationError):
        validate_payload(
            "capability-report",
            {
                "generated_at": "2026-07-15T09:00:00Z",
                "capabilities": [
                    {
                        "capability": "notion.content.read",
                        "state": "PROBABLY_AVAILABLE",
                        "detail": "Unsupported state",
                    }
                ],
            },
        )


def test_capability_report_rejects_invalid_generated_at_format() -> None:
    with pytest.raises(ValidationError):
        validate_payload(
            "capability-report",
            {
                "generated_at": "2026-13-40T25:61:61Z",
                "capabilities": [
                    {
                        "capability": "notion.content.read",
                        "state": "AVAILABLE_READ_ONLY",
                        "detail": "Read-only connector",
                    }
                ],
            },
        )


def test_context_briefing_requires_coverage() -> None:
    with pytest.raises(ValidationError):
        validate_payload(
            "context-briefing",
            {
                "generated_at": "2026-07-15T09:00:00Z",
                "workspace": {"title": "Example", "framework_version": "1.5.1"},
            },
        )
