"""
============================================================
RepoCoder Studio
dataset_loader.py  —  v2
============================================================

Dataset loading and adapter layer.

v2 changes
----------
Explicit disk-first cache layer (spec Chapter 6).

Flow for every HuggingFace dataset:

    Dataset Cache
         ↓
    Load if exists   ← save_to_disk / load_from_disk
         ↓
    Download only if absent

When dataset_cache_enabled = True:
  - On first run: download from HuggingFace, save_to_disk().
  - On all subsequent runs: load_from_disk() — no network required.

This is faster and more reliable than HuggingFace's internal
fingerprint-based caching, which still touches the network to
validate metadata even when all data is local.

Cache directory layout (relative to project root):
  datasets/cache/
    xlcost_python/      ← DatasetDict saved by XLCoST python config
    xlcost_java/        ← DatasetDict saved by XLCoST java config
    codexglue_python/   ← DatasetDict saved by CodeXGLUE python config
    codexglue_java/     ← DatasetDict saved by CodeXGLUE java config

Important Stage 3 learning
--------------------------
For XLCoST, the reliable approach is:
- datasets==2.21.0
- load_dataset("codeparrot/xlcost-text-to-code", "Python-program-level")
- load_dataset("codeparrot/xlcost-text-to-code", "Java-program-level")

Do not rely on TransCoder Hub mirrors.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from datasets import load_dataset, load_from_disk

from src.config import CONFIG, AppConfig
from src.logger import LOG, SectionPrinter, SummaryPrinter
from src.utils import normalize_whitespace


class DatasetLoader:
    """
    Loads raw datasets and exposes them to the corpus builder.

    This class does not create CandidateRow objects.
    That responsibility belongs to corpus_builder.py.
    """

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config

    # --------------------------------------------------------
    # Dataset cache resolution
    # --------------------------------------------------------

    def _resolve_cache_dir(self) -> Optional[Path]:
        """
        Returns the absolute cache directory Path when caching is enabled,
        or None when caching is disabled.

        The directory is created if it does not exist.
        """
        if not self.config.dataset.dataset_cache_enabled:
            return None
        cache_path = self.config.storage.resolve(self.config.dataset.dataset_cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path

    def _xlcost_cache_paths(self, cache_dir: Path) -> Tuple[Path, Path]:
        return cache_dir / "xlcost_python", cache_dir / "xlcost_java"

    def _codexglue_cache_paths(self, cache_dir: Path) -> Tuple[Path, Path]:
        return cache_dir / "codexglue_python", cache_dir / "codexglue_java"

    # --------------------------------------------------------
    # Split limiting
    # --------------------------------------------------------

    def limit_split(self, dataset_split, split_name: str):
        """
        Applies demo/full split limits.

        Demo mode keeps the notebook fast.
        Full mode uses the configured full limit or all rows.
        """
        limit = self.config.dataset.get_split_limit(
            split=split_name,
            run_mode=self.config.runtime.run_mode,
        )

        if limit is None:
            LOG.info(f"{split_name}: using full split ({len(dataset_split)} rows)")
            return dataset_split

        n = min(limit, len(dataset_split))
        LOG.info(f"{split_name}: using {n}/{len(dataset_split)} rows")
        return dataset_split.select(range(n))

    # --------------------------------------------------------
    # XLCoST loading  (explicit disk-first cache)
    # --------------------------------------------------------

    def load_xlcost(self) -> Tuple[Any, Any]:
        """
        Loads XLCoST Python and Java program-level configurations.

        Checks the disk cache first; downloads from HuggingFace and saves
        to disk only when the cache is absent.

        Returns
        -------
        tuple
            (python_dataset_dict, java_dataset_dict)
        """
        SectionPrinter.header("Loading XLCoST")

        cache_dir = self._resolve_cache_dir()

        if cache_dir is not None:
            py_path, java_path = self._xlcost_cache_paths(cache_dir)

            if py_path.exists() and java_path.exists():
                LOG.info(f"[cache HIT] Loading XLCoST from disk: {cache_dir}")
                xlcost_python = load_from_disk(str(py_path))
                xlcost_java = load_from_disk(str(java_path))

                SummaryPrinter.print_summary(
                    "XLCoST Load Summary  [from cache]",
                    {
                        "Python Splits": list(xlcost_python.keys()),
                        "Java Splits": list(xlcost_java.keys()),
                        "Cache Path": str(cache_dir),
                    },
                )
                return xlcost_python, xlcost_java

            LOG.info(f"[cache MISS] XLCoST not in cache — downloading from HuggingFace")

        LOG.info("Downloading XLCoST Python config...")
        xlcost_python = load_dataset(
            self.config.dataset.xlcost_dataset_name,
            self.config.dataset.xlcost_python_config,
        )

        LOG.info("Downloading XLCoST Java config...")
        xlcost_java = load_dataset(
            self.config.dataset.xlcost_dataset_name,
            self.config.dataset.xlcost_java_config,
        )

        assert xlcost_python is not None, "XLCoST Python dataset failed to load."
        assert xlcost_java is not None, "XLCoST Java dataset failed to load."

        if cache_dir is not None:
            py_path, java_path = self._xlcost_cache_paths(cache_dir)
            LOG.info(f"Saving XLCoST to disk cache: {cache_dir}")
            xlcost_python.save_to_disk(str(py_path))
            xlcost_java.save_to_disk(str(java_path))
            LOG.info("XLCoST saved to cache.")

        SummaryPrinter.print_summary(
            "XLCoST Load Summary  [downloaded]",
            {
                "Python Splits": list(xlcost_python.keys()),
                "Java Splits": list(xlcost_java.keys()),
                "Cached": cache_dir is not None,
            },
        )

        return xlcost_python, xlcost_java

    # --------------------------------------------------------
    # CodeXGLUE loading  (explicit disk-first cache)
    # --------------------------------------------------------

    def load_codexglue(self) -> Tuple[Any, Any]:
        """
        Loads CodeXGLUE Python and Java configurations.

        Checks the disk cache first; downloads from HuggingFace and saves
        to disk only when the cache is absent.

        Each split row has the following relevant fields:
          docstring / func_documentation_string  — NL docstring
          code / func_code_string           — source code
          function / func_name              — function name

        Returns
        -------
        tuple
            (python_dataset_dict, java_dataset_dict)
        """
        SectionPrinter.header("Loading CodeXGLUE")

        cache_dir = self._resolve_cache_dir()

        if cache_dir is not None:
            py_path, java_path = self._codexglue_cache_paths(cache_dir)

            if py_path.exists() and java_path.exists():
                LOG.info(f"[cache HIT] Loading CodeXGLUE from disk: {cache_dir}")
                codexglue_python = load_from_disk(str(py_path))
                codexglue_java = load_from_disk(str(java_path))

                SummaryPrinter.print_summary(
                    "CodeXGLUE Load Summary  [from cache]",
                    {
                        "Python Splits": list(codexglue_python.keys()),
                        "Java Splits": list(codexglue_java.keys()),
                        "Cache Path": str(cache_dir),
                    },
                )
                return codexglue_python, codexglue_java

            LOG.info(f"[cache MISS] CodeXGLUE not in cache — downloading from HuggingFace")

        def _download_codexglue(config_name: str):
            """
            Downloads CodeXGLUE using the configured dataset name.

            The finalized design targets google/code_x_glue_ct_code_to_text.
            Some Colab/HF environments may expose the same CodeSearchNet
            code-to-text corpus through code_search_net.  The fallback keeps
            the notebook runnable while logging the provenance difference.
            """
            try:
                return load_dataset(
                    self.config.dataset.codexglue_dataset_name,
                    config_name,
                    trust_remote_code=True,
                )
            except Exception as primary_error:
                fallback_name = getattr(self.config.dataset, "codexglue_fallback_dataset_name", "code_search_net")
                LOG.warning(
                    f"Primary CodeXGLUE dataset load failed for {self.config.dataset.codexglue_dataset_name}/{config_name}: "
                    f"{primary_error}. Trying fallback {fallback_name}/{config_name}."
                )
                return load_dataset(
                    fallback_name,
                    config_name,
                    trust_remote_code=True,
                )

        LOG.info("Downloading CodeXGLUE Python config...")
        codexglue_python = _download_codexglue(self.config.dataset.codexglue_python_config)

        LOG.info("Downloading CodeXGLUE Java config...")
        codexglue_java = _download_codexglue(self.config.dataset.codexglue_java_config)

        assert codexglue_python is not None, "CodeXGLUE Python dataset failed to load."
        assert codexglue_java is not None, "CodeXGLUE Java dataset failed to load."

        if cache_dir is not None:
            py_path, java_path = self._codexglue_cache_paths(cache_dir)
            LOG.info(f"Saving CodeXGLUE to disk cache: {cache_dir}")
            codexglue_python.save_to_disk(str(py_path))
            codexglue_java.save_to_disk(str(java_path))
            LOG.info("CodeXGLUE saved to cache.")

        SummaryPrinter.print_summary(
            "CodeXGLUE Load Summary  [downloaded]",
            {
                "Python Splits": list(codexglue_python.keys()),
                "Java Splits": list(codexglue_java.keys()),
                "Cached": cache_dir is not None,
            },
        )

        return codexglue_python, codexglue_java


    # --------------------------------------------------------
    # Main loader
    # --------------------------------------------------------

    def load_all(self) -> Dict[str, Any]:
        """
        Loads all enabled datasets.

        Returns
        -------
        dict
            Raw dataset bundle for corpus construction.
        """
        datasets = {}

        if self.config.dataset.use_xlcost:
            xlcost_python, xlcost_java = self.load_xlcost()
            datasets["XLCoST"] = {
                "python": xlcost_python,
                "java": xlcost_java,
            }

        if self.config.dataset.use_codexglue:
            codexglue_python, codexglue_java = self.load_codexglue()
            datasets["CodeXGLUE"] = {
                "python": codexglue_python,
                "java": codexglue_java,
            }

        assert "XLCoST" in datasets, "XLCoST must be loaded as primary corpus."

        return datasets
