from pathlib import Path

import pytest

import paiw_skill_pack.scanner as scanner
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


def test_validator_enforces_shared_stat_size_limit_before_reading_distributed_text(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    target = built / "SKILL.md"
    monkeypatch.setattr(scanner, "MAX_SCANNED_FILE_SIZE", 1)
    original_read_text = Path.read_text

    def fail_if_read(candidate: Path, *args: object, **kwargs: object) -> str:
        if candidate == target:
            pytest.fail("validator read oversized distributed text before its stat limit check")
        return original_read_text(candidate, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_if_read)

    assert "file exceeds size limit: SKILL.md" in validate_skill_root(built)


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


def test_inline_markdown_link_with_balanced_parentheses_and_title_cannot_escape_skill_root(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "SKILL.md").write_text(
        (built / "SKILL.md").read_text(encoding="utf-8")
        + '\n[outside](../../private(archive).md "optional (title)")\n',
        encoding="utf-8",
    )

    assert any("link escapes skill root" in error for error in validate_skill_root(built))


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


@pytest.mark.parametrize(
    ("contents", "expected_error"),
    [
        (
            "include: ../../_shared/contract/governance.md\n",
            "runtime.yaml file reference escapes skill root",
        ),
        (
            "unrelated_setting: file:///tmp/private-config.yaml\n",
            "runtime.yaml local or host filesystem file reference is not allowed",
        ),
        (
            "unrelated_setting: ../../_shared/contract/governance.md\n",
            "runtime.yaml file reference escapes skill root",
        ),
    ],
)
def test_all_structured_config_path_forms_cannot_escape_skill_root(
    tmp_path: Path, contents: str, expected_error: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "agents" / "runtime.yaml").write_text(contents, encoding="utf-8")

    assert any(expected_error in error for error in validate_skill_root(built))


def test_nested_arbitrary_structured_config_values_cannot_escape_skill_root(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "agents" / "runtime.yaml").write_text(
        "extensions:\n"
        "  - arbitrary:\n"
        "      nested:\n"
        "        - file:///tmp/private-config.yaml\n"
        "        - ../../private-config.yaml\n",
        encoding="utf-8",
    )

    errors = validate_skill_root(built)

    assert sum("runtime.yaml" in error and "file reference" in error for error in errors) == 2


@pytest.mark.parametrize(
    "contents",
    [
        '<meta http-equiv="refresh" content="0; url=file:///tmp/private.html">\n',
        '<meta http-equiv="refresh" content="0; URL=../../outside.html">\n',
    ],
)
def test_html_meta_refresh_cannot_escape_skill_root(
    tmp_path: Path, contents: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "references" / "redirect.html").write_text(contents, encoding="utf-8")

    assert any(
        "references/redirect.html" in error and "meta refresh" in error
        for error in validate_skill_root(built)
    )


def test_in_root_html_meta_refresh_is_allowed(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "references" / "redirect.html").write_text(
        '<meta http-equiv="refresh" content="0; url=local.md">\n', encoding="utf-8"
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


def test_os_path_dirname_join_open_escape_is_rejected(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "escape.py").write_text(
        "import os\n"
        "script_dir = os.path.dirname(__file__)\n"
        'target = os.path.join(script_dir, "..", "..", "private.txt")\n'
        'with open(target, encoding="utf-8") as handle:\n'
        "    handle.read()\n",
        encoding="utf-8",
    )

    assert any(
        "scripts/escape.py runtime file reference escapes skill root" in error
        for error in validate_skill_root(built)
    )


def test_dynamic_runtime_python_file_io_is_rejected(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "dynamic.py").write_text(
        "import os\n"
        'target = os.environ["PRIVATE_RESOURCE"]\n'
        'with open(target, encoding="utf-8") as handle:\n'
        "    handle.read()\n",
        encoding="utf-8",
    )

    assert any(
        "scripts/dynamic.py runtime file reference cannot be statically resolved" in error
        for error in validate_skill_root(built)
    )


def test_conditionally_dynamic_runtime_python_file_io_is_rejected(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "conditional.py").write_text(
        "import os\n"
        'if os.environ.get("USE_PRIVATE_RESOURCE"):\n'
        '    target = os.environ["PRIVATE_RESOURCE"]\n'
        "else:\n"
        "    script_dir = os.path.dirname(__file__)\n"
        '    target = os.path.join(script_dir, "..", "references", "local.md")\n'
        'with open(target, encoding="utf-8") as handle:\n'
        "    handle.read()\n",
        encoding="utf-8",
    )

    assert any(
        "scripts/conditional.py runtime file reference cannot be statically resolved"
        in error
        for error in validate_skill_root(built)
    )


def test_in_root_os_path_dirname_join_open_reference_is_allowed(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "read_local.py").write_text(
        "import os\n"
        "script_dir = os.path.dirname(__file__)\n"
        'local = os.path.join(script_dir, "..", "references", "local.md")\n'
        'with open(local, encoding="utf-8") as handle:\n'
        "    handle.read()\n",
        encoding="utf-8",
    )

    assert validate_skill_root(built) == []


@pytest.mark.parametrize(
    ("contents", "expected_error"),
    [
        (
            "from builtins import open as read_external\n"
            "read_external('../private-resource.txt')\n",
            "runtime file reference escapes skill root",
        ),
        (
            "import io as local_io\n"
            "local_io.open('../private-resource.txt')\n",
            "runtime file reference escapes skill root",
        ),
        (
            "import builtins\n"
            "read_external = builtins.open\n"
            "read_external('../private-resource.txt')\n",
            "runtime file reference escapes skill root",
        ),
        (
            "from shutil import move as relocate\n"
            "relocate('../private-resource.txt', 'references/local.md')\n",
            "runtime file reference escapes skill root",
        ),
        (
            "import shutil as file_ops\n"
            "file_ops.copy('references/local.md', '../private-resource.txt')\n",
            "runtime file reference escapes skill root",
        ),
        (
            "from builtins import eval as evaluate\n"
            "evaluate('1 + 1')\n",
            "dynamic code execution is not allowed",
        ),
        (
            "compile_and_run = exec\n"
            "compile_and_run('pass')\n",
            "dynamic code execution is not allowed",
        ),
        (
            "if __name__:\n"
            "    from io import open as conditionally_bound\n"
            "conditionally_bound('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "loaded = __import__('io')\n"
            "loaded.open('../private-resource.txt')\n",
            "dynamic runtime resolution is not allowed",
        ),
        (
            "import importlib as loader\n"
            "loaded = loader.import_module('io')\n"
            "loaded.open('../private-resource.txt')\n",
            "dynamic runtime resolution is not allowed",
        ),
        (
            "read_external = __builtins__['open']\n"
            "read_external('../private-resource.txt')\n",
            "dynamic callable lookup is not allowed",
        ),
    ],
)
def test_runtime_python_external_io_and_dynamic_code_aliases_are_rejected(
    tmp_path: Path, contents: str, expected_error: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "unsafe.py").write_text(contents, encoding="utf-8")

    assert any(expected_error in error for error in validate_skill_root(built))


@pytest.mark.parametrize(
    "contents",
    [
        "from builtins import open as read_local\n"
        "read_local('references/local.md')\n",
        "import io as local_io\n"
        "local_io.open('references/local.md')\n",
        "from shutil import copy as copy_local\n"
        "copy_local('references/local.md', 'references/copied.md')\n",
    ],
)
def test_runtime_python_static_external_io_aliases_allow_in_root_paths(
    tmp_path: Path, contents: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "safe.py").write_text(contents, encoding="utf-8")

    assert validate_skill_root(built) == []


@pytest.mark.parametrize(
    ("contents", "expected_error"),
    [
        (
            "read_external = open if enabled else print\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "callables = {'read': open}\n"
            "read_external = callables['read']\n"
            "read_external('../private-resource.txt')\n",
            "runtime file reference escapes skill root",
        ),
        (
            "callables = {'read': open}\n"
            "read_external = callables[key]\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "read_external = __builtins__.get('open')\n"
            "read_external('../private-resource.txt')\n",
            "dynamic callable lookup is not allowed",
        ),
        (
            "compile_and_run = {'run': eval}['run']\n"
            "compile_and_run('1 + 1')\n",
            "dynamic code execution is not allowed",
        ),
        (
            "compile_and_run = eval if enabled else print\n"
            "compile_and_run('1 + 1')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "callables = {'nested': {'read': open}}\n"
            "read_external = callables['nested']['read']\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "callables = ({'read': open},)\n"
            "read_external = callables[0]['read']\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "callables = {'nested': {'read': open}}\n"
            "read_external = callables.get('nested').get('read')\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "read_external = (lambda: open)()\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "factory = lambda: open\n"
            "read_external = factory()\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "read_external = (lambda item: item)(open)\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "compile_and_run = (lambda item: item)(eval)\n"
            "compile_and_run('1 + 1')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "read_external = next(iter({'read': open}.values()))\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "read_external = dict(read=open)['read']\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "read_external = {'read': open}.copy()['read']\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
    ],
)
def test_runtime_python_wrapped_monitored_aliases_fail_closed(
    tmp_path: Path, contents: str, expected_error: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "wrapped-alias.py").write_text(contents, encoding="utf-8")

    assert any(expected_error in error for error in validate_skill_root(built))


def test_runtime_python_static_dictionary_alias_allows_in_root_path(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "static-dictionary-alias.py").write_text(
        "callables = {'read': open}\n"
        "read_local = callables['read']\n"
        "read_local('references/local.md')\n",
        encoding="utf-8",
    )

    assert validate_skill_root(built) == []


def test_runtime_python_static_dictionary_get_allows_in_root_path(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "static-dictionary-get.py").write_text(
        "callables = {'read': open}\n"
        "read_local = callables.get('read')\n"
        "read_local('references/local.md')\n",
        encoding="utf-8",
    )

    assert validate_skill_root(built) == []


@pytest.mark.parametrize(
    ("contents", "expected_error"),
    [
        (
            '@import "../../private.css";\n',
            "CSS import escapes skill root",
        ),
        (
            ".hero { background-image: url('../../private.png'); }\n",
            "CSS url escapes skill root",
        ),
    ],
)
def test_css_references_cannot_escape_the_skill_root(
    tmp_path: Path, contents: str, expected_error: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    assets = built / "assets"
    assets.mkdir()
    (assets / "style.css").write_text(contents, encoding="utf-8")

    assert any(expected_error in error for error in validate_skill_root(built))


def test_css_references_allow_existing_in_root_assets(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path,
        "0.1.0-beta.1",
    )
    assets = built / "assets"
    assets.mkdir()
    (assets / "logo.svg").write_text("<svg></svg>\n", encoding="utf-8")
    (assets / "base.css").write_text(".base {}\n", encoding="utf-8")
    (assets / "style.css").write_text(
        '@import "base.css";\n.hero { background-image: url("logo.svg"); }\n',
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
