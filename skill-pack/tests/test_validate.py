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


def test_html_and_structured_config_references_cannot_escape_skill_root(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "references" / "escape.html").write_text(
        '<a href="../../_shared/contract/governance.md">outside</a>\n',
        encoding="utf-8",
    )
    (built / "agents" / "runtime.yaml").write_text(
        "template: ../../_shared/contract/governance.md\n",
        encoding="utf-8",
    )
    (built / "runtime.json").write_text(
        '{"template": "../../_shared/contract/governance.md"}\n',
        encoding="utf-8",
    )

    errors = validate_skill_root(built)

    assert any("escape.html link escapes skill root" in error for error in errors)
    assert any("runtime.yaml file reference escapes skill root" in error for error in errors)
    assert any("runtime.json file reference escapes skill root" in error for error in errors)


def test_in_root_html_and_structured_config_references_are_allowed(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "references" / "index.html").write_text(
        '<a href="local.md">local</a>\n', encoding="utf-8"
    )
    (built / "agents" / "runtime.yaml").write_text(
        "template: ../references/local.md\n", encoding="utf-8"
    )
    (built / "runtime.json").write_text(
        '{"template": "references/local.md"}\n', encoding="utf-8"
    )

    assert validate_skill_root(built) == []


def test_runtime_python_path_escape_is_rejected_before_packaging(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "escape.py").write_text(
        "from pathlib import Path\n"
        'SHARED = Path(__file__).resolve().parents[2] / "_shared"\n',
        encoding="utf-8",
    )

    assert any(
        "scripts/escape.py runtime file reference escapes skill root" in error
        for error in validate_skill_root(built)
    )


@pytest.mark.parametrize(
    "contents",
    [
        "from pathlib import Path\nPRIVATE = Path('/tmp/private-resource')\n",
        "with open('../private-resource.txt', encoding='utf-8') as handle:\n    handle.read()\n",
    ],
)
def test_runtime_python_absolute_and_parent_literal_paths_are_rejected(
    tmp_path: Path, contents: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "escape.py").write_text(contents, encoding="utf-8")

    assert any(
        "scripts/escape.py runtime file reference" in error
        for error in validate_skill_root(built)
    )


def test_in_root_runtime_python_path_reference_is_allowed(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "read_local.py").write_text(
        "from pathlib import Path\n"
        'LOCAL = Path(__file__).resolve().parents[1] / "references" / "local.md"\n'
        "contents = LOCAL.read_text(encoding=\"utf-8\")\n",
        encoding="utf-8",
    )

    assert validate_skill_root(built) == []


@pytest.mark.parametrize(
    "reference",
    [
        "[file-uri](file:///tmp/private.md)",
        "[protocol-relative](//private.example.test/secret.md)",
        r"[unc](\\\\private-host\\share\\secret.md)",
        r"[windows-drive](C:\\private\\secret.md)",
        '<a href="file:///tmp/private.md">file URI</a>',
    ],
)
def test_local_or_hosted_filesystem_link_forms_are_rejected(
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

    assert any(
        "local or host filesystem link is not allowed" in error
        for error in validate_skill_root(built)
    )


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
    ("filename", "contents"),
    [
        ("LICENSE", "Apache License\nVersion 2.0\n"),
        ("NOTICE", "Personal AI Workspace\nApache License, Version 2.0\n"),
    ],
)
def test_marker_only_legal_file_substitutions_are_rejected(
    tmp_path: Path, filename: str, contents: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / filename).write_text(contents, encoding="utf-8")

    assert f"{filename} does not match canonical repository legal file" in validate_skill_root(
        built
    )


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
