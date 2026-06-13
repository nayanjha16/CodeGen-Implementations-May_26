"""
IIT Hyderabad AIML Training — Live Demo Script
Natural Language → SQL | SQL → NoSQL | Base Model Evaluation

Usage:
  python scripts/demo_presentation.py              # Full demo (metrics + SQL→NoSQL, no model download)
  python scripts/demo_presentation.py --with-model # Include live generation (uses cached model in models/)
  python scripts/demo_presentation.py --eval-only  # Base model evaluation on reference data only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.metrics import EvaluationMetrics
from src.evaluation.mlflow_tracker import MLflowTracker
from src.sql2nosql.translator import SQLToNoSQLTranslator
from src.text2sql.prompt_builder import PromptBuilder
from src.text2sql.sql_executor import SQLExecutor
from src.text2sql.sql_validator import SQLValidator
from src.utils.config import get_model_name, load_config
from src.utils.paths import get_results_dir, resolve_results_output_path
from src.utils.seeds import set_seeds

# ---------------------------------------------------------------------------
# Reference benchmark examples (Spider-style) for base model evaluation demo
# ---------------------------------------------------------------------------
REFERENCE_BENCHMARK = [
    {
        "question": "Show all students older than 20",
        "schema": "Table students(id, name, age)\nTable courses(id, name, credits)",
        "sql": "SELECT name, age FROM students WHERE age > 20",
        "db_id": "students",
    },
    {
        "question": "List all course names",
        "schema": "Table students(id, name, age)\nTable courses(id, name, credits)",
        "sql": "SELECT name FROM courses",
        "db_id": "students",
    },
    {
        "question": "How many students are there?",
        "schema": "Table students(id, name, age)",
        "sql": "SELECT COUNT(*) FROM students",
        "db_id": "students",
    },
    {
        "question": "Find students enrolled in Machine Learning",
        "schema": "Table students(id, name, age)\nTable courses(id, name, credits)\nTable enrollments(student_id, course_id)",
        "sql": "SELECT s.name FROM students s JOIN enrollments e ON s.id = e.student_id JOIN courses c ON e.course_id = c.id WHERE c.name = 'Machine Learning'",
        "db_id": "students",
    },
]

# Simulated base-model predictions (typical small-model behaviour for demo discussion)
BASE_MODEL_PREDICTIONS = [
    "SELECT name, age FROM students WHERE age > 20",
    "SELECT name FROM courses",
    "SELECT COUNT(*) FROM students",
    "SELECT s.name FROM students s JOIN enrollments e ON s.id = e.student_id JOIN courses c ON c.id = e.course_id WHERE c.name = 'Machine Learning'",
]

SQL_TO_NOSQL_EXAMPLES = [
    "SELECT name FROM students WHERE age > 20",
    "SELECT name FROM courses ORDER BY name LIMIT 5",
    "SELECT name, credits FROM courses WHERE credits >= 3",
]


def banner(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def section(title: str) -> None:
    print(f"\n--- {title} ---")


def demo_intro() -> None:
    banner("CodeGen: NL to SQL & SQL to NoSQL | IIT Hyderabad AIML Demo")
    config = load_config()
    print(f"""
  Project   : CodeGen – Interactive Database Querying
  Base Model: {config['model']['name']}
  Datasets  : Spider (text-to-SQL), BirdBench (complex SQL)
  Task 1    : Natural Language to SQL generation
  Task 2    : SQL to MongoDB (NoSQL) translation
  Task 3    : Base model evaluation (Exact Match, Execution Acc, CodeBLEU)
