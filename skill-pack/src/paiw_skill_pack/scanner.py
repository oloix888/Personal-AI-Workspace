from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re

# Public-root policy: inspect every regular UTF-8 text file, irrespective of
# suffix. The exclusions are private VCS internals, generated environments or
# caches, and implementation-governance records that intentionally quote
# restricted identifiers while defining the boundary. Unknown non-text files
# fail closed; only these established binary asset formats may be skipped.
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
EXCLUDED_RELATIVE_DIRECTORIES = frozenset(
    {
        Path(".superpowers"),
        Path("docs/superpowers"),
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
    r"https?://(?:www\.)?notion\.com/[^\s)]*[0-9a-f]{32}(?=[/?#\s)'\"]|$)|"
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


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    line: int
    rule: str
    excerpt: str


class PublicSafetyError(RuntimeError):
    pass


def _is_excluded_directory(relative: Path) -> bool:
    return (
        relative.name in EXCLUDED_DIRECTORY_NAMES
        or relative in EXCLUDED_RELATIVE_DIRECTORIES
    )


def _iter_public_files(root: Path):
    for directory, directory_names, filenames in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        relative_directory = directory_path.relative_to(root)
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
            if path.is_file():
                yield path, relative


def _read_text_file(path: Path, relative: Path) -> str | None:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return None

    contents = path.read_bytes()
    if b"\x00" in contents:
        raise PublicSafetyError(f"unclassified binary-like file: {relative.as_posix()}")
    try:
        return contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PublicSafetyError(
            f"unclassified non-UTF-8 file: {relative.as_posix()}"
        ) from exc


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
    if not root.is_dir():
        raise PublicSafetyError(f"scan root is not a directory: {root}")

    findings: list[Finding] = []
    for path, relative_path in _iter_public_files(root):
        text = _read_text_file(path, relative_path)
        if text is None:
            continue
        relative = relative_path.as_posix()
        for line_number, line in enumerate(text.splitlines(), 1):
            findings.extend(_scan_line(relative, line_number, line, public_email))
    return findings


def assert_public_safe(root: Path, public_email: str) -> None:
    findings = scan_tree(root, public_email)
    if findings:
        detail = "\n".join(
            f"{item.path}:{item.line} [{item.rule}] {item.excerpt}" for item in findings
        )
        raise PublicSafetyError(detail)
