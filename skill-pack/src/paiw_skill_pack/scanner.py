from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".html", ".css", ".js"}
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PRIVATE_REPO_RE = re.compile(r"\boloix888/Apex\b", re.IGNORECASE)
AUTH_SECRET_RE = re.compile(
    r"(?i)\b(password|one[- ]time code|reset link|api[_ -]?key|access[_ -]?token|session cookie|private key)\b\s*[:=]"
)
NOTION_PRIVATE_RE = re.compile(r"(?i)https?://(?:www\.)?notion\.(?:site|so)/[^\s)]+")
GOOGLE_DRIVE_ID_RE = re.compile(r"(?i)\b(?:drive[_ -]?folder[_ -]?id|google[_ -]?drive[_ -]?id)\b\s*[:=]")
PRIVATE_MANIFEST_RE = re.compile(r"\bemma-workspace-memory\b", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    line: int
    rule: str
    excerpt: str


class PublicSafetyError(RuntimeError):
    pass


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
    if GOOGLE_DRIVE_ID_RE.search(line):
        findings.append(Finding(relative, line_number, "google_drive_identifier", stripped))
    if PRIVATE_MANIFEST_RE.search(line):
        findings.append(Finding(relative, line_number, "private_manifest_reference", stripped))
    return findings


def scan_tree(root: Path, public_email: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            findings.extend(_scan_line(relative, line_number, line, public_email))
    return findings


def assert_public_safe(root: Path, public_email: str) -> None:
    findings = scan_tree(root, public_email)
    if findings:
        detail = "\n".join(
            f"{item.path}:{item.line} [{item.rule}] {item.excerpt}" for item in findings
        )
        raise PublicSafetyError(detail)
