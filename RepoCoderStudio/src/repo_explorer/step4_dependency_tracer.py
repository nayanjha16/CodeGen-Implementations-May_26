"""
============================================================
RepoCoder Studio — Stage 4
step4_dependency_tracer.py
============================================================

Import graph and call graph construction for structural queries.

NOTE: Reconstructed from the Stage 4 documentation — see step1_ast_parser.py
for the reconstruction disclaimer, which applies to this whole package.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Dict, List

from .step1_ast_parser import _TS_JAVA_AVAILABLE, _TS_JAVA_PARSER, _ts_walk


class DependencyTracer:
    """Builds the import graph and the function call graph."""

    def __init__(self, indexer):
        self.indexer = indexer
        self.import_graph: Dict[str, List[str]] = {}
        self.call_graph: Dict[str, List[str]] = {}
        self._files_by_module_stem = {
            Path(m.file_path).name: m.file_path for m in indexer.modules
        }

    def _resolve_import(self, import_line: str) -> str | None:
        # import_line is like "import foo.bar" (Python), "from foo.bar
        # import baz" (Python), or "import pkg.Class;" / "import pkg.*;"
        # (Java). Try both file extensions on the last dotted segment --
        # whichever actually exists in this repo's index wins; a Java
        # wildcard import ("*") or an import naming a file outside this
        # repo simply resolves to nothing, which is the correct outcome.
        parts = import_line.split()
        if len(parts) < 2:
            return None
        module_token = parts[1].rstrip(";")
        last_segment = module_token.split(".")[-1]
        for ext in (".py", ".java"):
            target = self._files_by_module_stem.get(last_segment + ext)
            if target:
                return target
        return None

    def build_import_graph(self) -> Dict[str, List[str]]:
        graph: Dict[str, List[str]] = {m.file_path: [] for m in self.indexer.modules}
        for module in self.indexer.modules:
            for import_line in module.imports:
                target = self._resolve_import(import_line)
                if target and target != module.file_path:
                    graph[module.file_path].append(target)
        self.import_graph = graph
        return graph

    def build_call_graph(self) -> Dict[str, List[str]]:
        known_functions = {f.name: f for f in self.indexer.all_functions()}
        graph: Dict[str, List[str]] = {}

        for module in self.indexer.modules:
            for fn in module.functions:
                caller_id = f"{fn.file_path}::{fn.name}"
                graph.setdefault(caller_id, [])
                called_names = (
                    self._java_call_names(fn.source)
                    if fn.file_path.endswith(".java")
                    else self._python_call_names(fn.source)
                )
                for called_name in called_names:
                    if called_name in known_functions and called_name != fn.name:
                        callee = known_functions[called_name]
                        callee_id = f"{callee.file_path}::{callee.name}"
                        graph[caller_id].append(callee_id)

        self.call_graph = graph
        return graph

    def _python_call_names(self, source: str) -> List[str]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        names: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    names.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    names.append(node.func.attr)
        return names

    def _java_call_names(self, source: str) -> List[str]:
        # Same tree-sitter-java parser step1_ast_parser.py uses for indexing
        # method bodies -- reused here so call-graph tracing isn't
        # Python-only, matching Stage 4's stated dependency-tracing goal
        # for a genuinely bilingual repository.
        if not _TS_JAVA_AVAILABLE or _TS_JAVA_PARSER is None:
            return []
        try:
            src = source.encode("utf-8", errors="replace")
            tree = _TS_JAVA_PARSER.parse(src)
        except Exception:
            return []
        names: List[str] = []
        for node in _ts_walk(tree.root_node):
            if node.type == "method_invocation":
                name_node = node.child_by_field_name("name")
                if name_node is not None:
                    names.append(src[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace"))
        return names

    def get_dependents(self, file_path: str) -> List[str]:
        return [src for src, targets in self.import_graph.items() if file_path in targets]

    def get_dependencies(self, file_path: str) -> List[str]:
        return list(self.import_graph.get(file_path, []))

    def get_transitive_dependencies(self, file_path: str) -> List[str]:
        seen: set[str] = set()
        stack = list(self.import_graph.get(file_path, []))
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self.import_graph.get(current, []))
        return sorted(seen)

    def get_callees(self, function_id: str) -> List[str]:
        """Return `file::function` targets called by the given function."""
        return list(dict.fromkeys(self.call_graph.get(function_id, [])))

    def get_callers(self, function_id: str) -> List[str]:
        """Return `file::function` callers of the given function."""
        return [
            caller
            for caller, callees in self.call_graph.items()
            if function_id in callees
        ]

    def save_graphs(self, output_dir: str) -> None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "dependency_graph.json").write_text(json.dumps(self.import_graph, indent=2))
        (out / "call_graph.json").write_text(json.dumps(self.call_graph, indent=2))


class GraphVisualizer:
    """Renders the import graph as a PNG using networkx + matplotlib."""

    def __init__(self, tracer: DependencyTracer, output_dir: str):
        self.tracer = tracer
        self.output_dir = Path(output_dir)

    def print_dependency_report(self, repo_path: str) -> None:
        total_edges = sum(len(v) for v in self.tracer.import_graph.values())
        print(f"Dependency report for {repo_path}")
        print(f"  Files: {len(self.tracer.import_graph)}  Import edges: {total_edges}")

    def visualize_import_graph(self, repo_path: str) -> bool:
        edges = [(src, dst) for src, targets in self.tracer.import_graph.items() for dst in targets]
        if not edges:
            return False

        import networkx as nx
        import matplotlib.pyplot as plt

        graph = nx.DiGraph()
        graph.add_edges_from(edges)

        colors = []
        palette = {}
        for node in graph.nodes:
            parent = str(Path(node).parent)
            if parent not in palette:
                palette[parent] = f"C{len(palette) % 10}"
            colors.append(palette[parent])

        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(graph, seed=42)
        nx.draw(
            graph, pos, with_labels=True, node_color=colors,
            node_size=1200, font_size=7, arrows=True,
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.output_dir / "dependency_graph.png"
        plt.savefig(out_path, bbox_inches="tight")
        plt.close()
        return True
