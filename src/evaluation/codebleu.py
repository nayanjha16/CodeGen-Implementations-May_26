"""CodeBLEU and CodeBERTScore computation."""
from typing import Dict, List

from utils.logger import logger

CODEBLEU_WEIGHTS_NO_DATAFLOW = (1 / 3, 1 / 3, 1 / 3, 0.0)


def compute_codebleu(references: List[str], predictions: List[str], lang: str) -> dict:
    from codebleu import calc_codebleu
    return calc_codebleu(references, predictions, lang=lang)


def compute_codebleu_no_dataflow(references: List[str], predictions: List[str], lang: str) -> dict:
    from codebleu import calc_codebleu
    return calc_codebleu(references, predictions, lang=lang, weights=CODEBLEU_WEIGHTS_NO_DATAFLOW)


def compute_code_bert_score(predictions: List[str], references: List[str], lang: str) -> float:
    from code_bert_score import score
    result = score(predictions, references, lang=lang)
    f1 = result[2]
    return round(float(f1.mean()), 4)


def compute_code_metrics(references: List[str], predictions: List[str], lang: str = "java", label: str = "") -> Dict[str, object]:
    """CodeBLEU + CodeBERTScore for code predictions, robust to metric failures."""
    report: Dict[str, object] = {}

    try:
        report["CodeBLEU"] = compute_codebleu(references, predictions, lang)
        report["CodeBLEU_no_dataflow"] = compute_codebleu_no_dataflow(
            references, predictions, lang)
    except Exception as exc:
        logger.exception("CodeBLEU computation failed.")
        report["CodeBLEU"] = {"error": str(exc)}
        report["CodeBLEU_no_dataflow"] = {"error": str(exc)}

    try:
        report["CodeBERTScore_F1"] = compute_code_bert_score(
            predictions, references, lang)
    except Exception:
        logger.exception("CodeBERTScore computation failed.")
        report["CodeBERTScore_F1"] = None

    logger.info("[%s] metrics: %s", label, report)
    return report
