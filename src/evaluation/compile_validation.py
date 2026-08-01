"""C# syntax validity, AST similarity and compilation-rate checks."""
import math
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from typing import List, Optional, Tuple


def get_csharp_parser():
    """Best-effort tree-sitter C# parser; returns None if unavailable."""
    try:
        from tree_sitter import Language, Parser
        import tree_sitter_c_sharp as tscs

        lang = Language(tscs.language())
        try:
            return Parser(lang)  # tree-sitter >= 0.22 API
        except TypeError:
            parser = Parser()
            parser.set_language(lang)  # older API
            return parser
    except Exception:
        return None


_CS_PARSER = get_csharp_parser()


def _collect_node_types(node, acc: list) -> None:
    acc.append(node.type)
    for child in node.children:
        _collect_node_types(child, acc)


def ast_node_types(code: str) -> Optional[list]:
    if _CS_PARSER is None:
        return None
    try:
        tree = _CS_PARSER.parse(bytes(code, "utf8"))
        acc: list = []
        _collect_node_types(tree.root_node, acc)
        return acc
    except Exception:
        return None


def parse_is_valid(code: str) -> Optional[bool]:
    if _CS_PARSER is None:
        return None
    try:
        tree = _CS_PARSER.parse(bytes(code, "utf8"))
        return not tree.root_node.has_error
    except Exception:
        return False


def bag_cosine(a: list, b: list) -> float:
    counter_a, counter_b = Counter(a), Counter(b)
    keys = set(counter_a) | set(counter_b)
    dot = sum(counter_a[k] * counter_b[k] for k in keys)
    norm_a = math.sqrt(sum(v * v for v in counter_a.values()))
    norm_b = math.sqrt(sum(v * v for v in counter_b.values()))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def compute_ast_similarity(predictions: List[str], references: List[str]) -> Optional[float]:
    """Average cosine similarity over node-type bags (predictions vs references)."""
    similarities = []
    for pred, ref in zip(predictions, references):
        pred_types, ref_types = ast_node_types(pred), ast_node_types(ref)
        if pred_types is not None and ref_types is not None:
            similarities.append(bag_cosine(pred_types, ref_types))
    return round(sum(similarities) / len(similarities), 4) if similarities else None


def compute_syntax_accuracy(predictions: List[str]) -> Optional[float]:
    """Fraction of predictions that parse without errors."""
    valid = [v for v in (parse_is_valid(p)
                         for p in predictions) if v is not None]
    return round(sum(valid) / len(valid), 4) if valid else None


def find_csharp_compiler() -> Optional[str]:
    for tool in ("dotnet", "csc", "mcs"):
        if shutil.which(tool):
            return tool
    return None


_CSHARP_COMPILER = find_csharp_compiler()


def _wrap_csharp(code: str) -> str:
    """Wrap a bare snippet/method into a compilable class skeleton."""
    if re.search(r"\b(class|struct|interface|enum|namespace)\b", code):
        return code
    return "using System;\nusing System.Collections.Generic;\npublic class Wrapper {\n" + code + "\n}\n"


def _compiles_with_mono(code: str) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        src = f"{tmp}/Program.cs"
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(_wrap_csharp(code))
        try:
            result = subprocess.run(
                [_CSHARP_COMPILER, "-target:library", src], capture_output=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False


def compute_compilation_rate(predictions: List[str]) -> Tuple[Optional[float], str]:
    """Real-compiler compilation rate when csc/mcs is available, else a
    tree-sitter syntax-validity proxy."""
    if _CSHARP_COMPILER in ("csc", "mcs"):
        results = [_compiles_with_mono(p) for p in predictions]
        return sum(results) / len(predictions), f"real-compiler({_CSHARP_COMPILER})"

    valid = [v for v in (parse_is_valid(p)
                         for p in predictions) if v is not None]
    if not valid:
        return None, "unavailable"
    return sum(valid) / len(valid), "syntax-proxy(tree-sitter)"
