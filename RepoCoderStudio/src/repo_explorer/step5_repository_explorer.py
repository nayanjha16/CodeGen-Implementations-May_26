"""
============================================================
RepoCoder Studio — Stage 4
step5_repository_explorer.py
============================================================

RepositoryExplorer — the unified query interface that is the primary
deliverable of Stage 4, and the object Stage 5's retriever wraps.

NOTE: Reconstructed from the Stage 4 documentation — see step1_ast_parser.py
for the reconstruction disclaimer, which applies to this whole package.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from src.config import CONFIG, AppConfig
from src.logger import LOG
from src.storage import ProjectStorageManager
from src.artifact_manifest import (
    atomic_write_json,
    load_json,
    manifests_compatible,
    repository_manifest,
)

from .step1_ast_parser import RepositoryIndexer, FunctionInfo, ClassInfo
from .step2_embeddings import CodeEmbedder, EmbeddingBuilder
from .step3_faiss_index import FAISSIndexBuilder, CodeSearchEngine, SearchResult
from .step4_dependency_tracer import DependencyTracer


class RepositoryExplorer:
    """Combines AST index + embeddings + FAISS search + dependency graph
    behind a three-mode query interface: semantic search, exact lookup,
    and structural (dependency) queries.

    Owns a ProjectStorageManager the same way CandidateCorpusBuilder /
    ValidationEngine do, so its human-readable reports (generate_summary_report,
    run_evaluation) land under outputs/reports/ automatically instead of each
    caller having to remember to persist them.
    """

    def __init__(
        self,
        repo_path: str,
        output_dir: Optional[str] = None,
        embedding_dir: Optional[str] = None,
        model_name: str = "all-MiniLM-L6-v2",
        rebuild: bool = False,
        config: AppConfig = CONFIG,
        embedder: Optional[CodeEmbedder] = None,
    ):
        self.config = config
        self.storage = ProjectStorageManager(config)

        self.repo_path = repo_path
        # Default to the centralized StorageConfig locations (same pattern as
        # adapters_dir / checkpoints_dir) when the caller doesn't pin an
        # explicit dir -- callers that DO need a non-default location (e.g.
        # indexing a foreign repo while still reporting into this project)
        # can still override both.
        self.output_dir = output_dir or str(self.storage.repo_explorer_output_dir())
        self.embedding_dir = embedding_dir or str(self.storage.repo_explorer_embedding_dir())

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.embedding_dir).mkdir(parents=True, exist_ok=True)
        self.manifest_path = Path(self.embedding_dir) / "index_manifest.json"

        # Step 1
        self.indexer = RepositoryIndexer(repo_path=repo_path, output_dir=self.output_dir)
        # Always parse the live repository for exact lookup and dependency
        # data. Cached vectors may be reused only when their manifest proves
        # they belong to this exact source tree and embedding model.
        self.indexer.index_repository()

        # Step 2
        # Multiple selectable repositories share one sentence-transformer in
        # the notebook/API.  Their FAISS indexes remain physically isolated;
        # only the immutable embedding model instance is shared.
        self.embedder = embedder or CodeEmbedder(model_name=model_name)
        expected_manifest = repository_manifest(
            Path(repo_path),
            embedding_model=model_name,
            embedding_dimension=self.embedder.dimension,
            mock_embeddings=self.embedder.is_mock,
        )
        cached_manifest = load_json(self.manifest_path)
        manifest_keys = (
            "format_version",
            "parser_version",
            # Absolute roots legitimately change when an index built in
            # Colab is copied into /data in a deployment container. Content
            # identity remains fail-closed through source_tree_hash plus the
            # Git commit where available, so location is not an integrity key.
            "git_commit",
            "source_tree_hash",
            "embedding_model",
            "embedding_dimension",
            "mock_embeddings",
            "implementation_provenance",
        )
        cache_valid = bool(
            cached_manifest
            and manifests_compatible(expected_manifest, cached_manifest, manifest_keys)
        )
        func_emb_path = Path(self.embedding_dir) / "function_embeddings.npy"
        if not rebuild and func_emb_path.exists() and not cache_valid:
            raise RuntimeError(
                "Repository index artifacts are stale or incompatible with the configured "
                "repository/embedding model. Run scripts/build_repo_index.py offline."
            )
        if rebuild or not func_emb_path.exists():
            EmbeddingBuilder(self.indexer, self.embedder, self.embedding_dir).build_all()

        # Step 3
        self.faiss_builder = FAISSIndexBuilder(embedding_dir=self.embedding_dir)
        func_index_path = Path(self.embedding_dir) / "function_index.faiss"
        if rebuild or not func_index_path.exists():
            self.faiss_builder.build_all_indices()
        else:
            self.faiss_builder.load_existing_indices()
        self.search_engine = CodeSearchEngine(index_builder=self.faiss_builder, embedder=self.embedder)
        counts = {
            "modules": len(self.indexer.modules),
            "functions": len(self.indexer.all_functions()),
            "classes": len(self.indexer.all_classes()),
        }
        completed_manifest = repository_manifest(
            Path(repo_path),
            embedding_model=model_name,
            embedding_dimension=self.embedder.dimension,
            component_counts=counts,
            mock_embeddings=self.embedder.is_mock,
        )
        if rebuild or not self.manifest_path.exists():
            atomic_write_json(self.manifest_path, completed_manifest)
        elif cached_manifest and cached_manifest.get("component_counts") != counts:
            raise RuntimeError(
                "Repository index component counts do not match the live repository. "
                "Rebuild the index offline."
            )

        # Step 4 (always rebuilt in memory; graphs are cheap to recompute)
        self.tracer = DependencyTracer(indexer=self.indexer)
        self.tracer.build_import_graph()
        self.tracer.build_call_graph()

        # Lookup dictionaries for exact-lookup queries
        self._fn_by_name: Dict[str, List[FunctionInfo]] = {}
        self._cls_by_name: Dict[str, List[ClassInfo]] = {}
        self._fns_by_file: Dict[str, List[FunctionInfo]] = {}
        for fn in self.indexer.all_functions():
            self._fn_by_name.setdefault(fn.name, []).append(fn)
            self._fns_by_file.setdefault(fn.file_path, []).append(fn)
        for cls in self.indexer.all_classes():
            self._cls_by_name.setdefault(cls.name, []).append(cls)

        LOG.info(
            f"RepositoryExplorer ready: {len(self.indexer.modules)} files, "
            f"{len(self.indexer.all_functions())} functions, "
            f"{len(self.indexer.all_classes())} classes "
            f"(mock_embeddings={self.embedder.is_mock})"
        )

    # ------------------------------------------------------------
    # Mode 1: semantic search
    # ------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
        component_types: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        return self.search_engine.search(query, top_k=top_k, component_types=component_types)

    def display_search_results(self, query: str, results: List[SearchResult]) -> None:
        self.search_engine.display_results(query, results)

    # ------------------------------------------------------------
    # Mode 2: exact lookup
    # ------------------------------------------------------------

    def find_function(self, name: str) -> List[FunctionInfo]:
        return self._fn_by_name.get(name, [])

    def find_class(self, name: str) -> List[ClassInfo]:
        return self._cls_by_name.get(name, [])

    def list_functions_in_file(self, filename: str) -> List[FunctionInfo]:
        return self._fns_by_file.get(filename, [])

    def get_function_source(self, name: str) -> Optional[str]:
        matches = self.find_function(name)
        return matches[0].source if matches else None

    def display_function_info(self, fn: FunctionInfo) -> None:
        print(f"{fn.name}({', '.join(fn.args)})  {fn.file_path}:{fn.start_line}")
        if fn.docstring:
            print(f"  {fn.docstring.strip()}")

    # ------------------------------------------------------------
    # Mode 3: structural queries
    # ------------------------------------------------------------

    def get_dependencies(self, filename: str) -> List[str]:
        return self.tracer.get_dependencies(filename)

    def get_dependents(self, filename: str) -> List[str]:
        return self.tracer.get_dependents(filename)

    def get_transitive_dependencies(self, filename: str) -> List[str]:
        return self.tracer.get_transitive_dependencies(filename)

    def get_callees(self, file_path: str, function_name: str) -> List[FunctionInfo]:
        identifiers = self.tracer.get_callees(f"{file_path}::{function_name}")
        return self._functions_from_identifiers(identifiers)

    def get_callers(self, file_path: str, function_name: str) -> List[FunctionInfo]:
        identifiers = self.tracer.get_callers(f"{file_path}::{function_name}")
        return self._functions_from_identifiers(identifiers)

    def related_functions(
        self,
        file_path: str,
        function_name: str,
        include_same_file: bool = True,
    ) -> List[tuple[str, FunctionInfo]]:
        """Hierarchical expansion around a retrieved symbol.

        Relationships are labelled so downstream RAG can preserve why a
        function was added instead of presenting every neighbor as an equal
        semantic match.
        """
        related: List[tuple[str, FunctionInfo]] = []
        seen: set[tuple[str, str]] = {(file_path, function_name)}
        for relation, functions in (
            ("caller", self.get_callers(file_path, function_name)),
            ("callee", self.get_callees(file_path, function_name)),
        ):
            for function in functions:
                key = (function.file_path, function.name)
                if key not in seen:
                    related.append((relation, function))
                    seen.add(key)
        if include_same_file:
            for function in self.list_functions_in_file(file_path):
                key = (function.file_path, function.name)
                if key not in seen:
                    related.append(("same_file", function))
                    seen.add(key)
        return related

    def _functions_from_identifiers(self, identifiers: List[str]) -> List[FunctionInfo]:
        functions: List[FunctionInfo] = []
        for identifier in identifiers:
            file_path, separator, name = identifier.rpartition("::")
            if not separator:
                continue
            functions.extend(
                function
                for function in self._fn_by_name.get(name, [])
                if function.file_path == file_path
            )
        return functions

    # ------------------------------------------------------------
    # Mode 4: migration status (Python -> Java, in-progress repos)
    # ------------------------------------------------------------

    def migration_status(self, python_ext: str = ".py", java_ext: str = ".java") -> dict:
        """For a repository undergoing incremental Python -> Java migration
        (see repo_explorer_data/sample_repo/MIGRATION.md for the bundled
        demo repo's own status): which Python modules already have a
        same-directory Java counterpart, and which are still pending.

        Naming convention assumed: snake_case.py <-> PascalCase.java in the
        same directory (e.g. fraud_detector.py <-> FraudDetector.java) --
        the convention this project's own translated files follow. This is
        a real navigation question a migration lead would actually ask
        ("how much of this repo is migrated, what's left"), not a generic
        search demo.
        """
        java_by_dir_stem = {}
        for m in self.indexer.modules:
            if not m.file_path.endswith(java_ext):
                continue
            path = Path(m.file_path)
            java_by_dir_stem[(str(path.parent), path.stem)] = m.file_path

        translated: List[dict] = []
        pending: List[str] = []
        for m in self.indexer.modules:
            if not m.file_path.endswith(python_ext):
                continue
            path = Path(m.file_path)
            # Package markers are not migratable business modules. Counting
            # __init__.py as pending made the migration percentage disagree
            # with the documented module inventory.
            if path.name == "__init__.py":
                continue
            camel_case_stem = "".join(part.capitalize() for part in path.stem.split("_"))
            java_match = java_by_dir_stem.get((str(path.parent), camel_case_stem))
            if java_match:
                translated.append({"python": m.file_path, "java": java_match})
            else:
                pending.append(m.file_path)

        total = len(translated) + len(pending)
        return {
            "translated": translated,
            "pending": sorted(pending),
            "translated_count": len(translated),
            "pending_count": len(pending),
            "migration_progress_pct": round(100 * len(translated) / total, 1) if total else 0.0,
        }

    # ------------------------------------------------------------
    # Evaluation and reporting
    # ------------------------------------------------------------

    def run_evaluation(self, test_queries: Optional[List[dict]] = None) -> dict:
        """Computes Precision@5/Recall@5/MRR@5.

        Pass a hand-labeled test_queries list (see
        repo_explorer_data/sample_repo_eval_queries.json for the bundled
        sample repo's) whenever one is available for the indexed repo --
        that is a real retrieval-quality measurement. Without one, this
        falls back to _default_eval_queries(), which is a smoke test, not
        a benchmark: see that method's docstring for why.
        """
        queries = test_queries if test_queries is not None else self._default_eval_queries()
        metrics = self.search_engine.run_evaluation(queries, k=5)
        metrics["query_set"] = "hand_labeled" if test_queries is not None else "self_referential_smoke_test"
        metrics["query_count"] = len(queries)
        self.storage.save_json(metrics, self.storage.repo_explorer_eval_path())
        return metrics

    def _default_eval_queries(self) -> List[dict]:
        """Fallback only: each indexed function is its own ground truth for
        a query built from its own name. This exists so evaluation always
        has *something* to score on an unfamiliar repo with no curated
        fixture -- it is not a retrieval-quality benchmark. A query
        constructed directly from the name of its only relevant document
        will score near-perfectly regardless of whether the underlying
        embedding/search is any good; treat any run using this fallback as
        "the pipeline runs end to end", not "retrieval is measured to be
        good". Pass a real test_queries list to run_evaluation() instead
        whenever one exists for the repo being indexed.
        """
        functions = self.indexer.all_functions()[:5]
        return [
            {"query": fn.name.replace("_", " "), "relevant": [fn.name]}
            for fn in functions
        ]

    def generate_summary_report(self) -> dict:
        from src.artifact_manifest import STAGE4_IMPLEMENTATION_PROVENANCE

        stats = self.indexer._stats()
        report = {
            "repository": str(self.repo_path),
            "total_files": stats["total_files"],
            "total_functions": stats["total_functions"],
            "total_classes": stats["total_classes"],
            "total_loc": stats["total_lines"],
            "mock_embeddings": self.embedder.is_mock,
            "implementation_provenance": STAGE4_IMPLEMENTATION_PROVENANCE,
            "files": [
                {
                    "file_path": m.file_path,
                    "functions": [f.name for f in m.functions],
                    "classes": [c.name for c in m.classes],
                }
                for m in self.indexer.modules
            ],
        }
        # Same "engine persists its own report" rule as CandidateCorpusBuilder /
        # ValidationEngine: saved under outputs/reports/, not next to the raw
        # index/embedding artifacts in output_dir.
        self.storage.save_json(report, self.storage.repo_explorer_report_path())
        return report
