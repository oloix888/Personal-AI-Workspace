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
