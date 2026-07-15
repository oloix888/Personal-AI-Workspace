from __future__ import annotations

from dataclasses import dataclass
import io
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import stat
import zipfile

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
# Public governance records are scanned by default. These exact approved
# planning records intentionally quote restricted identifiers to document the
# public/private boundary; do not replace this list with a directory-level
# exclusion. New files in either public documentation tree remain scan scope.
EXCLUDED_RELATIVE_FILES = frozenset(
    {
        Path(".superpowers/sdd/progress.md"),
        Path("docs/superpowers/plans/2026-07-15-capability-catalog-plugin-orchestration.md"),
        Path("docs/superpowers/plans/2026-07-15-constitution-truncation-hardening.md"),
        Path("docs/superpowers/plans/2026-07-15-live-bootstrap-evidence-task-reconciliation.md"),
        Path("docs/superpowers/plans/2026-07-15-private-emma-workspace-adapter-v6.md"),
        Path("docs/superpowers/plans/2026-07-15-skill-pack-foundation-build-pipeline.md"),
        Path("docs/superpowers/specs/2026-07-15-autonomous-memory-capture-design.md"),
        Path("docs/superpowers/specs/2026-07-15-capability-catalog-plugin-orchestration-design.md"),
        Path("docs/superpowers/specs/2026-07-15-constitution-truncation-safety-addendum.md"),
        Path("docs/superpowers/specs/2026-07-15-live-bootstrap-evidence-task-reconciliation-addendum.md"),
        Path("docs/superpowers/specs/2026-07-15-one-time-disclosure-consent-addendum.md"),
        Path("docs/superpowers/specs/2026-07-15-personal-ai-workspace-skill-pack-phase-1-design.md"),
        Path("docs/superpowers/specs/2026-07-15-phase-1-release-scope-audit.md"),
        Path("docs/superpowers/specs/PHASE-1-CODEX-ENTRYPOINT.md"),
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
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PRIVATE_REPOSITORY = "oloix888" + "/" + "Apex"
PRIVATE_MANIFEST = "emma-workspace" + "-memory"
PRIVATE_REPO_RE = re.compile(r"\b" + re.escape(PRIVATE_REPOSITORY) + r"\b", re.IGNORECASE)
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
                session[ _-]?cookie
            )\b
        |
        (?<![A-Za-z0-9_-])token\b
        |
        (?<![A-Za-z0-9_-])cookie\b
        )\s*[:=]
        |
        \bauthorization\b\s*[:=]\s*bearer\b
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
    r"(?i)https?://drive\.google\.com/(?:drive/(?:u/\d+/)?folders|file/d)/[A-Za-z0-9_-]+"
)
GOOGLE_DRIVE_ID_RE = re.compile(
    r"(?i)\b(?:folder[_ -]?id|drive[_ -]?(?:folder|file)?[_ -]?id|google[_ -]?drive[_ -]?id)\b"
    r"\s*[:=]\s*[\"']?[A-Za-z0-9_-]{10,}"
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


def _iter_public_files(root: Path):
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
            if path.is_file() and relative not in EXCLUDED_RELATIVE_FILES:
                yield path, relative


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


def _iter_zip_texts(contents: bytes, archive_relative: str, nested_depth: int = 0):
    if nested_depth > MAX_ZIP_NESTED_DEPTH:
        raise PublicSafetyError(f"ZIP recursion depth exceeds limit: {archive_relative}")
    if len(contents) > MAX_ZIP_ARCHIVE_SIZE:
        raise PublicSafetyError(f"ZIP archive exceeds size limit: {archive_relative}")

    try:
        with zipfile.ZipFile(io.BytesIO(contents)) as archive:
            members = archive.infolist()
            if len(members) > MAX_ZIP_MEMBER_COUNT:
                raise PublicSafetyError(f"ZIP member count exceeds limit: {archive_relative}")
            seen_members: set[str] = set()
            total_uncompressed_size = 0
            files: list[zipfile.ZipInfo] = []
            for member in members:
                _validate_zip_member_path(archive_relative, member)
                relative = _member_relative_path(archive_relative, member.filename)
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


def _scan_line(relative: str, line_number: int, line: str, public_email: str) -> list[Finding]:
    findings: list[Finding] = []
    stripped = line.strip()
    for email in EMAIL_RE.findall(line):
        if email.lower() != public_email.lower():
            findings.append(Finding(relative, line_number, "non_allowlisted_email", stripped))
    if PRIVATE_REPO_RE.search(line):
        findings.append(Finding(relative, line_number, "private_repo_reference", stripped))
    if AUTH_SECRET_RE.search(line):
        findings.append(Finding(relative, line_number, "authentication_secret_literal", stripped))
    if NOTION_PRIVATE_RE.search(line):
        findings.append(Finding(relative, line_number, "notion_private_url", stripped))
    if GOOGLE_DRIVE_URL_RE.search(line) or GOOGLE_DRIVE_ID_RE.search(line):
        findings.append(Finding(relative, line_number, "google_drive_identifier", stripped))
    if PRIVATE_MANIFEST_RE.search(line):
        findings.append(Finding(relative, line_number, "private_manifest_reference", stripped))
    return findings


def scan_tree(root: Path, public_email: str) -> list[Finding]:
    if root.is_symlink():
        raise PublicSafetyError(f"unable to scan symlink: {root}")
    if not root.is_dir():
        raise PublicSafetyError(f"scan root is not a directory: {root}")

    findings: list[Finding] = []
    for path, relative_path in _iter_public_files(root):
        relative = relative_path.as_posix()
        contents = _read_file_bytes(path, relative)
        if path.suffix.lower() == ".zip" or _looks_like_zip(contents):
            text_sources = _iter_zip_texts(contents, relative)
        else:
            text_sources = ((relative, _decode_contents(contents, relative, path.suffix)),)
        for text_relative, text in text_sources:
            for line_number, line in enumerate(text.splitlines(), 1):
                findings.extend(_scan_line(text_relative, line_number, line, public_email))
    return findings


def assert_public_safe(root: Path, public_email: str) -> None:
    findings = scan_tree(root, public_email)
    if findings:
        detail = "\n".join(
            f"{item.path}:{item.line} [{item.rule}] {item.excerpt}" for item in findings
        )
        raise PublicSafetyError(detail)
