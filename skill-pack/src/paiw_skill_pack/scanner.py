from __future__ import annotations

from dataclasses import dataclass
import io
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import stat
import zipfile

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

# Public-root policy: inspect every regular UTF-8 text file, irrespective of
# suffix. The exclusions are private VCS internals and generated environments
# or caches. Known binary formats are inspected as lossless Latin-1 text so
# ASCII private identifiers cannot be hidden by a misleading extension.
EXCLUDED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".nox",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "node_modules",
    }
)
BINARY_SUFFIXES = frozenset(
    {
        ".7z",
        ".bmp",
        ".class",
        ".dll",
        ".eot",
        ".gif",
        ".gz",
        ".ico",
        ".jar",
        ".jpeg",
        ".jpg",
        ".mp3",
        ".mp4",
        ".o",
        ".otf",
        ".pdf",
        ".png",
        ".pyc",
        ".so",
        ".tar",
        ".tgz",
        ".ttf",
        ".wasm",
        ".webp",
        ".woff",
        ".woff2",
        ".zip",
    }
)
PUBLIC_PROJECT_EMAIL = "michal24749@gmail.com"
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PRIVATE_REPOSITORY = "oloix888" + "/" + "Apex"
PRIVATE_MANIFEST = "emma-workspace" + "-memory"
# Historical-reference exceptions apply only to the checked-out repository's
# public documentation. They never apply to a package, build staging tree, or
# archive, even when an exact historical line is copied there.
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_DOCUMENTATION_DIRECTORIES = frozenset({"docs"})
REPOSITORY_DOCUMENTATION_FILES = frozenset({".superpowers/sdd/progress.md"})
# These exact historical public-document lines and published Apex #6--#18
# references are retained only to explain the approved migration boundary.
# The policy suppresses neither arbitrary repository references nor any email,
# secret, Notion/Drive identifier, or other private value. Any documentation
# change that adds a private-manifest reference must be reviewed and added here
# explicitly.
APPROVED_HISTORICAL_MANIFEST_LINES = frozenset(
    {
        f"- Verified migration baseline and rollback target: {PRIVATE_MANIFEST} 5.6.0.",
        f"The private `{PRIVATE_MANIFEST} v6.0.0` adapter must:",
        (
            "- No public runtime package may contain private Notion IDs, private Google "
            f"account or Drive folder IDs, `{PRIVATE_REPOSITORY}`, private contacts, Gmail "
            f"content, or the private `{PRIVATE_MANIFEST}` manifest."
        ),
        (
            f"**Goal:** Migrate the private `{PRIVATE_MANIFEST}` skill from v5.5.0 to a thin "
            "v6.0.0 adapter that composes the public Personal AI Workspace Skill Pack with "
            "Michał's private identities, source map, Constitution, task backend and one-time "
            "disclosure controls."
        ),
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/SKILL.md`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/agents/openai.yaml`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/references/private-workspace-manifest.example.md`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/references/public-skill-compatibility.json`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/tests/test_adapter_contract.py`",
        f"python -m pytest private/{PRIVATE_MANIFEST}-v6/tests/test_adapter_contract.py -v",
        f"git add private/{PRIVATE_MANIFEST}-v6",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/scripts/load_private_manifest.py`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/references/private-manifest.schema.json`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/tests/test_private_manifest.py`",
        f"python -m pytest private/{PRIVATE_MANIFEST}-v6/tests/test_private_manifest.py -v",
        (
            f"git add private/{PRIVATE_MANIFEST}-v6/scripts "
            f"private/{PRIVATE_MANIFEST}-v6/references/private-manifest.schema.json "
            f"private/{PRIVATE_MANIFEST}-v6/tests"
        ),
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/references/external-disclosure-routing.md`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/scripts/validate_private_disclosure.py`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/tests/test_private_disclosure.py`",
        f"python -m pytest private/{PRIVATE_MANIFEST}-v6/tests/test_private_disclosure.py -v",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/references/context-routing.md`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/tests/test_context_routing.py`",
        f"- Modify: `private/{PRIVATE_MANIFEST}-v6/SKILL.md`",
        f"python -m pytest private/{PRIVATE_MANIFEST}-v6/tests/test_context_routing.py -v",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/migrations/5.5.0-to-6.0.0/migration.json`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/migrations/5.5.0-to-6.0.0/preconditions.md`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/migrations/5.5.0-to-6.0.0/operations.md`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/migrations/5.5.0-to-6.0.0/validation.md`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/migrations/5.5.0-to-6.0.0/rollback.md`",
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/tests/test_migration.py`",
        f"python -m pytest private/{PRIVATE_MANIFEST}-v6/tests/test_migration.py -v",
        (
            f"git add private/{PRIVATE_MANIFEST}-v6/migrations "
            f"private/{PRIVATE_MANIFEST}-v6/tests/test_migration.py"
        ),
        f"- Create: `private/{PRIVATE_MANIFEST}-v6/tests/test_packaging.py`",
        (
            "**Applies to:** public creator, Installer & Upgrader skill, Context Bootstrap skill, "
            "public ChatGPT/Codex Skill Pack, Codex installers and AGENTS.md guidance, future "
            "specialist skills, public documentation and tests, plus the private "
            f"`{PRIVATE_MANIFEST} v6.0.0` adapter."
        ),
        f"migration baseline: {PRIVATE_MANIFEST} 5.6.0",
        f"rollback target: {PRIVATE_MANIFEST} 5.6.0",
        f"build target: {PRIVATE_MANIFEST} 6.0.0-rc.1",
        (
            "**Applies to:** public creator, Installer & Upgrader, Context Bootstrap, shared "
            "Skill Pack contracts, ChatGPT/Codex installation guidance, validators, migrations, "
            "tests, release gates, and private "
            f"`{PRIVATE_MANIFEST} v6.0.0` adapter."
        ),
        f"**Target private adapter:** `{PRIVATE_MANIFEST} 6.0.0-rc.1`",
        f"{PRIVATE_MANIFEST} 6.0.0-rc.1",
    }
)
APPROVED_HISTORICAL_REPOSITORY_REFERENCES = frozenset(
    f"{PRIVATE_REPOSITORY.lower()}#{issue_number}" for issue_number in range(6, 19)
)
APPROVED_HISTORICAL_REPOSITORY_LINES = frozenset(
    {
        (
            "- Public packages contain no private Emma Workspace identifiers, private accounts, "
            "contacts, Gmail content, or "
            f"`{PRIVATE_REPOSITORY}` runtime references."
        ),
        (
            "- No public runtime package may contain private Notion IDs, private Google account "
            "or Drive folder IDs, "
            f"`{PRIVATE_REPOSITORY}`, private contacts, Gmail content, or the private "
            f"`{PRIVATE_MANIFEST}` manifest."
        ),
        f'PRIVATE_REPO_RE = re.compile(r"\\b{PRIVATE_REPOSITORY}\\b", re.IGNORECASE)',
        f"Private task repository: {PRIVATE_REPOSITORY}",
        f"- `{PRIVATE_REPOSITORY}` references inside public runtime packages;",
    }
)
PRIVATE_REPO_RE = re.compile(
    r"\b" + re.escape(PRIVATE_REPOSITORY) + r"(?:#\d+)?\b", re.IGNORECASE
)
AUTH_SECRET_RE = re.compile(
    r"""(?ix)
    (?:
        (?:
            \b(?:
                password|
                one[- ]time[ -]?code|
                reset[ -]?link|
                api[ _-]?key|
                access[ _-]?token|
                private[ _-]?key|
                session[ _-]?cookie|
                client[ _-]?secret|
                secret
            )\b
        |
        (?<![A-Za-z0-9_-])token\b
        |
        (?<![A-Za-z0-9_-])cookie\b
        )\s*[:=]\s*
        (?=
            (?:
                ["']\s*[^"'\s]
                |
                [^'"\s#;]
            )
        )
        |
        \bauthorization\b\s*[:=]\s*(?:bearer|basic)\b\s+\S+
    )
    """
)
MULTILINE_AUTH_SECRET_RE = re.compile(
    r"""(?ix)
    (?:
        \bauthorization\b[ \t]*[:=][ \t]*(?:bearer|basic)\b[ \t]*\r?\n[ \t]+\S+
        |
        \bauthorization\b[ \t]*[:=][ \t]*\r?\n[ \t]*(?:bearer|basic)\b[ \t]+\S+
    )
    """
)
NOTION_PRIVATE_RE = re.compile(
    r"(?i)(?:https?://(?:www\.)?notion\.(?:site|so)/[^\s)]+|"
    r"https?://(?:www\.)?notion\.com/[^\s)]*(?<![0-9a-f-])(?:[0-9a-f]{32}|"
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
    r"(?![0-9a-f-])(?=[/?#\s)'\".,;:]|$)|"
    r"\b(?:notion[_ -]?)?(?:page|database|view)[_ -]?id\b\s*[:=]\s*[\"']?[0-9a-f-]{32,})"
)
GOOGLE_DRIVE_URL_RE = re.compile(
    r"(?i)(?:"
    r"https?://drive\.google\.com/(?:"
    r"(?:drive/(?:u/\d+/)?folders|file/(?:u/\d+/)?d)/[A-Za-z0-9_-]+"
    r"|(?:open|uc|drive/u/\d+/open)\?[^#\s]*\bid=[A-Za-z0-9_-]+"
    r")"
    r"|https?://docs\.google\.com/(?:document|spreadsheets|presentation)/(?:u/\d+/)?d/"
    r"[A-Za-z0-9_-]+(?:[/?#]|\b)"
    r")"
)
GOOGLE_DRIVE_ID_RE = re.compile(
    r"(?i)\b(?:folder[_ -]?id|drive[_ -]?(?:folder|file)?[_ -]?id|google[_ -]?drive[_ -]?id)\b"
    r"\s*[:=]\s*[\"']?[A-Za-z0-9_-]{10,}"
)
NOTION_RESPONSE_OBJECTS = frozenset({"page", "database", "block"})
NOTION_IDENTIFIER_RE = re.compile(
    r"(?i)^(?:[0-9a-f]{32}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12})$"
)
GMAIL_MESSAGE_SENSITIVE_FIELDS = frozenset({"snippet", "raw", "body"})
GMAIL_PAYLOAD_SENSITIVE_FIELDS = frozenset({"headers", "body", "parts"})
PEOPLE_SENSITIVE_FIELDS = frozenset(
    {
        "names",
        "emailaddresses",
        "relations",
        "phonenumbers",
        "organizations",
        "biographies",
    }
)
STRUCTURED_FENCE_RE = re.compile(
    r"(?ms)^[ \t]*```(?:json|yaml|yml)[ \t]*\r?$\n(.*?)^[ \t]*```[ \t]*\r?$"
)
PRIVATE_MANIFEST_RE = re.compile(r"\b" + re.escape(PRIVATE_MANIFEST) + r"\b", re.IGNORECASE)
ZIP_SIGNATURES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
# Archive inspection is deliberately bounded. Limits apply to each archive in
# a nested chain so untrusted public artifacts cannot consume unbounded memory
# or decompression work while the scanner fails closed.
MAX_ZIP_ARCHIVE_SIZE = 50 * 1024 * 1024
MAX_ZIP_MEMBER_COUNT = 1_024
MAX_ZIP_MEMBER_SIZE = 10 * 1024 * 1024
MAX_ZIP_TOTAL_UNCOMPRESSED_SIZE = 50 * 1024 * 1024
MAX_ZIP_NESTED_DEPTH = 3
# ZIP headers use 16-bit metadata lengths. Cap individual member metadata at
# 32 KiB so a malicious archive cannot use every format-allowed byte without
# inspection.
MAX_ZIP_MEMBER_METADATA_SIZE = 32 * 1024


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    line: int
    rule: str
    excerpt: str


class PublicSafetyError(RuntimeError):
    pass


def _is_excluded_directory(relative: Path) -> bool:
    return relative.name in EXCLUDED_DIRECTORY_NAMES


def _display_relative_path(root: Path, path: str | Path | None) -> str:
    if path is None:
        return str(root)
    candidate = Path(path)
    for base in (root, root.resolve()):
        try:
            return candidate.relative_to(base).as_posix()
        except ValueError:
            continue
    return candidate.as_posix()


def _raise_walk_error(root: Path, error: OSError) -> None:
    location = _display_relative_path(root, error.filename)
    raise PublicSafetyError(f"unable to scan directory: {location}") from error


def _iter_public_paths(root: Path):
    for directory, directory_names, filenames in os.walk(
        root,
        followlinks=False,
        onerror=lambda error: _raise_walk_error(root, error),
    ):
        directory_path = Path(directory)
        relative_directory = directory_path.relative_to(root)
        for name in directory_names:
            relative = relative_directory / name
            if (directory_path / name).is_symlink():
                raise PublicSafetyError(f"unable to scan symlink: {relative.as_posix()}")
            yield None, relative
        directory_names[:] = sorted(
            name
            for name in directory_names
            if not _is_excluded_directory(relative_directory / name)
        )
        for filename in sorted(filenames):
            path = directory_path / filename
            relative = path.relative_to(root)
            if path.is_symlink():
                raise PublicSafetyError(f"unable to scan symlink: {relative.as_posix()}")
            yield path if path.is_file() else None, relative


def _read_file_bytes(path: Path, relative: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise PublicSafetyError(f"unable to read file: {relative}") from exc


def _decode_contents(contents: bytes, relative: str, suffix: str) -> str:
    is_known_binary = suffix.lower() in BINARY_SUFFIXES
    if b"\x00" in contents:
        if is_known_binary:
            return contents.decode("latin-1")
        raise PublicSafetyError(f"unclassified binary-like file: {relative}")

    try:
        return contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        if is_known_binary:
            return contents.decode("latin-1")
        raise PublicSafetyError(
            f"unclassified non-UTF-8 file: {relative}"
        ) from exc


def _member_relative_path(archive_relative: str, member_name: str) -> str:
    return f"{archive_relative}!{member_name}"


def _is_repository_documentation(root: Path, relative: str) -> bool:
    """Return whether a checked-out root-documentation file may use history exceptions."""
    try:
        if root.resolve() != REPOSITORY_ROOT:
            return False
    except OSError:
        return False

    path = PurePosixPath(relative)
    return (
        relative in REPOSITORY_DOCUMENTATION_FILES
        or bool(path.parts and path.parts[0] in REPOSITORY_DOCUMENTATION_DIRECTORIES)
    )


def _validate_zip_member_path(archive_relative: str, member: zipfile.ZipInfo) -> None:
    member_path = PurePosixPath(member.filename)
    relative = _member_relative_path(archive_relative, member.filename)
    if (
        not member.filename
        or member_path.is_absolute()
        or ".." in member_path.parts
        or "\\" in member.filename
    ):
        raise PublicSafetyError(f"invalid ZIP member path: {relative}")
    if stat.S_ISLNK(member.external_attr >> 16):
        raise PublicSafetyError(f"unable to scan symlink: {relative}")
    if member.flag_bits & 0x1:
        raise PublicSafetyError(f"encrypted ZIP member: {relative}")


def _looks_like_zip(contents: bytes) -> bool:
    return contents.startswith(ZIP_SIGNATURES) or zipfile.is_zipfile(io.BytesIO(contents))


def _decode_zip_metadata(contents: bytes, relative: str) -> str:
    """Decode ZIP metadata only when it can be inspected without ambiguity."""
    if b"\x00" in contents:
        raise PublicSafetyError(f"unclassified ZIP metadata: {relative}")
    try:
        return contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PublicSafetyError(f"unclassified ZIP metadata: {relative}") from exc


def _decode_zip_member_metadata(contents: bytes, relative: str) -> str:
    if len(contents) > MAX_ZIP_MEMBER_METADATA_SIZE:
        raise PublicSafetyError(f"ZIP metadata exceeds size limit: {relative}")
    return _decode_zip_metadata(contents, relative)


def _iter_zip_member_extra_metadata(member: zipfile.ZipInfo, relative: str):
    """Yield decoded extra-field values after validating their ZIP structure."""
    extra = member.extra
    offset = 0
    while offset < len(extra):
        if len(extra) - offset < 4:
            raise PublicSafetyError(f"malformed ZIP metadata: {relative}!<member-extra>")
        field_id = int.from_bytes(extra[offset : offset + 2], "little")
        field_size = int.from_bytes(extra[offset + 2 : offset + 4], "little")
        value_start = offset + 4
        value_end = value_start + field_size
        location = f"{relative}!<member-extra:0x{field_id:04x}>"
        if value_end > len(extra):
            raise PublicSafetyError(f"malformed ZIP metadata: {location}")
        yield location, _decode_zip_member_metadata(extra[value_start:value_end], location)
        offset = value_end


def _zip_trailing_bytes(contents: bytes, archive_relative: str) -> bytes:
    """Return data after the declared end-of-central-directory record.

    ZIP permits at most 65,535 comment bytes. A reader cannot safely identify
    an end record that lies farther from EOF than that allowed structure, so
    malformed archives with a larger appended payload fail closed.
    """
    record_signature = b"PK\x05\x06"
    record_size = 22
    comment_length_offset = 20
    search_start = max(0, len(contents) - (0xFFFF + record_size))
    candidate = contents.rfind(record_signature, search_start)
    while candidate >= search_start:
        if candidate + record_size <= len(contents):
            comment_length = int.from_bytes(
                contents[
                    candidate + comment_length_offset : candidate + record_size
                ],
                "little",
            )
            declared_end = candidate + record_size + comment_length
            if declared_end <= len(contents):
                return contents[declared_end:]
        candidate = contents.rfind(record_signature, search_start, candidate)
    raise PublicSafetyError(f"invalid ZIP archive: {archive_relative}")


def _archive_leaf_name(archive_relative: str) -> str:
    return archive_relative.rsplit("!", 1)[-1]


def _iter_zip_texts(contents: bytes, archive_relative: str, nested_depth: int = 0):
    if nested_depth > MAX_ZIP_NESTED_DEPTH:
        raise PublicSafetyError(f"ZIP recursion depth exceeds limit: {archive_relative}")
    if len(contents) > MAX_ZIP_ARCHIVE_SIZE:
        raise PublicSafetyError(f"ZIP archive exceeds size limit: {archive_relative}")

    try:
        with zipfile.ZipFile(io.BytesIO(contents)) as archive:
            yield f"{archive_relative}!<archive-name>", _archive_leaf_name(archive_relative)
            if archive.comment:
                yield (
                    f"{archive_relative}!<archive-comment>",
                    _decode_zip_metadata(
                        archive.comment, f"{archive_relative}!<archive-comment>"
                    ),
                )
            trailing_bytes = _zip_trailing_bytes(contents, archive_relative)
            if trailing_bytes:
                yield (
                    f"{archive_relative}!<trailing-bytes>",
                    _decode_zip_metadata(
                        trailing_bytes, f"{archive_relative}!<trailing-bytes>"
                    ),
                )
            members = archive.infolist()
            if len(members) > MAX_ZIP_MEMBER_COUNT:
                raise PublicSafetyError(f"ZIP member count exceeds limit: {archive_relative}")
            seen_members: set[str] = set()
            total_uncompressed_size = 0
            files: list[zipfile.ZipInfo] = []
            for member in members:
                _validate_zip_member_path(archive_relative, member)
                relative = _member_relative_path(archive_relative, member.filename)
                yield f"{relative}!<member-name>", member.filename
                if member.comment:
                    yield (
                        f"{relative}!<member-comment>",
                        _decode_zip_member_metadata(
                            member.comment, f"{relative}!<member-comment>"
                        ),
                    )
                yield from _iter_zip_member_extra_metadata(member, relative)
                if member.filename in seen_members:
                    raise PublicSafetyError(f"duplicate ZIP member: {relative}")
                seen_members.add(member.filename)
                if member.is_dir():
                    continue
                if member.file_size > MAX_ZIP_MEMBER_SIZE:
                    raise PublicSafetyError(f"ZIP member exceeds size limit: {relative}")
                total_uncompressed_size += member.file_size
                if total_uncompressed_size > MAX_ZIP_TOTAL_UNCOMPRESSED_SIZE:
                    raise PublicSafetyError(
                        f"ZIP total uncompressed size exceeds limit: {archive_relative}"
                    )
                files.append(member)
            for member in files:
                relative = _member_relative_path(archive_relative, member.filename)
                member_contents = archive.read(member)
                if member.filename.lower().endswith(".zip") or _looks_like_zip(member_contents):
                    yield from _iter_zip_texts(member_contents, relative, nested_depth + 1)
                else:
                    yield relative, _decode_contents(
                        member_contents, relative, Path(member.filename).suffix
                    )
    except PublicSafetyError:
        raise
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        raise PublicSafetyError(f"invalid ZIP archive: {archive_relative}") from exc


def _scan_line(
    relative: str,
    line_number: int,
    line: str,
    public_email: str,
    allow_historical_references: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    stripped = line.strip()
    for email in EMAIL_RE.findall(line):
        if email.lower() != public_email.lower():
            findings.append(Finding(relative, line_number, "non_allowlisted_email", stripped))
    if (
        (
            not allow_historical_references
            or stripped not in APPROVED_HISTORICAL_REPOSITORY_LINES
        )
        and any(
            (
                not allow_historical_references
                or match.group(0).lower()
                not in APPROVED_HISTORICAL_REPOSITORY_REFERENCES
            )
            for match in PRIVATE_REPO_RE.finditer(line)
        )
    ):
        findings.append(Finding(relative, line_number, "private_repo_reference", stripped))
    if AUTH_SECRET_RE.search(line):
        findings.append(Finding(relative, line_number, "authentication_secret_literal", stripped))
    if NOTION_PRIVATE_RE.search(line):
        findings.append(Finding(relative, line_number, "notion_private_url", stripped))
    if GOOGLE_DRIVE_URL_RE.search(line) or GOOGLE_DRIVE_ID_RE.search(line):
        findings.append(Finding(relative, line_number, "google_drive_identifier", stripped))
    if PRIVATE_MANIFEST_RE.search(line) and (
        not allow_historical_references
        or stripped not in APPROVED_HISTORICAL_MANIFEST_LINES
    ):
        findings.append(Finding(relative, line_number, "private_manifest_reference", stripped))
    return findings


def _multiline_authentication_secret_findings(relative: str, text: str) -> list[Finding]:
    """Find folded Authorization credentials while retaining a non-secret excerpt."""
    findings: list[Finding] = []
    lines = text.splitlines()
    for match in MULTILINE_AUTH_SECRET_RE.finditer(text):
        line_number = text.count("\n", 0, match.start()) + 1
        excerpt = lines[line_number - 1].strip() if line_number <= len(lines) else "Authorization"
        findings.append(
            Finding(relative, line_number, "authentication_secret_literal", excerpt)
        )
    return findings


def _normalise_structured_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _mapping_values(node: Node) -> dict[str, Node]:
    if not isinstance(node, MappingNode):
        return {}
    return {
        _normalise_structured_key(key.value): value
        for key, value in node.value
        if isinstance(key, ScalarNode)
    }


def _scalar_value(node: Node | None) -> str | None:
    if not isinstance(node, ScalarNode):
        return None
    return node.value


def _iter_mapping_nodes(node: Node):
    """Yield every mapping node once, including recursively nested values.

    YAML aliases may make the composed document graph cyclic. Tracking node
    identity preserves complete traversal without following an alias forever.
    """
    seen: set[int] = set()

    def visit(current: Node):
        if id(current) in seen:
            return
        seen.add(id(current))
        if isinstance(current, MappingNode):
            yield current
            for key, value in current.value:
                yield from visit(key)
                yield from visit(value)
        elif isinstance(current, SequenceNode):
            for value in current.value:
                yield from visit(value)

    yield from visit(node)


def _has_gmail_payload_content(node: Node | None) -> bool:
    return bool(GMAIL_PAYLOAD_SENSITIVE_FIELDS & _mapping_values(node).keys())


def _is_gmail_message(fields: dict[str, Node]) -> bool:
    has_identity = bool(_scalar_value(fields.get("id"))) and bool(
        _scalar_value(fields.get("threadid"))
    )
    if not has_identity:
        return False
    return bool(GMAIL_MESSAGE_SENSITIVE_FIELDS & fields.keys()) or _has_gmail_payload_content(
        fields.get("payload")
    )


def _contains_gmail_message(node: Node) -> bool:
    return any(_is_gmail_message(_mapping_values(item)) for item in _iter_mapping_nodes(node))


def _is_gmail_thread(fields: dict[str, Node]) -> bool:
    return (
        bool(_scalar_value(fields.get("id")))
        and bool(_scalar_value(fields.get("historyid")))
        and fields.get("messages") is not None
        and _contains_gmail_message(fields["messages"])
    )


def _redacted_connector_excerpt(kind: str) -> str:
    return f"[redacted structured {kind} connector response]"


def _finding_for_node(
    relative: str,
    node: Node,
    line_offset: int,
    rule: str,
    kind: str,
) -> Finding:
    return Finding(
        relative,
        node.start_mark.line + 1 + line_offset,
        rule,
        _redacted_connector_excerpt(kind),
    )


def _connector_finding_for_mapping(
    relative: str, node: MappingNode, line_offset: int
) -> Finding | None:
    fields = _mapping_values(node)
    object_type = (_scalar_value(fields.get("object")) or "").lower()
    identifier = _scalar_value(fields.get("id"))
    has_notion_identifier = bool(identifier and NOTION_IDENTIFIER_RE.fullmatch(identifier))
    if object_type in NOTION_RESPONSE_OBJECTS and (
        has_notion_identifier or "properties" in fields
    ):
        return _finding_for_node(
            relative,
            fields["id"] if has_notion_identifier else node,
            line_offset,
            "notion_private_url",
            f"Notion {object_type}",
        )

    if (
        (_scalar_value(fields.get("kind")) or "").lower() == "drive#file"
        and identifier is not None
        and len(identifier) >= 10
    ):
        return _finding_for_node(
            relative, fields["id"], line_offset, "google_drive_identifier", "Google Drive file"
        )

    if _is_gmail_message(fields):
        return _finding_for_node(
            relative, node, line_offset, "gmail_connector_response", "Gmail message"
        )

    if _is_gmail_thread(fields):
        return _finding_for_node(
            relative, node, line_offset, "gmail_connector_response", "Gmail thread"
        )

    resource_name = _scalar_value(fields.get("resourcename")) or ""
    if resource_name.lower().startswith("people/") and PEOPLE_SENSITIVE_FIELDS & fields.keys():
        return _finding_for_node(
            relative, node, line_offset, "people_connector_response", "People contact"
        )
    return None


def _compose_yaml_documents(text: str):
    try:
        yield from yaml.compose_all(text, Loader=yaml.SafeLoader)
    except yaml.YAMLError:
        return


def _iter_embedded_json_documents(text: str):
    decoder = json.JSONDecoder()
    position = 0
    while position < len(text):
        starts = [index for index in (text.find("{", position), text.find("[", position)) if index >= 0]
        if not starts:
            return
        start = min(starts)
        try:
            _, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            position = start + 1
            continue
        try:
            node = yaml.compose(text[start : start + end], Loader=yaml.SafeLoader)
        except yaml.YAMLError:
            position = start + 1
            continue
        if node is not None:
            yield node, text.count("\n", 0, start)
        position = start + end


def _iter_structured_documents(text: str):
    for node in _compose_yaml_documents(text):
        if node is not None:
            yield node, 0
    for match in STRUCTURED_FENCE_RE.finditer(text):
        line_offset = text.count("\n", 0, match.start(1))
        for node in _compose_yaml_documents(match.group(1)):
            if node is not None:
                yield node, line_offset
    yield from _iter_embedded_json_documents(text)


def _connector_response_findings(relative: str, text: str) -> list[Finding]:
    """Find nested connector responses without treating ordinary JSON as private.

    Provider-specific signature combinations make copied connector payloads
    sensitive even when they contain no standalone ID, email, or secret. The
    parser considers structured JSON and YAML in every scanned text source,
    including ZIP members and fenced payloads, and only reports a mapping when
    that mapping itself establishes a Notion, Gmail, Google Drive, or People
    response context.
    """
    findings: list[Finding] = []
    for document, line_offset in _iter_structured_documents(text):
        for node in _iter_mapping_nodes(document):
            finding = _connector_finding_for_mapping(relative, node, line_offset)
            if finding is not None:
                findings.append(finding)
    return list(dict.fromkeys(findings))


def _scan_relative_path(relative: Path, public_email: str) -> list[Finding]:
    rendered = relative.as_posix()
    return _scan_line(rendered, 1, rendered, public_email, False)


def _scan_file(
    path: Path,
    relative: str,
    public_email: str,
    allow_historical_references: bool = False,
) -> list[Finding]:
    contents = _read_file_bytes(path, relative)
    if path.suffix.lower() == ".zip" or _looks_like_zip(contents):
        text_sources = (
            (text_relative, text, False)
            for text_relative, text in _iter_zip_texts(contents, relative)
        )
    else:
        text_sources = (
            (relative, _decode_contents(contents, relative, path.suffix), allow_historical_references),
        )

    findings: list[Finding] = []
    for text_relative, text, source_allows_historical_references in text_sources:
        findings.extend(_connector_response_findings(text_relative, text))
        findings.extend(_multiline_authentication_secret_findings(text_relative, text))
        for line_number, line in enumerate(text.splitlines(), 1):
            findings.extend(
                _scan_line(
                    text_relative,
                    line_number,
                    line,
                    public_email,
                    source_allows_historical_references,
                )
            )
    return list(dict.fromkeys(findings))


def scan_file(path: Path, public_email: str = PUBLIC_PROJECT_EMAIL) -> list[Finding]:
    if path.is_symlink():
        raise PublicSafetyError(f"unable to scan symlink: {path}")
    if not path.is_file():
        raise PublicSafetyError(f"scan target is not a file: {path}")
    return _scan_file(path, path.name, public_email)


def scan_tree(root: Path, public_email: str = PUBLIC_PROJECT_EMAIL) -> list[Finding]:
    if root.is_symlink():
        raise PublicSafetyError(f"unable to scan symlink: {root}")
    if not root.is_dir():
        raise PublicSafetyError(f"scan root is not a directory: {root}")

    findings: list[Finding] = []
    for path, relative_path in _iter_public_paths(root):
        relative = relative_path.as_posix()
        findings.extend(_scan_relative_path(relative_path, public_email))
        if path is None:
            continue
        findings.extend(
            _scan_file(
                path,
                relative,
                public_email,
                _is_repository_documentation(root, relative),
            )
        )
    return findings


def _assert_no_findings(findings: list[Finding]) -> None:
    if findings:
        detail = "\n".join(
            f"{item.path}:{item.line} [{item.rule}] {item.excerpt}" for item in findings
        )
        raise PublicSafetyError(detail)


def assert_public_safe(root: Path, public_email: str = PUBLIC_PROJECT_EMAIL) -> None:
    findings = scan_tree(root, public_email)
    _assert_no_findings(findings)


def assert_public_file_safe(path: Path, public_email: str = PUBLIC_PROJECT_EMAIL) -> None:
    _assert_no_findings(scan_file(path, public_email))
