import hashlib
import json
import os
import re
import sys
from functools import lru_cache
from pathlib import Path

import faiss
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.device import describe_device, get_inference_dtype

INDEX_DIR = PROJECT_ROOT / "models" / "repo_rag_indices"
DEFAULT_MIN_SCORE = float(os.environ.get("RAG_MIN_SCORE", "0.30"))
DEFAULT_WEAK_SCORE = float(os.environ.get("RAG_WEAK_SCORE", "0.45"))
OVERVIEW_PREFERRED_TYPES = frozenset({"doc", "summary"})

# A dedicated sentence embedding model. The previous implementation pooled a
# CausalLM's logits (vocab-sized vectors), which made every pair of texts look
# near-identical and destroyed ranking.
EMBED_MODEL_ID = os.environ.get("RAG_EMBED_MODEL_ID", "BAAI/bge-small-en-v1.5")
EMBED_MAX_LENGTH = int(os.environ.get("RAG_EMBED_MAX_LENGTH", "512"))
EMBED_BATCH_SIZE = int(os.environ.get("RAG_EMBED_BATCH_SIZE", "16"))
EMBED_CONFIG_FILE = "embedder.json"

# Additive bonus when query terms match a chunk's file path or basename.
PATH_BOOST_WEIGHT = float(os.environ.get("RAG_PATH_BOOST", "0.08"))
_WORD_RE = re.compile(r"[A-Za-z0-9_]+")


def repo_index_key(repo_root: str) -> str:
    """Stable index folder id from the resolved repo path (avoids basename collisions)."""
    resolved = str(Path(repo_root).expanduser().resolve())
    return hashlib.sha256(resolved.encode()).hexdigest()[:16]


def repo_index_dir(repo_root: str) -> Path:
    """Primary index directory for a repo (hash of full path)."""
    return INDEX_DIR / repo_index_key(repo_root)


def legacy_repo_index_dir(repo_root: str) -> Path:
    """Legacy index path keyed only by folder basename (pre-fix builds)."""
    return INDEX_DIR / Path(repo_root).expanduser().resolve().name


def resolve_repo_index_dir(repo_root: str) -> Path | None:
    """Return an existing index directory (new hash path, else legacy basename)."""
    primary = repo_index_dir(repo_root)
    if (primary / "faiss.index").exists() and (primary / "metadata.json").exists():
        return primary
    legacy = legacy_repo_index_dir(repo_root)
    if (legacy / "faiss.index").exists() and (legacy / "metadata.json").exists():
        return legacy
    return None


def rag_index_exists(repo_root: str) -> bool:
    return resolve_repo_index_dir(repo_root) is not None


@lru_cache(maxsize=2)
def load_embedder(model_id: str) -> tuple[object, object, int]:
    """Load and cache the embedding model process-wide.

    Returns (tokenizer, model, embedding_dim). Cached so repeated retrievals
    never pay the model load cost again.
    """
    dtype = get_inference_dtype("cpu")
    print(f"Loading RAG embedder ({model_id}) on {describe_device('cpu')}")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModel.from_pretrained(model_id, torch_dtype=dtype)
    model.eval()
    dim = int(model.config.hidden_size)
    return tokenizer, model, dim


def embedding_dim(model_id: str | None = None) -> int:
    """Embedding width of the configured model (loads it once, then cached)."""
    return load_embedder(model_id or EMBED_MODEL_ID)[2]


class StaleIndexError(RuntimeError):
    """Raised when an index was built with an incompatible embedder."""


