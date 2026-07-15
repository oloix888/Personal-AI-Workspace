import io
from collections.abc import Callable
from pathlib import Path
import zipfile

import pytest

import paiw_skill_pack.scanner as scanner
from paiw_skill_pack.scanner import PublicSafetyError, scan_file, scan_tree

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
        f"Unexpected task-tracker reference: {synthetic_private_reference}\n",
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


def _join(*parts: str) -> str:
    return "".join(parts)


def _reviewer_synthetic_private_json() -> str:
    """Generate the review fixture without making the repository scanner flag its test source."""
    fields = (
        (_join("authori", "zation"), "Basic c3ludGhldGljOnNlY3JldA=="),
        (_join("api_", "key"), "synthetic-secret"),
        (_join("notion_", "page_id"), "a" * 32),
        (_join("drive_", "folder_id"), "1AbCdEfGhIjKlMnOp"),
        (
            _join("drive_", "url"),
            _join(
                "https://drive.google",
                ".com/a/example.invalid/file/d/1AbCdEfGhIjKlMnOp/view",
            ),
        ),
    )
    return "{" + ",".join(f'"{key}":"{value}"' for key, value in fields) + "}"


def _quoted_sensitive_payload(
    separator: str, quote_choices: tuple[str, ...], wrap_in_braces: bool
) -> str:
    fields = (
        (_join("authori", "zation"), "Bearer synthetic-access-token"),
        (_join("api_", "key"), "synthetic-api-key"),
        (_join("client_", "secret"), "synthetic-client-secret"),
        (_join("notion_", "database_id"), "b" * 32),
        (_join("notion_", "view_id"), "323e4567-e89b-12d3-a456-426614174000"),
        (_join("drive_", "file_id"), "1QrStUvWxYz012345"),
        (
            _join("drive_", "url"),
            _join(
                "https://docs.google",
                ".com/a/example.invalid/document/d/1QrStUvWxYz012345/edit",
            ),
        ),
    )
    rendered_fields = []
    for index, (key, value) in enumerate(fields):
        quote = quote_choices[index % len(quote_choices)]
        suffix = "," if wrap_in_braces and index + 1 < len(fields) else ""
        rendered_fields.append(f"  {quote}{key}{quote}{separator} {quote}{value}{quote}{suffix}")
    body = "\n".join(rendered_fields)
    return f"{{\n{body}\n}}\n" if wrap_in_braces else f"{body}\n"


def test_scanner_rejects_reviewers_quoted_private_json_in_source_and_zip(tmp_path: Path) -> None:
    """Quoted JSON keys must not bypass source or distributable-package scans."""
    payload = _reviewer_synthetic_private_json()
    source = tmp_path / "private.json"
    source.write_text(payload, encoding="utf-8")
    archive_path = tmp_path / "artifact.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("config/private.json", payload)

    source_rules = {finding.rule for finding in scan_file(source)}
    archive_rules = {finding.rule for finding in scan_file(archive_path)}

    expected_rules = {
        "authentication_secret_literal",
        "notion_private_url",
        "google_drive_identifier",
    }
    assert expected_rules <= source_rules
    assert expected_rules <= archive_rules


@pytest.mark.parametrize(
    ("filename", "separator", "quote_choices", "wrap_in_braces"),
    [
        ("private.json", ":", ('"',), True),
        ("private.yaml", ":", ('"', "'"), False),
        ("private.toml", "=", ('"', "'"), False),
    ],
)
def test_scanner_rejects_quoted_sensitive_keys_across_structured_text_formats(
    tmp_path: Path,
    filename: str,
    separator: str,
    quote_choices: tuple[str, ...],
    wrap_in_braces: bool,
) -> None:
    payload = _quoted_sensitive_payload(separator, quote_choices, wrap_in_braces)
    (tmp_path / filename).write_text(payload, encoding="utf-8")

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert {
        "authentication_secret_literal",
        "notion_private_url",
        "google_drive_identifier",
    } <= rules


def test_scanner_allows_generic_quoted_structured_values_without_private_context(
    tmp_path: Path,
) -> None:
    (tmp_path / "generic.json").write_text(
        "{\n"
        '  "authorization_status": "enabled",\n'
        '  "api_keys": ["documentation"],\n'
        '  "client_secret_hint": "configured elsewhere",\n'
        '  "notion_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",\n'
        '  "file_id": "1QrStUvWxYz012345"\n'
        "}\n",
        encoding="utf-8",
    )

    assert scan_tree(tmp_path, "michal24749@gmail.com") == []


