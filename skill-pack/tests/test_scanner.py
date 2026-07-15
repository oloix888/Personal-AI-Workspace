import io
from pathlib import Path
import zipfile

import pytest

import paiw_skill_pack.scanner as scanner
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


@pytest.mark.parametrize("host", ["notion.com", "www.notion.com"])
def test_scanner_detects_hyphenated_notion_uuid_identifier(tmp_path: Path, host: str) -> None:
    identifier = "123e4567-e89b-12d3-a456-426614174000"
    (tmp_path / "public-reference.txt").write_text(
        f"https://{host}/workspace/{identifier}\n", encoding="utf-8"
    )

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "notion_private_url" in rules


def test_scanner_allows_fictional_notion_fixture_without_private_identifier(
    tmp_path: Path,
) -> None:
    (tmp_path / "fixture.md").write_text(
        "https://www.notion.com/fictional-workspace/constitution\n", encoding="utf-8"
    )

    assert scan_tree(tmp_path, "michal24749@gmail.com") == []


def test_scanner_fails_closed_for_unclassified_non_utf8_files(tmp_path: Path) -> None:
    (tmp_path / "unclassified.data").write_bytes(b"\xff\xfe")

    with pytest.raises(PublicSafetyError, match="unclassified non-UTF-8 file: unclassified.data"):
        scan_tree(tmp_path, "michal24749@gmail.com")


def test_scanner_fails_closed_for_directory_symlinks(tmp_path: Path) -> None:
    target = tmp_path / "external"
    target.mkdir()
    symlink = tmp_path / "linked"
    try:
        symlink.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlinks are unavailable on this platform: {exc}")

    with pytest.raises(PublicSafetyError, match="unable to scan symlink: linked"):
        scan_tree(tmp_path, "michal24749@gmail.com")


@pytest.mark.parametrize(
    ("filename", "contents"),
    [
        ("opaque.pdf", b"private.user" + b"@example.com"),
        ("opaque.png", b"\x00private.user" + b"@example.com"),
    ],
)
def test_scanner_scans_private_text_hidden_by_a_known_binary_suffix(
    tmp_path: Path, filename: str, contents: bytes
) -> None:
    (tmp_path / filename).write_bytes(contents)

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "non_allowlisted_email" in rules


def test_scanner_scans_zip_members(tmp_path: Path) -> None:
    private_email = "private.user" + "@example.com"
    with zipfile.ZipFile(tmp_path / "artifact.zip", "w") as archive:
        archive.writestr("nested/private.md", private_email)

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    assert [(finding.path, finding.rule) for finding in findings] == [
        ("artifact.zip!nested/private.md", "non_allowlisted_email")
    ]