class RepoRAGPipeline:
    def __init__(
        self,
        repo_root: str,
        device: str | None = None,
    ):
        self.repo_root = Path(repo_root).resolve()
        # Embedding runs on CPU: the model is tiny and this avoids MPS quirks.
        self.device = torch.device("cpu")
        existing = resolve_repo_index_dir(str(self.repo_root))
        self.index_dir = existing or repo_index_dir(str(self.repo_root))
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.model_id = EMBED_MODEL_ID
        self.tokenizer, self.encoder, self.embed_dim = load_embedder(self.model_id)

        self.index: faiss.IndexFlatIP | None = None
        self.chunks_meta: list[dict] = []
        self.stale_index = False

        index_path = self.index_dir / "faiss.index"
        meta_path = self.index_dir / "metadata.json"
        if index_path.exists() and meta_path.exists():
            self._load_index(index_path, meta_path)

    def _encode(self, texts: list[str]) -> np.ndarray:
        embeddings = []
        for i in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[i : i + EMBED_BATCH_SIZE]
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=EMBED_MAX_LENGTH,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.encoder(**inputs)
                # BGE models are trained with CLS pooling.
                pooled = outputs.last_hidden_state[:, 0]
                pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
                embeddings.append(pooled.float().cpu().numpy())
        return np.vstack(embeddings).astype(np.float32)

    def _embedder_config(self) -> dict:
        return {"model_id": self.model_id, "dim": self.embed_dim}

    def build_index(self, chunks: list[dict]):
        """Build FAISS index from code chunks."""
        self.chunks_meta = chunks
        if not chunks:
            print("No chunks provided to index.")
            return

        texts_to_embed = []
        for c in chunks:
            # We embed a combination of metadata and content for better semantic matching
            meta = c["metadata"]
            text = f"File: {meta.get('file_path')}\nType: {meta.get('type')} {meta.get('name', '')}\n{c['content']}"
            texts_to_embed.append(text)

        print(f"Encoding {len(texts_to_embed)} chunks for repo RAG...")
        embeddings = self._encode(texts_to_embed)
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        self.stale_index = False

        faiss.write_index(self.index, str(self.index_dir / "faiss.index"))
        with open(self.index_dir / "metadata.json", "w") as f:
            json.dump(self.chunks_meta, f)
        with open(self.index_dir / EMBED_CONFIG_FILE, "w") as f:
            json.dump(self._embedder_config(), f)
        print(
            f"Repo RAG Index saved to {self.index_dir} "
            f"({len(self.chunks_meta)} vectors, dim={dim}, embedder={self.model_id})"
        )

    def _load_index(self, index_path: Path, meta_path: Path):
        index = faiss.read_index(str(index_path))
        if int(index.d) != int(self.embed_dim):
            # An index built by a different embedder cannot be searched with the
            # current one; FAISS would abort on the dimension mismatch.
            self.index = None
            self.chunks_meta = []
            self.stale_index = True
            print(
                f"Ignoring stale RAG index at {self.index_dir}: it has dim={index.d} "
                f"but embedder {self.model_id} produces dim={self.embed_dim}. "
                "Rebuild it with: python scripts/build_repo_index.py --repo-root <path>"
            )
            return
        self.index = index
        with open(meta_path) as f:
            self.chunks_meta = json.load(f)

    def index_file_paths(self) -> list[str]:
        """Distinct file paths present in the index metadata."""
        seen: list[str] = []
        known: set[str] = set()
        for chunk in self.chunks_meta:
            path = str((chunk.get("metadata") or {}).get("file_path", "") or "")
            if path and path not in known:
                known.add(path)
                seen.append(path)
        return seen

    def resolve_index_paths(self, refs: list[str]) -> list[str]:
        """Map user file mentions onto file paths as stored in the index.

        ``readme.md`` resolves to ``mini-git/README.md`` without consulting the
        filesystem, so index path formatting is always respected.
        """
        matches: list[str] = []
        for ref in refs:
            needle = str(ref or "").strip().lstrip("@").replace("\\", "/").lower()
            if not needle:
                continue
            base = Path(needle).name
            for path in self.index_file_paths():
                candidate = path.replace("\\", "/").lower()
                if (
                    candidate == needle
                    or candidate.endswith("/" + needle)
                    or Path(candidate).name == base
                ) and path not in matches:
                    matches.append(path)
        return matches

    @staticmethod
    def _path_boost(query: str, file_path: str, name: str = "") -> float:
        """Bonus for chunks whose path/basename overlaps the query terms."""
        if PATH_BOOST_WEIGHT <= 0:
            return 0.0
        terms = {t for t in _WORD_RE.findall(query.lower()) if len(t) > 2}
        if not terms:
            return 0.0
        path = str(file_path or "").replace("\\", "/").lower()
        tokens = {t for t in _WORD_RE.findall(path) if t}
        tokens |= {t for t in _WORD_RE.findall(str(name or "").lower()) if t}
        stem = Path(path).stem
        if stem:
            tokens.add(stem)
        return PATH_BOOST_WEIGHT if terms & tokens else 0.0

    @staticmethod
    def _apply_score_margin(
        candidates: list[dict], score_margin: float | None
    ) -> list[dict]:
        """Drop candidates that score far below the best match.

        Gating uses the raw similarity, never a boosted score: a boost applied
        to one chunk would otherwise raise the cutoff and evict its peers.
        """
        if score_margin is None or not candidates:
            return candidates

        def base(chunk: dict) -> float:
            return float(chunk.get("base_score", chunk.get("score", 0)))

        cutoff = max(base(c) for c in candidates) - float(score_margin)
        return [c for c in candidates if base(c) >= cutoff]

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        *,
        min_score: float | None = None,
        dedupe_by_file: bool = True,
        file_paths: list[str] | None = None,
        score_margin: float | None = None,
        path_boost: bool = False,
    ) -> list[dict]:
        if self.index is None or not self.chunks_meta:
            return []
        threshold = DEFAULT_MIN_SCORE if min_score is None else min_score
        allowed_paths: set[str] | None = None
        if file_paths:
            allowed_paths = {str(p).replace("\\", "/") for p in file_paths if str(p).strip()}
            if allowed_paths:
                dedupe_by_file = False
        # Fetch extra candidates for filtering/deduping
        fetch_k = min(max(top_k * 4, top_k), len(self.chunks_meta))
        if allowed_paths:
            fetch_k = len(self.chunks_meta)
        embedding = self._encode([query])
        scores, indices = self.index.search(embedding, fetch_k)

        candidates: list[dict] = []
        for score, i in zip(scores[0], indices[0]):
            if i < 0 or i >= len(self.chunks_meta):
                continue
            if float(score) < threshold:
                continue
            res = self.chunks_meta[i].copy()
            res["score"] = float(score)
            res["base_score"] = float(score)
            meta = res.get("metadata") or {}
            if allowed_paths:
                file_path = str(meta.get("file_path", "") or "").replace("\\", "/")
                if file_path not in allowed_paths:
                    continue
            if path_boost:
                res["score"] += self._path_boost(
                    query,
                    str(meta.get("file_path", "") or ""),
                    str(meta.get("name", "") or ""),
                )
            candidates.append(res)

        if path_boost:
            candidates.sort(key=lambda c: float(c.get("score", 0)), reverse=True)
        candidates = self._apply_score_margin(candidates, score_margin)

        if not dedupe_by_file:
            return candidates[:top_k]

        # Keep best-scoring chunk per file, then fill from remaining files
        best_by_file: dict[str, dict] = {}
        for item in candidates:
            meta = item.get("metadata") or {}
            file_path = str(meta.get("file_path", "") or "")
            if not file_path:
                continue
            prev = best_by_file.get(file_path)
            if prev is None or item["score"] > prev["score"]:
                best_by_file[file_path] = item

        diversified = sorted(best_by_file.values(), key=lambda x: x["score"], reverse=True)
        if len(diversified) >= top_k:
            return diversified[:top_k]

        seen_files = set(best_by_file.keys())
        for item in candidates:
            meta = item.get("metadata") or {}
            file_path = str(meta.get("file_path", "") or "")
            if file_path in seen_files:
                continue
            diversified.append(item)
            seen_files.add(file_path)
            if len(diversified) >= top_k:
                break
        return diversified[:top_k]

    def find_doc_chunks(self) -> list[dict]:
        """Return README/doc chunks stored in the index metadata."""
        return [
            chunk.copy()
            for chunk in self.chunks_meta
            if (chunk.get("metadata") or {}).get("type") == "doc"
        ]

    @staticmethod
    def _rank_by_preferred_types(
        chunks: list[dict],
        prefer_types: frozenset[str],
    ) -> list[dict]:
        def sort_key(chunk: dict) -> float:
            chunk_type = str((chunk.get("metadata") or {}).get("type", ""))
            boost = 0.15 if chunk_type in prefer_types else 0.0
            return float(chunk.get("score", 0)) + boost

        return sorted(chunks, key=sort_key, reverse=True)

    def retrieve_overview(
        self,
        query: str,
        top_k: int = 8,
        *,
        min_score: float | None = None,
        prefer_types: frozenset[str] | None = None,
        file_paths: list[str] | None = None,
        score_margin: float | None = None,
        path_boost: bool = False,
    ) -> list[dict]:
        """Retrieve with doc/summary bias and inject README when missing."""
        if self.index is None or not self.chunks_meta:
            return []

        preferred = prefer_types or OVERVIEW_PREFERRED_TYPES
        fetch_k = min(max(top_k * 2, top_k), len(self.chunks_meta))
        results = self.retrieve(
            query,
            top_k=fetch_k,
            min_score=min_score,
            file_paths=file_paths,
            score_margin=score_margin,
            path_boost=path_boost,
        )
        results = self._rank_by_preferred_types(results, preferred)[:top_k]

        # When the caller scoped the search to specific files, injecting an
        # unrelated README would contradict that scope.
        if file_paths:
            return results

        seen_files = {
            str((chunk.get("metadata") or {}).get("file_path", ""))
            for chunk in results
        }
        for doc_chunk in self.find_doc_chunks():
            file_path = str((doc_chunk.get("metadata") or {}).get("file_path", ""))
            if not file_path or file_path in seen_files:
                continue
            injected = doc_chunk.copy()
            best_score = max((float(c.get("score", 0)) for c in results), default=0.0)
            injected["score"] = max(best_score, DEFAULT_WEAK_SCORE)
            results.insert(0, injected)
            results = results[:top_k]
            break

        return results


_PIPELINE_CACHE: dict[str, tuple[float, RepoRAGPipeline]] = {}


def _index_fingerprint(repo_root: str) -> tuple[str, float]:
    """Cache key parts: index location plus its last-modified time."""
    index_dir = resolve_repo_index_dir(repo_root) or repo_index_dir(repo_root)
    index_path = index_dir / "faiss.index"
    try:
        mtime = index_path.stat().st_mtime
    except OSError:
        mtime = 0.0
    return str(index_dir), mtime


def get_repo_rag_pipeline(repo_root: str) -> RepoRAGPipeline:
    """Return a cached pipeline for a repo, rebuilt when the index changes."""
    key, mtime = _index_fingerprint(repo_root)
    cached = _PIPELINE_CACHE.get(key)
    if cached is not None and cached[0] == mtime:
        return cached[1]
    pipeline = RepoRAGPipeline(repo_root=repo_root)
    _PIPELINE_CACHE[key] = (mtime, pipeline)
    return pipeline


def clear_repo_rag_cache() -> None:
    """Drop cached pipelines (used by tests and after rebuilding an index)."""
    _PIPELINE_CACHE.clear()
