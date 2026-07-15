from __future__ import annotations

import ast
from dataclasses import dataclass
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tomllib
from urllib.parse import unquote, urlsplit

import yaml

from .frontmatter import FrontmatterError, parse_skill_frontmatter

INLINE_LINK_RE = re.compile(
    r"\[[^\]\n]+\]\(\s*(?:<(?P<angle>[^>\n]+)>|(?P<bare>[^()\s]+))"
    r"(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^()\n]*\)))?\s*\)",
)
REFERENCE_DEFINITION_RE = re.compile(
    r"^[ \t]{0,3}\[[^\]\n]+\]:[ \t]*(?:<(?P<angle>[^>\n]*)>|(?P<bare>\S+))",
    re.MULTILINE,
)
HTML_LINK_ATTRIBUTES = frozenset(
    {
        "action",
        "background",
        "cite",
        "data",
        "formaction",
        "href",
        "poster",
        "src",
        "srcset",
        "xlink:href",
    }
)
STRUCTURED_CONFIG_SUFFIXES = frozenset({".json", ".toml", ".yaml", ".yml"})
FILE_REFERENCE_KEYS = frozenset(
    {
        "asset",
        "file",
        "filename",
        "manifest",
        "path",
        "schema",
        "script",
        "template",
    }
)
REQUIRED_OPENAI_INTERFACE_FIELDS = (
    "display_name",
    "short_description",
    "brand_color",
    "default_prompt",
)
CANONICAL_LEGAL_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_LEGAL_FILENAMES = ("LICENSE", "NOTICE")
REQUIRED_LEGAL_MARKERS = {
    "LICENSE": ("Apache License", "Version 2.0"),
    "NOTICE": ("Personal AI Workspace", "Apache License, Version 2.0"),
}
WINDOWS_DRIVE_PATH_RE = re.compile(r"^[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class _StaticPythonPath:
    """A lexical, non-executing model of a statically-known Python path."""

    parts: tuple[str, ...]
    error: str | None = None
    target: str | None = None


class _HTMLLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect(attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect(attrs)

    def _collect(self, attrs: list[tuple[str, str | None]]) -> None:
        for attribute, value in attrs:
            if value is None or attribute.lower() not in HTML_LINK_ATTRIBUTES:
                continue
            if attribute.lower() == "srcset":
                self.targets.extend(
                    candidate.strip().split(maxsplit=1)[0]
                    for candidate in value.split(",")
                    if candidate.strip()
                )
            else:
                self.targets.append(value)


def _markdown_link_targets(text: str) -> list[str]:
    targets: list[str] = []
    for expression in (INLINE_LINK_RE, REFERENCE_DEFINITION_RE):
        for match in expression.finditer(text):
            targets.append(match.group("angle") or match.group("bare"))
    return targets


def _html_link_targets(text: str) -> list[str]:
    parser = _HTMLLinkParser()
    parser.feed(text)
    parser.close()
    return parser.targets


def _is_local_or_host_filesystem_target(target: str, parsed_target: object) -> bool:
    return (
        getattr(parsed_target, "scheme", "").lower() == "file"
        or target.startswith(("//", "\\\\"))
        or WINDOWS_DRIVE_PATH_RE.match(target) is not None
    )


def _validate_relative_target(
    root: Path, source: Path, target: str, reference_kind: str
) -> str | None:
    target = target.strip()
    if not target or target.startswith("#"):
        return None

    parsed = urlsplit(target)
    if _is_local_or_host_filesystem_target(target, parsed):
        return (
            f"{source.relative_to(root)} local or host filesystem {reference_kind} is not allowed: "
            f"{target}"
        )
    if parsed.scheme or parsed.netloc:
        return None
    clean = unquote(parsed.path)
    if not clean:
        return None

    resolved = (source.parent / clean).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return f"{source.relative_to(root)} {reference_kind} escapes skill root: {target}"
    if not resolved.exists():
        return f"{source.relative_to(root)} has broken {reference_kind}: {target}"
    return None


def _validate_link_target(root: Path, source: Path, target: str) -> str | None:
    return _validate_relative_target(root, source, target, "link")


def _is_file_reference_key(key: object) -> bool:
    if not isinstance(key, str):
        return False
    normalized = key.lower().replace("-", "_")
    return normalized in FILE_REFERENCE_KEYS or normalized.endswith(
        ("_file", "_filename", "_path")
    )


def _structured_file_reference_targets(payload: object) -> list[str]:
    targets: list[str] = []
    pending = [payload]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                if _is_file_reference_key(key) and isinstance(value, str):
                    targets.append(value)
                pending.append(value)
        elif isinstance(current, list):
            pending.extend(current)
    return targets


def _read_structured_config(path: Path) -> object:
    contents = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(contents)
    if path.suffix == ".toml":
        return tomllib.loads(contents)
    return yaml.safe_load(contents)


def _validate_structured_config_file_references(root: Path, path: Path) -> list[str]:
    try:
        payload = _read_structured_config(path)
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, yaml.YAMLError) as exc:
        return [f"{path.relative_to(root)} contains invalid structured configuration: {exc}"]
    errors: list[str] = []
    for target in _structured_file_reference_targets(payload):
        error = _validate_relative_target(root, path, target, "file reference")
        if error:
            errors.append(error)
    return errors


def _string_literal(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _is_dunder_file(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and node.id == "__file__"


def _path_constructor_argument(node: ast.Call) -> ast.AST | None:
    if isinstance(node.func, ast.Name) and node.func.id == "Path" and node.args:
        return node.args[0]
    return None


def _path_from_literal(value: str) -> _StaticPythonPath:
    parsed = urlsplit(value)
    if _is_local_or_host_filesystem_target(value, parsed) or value.startswith("/"):
        return _StaticPythonPath(
            (), "uses a local or host filesystem path", value
        )
    parts: tuple[str, ...] = ()
    for component in value.replace("\\", "/").split("/"):
        if not component or component == ".":
            continue
        if component == "..":
            if not parts:
                return _StaticPythonPath(
                    (), "escapes skill root", value
                )
            parts = parts[:-1]
        else:
            parts += (component,)
    return _StaticPythonPath(parts)


def _append_python_literal(
    path: _StaticPythonPath, value: str
) -> _StaticPythonPath:
    if path.error:
        return path
    parsed = urlsplit(value)
    if _is_local_or_host_filesystem_target(value, parsed) or value.startswith("/"):
        return _StaticPythonPath((), "uses a local or host filesystem path", value)
    parts = path.parts
    for component in value.replace("\\", "/").split("/"):
        if not component or component == ".":
            continue
        if component == "..":
            if not parts:
                return _StaticPythonPath((), "escapes skill root", value)
            parts = parts[:-1]
        else:
            parts += (component,)
    return _StaticPythonPath(parts)


def _python_path_expression(
    node: ast.AST, source: Path, root: Path
) -> _StaticPythonPath | None:
    """Recognize only direct ``Path``/``__file__`` expressions; never execute code.

    This intentionally does not resolve variables, imports, custom helpers, or dynamic
    values. It provides a conservative package gate for the common direct runtime path
    patterns used by distributed scripts: ``Path(__file__)`` with ``parent``/``parents``,
    ``/`` joins, ``joinpath()``, and direct literal ``Path``/``open`` arguments.
    """

    literal = _string_literal(node)
    if literal is not None:
        return _path_from_literal(literal)

    if isinstance(node, ast.Call):
        constructor_argument = _path_constructor_argument(node)
        if constructor_argument is not None:
            if _is_dunder_file(constructor_argument):
                return _StaticPythonPath(source.relative_to(root).parts)
            literal = _string_literal(constructor_argument)
            if literal is not None:
                return _path_from_literal(literal)
            return None
        if isinstance(node.func, ast.Attribute):
            base = _python_path_expression(node.func.value, source, root)
            if base is None:
                return None
            if node.func.attr in {"absolute", "resolve"}:
                return base
            if node.func.attr == "joinpath":
                for argument in node.args:
                    literal = _string_literal(argument)
                    if literal is None:
                        return base
                    base = _append_python_literal(base, literal)
                return base
        return None

    if isinstance(node, ast.Attribute) and node.attr == "parent":
        base = _python_path_expression(node.value, source, root)
        if base is None or base.error:
            return base
        if not base.parts:
            return _StaticPythonPath((), "escapes skill root", "parent")
        return _StaticPythonPath(base.parts[:-1])

    if (
        isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "parents"
        and isinstance(node.slice, ast.Constant)
        and isinstance(node.slice.value, int)
        and node.slice.value >= 0
    ):
        base = _python_path_expression(node.value.value, source, root)
        if base is None or base.error:
            return base
        levels = node.slice.value + 1
        if levels > len(base.parts):
            return _StaticPythonPath(
                (), "escapes skill root", f"parents[{node.slice.value}]"
            )
        return _StaticPythonPath(base.parts[:-levels])

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        base = _python_path_expression(node.left, source, root)
        literal = _string_literal(node.right)
        if base is None or literal is None:
            return base
        return _append_python_literal(base, literal)
    return None


class _PythonRuntimePathVisitor(ast.NodeVisitor):
    def __init__(self, root: Path, source: Path) -> None:
        self.root = root
        self.source = source
        self.errors: list[str] = []
        self._reported: set[tuple[int, int, str, str | None]] = set()

    def _check_expression(self, node: ast.AST) -> None:
        path = _python_path_expression(node, self.source, self.root)
        if path is None or path.error is None:
            return
        key = (node.lineno, node.col_offset, path.error, path.target)
        if key in self._reported:
            return
        self._reported.add(key)
        target = f": {path.target}" if path.target else ""
        self.errors.append(
            f"{self.source.relative_to(self.root)} runtime file reference {path.error}{target}"
        )

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self._check_expression(node)
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self._check_expression(node)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        self._check_expression(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        self._check_expression(node)
        if isinstance(node.func, ast.Name) and node.func.id == "open" and node.args:
            self._check_expression(node.args[0])
        if isinstance(node.func, ast.Attribute) and node.func.attr in {
            "read_bytes",
            "read_text",
            "write_bytes",
            "write_text",
        }:
            self._check_expression(node.func.value)
        self.generic_visit(node)


def _validate_runtime_python_paths(root: Path, path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [f"{path.relative_to(root)} contains invalid Python: {exc.msg}"]
    visitor = _PythonRuntimePathVisitor(root, path)
    visitor.visit(tree)
    return visitor.errors


def _validate_openai_metadata(path: Path) -> list[str]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return ["agents/openai.yaml contains invalid YAML"]

    if not isinstance(payload, dict):
        return ["agents/openai.yaml must contain a mapping"]

    errors: list[str] = []
    interface = payload.get("interface")
    if not isinstance(interface, dict):
        errors.append("agents/openai.yaml interface must be a mapping")
    else:
        for field in REQUIRED_OPENAI_INTERFACE_FIELDS:
            value = interface.get(field)
            if value is None:
                errors.append(f"agents/openai.yaml interface missing required field: {field}")
            elif not isinstance(value, str) or not value.strip():
                errors.append(
                    f"agents/openai.yaml interface field must be a non-empty string: {field}"
                )

    policy = payload.get("policy")
    if not isinstance(policy, dict):
        errors.append("agents/openai.yaml policy must be a mapping")
    elif not isinstance(policy.get("allow_implicit_invocation"), bool):
        errors.append(
            "agents/openai.yaml policy.allow_implicit_invocation must be a boolean"
        )
    return errors


def _validate_legal_files(root: Path) -> list[str]:
    errors: list[str] = []
    for filename in CANONICAL_LEGAL_FILENAMES:
        path = root / filename
        if not path.is_file():
            errors.append(f"missing {filename}")
            continue
        try:
            actual = path.read_bytes()
        except OSError:
            errors.append(f"unable to read {filename}")
            continue
        try:
            contents = actual.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{filename} must be UTF-8 text")
            continue
        if not all(marker in contents for marker in REQUIRED_LEGAL_MARKERS[filename]):
            if filename == "NOTICE":
                errors.append("NOTICE missing required attribution")
            else:
                errors.append("LICENSE missing Apache-2.0 text")
        canonical_path = CANONICAL_LEGAL_ROOT / filename
        try:
            canonical = canonical_path.read_bytes()
        except OSError:
            errors.append(f"unable to read canonical {filename}")
            continue
        if actual != canonical:
            errors.append(f"{filename} does not match canonical repository legal file")
    return errors


def validate_skill_root(root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return ["missing SKILL.md"]
    try:
        metadata = parse_skill_frontmatter(skill_md.read_text(encoding="utf-8"))
    except FrontmatterError as exc:
        errors.append(str(exc))
        metadata = {}
    if metadata.get("name") and metadata["name"] != root.name:
        errors.append("frontmatter name must match skill directory")
    openai_metadata = root / "agents/openai.yaml"
    if not openai_metadata.is_file():
        errors.append("missing agents/openai.yaml")
    else:
        errors.extend(_validate_openai_metadata(openai_metadata))
    if not (root / "VERSION").is_file():
        errors.append("missing VERSION")
    errors.extend(_validate_legal_files(root))

    for markdown in sorted(root.rglob("*.md")):
        text = markdown.read_text(encoding="utf-8")
        for target in _markdown_link_targets(text) + _html_link_targets(text):
            error = _validate_link_target(root, markdown, target)
            if error:
                errors.append(error)
    for html in sorted(
        path
        for suffix in ("*.html", "*.htm", "*.xhtml")
        for path in root.rglob(suffix)
    ):
        for target in _html_link_targets(html.read_text(encoding="utf-8")):
            error = _validate_link_target(root, html, target)
            if error:
                errors.append(error)
    for config in sorted(
        path
        for suffix in STRUCTURED_CONFIG_SUFFIXES
        for path in root.rglob(f"*{suffix}")
    ):
        errors.extend(_validate_structured_config_file_references(root, config))
    for python_source in sorted(root.rglob("*.py")):
        errors.extend(_validate_runtime_python_paths(root, python_source))
    return errors


def assert_valid_skill(root: Path) -> None:
    errors = validate_skill_root(root)
    if errors:
        raise ValueError("\n".join(errors))
