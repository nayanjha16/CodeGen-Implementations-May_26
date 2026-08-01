"""Dependency-light offline smoke tests for the final handoff."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.code_extraction import extract_code, extract_natural_language
from src.demo_showcases import showcase_examples
from src.repository_catalog import repository_catalog


python_raw = "def add(a, b):\n    return a + b\n\nthis is an incomplete tail"
assert extract_code(python_raw, "python") == "def add(a, b):\n    return a + b"

java_raw = "public class A { public int x(){ return 1; } } } repeated"
java_scored = extract_code(java_raw, "java")
assert java_scored.endswith("}") and "repeated" not in java_scored

nl = extract_natural_language("Reads a value; writes a value; reads a value;")
assert nl.lower().count("reads a value") == 1

fenced = "```python\nprint(1)\n```"
assert extract_natural_language(fenced).startswith("```")
assert extract_code('x = "▁hello"', "python") == 'x = " hello"'

catalog = repository_catalog()
assert [row["repository_id"] for row in catalog] == ["generic", "ledgerflow", "aws_s3"]
examples = showcase_examples(ROOT)
assert len(examples) == 18
for repository_id in ("generic", "ledgerflow", "aws_s3"):
    assert {row["task_id"] for row in examples if row["repository_id"] == repository_id} == {
        "T1", "T2", "T3", "T4", "T5", "T6"
    }

python_files = [
    ROOT / "src" / "saved_prediction_rescorer.py",
    ROOT / "src" / "repository_catalog.py",
    ROOT / "src" / "demo_showcases.py",
    ROOT / "src" / "gradio_showcase.py",
    ROOT / "src" / "evaluator.py",
    ROOT / "app" / "main.py",
    ROOT / "app" / "schemas.py",
]
for path in python_files:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

known_notebooks = {
    "RepoCoderStudio_till_Stage5.ipynb": 60,
    "RepoCoderStudio_Fast_Corrected_Retrain.ipynb": 60,
    "RepoCoderStudio_Presentation_Recovery.ipynb": 24,
}
all_present_notebooks = {
    path.name for path in (ROOT / "notebooks").glob("*.ipynb")
}
known_present = set(known_notebooks) & all_present_notebooks
assert known_present in (
    set(known_notebooks),
    {"RepoCoderStudio_Fast_Corrected_Retrain.ipynb"},
    {
        "RepoCoderStudio_till_Stage5.ipynb",
        "RepoCoderStudio_Presentation_Recovery.ipynb",
    },
), f"Unexpected notebook delivery set: {sorted(all_present_notebooks)}"

for notebook_name in sorted(known_present):
    minimum_cells = known_notebooks[notebook_name]
    notebook_path = ROOT / "notebooks" / notebook_name
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4 and len(notebook["cells"]) >= minimum_cells
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] == "code":
            ast.parse(
                "".join(cell.get("source", [])),
                filename=f"{notebook_name}_cell_{index}",
            )

fast_path = ROOT / "notebooks" / "RepoCoderStudio_Fast_Corrected_Retrain.ipynb"
if fast_path.exists():
    fast_text = fast_path.read_text(encoding="utf-8")
    assert 'REPOCODER_RUN_MODE\\\"] = \\\"demo' in fast_text
    assert 'REPOCODER_LEARNING_RATE\\\"] = \\\"5e-5' in fast_text
    assert "RepoCoderStudio_FastCorrected_LoRA_v1_0" in fast_text

full_path = ROOT / "notebooks" / "RepoCoderStudio_till_Stage5.ipynb"
if full_path.exists():
    full_text = full_path.read_text(encoding="utf-8")
    assert 'REPOCODER_RUN_MODE\\\"] = \\\"capstone' in full_text
    assert 'REPOCODER_RAG_TUNING_EXAMPLES_PER_TASK\\\"] = \\\"50' in full_text

print("final offline smoke tests: PASS")
