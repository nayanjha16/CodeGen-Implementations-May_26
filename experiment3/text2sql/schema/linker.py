import re
from text2sql.types import SchemaInfo

def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 1}

def _norm(name: str) -> set[str]:
    return _tokens(name.replace("_", " "))

class SchemaLinker:
    """Deterministic lexical schema linker (no model required)."""

    def link(self, question: str, schema: SchemaInfo, evidence: str = "") -> list[str]:
        q = _tokens(question) | _tokens(evidence)
        kept: set[str] = set()
        for table, cols in schema.tables.items():
            if _norm(table) & q:
                kept.add(table)
                continue
            if any(_norm(c) & q for c in cols):
                kept.add(table)
        for a, b in schema.foreign_keys:
            ta, tb = a.split(".")[0], b.split(".")[0]
            if ta in kept:
                kept.add(tb)
            if tb in kept:
                kept.add(ta)
        if not kept:
            return list(schema.tables.keys())
        return [t for t in schema.tables if t in kept]
