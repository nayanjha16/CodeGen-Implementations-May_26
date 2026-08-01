"""Dataset loading for both training stages."""
from typing import Sequence

from datasets import load_dataset

from config.config import CFG
from utils.logger import logger

STAGE1_DOC_COL = "func_documentation_string"
STAGE1_CODE_COL = "func_code_string"

CODEXGLUE_DATASET_KWARGS = dict(
    path="google/code_x_glue_cc_code_to_code_trans")
CODEXGLUE_JAVA_COL = "java"
CODEXGLUE_CS_COL = "cs"


def load_code_dataset(split: str, dataset_name: str = CFG.DATASET_NAME, config: str = CFG.DATASET_CONFIG):
    """Load a split of the Stage 1 (NL -> Java) dataset."""
    logger.info("Loading %s/%s split='%s' ...", dataset_name, config, split)
    dataset = load_dataset(dataset_name, config, split=split)
    logger.info("Loaded %d examples for split '%s'.", len(dataset), split)
    return dataset


def validate_dataset(dataset, required_columns: Sequence[str], n_check: int = 100) -> None:
    """Validate that required columns exist and are largely non-empty."""
    if dataset is None or len(dataset) == 0:
        raise ValueError("Dataset is empty or None.")

    missing = [c for c in required_columns if c not in dataset.column_names]
    if missing:
        raise ValueError(
            f"Dataset missing required columns: {missing} (available: {dataset.column_names})")

    sample = dataset.select(range(min(n_check, len(dataset))))
    for col in required_columns:
        n_null = sum(1 for v in sample[col] if v is None or not str(v).strip())
        if n_null:
            logger.warning(
                "Column '%s' has %d empty values in first %d rows.", col, n_null, len(sample))

    logger.info("Dataset validation passed for columns: %s",
                list(required_columns))


def _normalize_split(dataset, java_col, csharp_col):
    """Return a list of {'java', 'cs'} dicts, or None if columns are not usable."""
    columns = set(dataset.column_names)
    if java_col is None or java_col not in columns:
        java_col = next((c for c in columns if c.lower() in (
            "java", "java_code", "src", "source")), None)
    if csharp_col is None or csharp_col not in columns:
        csharp_col = next((c for c in columns if c.lower() in (
            "cs", "csharp", "c#", "cs_code", "tgt", "target")), None)
    if not java_col or not csharp_col:
        return None

    pairs = [
        {"java": j, "cs": c}
        for j, c in zip(dataset[java_col], dataset[csharp_col])
        if isinstance(j, str) and isinstance(c, str) and j.strip() and c.strip()
    ]
    return pairs or None


def load_java_csharp_dataset():
    """Load the Java<->C# dataset (CodeXGLUE-Java-CS); return (label, {split: pairs})."""
    label = "CodeXGLUE-Java-CS"
    try:
        logger.info("Loading Java/C# dataset: %s (%s) ...",
                    label, CODEXGLUE_DATASET_KWARGS["path"])
        raw = load_dataset(**CODEXGLUE_DATASET_KWARGS)
        split_names = list(raw.keys()) if hasattr(raw, "keys") else ["train"]

        collected = {}
        for split in split_names:
            pairs = _normalize_split(
                raw[split], CODEXGLUE_JAVA_COL, CODEXGLUE_CS_COL)
            if pairs:
                collected[split] = pairs

        if not collected:
            raise RuntimeError(f"{label} has no usable Java/C# columns.")

        total = sum(len(v) for v in collected.values())
        logger.info("Loaded %s: %d Java/C# pairs across splits %s",
                    label, total, list(collected))
        return label, collected
    except Exception:
        logger.exception("Failed to load %s dataset.", label)
        raise
