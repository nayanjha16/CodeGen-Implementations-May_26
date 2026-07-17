"""RAG pipeline: FAISS index over CodeGen embeddings for few-shot retrieval."""

import argparse
import json
import sys
from pathlib import Path

import faiss
import numpy as np
import torch
from datasets import load_from_disk
from transformers import AutoModel, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "data" / "scripts"))

from utils.device import describe_device, get_best_device, get_inference_dtype

from prompt_templates import (
    RAG_FEW_SHOT_JAVA2PY,
    RAG_FEW_SHOT_NL2PY,
    format_java2py_inference,
    format_nl2py_inference,
)

EMBEDDING_MODEL = "Salesforce/codegen-350M-multi"
INDEX_DIR = PROJECT_ROOT / "models" / "rag_indices"


class RAGPipeline:
    def __init__(
        self,
        task: str,
        embedding_model: str = EMBEDDING_MODEL,
        top_k: int = 3,
        device: str | None = None,
    ):
        self.task = task
        self.top_k = top_k
        self.device = get_best_device(device)
        self.index_dir = INDEX_DIR / task
        self.index_dir.mkdir(parents=True, exist_ok=True)
        dtype = get_inference_dtype(self.device)

        print(f"Loading RAG encoder on {describe_device(self.device)} (dtype={dtype})")
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model, trust_remote_code=True)
        self.encoder = AutoModel.from_pretrained(
            embedding_model,
            trust_remote_code=True,
            torch_dtype=dtype,
        )
        self.encoder.to(self.device)
        self.encoder.eval()

        self.index: faiss.IndexFlatIP | None = None
        self.examples: list[dict] = []

        index_path = self.index_dir / "faiss.index"
        meta_path = self.index_dir / "metadata.json"
        if index_path.exists() and meta_path.exists():
            self._load_index(index_path, meta_path)

    def _encode(self, texts: list[str]) -> np.ndarray:
        embeddings = []
        batch_size = 8
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.encoder(**inputs, output_hidden_states=True)
                hidden = outputs.hidden_states[-1]
                mask = inputs["attention_mask"].unsqueeze(-1).float()
                pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
                pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
                embeddings.append(pooled.cpu().numpy())
        return np.vstack(embeddings).astype(np.float32)

    def build_index(self, dataset_path: Path | None = None):
        """Build FAISS index from training split."""
        dataset_path = dataset_path or (PROJECT_ROOT / "data" / "processed" / self.task / "train")
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        ds = load_from_disk(str(dataset_path))
        self.examples = [ds[i] for i in range(len(ds))]

        if self.task == "nl2py":
            query_texts = [ex["nl_query"] for ex in self.examples]
        else:
            query_texts = [ex["java_code"] for ex in self.examples]

        print(f"Encoding {len(query_texts)} examples for {self.task}...")
        embeddings = self._encode(query_texts)
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

        faiss.write_index(self.index, str(self.index_dir / "faiss.index"))
        with open(self.index_dir / "metadata.json", "w") as f:
            json.dump(self.examples, f)
        print(f"Index saved to {self.index_dir} ({len(self.examples)} vectors)")

    def _load_index(self, index_path: Path, meta_path: Path):
        self.index = faiss.read_index(str(index_path))
        with open(meta_path) as f:
            self.examples = json.load(f)

    def retrieve(self, query: str) -> list[dict]:
        if self.index is None or not self.examples:
            return []
        embedding = self._encode([query])
        scores, indices = self.index.search(embedding, self.top_k)
        return [self.examples[i] for i in indices[0] if i >= 0]

    def build_prompt(self, query: str, query_key: str = "nl_query") -> str:
        """Build few-shot prompt with retrieved examples."""
        examples = self.retrieve(query)
        few_shot = ""

        for idx, ex in enumerate(examples, 1):
            if self.task == "nl2py":
                few_shot += RAG_FEW_SHOT_NL2PY.format(
                    idx=idx,
                    nl_query=ex["nl_query"],
                    python_code=ex["python_code"],
                )
            else:
                few_shot += RAG_FEW_SHOT_JAVA2PY.format(
                    idx=idx,
                    java_code=ex["java_code"],
                    python_code=ex["python_code"],
                )

        if self.task == "nl2py":
            return format_nl2py_inference(query, few_shot=few_shot)
        return format_java2py_inference(query, few_shot=few_shot)


def main():
    parser = argparse.ArgumentParser(description="Build or query RAG index")
    parser.add_argument("--task", choices=["nl2py", "java2py"], required=True)
    parser.add_argument("--build-index", action="store_true")
    parser.add_argument("--query", type=str, default=None)
    args = parser.parse_args()

    rag = RAGPipeline(task=args.task)
    if args.build_index:
        rag.build_index()
    if args.query:
        prompt = rag.build_prompt(args.query)
        print(prompt)


if __name__ == "__main__":
    main()
