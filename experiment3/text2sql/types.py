from dataclasses import dataclass, field

@dataclass
class Example:
    db_id: str
    question: str
    gold_sql: str
    evidence: str = ""          # BIRD external-knowledge hint; "" for Spider

@dataclass
class SchemaInfo:
    db_id: str
    tables: dict[str, list[str]]                 # table_name -> [column_name, ...]
    foreign_keys: list[tuple[str, str]] = field(default_factory=list)  # ("t.col","t2.col")
    primary_keys: list[str] = field(default_factory=list)              # ["t.col", ...]
    column_types: dict[str, str] = field(default_factory=dict)         # "t.col" -> "TEXT"

@dataclass
class GenResult:
    example: Example
    raw_output: str
    sql: str

@dataclass
class EvalResult:
    metrics: dict[str, float]
