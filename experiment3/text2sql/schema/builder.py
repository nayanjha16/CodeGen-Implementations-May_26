import sqlite3
from pathlib import Path
from text2sql.types import SchemaInfo

class SchemaBuilder:
    """Renders selected tables as CREATE TABLE statements plus a few sample rows."""

    def __init__(self, sample_rows: int = 3):
        self.sample_rows = sample_rows

    def build(self, schema: SchemaInfo, tables: list[str], db_path: Path | None) -> str:
        blocks: list[str] = []
        for t in tables:
            cols = schema.tables[t]
            col_lines = []
            for c in cols:
                ctype = schema.column_types.get(f"{t}.{c}", "TEXT")
                pk = " PRIMARY KEY" if f"{t}.{c}" in schema.primary_keys else ""
                col_lines.append(f"  {c} {ctype}{pk}")
            ddl = f"CREATE TABLE {t} (\n" + ",\n".join(col_lines) + "\n);"
            block = ddl
            if self.sample_rows > 0 and db_path is not None:
                rows = self._sample(db_path, t, cols, self.sample_rows)
                if rows:
                    block += f"\n/* {self.sample_rows} example rows:\n"
                    block += " | ".join(cols) + "\n"
                    for r in rows:
                        block += " | ".join(str(v) for v in r) + "\n"
                    block += "*/"
            blocks.append(block)
        return "\n\n".join(blocks)

    def _sample(self, db_path: Path, table: str, cols: list[str], n: int) -> list[tuple]:
        con = sqlite3.connect(db_path)
        try:
            quoted = ", ".join(f'"{c}"' for c in cols)
            return con.execute(f'SELECT {quoted} FROM "{table}" LIMIT {n}').fetchall()
        except sqlite3.Error:
            return []
        finally:
            con.close()
