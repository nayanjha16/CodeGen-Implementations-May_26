"""
RepoCoder Studio — offline Stage 4/5 index builder.

Builds the AST index, embeddings, FAISS indices, and dependency graphs
for one repository (Stage 4), plus a second FAISS index built directly
over this project's own approved corpus (Stage 5's CorpusIndex, see
src/corpus_retriever.py) -- so the inference container only ever has to
*load* them (see app/main.py's lifespan) rather than build them at
request time. This mirrors scripts/run_training_pipeline.py's
offline/inference split for the LoRA adapter.

Usage
-----
    python scripts/build_repo_index.py
    python scripts/build_repo_index.py --repo-path /path/to/other/repo
    python scripts/build_repo_index.py --skip-corpus-index

Run this once (locally, in a notebook, or as a one-off container step)
before starting app/main.py with RAG enabled. The corpus index build is
a no-op (0 rows indexed, not an error) if approved_corpus.jsonl doesn't
exist yet on this project root -- run the corpus-building/validation
stages first if you want corpus-grounded RAG.
"""

import argparse
import json
import tempfile
from pathlib import Path

from src.config import CONFIG
from src.logger import LOG, SectionPrinter, SummaryPrinter
from src.repo_explorer import RepositoryExplorer
from src.corpus_retriever import CorpusIndex
from src.storage import ProjectStorageManager
from src.artifact_manifest import promote_directory


def main() -> None:
    storage = ProjectStorageManager(CONFIG)

    parser = argparse.ArgumentParser(description="Build the Stage 4/5 repository + corpus indices.")
    parser.add_argument("--repo-path", default=CONFIG.retrieval.repo_path)
    parser.add_argument("--output-dir", default=str(storage.repo_explorer_output_dir()))
    parser.add_argument("--embedding-dir", default=str(storage.repo_explorer_embedding_dir()))
    parser.add_argument("--model-name", default=CONFIG.retrieval.embedding_model)
    parser.add_argument(
        "--skip-corpus-index",
        action="store_true",
        help="Only build the Stage 4 repository index, skip the Stage 5 approved-corpus index.",
    )
    args = parser.parse_args()

    SectionPrinter.header("Stage 4 — Building Repository Index")
    LOG.info(f"Repo path: {args.repo_path}")

    output_target = Path(args.output_dir)
    embedding_target = Path(args.embedding_dir)
    with tempfile.TemporaryDirectory(prefix="repocoder_index_build_") as tmp:
        staged_root = Path(tmp)
        staged_output = staged_root / "output"
        staged_embeddings = staged_root / "embeddings"
        explorer = RepositoryExplorer(
            repo_path=args.repo_path,
            output_dir=str(staged_output),
            embedding_dir=str(staged_embeddings),
            model_name=args.model_name,
            rebuild=True,
            config=CONFIG,
        )
        if explorer.embedder.is_mock and not CONFIG.retrieval.allow_mock_embeddings:
            raise RuntimeError(
                "Embedding model unavailable and mock embeddings are disabled. "
                "No index was promoted."
            )
        promote_directory(staged_output, output_target)
        promote_directory(staged_embeddings, embedding_target)

    # A hand-labeled query set for this repo, if one exists as a sibling
    # fixture ("<repo_path>_eval_queries.json") -- e.g.
    # repo_explorer_data/sample_repo_eval_queries.json for the bundled
    # sample repo. Falls back to the weaker self-referential smoke test
    # (see RepositoryExplorer.run_evaluation's docstring) when there is no
    # curated fixture for the repo being indexed.
    repo_path_obj = Path(args.repo_path)
    eval_fixture = repo_path_obj.parent / f"{repo_path_obj.name}_eval_queries.json"
    test_queries = None
    if eval_fixture.exists():
        test_queries = json.loads(eval_fixture.read_text(encoding="utf-8"))
        LOG.info(f"Using hand-labeled eval query set: {eval_fixture} ({len(test_queries)} queries)")
    else:
        LOG.info(
            f"No hand-labeled eval fixture at {eval_fixture} -- falling back to the "
            "self-referential smoke test (see run_evaluation's docstring for why that "
            "is not a real retrieval-quality measurement)."
        )

    # Both calls also self-persist under outputs/reports/ via
    # ProjectStorageManager -- repo_explorer_report_path() / repo_explorer_eval_path().
    report = explorer.generate_summary_report()
    metrics = explorer.run_evaluation(test_queries=test_queries)

    SummaryPrinter.print_summary(
        "Stage 4 Index Build Complete",
        {
            "Files": report["total_files"],
            "Functions": report["total_functions"],
            "Classes": report["total_classes"],
            "Total LOC": report["total_loc"],
            "Mock Embeddings": explorer.embedder.is_mock,
            "Self-check metrics": metrics,
            "Output dir": args.output_dir,
            "Embedding dir": args.embedding_dir,
            "Report saved to": storage.repo_explorer_report_path(),
            "Eval metrics saved to": storage.repo_explorer_eval_path(),
        },
    )

    if args.skip_corpus_index:
        return

    SectionPrinter.header("Stage 5 — Building Approved-Corpus Retrieval Index")

    # Reuses explorer.embedder (built above, from --model-name) instead of
    # letting CorpusIndex load its own separate copy -- avoids resident
    # duplicate model memory, and also avoids repo/corpus ending up on
    # different embedding models if --model-name ever overrides the config
    # default.
    corpus_index = CorpusIndex(config=CONFIG, embedder=explorer.embedder)
    indexed_rows = corpus_index.build(rebuild=True)

    SummaryPrinter.print_summary(
        "Stage 5 Corpus Index Build Complete",
        {
            "Train-split rows indexed": indexed_rows,
            "Mock Embeddings": corpus_index.embedder.is_mock,
            "Index dir": str(storage.corpus_index_dir()),
            "Report saved to": storage.corpus_index_report_path(),
        },
    )


if __name__ == "__main__":
    main()
