import sqlglot
from sqlglot import exp

def _components(sql: str) -> set[str]:
    tree = sqlglot.parse_one(sql, read="sqlite")
    comps: set[str] = set()
    for node, kind in [(exp.Select, "select"), (exp.Where, "where"),
                       (exp.Group, "group"), (exp.Order, "order"), (exp.Join, "join")]:
        for found in tree.find_all(node):
            if node is exp.Select:
                for e in found.expressions:
                    comps.add("select:" + e.sql(dialect="sqlite").lower())
            else:
                comps.add(kind + ":" + found.sql(dialect="sqlite").lower())
    return comps

def component_f1(pred_sql: str, gold_sql: str) -> float:
    try:
        p, g = _components(pred_sql), _components(gold_sql)
    except Exception:
        return 0.0
    if not p and not g:
        return 1.0
    if not p or not g:
        return 0.0
    tp = len(p & g)
    if tp == 0:
        return 0.0
    precision = tp / len(p)
    recall = tp / len(g)
    return 2 * precision * recall / (precision + recall)