def test_scanner_detects_structured_connector_response_ids_without_flagging_unrelated_uuids(
    tmp_path: Path,
) -> None:
    notion_page_uuid = "123e4567-e89b-12d3-a456-426614174000"
    unrelated_uuid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    synthetic_file_value = "1AbCdEfGhIjKlMnOp" + "QrStUvWxYz012345"
    (tmp_path / "connector-response.json").write_text(
        "{\n"
        '  "object": "page",\n'
        f'  "id": "{notion_page_uuid}"\n'
        "}\n"
        "{\n"
        '  "kind": "drive#file",\n'
        f'  "id": "{synthetic_file_value}"\n'
        "}\n"
        f'unrelated_uuid = "{unrelated_uuid}"\n',
        encoding="utf-8",
    )

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    assert {(item.line, item.rule) for item in findings} == {
        (3, "notion_private_url"),
        (7, "google_drive_identifier"),
    }


def test_scanner_recursively_detects_nested_notion_gmail_and_people_payloads(
    tmp_path: Path,
) -> None:
    page_uuid = "123e4567-e89b-12d3-a456-426614174000"
    database_uuid = "b" * 32
    block_uuid = "323e4567-e89b-12d3-a456-426614174000"
    (tmp_path / "connector-response.json").write_text(
        "{\n"
        '  "result": {\n'
        '    "records": [\n'
        "      {\n"
        '        "object": "page",\n'
        f'        "id": "{page_uuid}",\n'
        '        "properties": {"Title": {"title": [{"plain_text": "Synthetic"}]}}\n'
        "      },\n"
        "      {\n"
        '        "object": "database",\n'
        f'        "id": "{database_uuid}",\n'
        '        "properties": {"Status": {"type": "select"}}\n'
        "      },\n"
        "      {\n"
        '        "object": "block",\n'
        f'        "id": "{block_uuid}",\n'
        '        "type": "paragraph"\n'
        "      },\n"
        "      {\n"
        '        "object": "page",\n'
        '        "properties": {"Title": {"title": [{"plain_text": "Synthetic partial response"}]}}\n'
        "      },\n"
        "      {\n"
        '        "id": "synthetic-message",\n'
        '        "threadId": "synthetic-thread",\n'
        '        "snippet": "Synthetic private Gmail excerpt",\n'
        '        "payload": {\n'
        '          "headers": [{"name": "Subject", "value": "Synthetic subject"}],\n'
        '          "body": {"data": "c3ludGhldGlj"}\n'
        "        }\n"
        "      },\n"
        "      {\n"
        '        "resourceName": "people/synthetic-contact",\n'
        '        "names": [{"displayName": "Synthetic Contact"}],\n'
        '        "relations": [{"type": "assistant", "person": "Synthetic Relation"}]\n'
        "      }\n"
        "    ]\n"
        "  }\n"
        "}\n",
        encoding="utf-8",
    )

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    rules = [finding.rule for finding in findings]
    assert rules.count("notion_private_url") == 4
    assert "gmail_connector_response" in rules
    assert "people_connector_response" in rules
    assert all("Synthetic private Gmail excerpt" not in finding.excerpt for finding in findings)


def test_scanner_detects_nested_connector_payloads_in_yaml_and_zip_members(
    tmp_path: Path,
) -> None:
    synthetic_contact_email = "synthetic.contact" + "@public.example"
    payload = f"""\
response:
  thread:
    id: synthetic-thread
    historyId: synthetic-history
    messages:
      - id: synthetic-message
        threadId: synthetic-thread
        payload:
          headers:
            - name: Subject
              value: Synthetic subject
          body:
            data: c3ludGhldGlj
  contacts:
    - resourceName: people/synthetic-contact
      names:
        - displayName: Synthetic Contact
      emailAddresses:
        - value: {synthetic_contact_email}
"""
    (tmp_path / "connector-response.yaml").write_text(payload, encoding="utf-8")
    with zipfile.ZipFile(tmp_path / "connector-export.zip", "w") as archive:
        archive.writestr("exports/response.yml", payload)

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    source_rules = {
        finding.rule for finding in findings if finding.path == "connector-response.yaml"
    }
    archive_rules = {
        finding.rule
        for finding in findings
        if finding.path == "connector-export.zip!exports/response.yml"
    }
    assert {"gmail_connector_response", "people_connector_response"} <= source_rules
    assert {"gmail_connector_response", "people_connector_response"} <= archive_rules