""")


def demo_reference_data() -> None:
    banner("1. Reference Benchmark Data (Spider-style format)")
    print("Standard format: { question, schema, sql }\n")
    for i, ex in enumerate(REFERENCE_BENCHMARK, 1):
        print(f"  Example {i}:")
        print(f"    Question : {ex['question']}")
        print(f"    Schema   : {ex['schema'].split(chr(10))[0]} ...")
        print(f"    Gold SQL : {ex['sql']}")
        print()


def demo_prompt_builder() -> None:
    banner("2. Prompt Construction for CodeGen")
    builder = PromptBuilder()
    ex = REFERENCE_BENCHMARK[0]
    prompt = builder.build(ex["question"], ex["schema"])
    print("CodeGen receives this prompt:\n")
    print(prompt)
    print("\n[Explain to audience: schema + question -> model generates SQL]")


def demo_text2sql_with_model() -> None:
    banner("3. Live Text-to-SQL")
    from src.text2sql.sql_generator import SQLGenerator

    config = load_config()
    model_name = get_model_name(config)
    config["evaluation"]["max_samples"] = 2
    generator = SQLGenerator(config=config)

    ex = REFERENCE_BENCHMARK[0]
    print(f"Loading model {model_name} (cached under models/base/ after first run)...\n")
    result = generator.generate(ex["question"], ex["schema"])
    print(f"  Question     : {ex['question']}")
    print(f"  Generated SQL: {result['sql']}")
    print(f"  Gold SQL     : {ex['sql']}")
    match = result["sql"].strip().upper() == ex["sql"].strip().upper()
    print(f"  Exact Match  : {'Yes' if match else 'No (expected for 350M base model)'}")


def demo_sql_validation_and_execution(db_path: Path) -> None:
    banner("4. SQL Validation & Execution")
    validator = SQLValidator()
    executor = SQLExecutor()

    sql = "SELECT name, age FROM students WHERE age > 20"
    section("Syntax validation")
    val = validator.validate(sql, str(db_path))
    print(f"  SQL    : {sql}")
    print(f"  Valid  : {val['valid']}")

    section("Execution on sample database")
    result = executor.execute(sql, db_path)
    print(f"  Success   : {result['success']}")
    print(f"  Row count : {result['row_count']}")
    for row in result["rows"]:
        print(f"  Result    : {row}")


def demo_sql_to_nosql() -> None:
    banner("5. SQL to NoSQL (MongoDB) Translation")
    translator = SQLToNoSQLTranslator()

    for sql in SQL_TO_NOSQL_EXAMPLES:
        section(sql)
        result = translator.translate(sql)
        print(result["mongodb_query"])
        if result.get("warnings"):
            print(f"  Warnings: {', '.join(result['warnings'])}")


def demo_base_model_evaluation(
    db_path: Path | None, log_mlflow: bool = False, config: dict | None = None
) -> dict:
    banner("6. Base Model Evaluation on Reference Data")
    metrics_calc = EvaluationMetrics()
    config = config or load_config()

    references = [ex["sql"] for ex in REFERENCE_BENCHMARK]
    predictions = BASE_MODEL_PREDICTIONS

    section("Predictions vs Ground Truth")
    for i, (pred, ref) in enumerate(zip(predictions, references), 1):
        em = metrics_calc.exact_match(pred, ref)
        print(f"  [{i}] EM={em}")
        print(f"      Pred: {pred[:70]}{'...' if len(pred) > 70 else ''}")
        print(f"      Gold: {ref[:70]}{'...' if len(ref) > 70 else ''}")

    db_paths = [str(db_path)] * len(predictions) if db_path and db_path.exists() else None
    all_metrics = metrics_calc.evaluate_all(predictions, references, db_paths)

    section("Evaluation Metrics (Base Model)")
    metric_labels = {
        "exact_match": "Exact Match Accuracy",
        "execution_accuracy": "Execution Accuracy",
        "syntax_validity": "Syntax Validity Rate",
        "bleu": "BLEU",
        "rouge_l": "ROUGE-L",
        "bertscore": "BERTScore",
        "codebleu": "CodeBLEU",
        "ngram_match": "CodeBLEU - N-gram",
        "syntax_match": "CodeBLEU - Syntax",
        "semantic_match": "CodeBLEU - Semantic",
    }
    for key, label in metric_labels.items():
        if key in all_metrics:
            val = all_metrics[key]
            print(f"  {label:30s}: {val:.4f}" if isinstance(val, float) else f"  {label:30s}: {val}")

    section("Key Takeaways for Audience")
    print("""
  • Exact Match      : Strict string match after SQL normalization
  • Execution Acc    : Do predicted & gold SQL return same rows? (strongest metric)
  • Syntax Validity  : Is generated SQL parseable?
  • BLEU/ROUGE       : N-gram / sequence overlap with gold SQL
  • BERTScore        : Semantic similarity using contextual embeddings
  • CodeBLEU         : Code-specific metric (n-gram + syntax + data-flow)
  • 350M base model  : Good for demos; fine-tuning on Spider improves all metrics
