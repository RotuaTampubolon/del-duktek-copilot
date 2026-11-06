"""Run reproducible Sentence-Transformers retrieval evaluations.

The runner requires a human-reviewed relevance JSONL. It intentionally refuses
to score a corpus without that file so that retrieval results cannot be
mistaken for a labelled benchmark.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

MODEL_NAMES = (
    "intfloat/multilingual-e5-base",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)


@dataclass(frozen=True)
class ChunkRecord:
    text: str
    metadata: dict[str, Any]

    @property
    def chunk_id(self) -> str:
        return self.metadata["chunk_id"]


@dataclass(frozen=True)
class BenchmarkQuery:
    query_id: str
    query: str
    relevant_chunk_ids: frozenset[str]


def _read_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"{path}:{line_number}: expected a JSON object")
                yield line_number, value


def load_chunks(path: Path) -> list[ChunkRecord]:
    """Load and validate chunk records without modifying their content."""
    records: list[ChunkRecord] = []
    seen_ids: set[str] = set()
    required_metadata = (
        "document_id",
        "source",
        "category",
        "source_status",
        "authority_status",
        "source_file",
        "document_title",
        "page_number",
        "chunk_index",
        "chunk_id",
    )
    for line_number, value in _read_jsonl(path):
        text = value.get("text")
        metadata = value.get("metadata")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"{path}:{line_number}: text must be a non-empty string")
        if not isinstance(metadata, dict):
            raise ValueError(f"{path}:{line_number}: metadata must be an object")
        missing = [key for key in required_metadata if key not in metadata]
        if missing:
            raise ValueError(f"{path}:{line_number}: missing metadata: {missing}")
        chunk_id = metadata["chunk_id"]
        if not isinstance(chunk_id, str) or not chunk_id.strip():
            raise ValueError(f"{path}:{line_number}: chunk_id must be a non-empty string")
        if chunk_id in seen_ids:
            raise ValueError(f"{path}:{line_number}: duplicate chunk_id: {chunk_id}")
        seen_ids.add(chunk_id)
        records.append(ChunkRecord(text=text, metadata=dict(metadata)))
    if not records:
        raise ValueError(f"{path}: no JSONL records found")
    return records


def load_relevance(path: Path, chunk_ids: set[str]) -> list[BenchmarkQuery]:
    """Load human-reviewed query relevance labels and validate references."""
    queries: list[BenchmarkQuery] = []
    seen_ids: set[str] = set()
    for line_number, value in _read_jsonl(path):
        query_id = value.get("query_id")
        query = value.get("query")
        relevant = value.get("relevant_chunk_ids")
        if not isinstance(query_id, str) or not query_id.strip():
            raise ValueError(f"{path}:{line_number}: query_id must be non-empty")
        if query_id in seen_ids:
            raise ValueError(f"{path}:{line_number}: duplicate query_id: {query_id}")
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"{path}:{line_number}: query must be non-empty")
        if not isinstance(relevant, list) or not relevant:
            raise ValueError(
                f"{path}:{line_number}: relevant_chunk_ids must be a non-empty list"
            )
        unknown = set(relevant) - chunk_ids
        if unknown:
            raise ValueError(
                f"{path}:{line_number}: unknown relevant chunk IDs: {sorted(unknown)}"
            )
        if not all(isinstance(item, str) and item for item in relevant):
            raise ValueError(f"{path}:{line_number}: relevance IDs must be strings")
        seen_ids.add(query_id)
        queries.append(
            BenchmarkQuery(query_id, query, frozenset(relevant))
        )
    if not queries:
        raise ValueError(f"{path}: no relevance records found")
    return queries


def recall_at_k(ranked_ids: list[str], relevant: frozenset[str], k: int) -> float:
    return float(bool(set(ranked_ids[:k]) & relevant))


def reciprocal_rank_at_k(
    ranked_ids: list[str], relevant: frozenset[str], k: int
) -> float:
    for rank, chunk_id in enumerate(ranked_ids[:k], 1):
        if chunk_id in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ranked_ids: list[str], relevant: frozenset[str], k: int) -> float:
    gains = [1.0 if chunk_id in relevant else 0.0 for chunk_id in ranked_ids[:k]]
    dcg = sum(gain / np.log2(rank + 2) for rank, gain in enumerate(gains))
    ideal = min(len(relevant), k)
    if ideal == 0:
        return 0.0
    idcg = sum(1.0 / np.log2(rank + 2) for rank in range(ideal))
    return float(dcg / idcg)


def _prefix(model_name: str, text: str, kind: str) -> str:
    if model_name == MODEL_NAMES[0]:
        return f"{kind}: {text}"
    return text


def _resource_snapshot() -> dict[str, Any]:
    snapshot: dict[str, Any] = {"pid": os.getpid()}
    try:
        import psutil

        snapshot["rss_bytes"] = psutil.Process().memory_info().rss
    except ImportError:
        snapshot["rss_bytes"] = None
    return snapshot


def evaluate_model(
    model_name: str,
    chunks: list[ChunkRecord],
    queries: list[BenchmarkQuery],
    *,
    batch_size: int,
    device: str | None,
) -> dict[str, Any]:
    """Evaluate one model and return measured metrics and resource facts."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise RuntimeError(
            "sentence-transformers is required to run the embedding experiment"
        ) from error

    model_kwargs = {} if device is None else {"device": device}
    model = SentenceTransformer(model_name, **model_kwargs)
    passage_texts = [_prefix(model_name, chunk.text, "passage") for chunk in chunks]
    query_texts = [_prefix(model_name, item.query, "query") for item in queries]
    started = time.perf_counter()
    passage_embeddings = model.encode(
        passage_texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    passage_seconds = time.perf_counter() - started
    started = time.perf_counter()
    query_embeddings = model.encode(
        query_texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    query_seconds = time.perf_counter() - started

    chunk_ids = [chunk.chunk_id for chunk in chunks]
    per_query: list[dict[str, Any]] = []
    for query, embedding in zip(queries, query_embeddings):
        scores = passage_embeddings @ embedding
        ranking = np.argsort(-scores, kind="stable")
        ranked_ids = [chunk_ids[index] for index in ranking]
        per_query.append(
            {
                "query_id": query.query_id,
                "recall_at_5": recall_at_k(ranked_ids, query.relevant_chunk_ids, 5),
                "recall_at_10": recall_at_k(ranked_ids, query.relevant_chunk_ids, 10),
                "mrr_at_10": reciprocal_rank_at_k(
                    ranked_ids, query.relevant_chunk_ids, 10
                ),
                "ndcg_at_10": ndcg_at_k(ranked_ids, query.relevant_chunk_ids, 10),
                "top_10_chunk_ids": ranked_ids[:10],
            }
        )

    def mean(metric: str) -> float:
        return float(np.mean([item[metric] for item in per_query]))

    return {
        "model_name": model_name,
        "embedding_dimension": int(model.get_sentence_embedding_dimension()),
        "device": str(getattr(model, "device", device or "auto")),
        "batch_size": batch_size,
        "passage_encoding_seconds": passage_seconds,
        "query_encoding_seconds": query_seconds,
        "resource_after_encoding": _resource_snapshot(),
        "metrics": {
            "recall_at_5": mean("recall_at_5"),
            "recall_at_10": mean("recall_at_10"),
            "mrr_at_10": mean("mrr_at_10"),
            "ndcg_at_10": mean("ndcg_at_10"),
        },
        "per_query": per_query,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, required=True)
    parser.add_argument("--relevance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()
    chunks = load_chunks(args.chunks)
    queries = load_relevance(args.relevance, {chunk.chunk_id for chunk in chunks})
    results = {
        "corpus_path": str(args.chunks),
        "relevance_path": str(args.relevance),
        "chunk_count": len(chunks),
        "query_count": len(queries),
        "models": [
            evaluate_model(
                model_name,
                chunks,
                queries,
                batch_size=args.batch_size,
                device=args.device,
            )
            for model_name in MODEL_NAMES
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