def test_scanner_scans_deflated_zip_hidden_by_binary_extension(tmp_path: Path) -> None:
    private_email = "private.user" + "@example.com"
    with zipfile.ZipFile(
        tmp_path / "payload.pdf", "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        archive.writestr("private.md", private_email)

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    assert [(finding.path, finding.rule) for finding in findings] == [
        ("payload.pdf!private.md", "non_allowlisted_email")
    ]


def test_scanner_recursively_scans_nested_zip_members(tmp_path: Path) -> None:
    private_email = "private.user" + "@example.com"
    inner_bytes = io.BytesIO()
    with zipfile.ZipFile(inner_bytes, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("private.md", private_email)
    with zipfile.ZipFile(tmp_path / "outer.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("nested/inner.zip", inner_bytes.getvalue())

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    assert [(finding.path, finding.rule) for finding in findings] == [
        ("outer.zip!nested/inner.zip!private.md", "non_allowlisted_email")
    ]


@pytest.mark.parametrize(
    ("limit_name", "limit", "expected_error"),
    [
        ("MAX_ZIP_ARCHIVE_SIZE", 1, "ZIP archive exceeds size limit: archive.zip"),
        ("MAX_ZIP_MEMBER_COUNT", 1, "ZIP member count exceeds limit: archive.zip"),
        (
            "MAX_ZIP_MEMBER_SIZE",
            1,
            "ZIP member exceeds size limit: archive.zip!first.txt",
        ),
        (
            "MAX_ZIP_TOTAL_UNCOMPRESSED_SIZE",
            1,
            "ZIP total uncompressed size exceeds limit: archive.zip",
        ),
    ],
)
def test_scanner_fails_closed_at_configured_zip_size_and_member_limits(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    limit_name: str,
    limit: int,
    expected_error: str,
) -> None:
    with zipfile.ZipFile(tmp_path / "archive.zip", "w") as archive:
        archive.writestr("first.txt", "xx")
        archive.writestr("second.txt", "x")
    monkeypatch.setattr(scanner, limit_name, limit)

    with pytest.raises(PublicSafetyError, match=expected_error):
        scan_tree(tmp_path, "michal24749@gmail.com")


def test_scanner_fails_closed_at_configured_zip_nesting_limit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    inner_bytes = io.BytesIO()
    with zipfile.ZipFile(inner_bytes, "w") as archive:
        archive.writestr("safe.txt", "safe")
    with zipfile.ZipFile(tmp_path / "outer.zip", "w") as archive:
        archive.writestr("inner.zip", inner_bytes.getvalue())
    monkeypatch.setattr(scanner, "MAX_ZIP_NESTED_DEPTH", 0)

    with pytest.raises(
        PublicSafetyError, match="ZIP recursion depth exceeds limit: outer.zip!inner.zip"
    ):
        scan_tree(tmp_path, "michal24749@gmail.com")


def test_scanner_fails_closed_for_invalid_zip_archives(tmp_path: Path) -> None:
    (tmp_path / "artifact.zip").write_bytes(b"not a ZIP archive")

    with pytest.raises(PublicSafetyError, match="invalid ZIP archive: artifact.zip"):
        scan_tree(tmp_path, "michal24749@gmail.com")


def test_scanner_fails_closed_for_invalid_zip_signature_with_binary_extension(
    tmp_path: Path,
) -> None:
    (tmp_path / "payload.pdf").write_bytes(b"PK\x03\x04not a ZIP archive")

    with pytest.raises(PublicSafetyError, match="invalid ZIP archive: payload.pdf"):
        scan_tree(tmp_path, "michal24749@gmail.com")


@pytest.mark.parametrize(
    "relative",
    [Path(".superpowers/sdd/unlisted.md"), Path("docs/superpowers/unlisted.md")],
)
def test_scanner_scans_unlisted_governance_and_documentation_files(
    tmp_path: Path, relative: Path
) -> None:
    private_email = "private.user" + "@example.com"
    unsafe = tmp_path / relative
    unsafe.parent.mkdir(parents=True)
    unsafe.write_text(private_email, encoding="utf-8")

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "non_allowlisted_email" in rules


def test_scanner_fails_closed_for_unreadable_directories(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    unreadable = tmp_path / "unreadable"

    def walk_with_error(
        root: Path, topdown: bool = True, onerror=None, followlinks: bool = False
    ):
        assert topdown is True
        assert followlinks is False
        assert onerror is not None
        onerror(PermissionError(13, "Permission denied", str(unreadable)))
        return iter(())

    monkeypatch.setattr(scanner.os, "walk", walk_with_error)

    with pytest.raises(PublicSafetyError, match="unable to scan directory"):
        scan_tree(tmp_path, "michal24749@gmail.com")


def test_scanner_fails_closed_for_unreadable_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    unreadable = tmp_path / "unreadable.md"
    unreadable.write_text("safe", encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def read_bytes_with_error(path: Path) -> bytes:
        if path == unreadable:
            raise PermissionError(13, "Permission denied", str(path))
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", read_bytes_with_error)

    with pytest.raises(PublicSafetyError, match="unable to read file: unreadable.md"):
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
