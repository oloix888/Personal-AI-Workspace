from pathlib import Path

import pytest

from paiw_skill_pack.scanner import PublicSafetyError, scan_tree

FIXTURES = Path(__file__).parent / "fixtures" / "scanner"


def test_safe_tree_allows_public_project_contact() -> None:
    findings = scan_tree(FIXTURES / "safe", "michal24749@gmail.com")
    assert findings == []


def test_scanner_detects_non_allowlisted_email_and_private_repo(tmp_path: Path) -> None:
    synthetic_private_reference = "/".join(("oloix888", "Apex"))
    synthetic_private_email = "private.user" + "@example.com"
    unsafe = tmp_path / "unsafe.md"
    unsafe.write_text(
        f"Private account: {synthetic_private_email}\n"
        f"Private task repository: {synthetic_private_reference}\n",
        encoding="utf-8",
    )

    findings = scan_tree(tmp_path, "michal24749@gmail.com")
    rules = {finding.rule for finding in findings}
    assert "non_allowlisted_email" in rules
    assert "private_repo_reference" in rules


def test_scanner_detects_private_notion_and_drive_references_in_toml(tmp_path: Path) -> None:
    notion_url = "https://www." + "notion.so/" + ("a" * 32)
    drive_url = "https://drive.google." + "com/drive/folders/" + "1AbCdEfGhIjKlMnOp"
    folder_key = "folder" + "_id"
    unsafe = tmp_path / "private.toml"
    unsafe.write_text(
        f'notion_url = "{notion_url}"\n'
        f'drive_url = "{drive_url}"\n'
        f'{folder_key} = "1QrStUvWxYz012345"\n',
        encoding="utf-8",
    )

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "notion_private_url" in rules
    assert "google_drive_identifier" in rules


@pytest.mark.parametrize(
    ("filename", "key_parts", "separator", "value_parts"),
    [
        ("install.sh", ("to", "ken"), ":", ("synthetic", "-value")),
        (".env", ("coo", "kie"), "=", ("synthetic", "-value")),
        (
            "NOTICE",
            ("authori", "zation"),
            ":",
            ("Be", "arer synthetic-value"),
        ),
        ("settings.conf", ("api", "Key"), "=", ("synthetic", "-value")),
    ],
)
def test_scanner_catches_secret_literals_in_text_and_extensionless_files(
    tmp_path: Path,
    filename: str,
    key_parts: tuple[str, str],
    separator: str,
    value_parts: tuple[str, str],
) -> None:
    key = "".join(key_parts)
    value = "".join(value_parts)
    (tmp_path / filename).write_text(f"{key}{separator}{value}\n", encoding="utf-8")

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    assert [(item.path, item.rule) for item in findings] == [
        (filename, "authentication_secret_literal")
    ]


def test_scanner_detects_synthetic_notion_dot_com_identifier(tmp_path: Path) -> None:
    host = "notion" + ".com"
    identifier = "a" * 32
    (tmp_path / "public-reference.txt").write_text(
        f"https://www.{host}/{identifier}\n", encoding="utf-8"
    )

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "notion_private_url" in rules


def test_scanner_fails_closed_for_unclassified_non_utf8_files(tmp_path: Path) -> None:
    (tmp_path / "unclassified.data").write_bytes(b"\xff\xfe")

    with pytest.raises(PublicSafetyError, match="unclassified non-UTF-8 file: unclassified.data"):
        scan_tree(tmp_path, "michal24749@gmail.com")


def test_scanner_excludes_private_git_and_generated_environment_directories(
    tmp_path: Path,
) -> None:
    private_email = "private.user" + "@example.com"
    for directory in (".git", ".venv"):
        target = tmp_path / directory
        target.mkdir()
        (target / "local.env").write_text(private_email, encoding="utf-8")

    assert scan_tree(tmp_path, "michal24749@gmail.com") == []


@pytest.mark.parametrize("root_kind", ["missing", "file"])
def test_scanner_rejects_missing_or_non_directory_roots(
    tmp_path: Path, root_kind: str
) -> None:
    root = tmp_path / root_kind
    if root_kind == "file":
        root.write_text("safe", encoding="utf-8")

    with pytest.raises(PublicSafetyError, match="scan root is not a directory"):
        scan_tree(root, "michal24749@gmail.com")


def test_public_safety_error_has_paths(tmp_path: Path) -> None:
    synthetic_private_email = "private.user" + "@example.com"
    unsafe = tmp_path / "unsafe.md"
    unsafe.write_text(f"Private account: {synthetic_private_email}\n", encoding="utf-8")

    with pytest.raises(PublicSafetyError) as exc:
        from paiw_skill_pack.scanner import assert_public_safe

        assert_public_safe(tmp_path, "michal24749@gmail.com")
    assert "unsafe.md" in str(exc.value)