@pytest.mark.parametrize(
    ("location", "writer", "expected_path"),
    [
        (
            "connector.yaml",
            lambda path, payload: path.write_text(payload, encoding="utf-8"),
            "connector.yaml",
        ),
        (
            "connector.md",
            lambda path, payload: path.write_text(
                f"""\\
```yaml
{payload}```
""",
                encoding="utf-8",
            ),
            "connector.md",
        ),
        (
            "connector.zip",
            lambda path, payload: _write_zip_member(path, "nested/connector.yml", payload),
            "connector.zip!nested/connector.yml",
        ),
    ],
)
def test_scanner_fails_closed_for_malformed_yaml_connector_payloads(
    tmp_path: Path,
    location: str,
    writer: Callable[[Path, str], object],
    expected_path: str,
) -> None:
    payload = """\\
object: page
id: 123e4567-e89b-12d3-a456-426614174000
    properties: [unterminated
"""
    path = tmp_path / location
    writer(path, payload)

    with pytest.raises(PublicSafetyError, match=rf"malformed structured document: {expected_path}"):
        scan_tree(tmp_path, "michal24749@gmail.com")


def _write_zip_member(path: Path, member_name: str, contents: str) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(member_name, contents)


@pytest.mark.parametrize("filename", ["ordinary.md", "archive.zip"])
def test_scanner_enforces_stat_size_limit_before_reading_disk_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, filename: str
) -> None:
    path = tmp_path / filename
    if path.suffix == ".zip":
        _write_zip_member(path, "safe.md", "safe")
    else:
        path.write_text("safe", encoding="utf-8")
    monkeypatch.setattr(scanner, "MAX_SCANNED_FILE_SIZE", 1)
    original_read_bytes = Path.read_bytes

    def fail_if_read(candidate: Path) -> bytes:
        if candidate == path:
            pytest.fail("scanner read an oversized on-disk file before its stat limit check")
        return original_read_bytes(candidate)

    monkeypatch.setattr(Path, "read_bytes", fail_if_read)

    with pytest.raises(PublicSafetyError, match=rf"file exceeds size limit: {filename}"):
        scan_tree(tmp_path, "michal24749@gmail.com")


