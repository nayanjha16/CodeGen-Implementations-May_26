"""
============================================================
RepoCoder Studio — Stage 4
step1_ast_parser.py
============================================================

AST parsing and repository indexing -- Python (stdlib ast) and Java
(tree-sitter-java, same library and initialization pattern already used
by src/java_validator.py for corpus validation).

NOTE: Reconstructed from "RepoCoder Studio — Stage 4: Repository
Understanding" (technical documentation) — the original Kaggle-authored
source for this file was not provided to Claude. The public interface
(RepositoryIndexer, FunctionInfo, ClassInfo, ModuleInfo, and the
repo_index.json output shape) matches the documented spec exactly, so
downstream steps 2-5 and the Stage 5 retrieval layer will work either
against this reconstruction or against the original file — just drop
the original in to replace this one if it differs in implementation
detail.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

from src.logger import LOG


@dataclass
class FunctionInfo:
    name: str
    file_path: str
    start_line: int
    end_line: int
    args: List[str] = field(default_factory=list)
    docstring: str = ""
    source: str = ""
    is_method: bool = False
    parent_class: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    return_type: Optional[str] = None

    def embedding_text(self) -> str:
        """Rich multi-part text used as the embedding input in Step 2."""
        signature = f"def {self.name}({', '.join(self.args)})"
        if self.return_type:
            signature += f" -> {self.return_type}"
        snippet = self.source or ""
        parts = [signature]
        if self.docstring:
            parts.append(self.docstring.strip())
        if snippet:
            parts.append(snippet)
        return "\n".join(parts)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ClassInfo:
    name: str
    file_path: str
    start_line: int
    end_line: int
    docstring: str = ""
    methods: List[str] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)

    def embedding_text(self) -> str:
        parts = [f"class {self.name}({', '.join(self.bases)})"]
        if self.docstring:
            parts.append(self.docstring.strip())
        if self.methods:
            parts.append("methods: " + ", ".join(self.methods))
        return "\n".join(parts)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ModuleInfo:
    module_name: str
    file_path: str
    docstring: str = ""
    imports: List[str] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    line_count: int = 0

    def embedding_text(self) -> str:
        parts = [self.module_name]
        if self.docstring:
            parts.append(self.docstring.strip())
        exports = [f.name for f in self.functions] + [c.name for c in self.classes]
        if exports:
            parts.append("exports: " + ", ".join(exports))
        return "\n".join(parts)

    def to_dict(self) -> dict:
        return {
            "module_name": self.module_name,
            "file_path": self.file_path,
            "docstring": self.docstring,
            "imports": self.imports,
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
            "line_count": self.line_count,
        }


def _format_import(node: ast.AST) -> List[str]:
    lines: List[str] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            lines.append(f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""
        names = ", ".join(
            a.name + (f" as {a.asname}" if a.asname else "") for a in node.names
        )
        lines.append(f"from {module} import {names}")
    return lines


# ============================================================
# Java parsing (tree-sitter-java)
# ============================================================
#
# Same lazy-init-with-graceful-fallback pattern as
# src/java_validator.py's _init_tree_sitter_java() -- kept separate
# (not imported from there) so this package doesn't take on a hard
# dependency on the corpus-validation module for an unrelated concern.
# If tree-sitter-java isn't installed/loadable, Java files are simply
# skipped during indexing rather than crashing the pipeline -- matching
# every other optional-dependency fallback in this project (mock
# embeddings, CSR Tree-sitter fallback, etc.).

_TS_JAVA_AVAILABLE = False
_TS_JAVA_PARSER = None
_TS_JAVA_INIT_ERROR: Optional[str] = None


def _init_tree_sitter_java() -> None:
    global _TS_JAVA_AVAILABLE, _TS_JAVA_PARSER, _TS_JAVA_INIT_ERROR
    try:
        from tree_sitter import Language, Parser  # type: ignore
        import tree_sitter_java as tsjava  # type: ignore

        language = Language(tsjava.language())
        try:
            parser = Parser(language)
        except TypeError:
            parser = Parser()
            parser.set_language(language)

        _TS_JAVA_PARSER = parser
        _TS_JAVA_AVAILABLE = True
        _TS_JAVA_INIT_ERROR = None
    except Exception as exc:  # pragma: no cover - environment dependent
        _TS_JAVA_AVAILABLE = False
        _TS_JAVA_PARSER = None
        _TS_JAVA_INIT_ERROR = repr(exc)


_init_tree_sitter_java()


def _ts_walk(node):
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(reversed(current.children))


def _ts_text(src: bytes, node) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _ts_javadoc_before(src: bytes, node) -> str:
    """Best-effort Javadoc extraction: if the immediately preceding sibling
    is a /** ... */ block comment, treat it as this node's docstring."""
    prev = node.prev_sibling
    if prev is None or prev.type != "block_comment":
        return ""
    text = _ts_text(src, prev)
    if not text.startswith("/**"):
        return ""
    text = text[3:].rstrip("*/").strip()
    lines = [ln.strip().lstrip("*").strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


class PythonASTParser:
    """Parses a single Python file into a ModuleInfo."""

    def parse_file(self, file_path: Path, repo_path: Path) -> Optional[ModuleInfo]:
        try:
            text = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return None

        try:
            tree = ast.parse(text, filename=str(file_path))
        except SyntaxError:
            return None

        lines = text.splitlines()
        rel_path = str(file_path.relative_to(repo_path)).replace("\\", "/")
        module_name = rel_path[:-3].replace("/", ".") if rel_path.endswith(".py") else rel_path

        module = ModuleInfo(
            module_name=module_name,
            file_path=rel_path,
            docstring=ast.get_docstring(tree) or "",
            line_count=len(lines),
        )

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module.imports.extend(_format_import(node))

        # Top-level and class-level function/class definitions only
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                module.classes.append(self._parse_class(node, rel_path, lines))
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        module.functions.append(
                            self._parse_function(sub, rel_path, lines, parent_class=node.name)
                        )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                module.functions.append(self._parse_function(node, rel_path, lines))

        return module

    def _parse_function(
        self,
        node,
        rel_path: str,
        lines: List[str],
        parent_class: Optional[str] = None,
    ) -> FunctionInfo:
        start = node.lineno
        end = getattr(node, "end_lineno", start)
        source = "\n".join(lines[start - 1:end])
        args = [a.arg for a in node.args.args]
        decorators = [
            d.id if isinstance(d, ast.Name) else getattr(d, "attr", ast.dump(d))
            for d in node.decorator_list
        ]
        return_type = ast.unparse(node.returns) if getattr(node, "returns", None) is not None else None

        return FunctionInfo(
            name=node.name,
            file_path=rel_path,
            start_line=start,
            end_line=end,
            args=args,
            docstring=ast.get_docstring(node) or "",
            source=source,
            is_method=parent_class is not None,
            parent_class=parent_class,
            decorators=decorators,
            return_type=return_type,
        )

    def _parse_class(self, node: ast.ClassDef, rel_path: str, lines: List[str]) -> ClassInfo:
        start = node.lineno
        end = getattr(node, "end_lineno", start)
        methods = [
            n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        bases = [
            b.id if isinstance(b, ast.Name) else getattr(b, "attr", ast.dump(b)) for b in node.bases
        ]
        return ClassInfo(
            name=node.name,
            file_path=rel_path,
            start_line=start,
            end_line=end,
            docstring=ast.get_docstring(node) or "",
            methods=methods,
            bases=bases,
        )


class JavaASTParser:
    """Parses a single Java file into a ModuleInfo, using tree-sitter-java.

    Structurally mirrors PythonASTParser's contract (same ModuleInfo /
    ClassInfo / FunctionInfo shapes) so steps 2-5 (embeddings, FAISS,
    dependency graph, RepositoryExplorer) work identically regardless of
    which language produced a given module -- none of them need to know
    or care that this parser exists.
    """

    def tree_sitter_available(self) -> bool:
        return _TS_JAVA_AVAILABLE

    def tree_sitter_error(self) -> Optional[str]:
        return _TS_JAVA_INIT_ERROR

    def parse_file(self, file_path: Path, repo_path: Path) -> Optional[ModuleInfo]:
        if not _TS_JAVA_AVAILABLE or _TS_JAVA_PARSER is None:
            return None

        try:
            text = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return None

        src = text.encode("utf-8", errors="replace")
        try:
            tree = _TS_JAVA_PARSER.parse(src)
        except Exception as exc:
            LOG.warning(f"Tree-sitter failed to parse {file_path}: {exc}")
            return None

        root = tree.root_node
        if bool(getattr(root, "has_error", False)):
            # Same rule as PythonASTParser returning None on SyntaxError --
            # a Java file that doesn't parse cleanly isn't indexed.
            return None

        rel_path = str(file_path.relative_to(repo_path)).replace("\\", "/")
        module_name = rel_path[:-5].replace("/", ".") if rel_path.endswith(".java") else rel_path
        lines = text.splitlines()

        module = ModuleInfo(module_name=module_name, file_path=rel_path, line_count=len(lines))

        for node in _ts_walk(root):
            nt = node.type
            if nt == "import_declaration":
                module.imports.append(_ts_text(src, node).strip())
            elif nt == "class_declaration":
                module.classes.append(self._parse_class(node, src, rel_path))
                class_name = self._name_of(src, node)
                # Direct children of this class's class_body only -- a
                # nested class's own methods are picked up independently
                # when the outer walk reaches that nested class_declaration,
                # so no identity/ancestor tracking is needed here.
                for body in node.children:
                    if body.type != "class_body":
                        continue
                    for member in body.children:
                        if member.type in {"method_declaration", "constructor_declaration"}:
                            module.functions.append(
                                self._parse_method(member, src, rel_path, parent_class=class_name)
                            )

        return module

    def _name_of(self, src: bytes, node) -> str:
        name_node = node.child_by_field_name("name")
        return _ts_text(src, name_node) if name_node is not None else "?"

    def _parse_class(self, node, src: bytes, rel_path: str) -> ClassInfo:
        start = node.start_point[0] + 1
        end = node.end_point[0] + 1
        name = self._name_of(src, node)

        superclass_node = node.child_by_field_name("superclass")
        interfaces_node = node.child_by_field_name("interfaces")
        bases: List[str] = []
        if superclass_node is not None:
            bases.append(_ts_text(src, superclass_node).replace("extends", "").strip())
        if interfaces_node is not None:
            bases.append(_ts_text(src, interfaces_node).replace("implements", "").strip())

        methods = [
            self._name_of(src, n)
            for n in node.children
            if n.type == "class_body"
            for n in n.children
            if n.type in {"method_declaration", "constructor_declaration"}
        ]

        return ClassInfo(
            name=name,
            file_path=rel_path,
            start_line=start,
            end_line=end,
            docstring=_ts_javadoc_before(src, node),
            methods=methods,
            bases=bases,
        )

    def _parse_method(self, node, src: bytes, rel_path: str, parent_class: str) -> FunctionInfo:
        start = node.start_point[0] + 1
        end = node.end_point[0] + 1
        name = self._name_of(src, node)
        source = _ts_text(src, node)

        params_node = node.child_by_field_name("parameters")
        args: List[str] = []
        if params_node is not None:
            for p in params_node.children:
                if p.type == "formal_parameter":
                    pname = p.child_by_field_name("name")
                    if pname is not None:
                        args.append(_ts_text(src, pname))

        type_node = node.child_by_field_name("type")
        return_type = _ts_text(src, type_node) if type_node is not None else None

        return FunctionInfo(
            name=name,
            file_path=rel_path,
            start_line=start,
            end_line=end,
            args=args,
            docstring=_ts_javadoc_before(src, node),
            source=source,
            is_method=True,
            parent_class=parent_class,
            decorators=[],
            return_type=return_type,
        )


class RepositoryIndexer:
    """Crawls a repository and builds the full structured AST index
    (Python via stdlib ast, Java via tree-sitter-java)."""

    def __init__(self, repo_path: str, output_dir: str):
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.modules: List[ModuleInfo] = []
        self._parser = PythonASTParser()
        self._java_parser = JavaASTParser()

    @property
    def index_file(self) -> Path:
        return self.output_dir / "repo_index.json"

    def index_repository(self) -> dict:
        self.modules = []
        python_files = self._source_files(".py")
        java_files = self._source_files(".java")
        for py_file in python_files:
            module = self._parser.parse_file(py_file, self.repo_path)
            if module is not None:
                self.modules.append(module)

        if java_files and not self._java_parser.tree_sitter_available():
            raise RuntimeError(
                "Repository contains Java files but tree-sitter-java is unavailable: "
                f"{self._java_parser.tree_sitter_error()}"
            )
        for java_file in java_files:
            module = self._java_parser.parse_file(java_file, self.repo_path)
            if module is not None:
                self.modules.append(module)

        stats = self._stats()
        payload = {
            "stats": stats,
            "modules": [m.to_dict() for m in self.modules],
        }
        self.index_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return stats

    def _source_files(self, suffix: str, max_bytes: int = 2_000_000) -> List[Path]:
        ignored = {
            ".git",
            ".hg",
            ".svn",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            "build",
            "dist",
            "target",
        }
        files: List[Path] = []
        for path in sorted(self.repo_path.rglob(f"*{suffix}")):
            if path.is_symlink() or any(part in ignored for part in path.parts):
                continue
            try:
                if not path.is_file() or path.stat().st_size > max_bytes:
                    continue
                path.resolve().relative_to(self.repo_path.resolve())
            except (OSError, ValueError):
                continue
            files.append(path)
        return files

    def load_index(self) -> dict:
        return json.loads(self.index_file.read_text(encoding="utf-8"))

    def all_functions(self) -> List[FunctionInfo]:
        return [f for m in self.modules for f in m.functions]

    def all_classes(self) -> List[ClassInfo]:
        return [c for m in self.modules for c in m.classes]

    def _stats(self) -> dict:
        functions = self.all_functions()
        classes = self.all_classes()
        return {
            "total_files": len(self.modules),
            "total_functions": len(functions),
            "total_classes": len(classes),
            "total_lines": sum(m.line_count for m in self.modules),
        }
