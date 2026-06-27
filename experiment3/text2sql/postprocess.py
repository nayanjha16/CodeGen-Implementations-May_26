import re

_SQL_START = re.compile(r"\b(SELECT|WITH|INSERT|UPDATE|DELETE)\b", re.IGNORECASE)

def extract_sql(raw: str) -> str:
    # Normalize GPT-2 byte-level BPE markers some MLX detokenizers leave behind
    # (Ġ -> space, Ċ -> newline); harmless for normal output (SQL never has these).
    text = raw.replace("Ġ", " ").replace("Ċ", "\n").strip()
    fence = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    m = _SQL_START.search(text)
    if m:
        text = text[m.start():]
    text = text.split(";")[0].strip()
    text = re.sub(r"\s+", " ", text)
    return text