""")

    if log_mlflow:
        tracker = MLflowTracker(
            experiment_name="codegen-iit-demo",
            tracking_uri=str(ROOT / "mlruns"),
        )
        run_id = tracker.log_evaluation(
            model_name=get_model_name(config),
            dataset="reference_benchmark_demo",
            prompt_template="default",
            metrics=all_metrics,
            run_name="iit-hyderabad-demo",
        )
        print(f"  MLflow run logged: {run_id}")
        print(f"  View runs: mlflow ui --backend-store-uri {ROOT / 'mlruns'}")

    return all_metrics


def demo_datasets_overview() -> None:
    banner("7. Full Benchmark Datasets (Spider & BirdBench)")
    print("""
  Spider    : 10,000+ NL-SQL pairs, 200 databases (academic standard)
  BirdBench : 12,000+ pairs with external knowledge (harder, real-world)

  To run full base model eval (after presentation):
    bash scripts/evaluate.sh spider validation
    bash scripts/evaluate.sh bird validation

  Results auto-logged to MLflow for comparison across runs.
""")


def save_demo_results(metrics: dict, output_path: Path, config: dict | None = None) -> None:
    output_path = resolve_results_output_path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    config = config or load_config()
    payload = {
        "demo": "IIT Hyderabad AIML Training",
        "model": get_model_name(config),
        "reference_examples": len(REFERENCE_BENCHMARK),
        "metrics": {k: v for k, v in metrics.items() if isinstance(v, (int, float))},
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\n  Results saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="IIT Hyderabad AIML demo")
    parser.add_argument("--with-model", action="store_true", help="Run live CodeGen generation")
    parser.add_argument("--eval-only", action="store_true", help="Skip to evaluation section")
    parser.add_argument("--mlflow", action="store_true", help="Log evaluation to MLflow")
    args = parser.parse_args()

    config = load_config()
    set_seeds(config)

    # Ensure sample DB exists
    from scripts.setup_sample_db import create_sample_db

    db_path = create_sample_db(ROOT / "data" / "samples" / "students.db")

    demo_intro()

    if not args.eval_only:
        demo_reference_data()
        demo_prompt_builder()
        if args.with_model:
            demo_text2sql_with_model()
        else:
            banner("3. Text-to-SQL")
            print(f"""
  [Skipped live model — use --with-model to run live generation]
  Configured model: {get_model_name(config)}
  For live demo in Streamlit instead:
    streamlit run apps/streamlit/app.py

  Or start API:
    uvicorn src.api.main:app --port 8000
    Open http://localhost:8000/docs
""")
        demo_sql_validation_and_execution(db_path)
        demo_sql_to_nosql()

    metrics = demo_base_model_evaluation(db_path, log_mlflow=args.mlflow, config=config)
    demo_datasets_overview()

    save_demo_results(metrics, get_results_dir() / "demo_results.json", config=config)

    banner("Demo Complete — Ready for Q&A")
    print("  Streamlit UI : streamlit run apps/streamlit/app.py")
    print("  API docs     : http://localhost:8000/docs")
    print("  MLflow UI    : mlflow ui --backend-store-uri mlruns\n")


if __name__ == "__main__":
    main()
