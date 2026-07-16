from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

import paiw_skill_pack.scanner as scanner
from paiw_skill_pack.build import build_skill
from paiw_skill_pack.package import create_deterministic_zip, write_checksums
from paiw_skill_pack.scanner import PublicSafetyError
from paiw_skill_pack.validate import validate_skill_root

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"
REVIEWER_SYNTHETIC_PRIVATE_JSON = (
    '{"authori'
    'zation":"Basic c3ludGhldGljOnNlY3JldA==","api_'
    'key":"synthetic-secret","notion_'
    'page_'
    'id":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","drive_'
    'folder_'
    'id":"1AbCdEfGhIjKlMnOp","drive_'
    'url":"https://drive.google'
    '.com/a/example.invalid/file/d/1AbCdEfGhIjKlMnOp/view"}'
)


def test_zip_is_reproducible(tmp_path: Path) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    first = create_deterministic_zip(built, tmp_path / "first.zip")
    second = create_deterministic_zip(built, tmp_path / "second.zip")
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert archive.testzip() is None
        assert "minimal-skill/SKILL.md" in archive.namelist()


def test_checksum_manifest_is_sorted(tmp_path: Path) -> None:
    a = tmp_path / "a.zip"
    b = tmp_path / "b.zip"
    a.write_bytes(b"a")
    b.write_bytes(b"b")
    output = write_checksums([b, a], tmp_path / "SHA256SUMS.txt")
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0].endswith("  a.zip")
    assert lines[1].endswith("  b.zip")


def test_checksum_manifest_rejects_duplicate_artifact_names(tmp_path: Path) -> None:
    first = tmp_path / "first" / "repeated.zip"
    second = tmp_path / "second" / "repeated.zip"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_bytes(b"first")
    second.write_bytes(b"second")

    with pytest.raises(ValueError, match="duplicate artifact/checksum name: repeated.zip"):
        write_checksums([first, second], tmp_path / "SHA256SUMS.txt")

    assert not (tmp_path / "SHA256SUMS.txt").exists()


