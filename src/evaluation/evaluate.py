"""End-to-end evaluation pipeline: generates predictions and computes the full
metric suite (BLEU, CodeBLEU, CodeBERTScore, Exact Match, Syntax Accuracy,
AST Similarity, Compilation Rate) for both stages."""
from typing import Callable, Dict, List, Sequence, Tuple

from config.config import CFG
from data.dataset import STAGE1_CODE_COL, STAGE1_DOC_COL, load_code_dataset, load_java_csharp_dataset, validate_dataset
from data.preprocessing import build_stage2_splits
from data.prompt_templates import STAGE1_RESPONSE_MARKER, build_stage1_prompt, clean_instruction
from evaluation.codebleu import compute_code_metrics, compute_codebleu
from evaluation.compile_validation import compute_ast_similarity, compute_compilation_rate, compute_syntax_accuracy
from evaluation.metrics import compute_bleu, compute_exact_match
from inference.pipeline import CodeGenPipeline, _run_generation
from utils.logger import logger


def generate_stage1_predictions(model, tokenizer, subset, max_new_tokens: int = 300) -> Tuple[List[str], List[str]]:
    predictions: List[str] = []
    references: List[str] = []

    for i, example in enumerate(subset):
        prompt = build_stage1_prompt(
            clean_instruction(example[STAGE1_DOC_COL]))
        try:
            decoded = _run_generation(model, tokenizer, prompt, max_new_tokens)
            prediction = decoded.split(STAGE1_RESPONSE_MARKER)[-1].strip()
        except Exception:
            logger.exception(
                "Generation failed at index %d; using empty prediction.", i)
            prediction = ""

        predictions.append(prediction)
        references.append(example[STAGE1_CODE_COL])
        if (i + 1) % 25 == 0:
            logger.info("Generated %d/%d", i + 1, len(subset))

    return predictions, references


def evaluate_stage1(model, tokenizer, n_samples: int = CFG.EVAL_SAMPLES, label: str = "fine-tuned") -> dict:
    """Generate Java predictions on a held-out test subset and score them."""
    test_data = load_code_dataset("test")
    validate_dataset(test_data, [STAGE1_DOC_COL, STAGE1_CODE_COL])
    subset = test_data.select(range(min(n_samples, len(test_data))))

    predictions, references = generate_stage1_predictions(
        model, tokenizer, subset)
    return compute_code_metrics(references, predictions, lang="java", label=label)


def run_stage2_eval_loop(gen_fn: Callable[[str], str], pairs: Sequence[dict], label: str = "") -> Tuple[List[str], List[str]]:
    predictions: List[str] = []
    references: List[str] = []

    for i, pair in enumerate(pairs):
        try:
            prediction = gen_fn(pair["java"])
        except Exception:
            logger.exception(
                "[%s] Stage 2 eval generation failed at index %d.", label, i)
            prediction = ""

        predictions.append(prediction)
        references.append(pair["cs"])
        if (i + 1) % 10 == 0:
            logger.info("[%s] evaluated %d/%d", label, i + 1, len(pairs))

    return predictions, references


def evaluate_stage2_predictions(predictions: List[str], references: List[str]) -> Dict[str, object]:
    report: Dict[str, object] = {"BLEU": compute_bleu(predictions, references)}

    try:
        report["CodeBLEU"] = compute_codebleu(
            references, predictions, lang="c_sharp")
    except Exception as exc:
        report["CodeBLEU"] = {"error": str(exc)}

    report["ExactMatch"] = compute_exact_match(predictions, references)
    report["SyntaxAccuracy"] = compute_syntax_accuracy(predictions)
    report["AST_Similarity"] = compute_ast_similarity(predictions, references)

    rate, method = compute_compilation_rate(predictions)
    report["CompilationRate"] = {"value": rate, "method": method}
    return report


def run_full_evaluation(stage1_repo: str = CFG.HF_REPO, stage2_repo: str = CFG.HF_REPO_STAGE2) -> dict:
    """Load the fine-tuned pipeline and produce a combined Stage 1 + Stage 2 report."""
    pipeline = CodeGenPipeline(
        stage1_repo=stage1_repo, stage2_repo=stage2_repo)

    stage1_report = evaluate_stage1(
        pipeline.stage1_model, pipeline.stage1_tokenizer)

    _, raw_pairs = load_java_csharp_dataset()
    _, val_pairs = build_stage2_splits(raw_pairs)
    eval_pairs = val_pairs[: CFG.STAGE2_EVAL_SAMPLES]

    predictions, references = run_stage2_eval_loop(
        pipeline.generate_csharp_from_java, eval_pairs, label="fine-tuned")
    stage2_report = evaluate_stage2_predictions(predictions, references)

    summary = {"stage1": stage1_report, "stage2": stage2_report}
    logger.info("Evaluation summary: %s", summary)
    return summary
