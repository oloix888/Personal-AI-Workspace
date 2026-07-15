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
FILE_REFERENCE_KEY_TOKENS = frozenset(
    {
        "asset",
        "directory",
        "dir",
        "file",
        "filename",
        "include",
        "import",
        "manifest",
        "path",
        "reference",
        "ref",
        "schema",
        "script",
        "source",
        "src",
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
PATH_TRAVERSAL_COMPONENT_RE = re.compile(r"(?:^|[\\/])\.\.(?:[\\/]|$)")
META_REFRESH_URL_RE = re.compile(
    r"(?:^|;)\s*url\s*=\s*(?:'(?P<single>[^']*)'|\"(?P<double>[^\"]*)\"|(?P<bare>[^;\s]*))",
    re.IGNORECASE,
)


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
        self.meta_refresh_targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect(tag, attrs)

    def _collect(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
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
        if tag.lower() != "meta":
            return
        normalized = {key.lower(): value for key, value in attrs}
        if (normalized.get("http-equiv") or "").lower() != "refresh":
            return
        content = normalized.get("content")
        if content is None:
            return
        match = META_REFRESH_URL_RE.search(content)
        if match:
            self.meta_refresh_targets.append(
                match.group("single") or match.group("double") or match.group("bare") or ""
            )


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


def _html_meta_refresh_targets(text: str) -> list[str]:
    parser = _HTMLLinkParser()
    parser.feed(text)
    parser.close()
    return parser.meta_refresh_targets


def _is_local_or_host_filesystem_target(target: str, parsed_target: object) -> bool:
    return (
        getattr(parsed_target, "scheme", "").lower() == "file"
        or target.startswith(("/", "\\\\"))
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
    normalized = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", key).lower()
    tokens = [token for token in re.split(r"[^a-z0-9]+", normalized) if token]
    return any(token.rstrip("s") in FILE_REFERENCE_KEY_TOKENS for token in tokens)


def _looks_like_unsafe_file_reference(target: str) -> bool:
    """Find boundary-escaping path forms even under unknown config keys.

    Structured configuration frequently permits arbitrary extension keys.  Those keys
    must not provide a loophole for a relative traversal, local absolute path, or
    ``file:`` URL merely because their names are not known to this validator.
    """

    target = target.strip()
    if not target:
        return False
    decoded_target = unquote(target)
    parsed = urlsplit(decoded_target)
    return (
        _is_local_or_host_filesystem_target(decoded_target, parsed)
        or PATH_TRAVERSAL_COMPONENT_RE.search(unquote(parsed.path)) is not None
    )


def _structured_file_reference_targets(payload: object) -> list[str]:
    targets: list[str] = []
    pending: list[tuple[object, bool]] = [(payload, False)]
    while pending:
        current, inherited_file_reference = pending.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                is_file_reference = inherited_file_reference or _is_file_reference_key(key)
                if isinstance(value, str) and (
                    is_file_reference or _looks_like_unsafe_file_reference(value)
                ):
                    targets.append(value)
                elif isinstance(value, list):
                    pending.append((value, is_file_reference))
                elif isinstance(value, dict):
                    # A field called ``source`` in a JSON Schema, for example, is a
                    # property name rather than a file-reference container.  Nested
                    # mappings therefore establish their own key context; only lists
                    # retain the parent field's file-reference meaning.
                    pending.append((value, False))
        elif isinstance(current, list):
            pending.extend((value, inherited_file_reference) for value in current)
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
    if _dotted_name(node.func) in {"Path", "pathlib.Path"} and node.args:
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


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else None
    return None


def _python_parent(path: _StaticPythonPath, target: str) -> _StaticPythonPath:
    if path.error:
        return path
    if not path.parts:
        return _StaticPythonPath((), "escapes skill root", target)
    return _StaticPythonPath(path.parts[:-1])


def _python_path_expression(
    node: ast.AST,
    source: Path,
    root: Path,
    bindings: dict[str, _StaticPythonPath | None],
) -> _StaticPythonPath | None:
    """Statically model supported runtime path expressions without executing code.

    The model intentionally covers the documented ``pathlib`` and ``os.path`` forms.
    It follows simple variable bindings so that a path cannot escape through an
    intermediate variable.  A caller that performs file I/O must reject an expression
    this model cannot resolve, rather than treating it as safe.
    """

    literal = _string_literal(node)
    if literal is not None:
        return _path_from_literal(literal)
    if _is_dunder_file(node):
        return _StaticPythonPath(source.relative_to(root).parts)
    if isinstance(node, ast.Name):
        return bindings.get(node.id)

    if isinstance(node, ast.Call):
        dotted_function = _dotted_name(node.func)
        if dotted_function == "os.path.dirname" and len(node.args) == 1:
            base = _python_path_expression(node.args[0], source, root, bindings)
            return _python_parent(base, "dirname") if base is not None else None
        if dotted_function == "os.path.join" and node.args:
            base = _python_path_expression(node.args[0], source, root, bindings)
            if base is None:
                return None
            for argument in node.args[1:]:
                literal = _string_literal(argument)
                if literal is None:
                    return None
                base = _append_python_literal(base, literal)
            return base
        if dotted_function in {
            "os.path.abspath",
            "os.path.normpath",
            "os.path.realpath",
        } and len(node.args) == 1:
            return _python_path_expression(node.args[0], source, root, bindings)

        constructor_argument = _path_constructor_argument(node)
        if constructor_argument is not None:
            return _python_path_expression(constructor_argument, source, root, bindings)
        if isinstance(node.func, ast.Attribute):
            base = _python_path_expression(node.func.value, source, root, bindings)
            if base is None:
                return None
            if node.func.attr in {"absolute", "resolve"}:
                return base
            if node.func.attr == "joinpath":
                for argument in node.args:
                    literal = _string_literal(argument)
                    if literal is None:
                        return None
                    base = _append_python_literal(base, literal)
                return base
        return None

    if isinstance(node, ast.Attribute) and node.attr == "parent":
        base = _python_path_expression(node.value, source, root, bindings)
        return _python_parent(base, "parent") if base is not None else None

    if (
        isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "parents"
        and isinstance(node.slice, ast.Constant)
        and isinstance(node.slice.value, int)
        and node.slice.value >= 0
    ):
        base = _python_path_expression(node.value.value, source, root, bindings)
        if base is None or base.error:
            return base
        levels = node.slice.value + 1
        if levels > len(base.parts):
            return _StaticPythonPath(
                (), "escapes skill root", f"parents[{node.slice.value}]"
            )
        return _StaticPythonPath(base.parts[:-levels])

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        base = _python_path_expression(node.left, source, root, bindings)
        literal = _string_literal(node.right)
        if base is None or literal is None:
            return None
        return _append_python_literal(base, literal)
    return None


class _PythonRuntimePathVisitor(ast.NodeVisitor):
    def __init__(self, root: Path, source: Path) -> None:
        self.root = root
        self.source = source
        self.errors: list[str] = []
        self.bindings: dict[str, _StaticPythonPath | None] = {}
        self._reported: set[tuple[str, str | None]] = set()

    def _report(self, error: str, target: str | None = None) -> None:
        key = (error, target)
        if key in self._reported:
            return
        self._reported.add(key)
        target_text = f": {target}" if target else ""
        self.errors.append(
            f"{self.source.relative_to(self.root)} runtime file reference {error}{target_text}"
        )

    def _check_expression(self, node: ast.AST, *, require_resolved: bool = False) -> None:
        path = _python_path_expression(node, self.source, self.root, self.bindings)
        if path is None:
            if require_resolved:
                self._report("cannot be statically resolved")
            return
        if path.error:
            self._report(path.error, path.target)

    def _bind(self, target: ast.AST, value: ast.AST) -> None:
        if isinstance(target, ast.Name):
            self.bindings[target.id] = _python_path_expression(
                value, self.source, self.root, self.bindings
            )

    def _visit_statements(
        self,
        statements: list[ast.stmt],
        initial_bindings: dict[str, _StaticPythonPath | None],
    ) -> dict[str, _StaticPythonPath | None]:
        outer_bindings = self.bindings
        self.bindings = initial_bindings.copy()
        for statement in statements:
            self.visit(statement)
        result = self.bindings
        self.bindings = outer_bindings
        return result

    @staticmethod
    def _merge_bindings(
        *branches: dict[str, _StaticPythonPath | None],
    ) -> dict[str, _StaticPythonPath | None]:
        names = set().union(*(branch.keys() for branch in branches))
        merged: dict[str, _StaticPythonPath | None] = {}
        for name in names:
            values = [branch.get(name) for branch in branches]
            merged[name] = values[0] if all(value == values[0] for value in values) else None
        return merged

    def _is_file_open_call(self, node: ast.Call) -> bool:
        name = _dotted_name(node.func)
        return name in {"open", "builtins.open", "io.open", "os.open"}

    def _is_path_file_io_call(self, node: ast.Call) -> bool:
        return isinstance(node.func, ast.Attribute) and node.func.attr in {
            "exists",
            "glob",
            "is_dir",
            "is_file",
            "iterdir",
            "mkdir",
            "open",
            "read_bytes",
            "read_text",
            "rename",
            "replace",
            "rglob",
            "stat",
            "touch",
            "unlink",
            "write_bytes",
            "write_text",
        }

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        for target in node.targets:
            self._bind(target, node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self.visit(node.value)
            self._bind(node.target, node.value)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self.bindings[node.target.id] = None

    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        initial_bindings = self.bindings.copy()
        body_bindings = self._visit_statements(node.body, initial_bindings)
        else_bindings = self._visit_statements(node.orelse, initial_bindings)
        self.bindings = self._merge_bindings(body_bindings, else_bindings)

    def visit_For(self, node: ast.For) -> None:
        self.visit(node.iter)
        initial_bindings = self.bindings.copy()
        body_bindings = self._visit_statements(node.body, initial_bindings)
        self.bindings = self._merge_bindings(initial_bindings, body_bindings)
        if node.orelse:
            self.bindings = self._visit_statements(node.orelse, self.bindings)

    def visit_While(self, node: ast.While) -> None:
        self.visit(node.test)
        initial_bindings = self.bindings.copy()
        body_bindings = self._visit_statements(node.body, initial_bindings)
        self.bindings = self._merge_bindings(initial_bindings, body_bindings)
        if node.orelse:
            self.bindings = self._visit_statements(node.orelse, self.bindings)

    def visit_Try(self, node: ast.Try) -> None:
        initial_bindings = self.bindings.copy()
        normal_bindings = self._visit_statements(node.body, initial_bindings)
        if node.orelse:
            normal_bindings = self._visit_statements(node.orelse, normal_bindings)
        handler_bindings = [
            self._visit_statements(handler.body, initial_bindings)
            for handler in node.handlers
        ]
        self.bindings = self._merge_bindings(normal_bindings, *handler_bindings)
        if node.finalbody:
            self.bindings = self._visit_statements(node.finalbody, self.bindings)

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        initial_bindings = self.bindings.copy()
        branches = [
            self._visit_statements(case.body, initial_bindings) for case in node.cases
        ]
        self.bindings = self._merge_bindings(initial_bindings, *branches)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_statements(node.body, self.bindings)

    visit_AsyncFunctionDef = visit_FunctionDef

    if hasattr(ast, "TryStar"):
        visit_TryStar = visit_Try

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._visit_statements(node.body, self.bindings)

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
        if self._is_file_open_call(node) and node.args:
            self._check_expression(node.args[0], require_resolved=True)
        if self._is_path_file_io_call(node):
            self._check_expression(node.func.value, require_resolved=True)
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
        for target in _html_meta_refresh_targets(text):
            error = _validate_relative_target(root, markdown, target, "meta refresh")
            if error:
                errors.append(error)
    for html in sorted(
        path
        for suffix in ("*.html", "*.htm", "*.xhtml")
        for path in root.rglob(suffix)
    ):
        text = html.read_text(encoding="utf-8")
        for target in _html_link_targets(text):
            error = _validate_link_target(root, html, target)
            if error:
                errors.append(error)
        for target in _html_meta_refresh_targets(text):
            error = _validate_relative_target(root, html, target, "meta refresh")
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
