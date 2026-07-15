from pathlib import Path

import pytest

from paiw_skill_pack.build import build_skill
from paiw_skill_pack.validate import validate_skill_root

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"


def test_built_fixture_is_valid(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    assert validate_skill_root(built) == []


def test_external_parent_reference_is_rejected(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "SKILL.md").write_text(
        (built / "SKILL.md").read_text(encoding="utf-8") + "\nRead [outside](../secret.md).\n",
        encoding="utf-8",
    )
    assert any("escapes skill root" in error for error in validate_skill_root(built))


@pytest.mark.parametrize(
    "reference",
    [
        "[outside]: ../secret.md",
        "[outside]: <../secret.md> \"Optional title\"",
        '<a href="../secret.md">outside</a>',
        '<img src="../secret.png" alt="outside">',
        '<object data="../secret.html"></object>',
    ],
)
def test_markdown_reference_definitions_and_html_links_cannot_escape_skill_root(
    tmp_path: Path, reference: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "SKILL.md").write_text(
        (built / "SKILL.md").read_text(encoding="utf-8") + f"\n{reference}\n",
        encoding="utf-8",
    )

    assert any("escapes skill root" in error for error in validate_skill_root(built))


def test_external_mailto_fragment_and_internal_markdown_html_links_are_allowed(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    recipient = "owner" + "@example.test"
    (built / "SKILL.md").write_text(
        (built / "SKILL.md").read_text(encoding="utf-8")
        + "\n[external]: https://example.test/reference \"Optional title\"\n"
        + f"[mail]: mailto:{recipient}\n"
        + "[fragment]: #internal-heading\n"
        + "[internal]: <references/local.md>\n"
        + '<a href="https://example.test/reference">external</a>\n'
        + '<img src="references/local.md" alt="internal">\n',
        encoding="utf-8",
    )

    assert validate_skill_root(built) == []


@pytest.mark.parametrize(
    ("filename", "contents", "expected_error"),
    [
        ("LICENSE", None, "missing LICENSE"),
        ("NOTICE", "not the canonical attribution\n", "NOTICE missing required attribution"),
    ],
)
def test_missing_or_invalid_legal_files_are_rejected(
    tmp_path: Path, filename: str, contents: str | None, expected_error: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    target = built / filename
    if contents is None:
        target.unlink()
    else:
        target.write_text(contents, encoding="utf-8")

    assert any(expected_error in error for error in validate_skill_root(built))


@pytest.mark.parametrize(
    ("contents", "expected_error"),
    [
        ("interface: [unterminated\n", "invalid YAML"),
        ("interface: minimal-skill\npolicy: {}\n", "interface must be a mapping"),
        (
            "interface:\n  display_name: Minimal\npolicy:\n  allow_implicit_invocation: false\n",
            "interface missing required field: short_description",
        ),
        (
            "interface:\n  display_name: Minimal\n  short_description: Builder fixture\n  brand_color: '#123456'\npolicy:\n  allow_implicit_invocation: false\n",
            "interface missing required field: default_prompt",
        ),
        (
            "interface:\n  display_name: Minimal\n  short_description: Builder fixture\n  brand_color: '#123456'\n  default_prompt: Build safely.\npolicy:\n  allow_implicit_invocation: 'false'\n",
            "policy.allow_implicit_invocation must be a boolean",
        ),
    ],
)
def test_invalid_openai_yaml_is_rejected(
    tmp_path: Path, contents: str, expected_error: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "agents/openai.yaml").write_text(contents, encoding="utf-8")

    assert any(expected_error in error for error in validate_skill_root(built))