def test_scanner_enforces_zip_archive_stat_limit_before_reading(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    archive = tmp_path / "oversized.zip"
    _write_zip_member(archive, "safe.md", "safe")
    monkeypatch.setattr(scanner, "MAX_ZIP_ARCHIVE_SIZE", 1)
    original_read_bytes = Path.read_bytes

    def fail_if_read(candidate: Path) -> bytes:
        if candidate == archive:
            pytest.fail("scanner read an oversized ZIP before its stat limit check")
        return original_read_bytes(candidate)

    monkeypatch.setattr(Path, "read_bytes", fail_if_read)

    with pytest.raises(PublicSafetyError, match="ZIP archive exceeds size limit: oversized.zip"):
        scan_file(archive, "michal24749@gmail.com")


def test_scanner_allows_generic_fictional_json_without_connector_context(tmp_path: Path) -> None:
    (tmp_path / "fictional.json").write_text(
        "{\n"
        '  "id": "fictional-record",\n'
        '  "properties": {"title": "Synthetic"},\n'
        '  "identity": {"displayName": "Synthetic Person"},\n'
        '  "relationships": ["Synthetic Relation"],\n'
        '  "excerpt": "Illustrative data only"\n'
        "}\n",
        encoding="utf-8",
    )

    assert scan_tree(tmp_path, "michal24749@gmail.com") == []


def test_scanner_scans_every_relative_file_and_directory_path(tmp_path: Path) -> None:
    private_email = "private.user" + "@example.test"
    directory_with_private_email = tmp_path / "nested" / private_email
    directory_with_private_email.mkdir(parents=True)
    private_repo_path = tmp_path / "oloix888" / "Apex"
    private_repo_path.mkdir(parents=True)
    synthetic_folder_value = "1AbCdEfGh" + "IjKlMnOp"
    drive_folder_path = "folder" + f"_id={synthetic_folder_value}"
    (tmp_path / drive_folder_path).write_text("safe", encoding="utf-8")
    private_repository = "/".join(("oloix888", "Apex"))

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    assert {(item.path, item.rule) for item in findings} >= {
        (f"nested/{private_email}", "non_allowlisted_email"),
        (private_repository, "private_repo_reference"),
        (drive_folder_path, "google_drive_identifier"),
    }


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


@pytest.mark.parametrize("label", ["secret", "client_secret", "clientSecret"])
def test_scanner_catches_nonempty_secret_assignments_in_supported_label_styles(
    tmp_path: Path, label: str
) -> None:
    (tmp_path / "settings.conf").write_text(
        f"{label} = synthetic-value\n", encoding="utf-8"
    )

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "authentication_secret_literal" in rules


def test_scanner_allows_empty_secret_assignment(tmp_path: Path) -> None:
    label = "se" + "cret"
    (tmp_path / "settings.conf").write_text(f'{label} = ""\n', encoding="utf-8")

    assert scan_tree(tmp_path, "michal24749@gmail.com") == []


@pytest.mark.parametrize(
    "path",
    [
        "/open?id=1AbCdEfGhIjKlMnOp",
        "/uc?id=1AbCdEfGhIjKlMnOp",
        "/drive/u/0/open?id=1AbCdEfGhIjKlMnOp",
        "/file/u/0/d/1AbCdEfGhIjKlMnOp/view",
    ],
)
def test_scanner_detects_google_drive_query_url_forms(tmp_path: Path, path: str) -> None:
    drive_host = "drive.google" + ".com"
    (tmp_path / "private-url.txt").write_text(
        f"https://{drive_host}{path}\n", encoding="utf-8"
    )

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "google_drive_identifier" in rules


@pytest.mark.parametrize(
    "path",
    [
        "/document/d/1AbCdEfGhIjKlMnOp/edit",
        "/document/u/0/d/1AbCdEfGhIjKlMnOp/edit",
        "/spreadsheets/d/1AbCdEfGhIjKlMnOp/edit",
        "/spreadsheets/u/0/d/1AbCdEfGhIjKlMnOp/edit",
        "/presentation/d/1AbCdEfGhIjKlMnOp/edit",
        "/presentation/u/0/d/1AbCdEfGhIjKlMnOp/edit",
    ],
)
def test_scanner_detects_google_docs_document_urls(tmp_path: Path, path: str) -> None:
    docs_host = "docs.google" + ".com"
    (tmp_path / "private-url.txt").write_text(
        f"https://{docs_host}{path}\n", encoding="utf-8"
    )

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "google_drive_identifier" in rules


@pytest.mark.parametrize(
    "contents",
    [
        "Authorization: " + "Ba" + "sic c3ludGhldGljOnNlY3JldA==\n",
        "Authorization: " + "Be" + "arer\n  synthetic-token\n",
        "Authorization:\n  " + "Be" + "arer synthetic-token\n",
    ],
)
def test_scanner_detects_basic_and_multiline_bearer_credentials(
    tmp_path: Path, contents: str
) -> None:
    (tmp_path / "credentials.txt").write_text(contents, encoding="utf-8")

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    assert {(item.path, item.line, item.rule) for item in findings} == {
        ("credentials.txt", 1, "authentication_secret_literal")
    }


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


def test_scanner_scans_zip_archive_comment_and_trailing_bytes(tmp_path: Path) -> None:
    private_email = "private.user" + "@example.com"
    archive_path = tmp_path / "metadata.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("safe.md", "safe")
        archive.comment = f"comment: {private_email}".encode("utf-8")
    archive_path.write_bytes(archive_path.read_bytes() + f"tail: {private_email}".encode("utf-8"))

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    assert {(finding.path, finding.rule) for finding in findings} == {
        ("metadata.zip!<archive-comment>", "non_allowlisted_email"),
        ("metadata.zip!<trailing-bytes>", "non_allowlisted_email"),
    }


def _zip_extra_field(field_id: int, value: bytes) -> bytes:
    return field_id.to_bytes(2, "little") + len(value).to_bytes(2, "little") + value


def test_scanner_scans_zip_member_comment_and_extra_metadata_at_every_nesting_level(
    tmp_path: Path,
) -> None:
    synthetic_private_email = b"synthetic.private" + b"@example.test"
    inner_bytes = io.BytesIO()
    inner_member = zipfile.ZipInfo("safe.md")
    inner_member.comment = b"inner-comment: " + synthetic_private_email
    inner_member.extra = _zip_extra_field(0xCAFE, b"inner-extra: " + synthetic_private_email)
    with zipfile.ZipFile(inner_bytes, "w") as archive:
        archive.writestr(inner_member, b"safe")

    outer_member = zipfile.ZipInfo("nested/inner.zip")
    outer_member.comment = b"outer-comment: " + synthetic_private_email
    outer_member.extra = _zip_extra_field(0xBEEF, b"outer-extra: " + synthetic_private_email)
    with zipfile.ZipFile(tmp_path / "outer.zip", "w") as archive:
        archive.writestr(outer_member, inner_bytes.getvalue())

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    assert {(finding.path, finding.rule) for finding in findings} == {
        ("outer.zip!nested/inner.zip!<member-comment>", "non_allowlisted_email"),
        ("outer.zip!nested/inner.zip!<member-extra:0xbeef>", "non_allowlisted_email"),
        (
            "outer.zip!nested/inner.zip!safe.md!<member-comment>",
            "non_allowlisted_email",
        ),
        (
            "outer.zip!nested/inner.zip!safe.md!<member-extra:0xcafe>",
            "non_allowlisted_email",
        ),
    }


@pytest.mark.parametrize(
    ("metadata_kind", "metadata", "expected_location"),
    [
        ("comment", b"unsafe\x00metadata", "metadata.zip!safe.md!<member-comment>"),
        (
            "extra",
            _zip_extra_field(0xCAFE, b"unsafe\xffmetadata"),
            "metadata.zip!safe.md!<member-extra:0xcafe>",
        ),
    ],
)
def test_scanner_fails_closed_for_unclassified_zip_member_metadata(
    tmp_path: Path, metadata_kind: str, metadata: bytes, expected_location: str
) -> None:
    member = zipfile.ZipInfo("safe.md")
    setattr(member, metadata_kind, metadata)
    with zipfile.ZipFile(tmp_path / "metadata.zip", "w") as archive:
        archive.writestr(member, b"safe")

    with pytest.raises(PublicSafetyError, match=f"unclassified ZIP metadata: {expected_location}"):
        scan_tree(tmp_path, "michal24749@gmail.com")


@pytest.mark.parametrize("metadata_kind", ["comment", "extra"])
def test_scanner_fails_closed_for_oversized_zip_member_metadata(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, metadata_kind: str
) -> None:
    member = zipfile.ZipInfo("safe.md")
    metadata = b"xx"
    setattr(
        member,
        metadata_kind,
        metadata if metadata_kind == "comment" else _zip_extra_field(0xCAFE, metadata),
    )
    with zipfile.ZipFile(tmp_path / "metadata.zip", "w") as archive:
        archive.writestr(member, b"safe")
    monkeypatch.setattr(scanner, "MAX_ZIP_MEMBER_METADATA_SIZE", 1)

    expected_location = (
        "metadata.zip!safe.md!<member-comment>"
        if metadata_kind == "comment"
        else "metadata.zip!safe.md!<member-extra:0xcafe>"
    )
    with pytest.raises(
        PublicSafetyError,
        match=f"ZIP metadata exceeds size limit: {expected_location}",
    ):
        scan_tree(tmp_path, "michal24749@gmail.com")


def test_scanner_fails_closed_for_malformed_zip_member_extra_metadata(tmp_path: Path) -> None:
    member = zipfile.ZipInfo("safe.md")
    member.extra = b"\xfe\xca\x01\x00"

    with pytest.raises(
        PublicSafetyError,
        match="malformed ZIP metadata: metadata.zip!safe.md!<member-extra:0xcafe>",
    ):
        list(scanner._iter_zip_member_extra_metadata(member, "metadata.zip!safe.md"))

    with zipfile.ZipFile(tmp_path / "metadata.zip", "w") as archive:
        archive.writestr(member, b"safe")

    with pytest.raises(PublicSafetyError, match="invalid ZIP archive: metadata.zip"):
        scan_tree(tmp_path, "michal24749@gmail.com")


def test_scanner_fails_closed_for_zip_trailing_bytes_beyond_the_zip_comment_window(
    tmp_path: Path,
) -> None:
    private_email = "private.user" + "@example.com"
    archive_path = tmp_path / "long-tail.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("safe.md", "safe")
    archive_path.write_bytes(
        archive_path.read_bytes() + (b"safe-" * 14_000) + private_email.encode("utf-8")
    )

    with pytest.raises(PublicSafetyError, match="invalid ZIP archive: long-tail.zip"):
        scan_tree(tmp_path, "michal24749@gmail.com")


@pytest.mark.parametrize(
    ("metadata_kind", "expected_location"),
    [
        ("comment", "metadata.zip!<archive-comment>"),
        ("trailing", "metadata.zip!<trailing-bytes>"),
    ],
)
def test_scanner_fails_closed_for_unclassified_zip_metadata(
    tmp_path: Path, metadata_kind: str, expected_location: str
) -> None:
    archive_path = tmp_path / "metadata.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("safe.md", "safe")
        if metadata_kind == "comment":
            archive.comment = b"\xff"
    if metadata_kind == "trailing":
        archive_path.write_bytes(archive_path.read_bytes() + b"\xff")

    with pytest.raises(PublicSafetyError, match=f"unclassified ZIP metadata: {expected_location}"):
        scan_tree(tmp_path, "michal24749@gmail.com")


def test_scanner_scans_zip_archive_and_member_names_at_every_nesting_level(
    tmp_path: Path,
) -> None:
    private_email = "private.user" + "@example.com"
    inner_bytes = io.BytesIO()
    with zipfile.ZipFile(inner_bytes, "w") as archive:
        archive.writestr("safe.md", "safe")
    outer_path = tmp_path / f"{private_email}.zip"
    with zipfile.ZipFile(outer_path, "w") as archive:
        archive.writestr(f"nested/{private_email}.zip", inner_bytes.getvalue())

    findings = scan_tree(tmp_path, "michal24749@gmail.com")

    assert {(finding.path, finding.rule) for finding in findings} == {
        (f"{private_email}.zip", "non_allowlisted_email"),
        (f"{private_email}.zip!<archive-name>", "non_allowlisted_email"),
        (f"{private_email}.zip!nested/{private_email}.zip!<member-name>", "non_allowlisted_email"),
        (
            f"{private_email}.zip!nested/{private_email}.zip!<archive-name>",
            "non_allowlisted_email",
        ),
    }


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
    [
        Path(".superpowers/sdd/unlisted.md"),
        Path("docs/superpowers/unlisted.md"),
        # This exact location was once excluded as a whole. A non-allowlisted
        # email here must now fail the same way as it would anywhere else.
        Path(".superpowers/sdd/progress.md"),
    ],
)
def test_scanner_scans_governance_and_documentation_files(
    tmp_path: Path, relative: Path
) -> None:
    private_email = "private.user" + "@example.com"
    unsafe = tmp_path / relative
    unsafe.parent.mkdir(parents=True)
    unsafe.write_text(private_email, encoding="utf-8")

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "non_allowlisted_email" in rules