def test_packaging_cli_rejects_duplicate_root_artifact_names_before_writing_output(
    tmp_path: Path,
) -> None:
    first = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "first",
        "0.1.0-beta.1",
    )
    second = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "second",
        "0.1.0-beta.1",
    )
    output = tmp_path / "dist"

    result = subprocess.run(
        [
            sys.executable,
            "skill-pack/scripts/package_skill_pack.py",
            str(first),
            str(second),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "duplicate artifact/checksum name: minimal-skill.zip" in result.stderr
    assert not output.exists()


def test_packaging_rejects_an_invalid_skill_tree_before_creating_an_archive(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    (built / "NOTICE").unlink()
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(ValueError, match="missing NOTICE"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


def test_packaging_does_not_read_oversized_input_before_the_scanner_gate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    target = built / "SKILL.md"
    destination = tmp_path / "minimal-skill.zip"
    monkeypatch.setattr(scanner, "MAX_SCANNED_FILE_SIZE", 1)
    original_read_text = Path.read_text

    def fail_if_read(candidate: Path, *args: object, **kwargs: object) -> str:
        if candidate == target:
            pytest.fail("package validation read oversized text before the scanner gate")
        return original_read_text(candidate, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_if_read)

    with pytest.raises(ValueError, match="file exceeds size limit: SKILL.md"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


def test_packaging_rejects_runtime_python_path_escape_before_creating_an_archive(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    (built / "scripts").mkdir()
    (built / "scripts" / "escape.py").write_text(
        "from pathlib import Path\n"
        'SHARED = Path(__file__).resolve().parents[2] / "_shared"\n',
        encoding="utf-8",
    )
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(ValueError, match="runtime file reference escapes skill root"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


def test_packaging_rejects_html_path_escape_before_creating_an_archive(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    (built / "references" / "escape.html").write_text(
        '<a href="../../_shared/contract/governance.md">outside</a>\n',
        encoding="utf-8",
    )
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(ValueError, match="link escapes skill root"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


@pytest.mark.parametrize(
    ("relative_path", "contents", "expected_error"),
    [
        (
            "agents/runtime.yaml",
            "include: ../../_shared/contract/governance.md\n",
            "file reference escapes skill root",
        ),
        (
            "agents/runtime.yaml",
            "unrelated_setting: file:///tmp/private-config.yaml\n",
            "local or host filesystem file reference",
        ),
        (
            "references/redirect.html",
            '<meta http-equiv="refresh" content="0; url=file:///tmp/private.html">\n',
            "local or host filesystem meta refresh",
        ),
        (
            "references/redirect.html",
            '<meta http-equiv="refresh" content="0; url=../../outside.html">\n',
            "meta refresh escapes skill root",
        ),
        (
            "scripts/escape.py",
            "import os\n"
            "script_dir = os.path.dirname(__file__)\n"
            'target = os.path.join(script_dir, "..", "..", "private.txt")\n'
            'with open(target, encoding="utf-8") as handle:\n'
            "    handle.read()\n",
            "runtime file reference escapes skill root",
        ),
        (
            "scripts/dynamic.py",
            "import os\n"
            'target = os.environ["PRIVATE_RESOURCE"]\n'
            'with open(target, encoding="utf-8") as handle:\n'
            "    handle.read()\n",
            "runtime file reference cannot be statically resolved",
        ),
        (
            "scripts/conditional-alias.py",
            "read_external = open if enabled else print\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "scripts/dictionary-alias.py",
            "callables = {'read': open}\n"
            "read_external = callables['read']\n"
            "read_external('../private-resource.txt')\n",
            "runtime file reference escapes skill root",
        ),
        (
            "scripts/builtins-get-alias.py",
            "read_external = __builtins__.get('open')\n"
            "read_external('../private-resource.txt')\n",
            "dynamic callable lookup is not allowed",
        ),
        (
            "scripts/nested-dictionary-alias.py",
            "callables = {'nested': {'read': open}}\n"
            "read_external = callables['nested']['read']\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "scripts/tuple-dictionary-alias.py",
            "callables = ({'read': open},)\n"
            "read_external = callables[0]['read']\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "scripts/chained-dictionary-get-alias.py",
            "callables = {'nested': {'read': open}}\n"
            "read_external = callables.get('nested').get('read')\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "scripts/lambda-alias.py",
            "read_external = (lambda: open)()\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "scripts/lambda-identity-alias.py",
            "read_external = (lambda item: item)(open)\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "scripts/lambda-identity-eval.py",
            "compile_and_run = (lambda item: item)(eval)\n"
            "compile_and_run('1 + 1')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "scripts/iterator-alias.py",
            "read_external = next(iter({'read': open}.values()))\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "scripts/dict-constructor-alias.py",
            "read_external = dict(read=open)['read']\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "scripts/dictionary-copy-alias.py",
            "read_external = {'read': open}.copy()['read']\n"
            "read_external('../private-resource.txt')\n",
            "monitored callable alias cannot be statically resolved",
        ),
        (
            "assets/escape-import.css",
            '@import "../../private.css";\n',
            "CSS import escapes skill root",
        ),
        (
            "assets/escape-url.css",
            ".hero { background-image: url('../../private.png'); }\n",
            "CSS url escapes skill root",
        ),
    ],
)
def test_packaging_rejects_all_runtime_boundary_bypasses_before_creating_an_archive(
    tmp_path: Path, relative_path: str, contents: str, expected_error: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    target = built / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(contents, encoding="utf-8")
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(ValueError, match=expected_error):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


@pytest.mark.parametrize(
    ("filename", "contents"),
    [
        ("LICENSE", "Apache License\nVersion 2.0\n"),
        ("NOTICE", "Personal AI Workspace\nApache License, Version 2.0\n"),
    ],
)
def test_packaging_rejects_marker_only_legal_file_substitutions(
    tmp_path: Path, filename: str, contents: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    (built / filename).write_text(contents, encoding="utf-8")
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(
        ValueError, match=f"{filename} does not match canonical repository legal file"
    ):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


def test_packaging_rejects_private_input_in_an_otherwise_valid_skill_tree(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    private_email = "private.user" + "@example.com"
    (built / "private-input.md").write_text(private_email, encoding="utf-8")
    assert validate_skill_root(built) == []
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(PublicSafetyError, match="private-input.md:1"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


def test_packaging_rejects_reviewers_quoted_private_json_before_creating_an_archive(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    (built / "private.json").write_text(REVIEWER_SYNTHETIC_PRIVATE_JSON, encoding="utf-8")
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(PublicSafetyError, match="private.json:1"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


def test_packaging_rejects_nested_structured_connector_response_input(
    tmp_path: Path,
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    (built / "connector-export.yaml").write_text(
        "response:\n"
        "  message:\n"
        "    id: synthetic-message\n"
        "    threadId: synthetic-thread\n"
        "    snippet: Synthetic private Gmail excerpt\n"
        "    payload:\n"
        "      headers:\n"
        "        - name: Subject\n"
        "          value: Synthetic subject\n",
        encoding="utf-8",
    )
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(PublicSafetyError, match="connector-export.yaml:3"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


@pytest.mark.parametrize(
    "historical_line",
    [
        "Private task repository: " + "oloix888" + "/" + "Apex",
        "migration baseline: " + "emma-workspace" + "-memory 5.6.0",
    ],
)
def test_packaging_rejects_historical_private_values_in_built_skill_content(
    tmp_path: Path, historical_line: str
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    (built / "historical-private-value.md").write_text(historical_line, encoding="utf-8")
    destination = tmp_path / "minimal-skill.zip"

    with pytest.raises(PublicSafetyError, match="historical-private-value.md:1"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()


def test_packaging_rejects_private_content_in_the_generated_archive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    built = build_skill(
        FIXTURES / "minimal-skill",
        ROOT / "skills/_shared",
        tmp_path / "build",
        "0.1.0-beta.1",
    )
    destination = tmp_path / "minimal-skill.zip"

    def write_unsafe_archive(skill_root: Path, archive_path: Path) -> None:
        private_email = "private.user" + "@example.com"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr(f"{skill_root.name}/private.md", private_email)

    monkeypatch.setattr(
        "paiw_skill_pack.package._write_deterministic_zip", write_unsafe_archive
    )

    with pytest.raises(PublicSafetyError, match="private.md:1"):
        create_deterministic_zip(built, destination)

    assert not destination.exists()