def test_historical_reference_policy_does_not_suppress_email_or_secret(
    tmp_path: Path,
) -> None:
    private_email = "private.user" + "@example.com"
    private_tracker = "/".join(("oloix888", "Apex"))
    token_key = "".join(("to", "ken"))
    former_exclusion = tmp_path / ".superpowers/sdd/progress.md"
    former_exclusion.parent.mkdir(parents=True)
    former_exclusion.write_text(
        f"Historical tracking: {private_tracker}\n"
        f"Unexpected contact: {private_email}\n"
        f"{token_key}=synthetic-value\n",
        encoding="utf-8",
    )

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "non_allowlisted_email" in rules
    assert "authentication_secret_literal" in rules


def test_scanner_detects_non_historical_private_manifest_reference(tmp_path: Path) -> None:
    private_manifest = "emma-workspace" + "-memory"
    (tmp_path / "unsafe-manifest.md").write_text(
        f"manifest = {private_manifest}\n", encoding="utf-8"
    )

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert "private_manifest_reference" in rules


@pytest.mark.parametrize(
    "historical_line",
    [
        "Private task repository: " + scanner.PRIVATE_REPOSITORY,
        "migration baseline: " + scanner.PRIVATE_MANIFEST + " 5.6.0",
    ],
)
def test_historical_reference_exceptions_do_not_apply_outside_repository_root_docs(
    tmp_path: Path, historical_line: str
) -> None:
    (tmp_path / "package-content.md").write_text(historical_line, encoding="utf-8")

    rules = {finding.rule for finding in scan_tree(tmp_path, "michal24749@gmail.com")}

    assert rules & {"private_repo_reference", "private_manifest_reference"}


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
