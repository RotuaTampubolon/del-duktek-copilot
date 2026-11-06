"""Run a reproducible document-level retrieval benchmark."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from .evaluation import (
    calibrate_ood_threshold,
    load_queries,
    ndcg_at_k,
    out_of_domain_rejection_precision,
    recall_at_k,
    reciprocal_rank_at_k,
)
from .semantic_search import cosine_similarity_from_distance


def run_benchmark(
    model_name: str,
    storage_path: Path,
    query_path: Path,
    output_path: Path,
    *,
    device: str | None = None,
) -> dict[str, Any]:
    """Evaluate an existing ChromaDB index and write measured JSON output."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise RuntimeError("sentence-transformers is required") from error

    queries = load_queries(query_path)
    model = SentenceTransformer(model_name, **({} if device is None else {"device": device}))
    from ..embedding.vector_store import PersistentVectorStore

    store = PersistentVectorStore(storage_path)
    started = time.perf_counter()
    embeddings = model.encode(
        [
            f"query: {query.query}" if "e5" in model_name.lower() else query.query
            for query in queries
        ],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    query_encoding_seconds = time.perf_counter() - started

    per_query: list[dict[str, Any]] = []
    for query, embedding in zip(queries, embeddings):
        response = store.query(embedding.tolist(), n_results=10)
        ids = response["ids"][0]
        metadatas = response["metadatas"][0]
        distances = response["distances"][0]
        ranked_documents = _unique_document_ids(metadatas)
        per_query.append(
            {
                "query_id": query.query_id,
                "query": query.query,
                "out_of_domain": query.out_of_domain,
                "top_similarity": cosine_similarity_from_distance(distances[0]),
                "top_document_ids": ranked_documents,
                "recall_at_5": recall_at_k(
                    ranked_documents, query.expected_document_ids, 5
                ),
                "recall_at_10": recall_at_k(
                    ranked_documents, query.expected_document_ids, 10
                ),
                "mrr_at_10": reciprocal_rank_at_k(
                    ranked_documents, query.expected_document_ids, 10
                ),
                "ndcg_at_10": ndcg_at_k(
                    ranked_documents, query.expected_document_ids, 10
                ),
                "top_results": [
                    {
                        "chunk_id": chunk_id,
                        "document_id": metadata["document_id"],
                        "source_file": metadata["source_file"],
                        "page_number": metadata["page_number"],
                        "cosine_distance": float(distance),
                        "cosine_similarity": cosine_similarity_from_distance(distance),
                    }
                    for chunk_id, metadata, distance in zip(
                        ids[:3], metadatas[:3], distances[:3]
                    )
                ],
            }
        )

    in_domain = [item for item in per_query if not item["out_of_domain"]]
    in_scores = [item["top_similarity"] for item in in_domain]
    ood_scores = [item["top_similarity"] for item in per_query if item["out_of_domain"]]
    threshold = calibrate_ood_threshold(in_scores, ood_scores)
    result = {
        "model_name": model_name,
        "device": str(getattr(model, "device", device or "auto")),
        "chunk_count": store.count,
        "query_count": len(queries),
        "query_encoding_seconds": query_encoding_seconds,
        "metrics_in_domain": {
            metric: sum(item[metric] for item in in_domain) / len(in_domain)
            for metric in ("recall_at_5", "recall_at_10", "mrr_at_10", "ndcg_at_10")
        },
        "ood_threshold": threshold,
        "ood_rejection_precision": out_of_domain_rejection_precision(
            [item["top_similarity"] for item in per_query],
            [item["out_of_domain"] for item in per_query],
            threshold,
        ),
        "per_query": per_query,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def _unique_document_ids(metadatas: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for metadata in metadatas:
        document_id = metadata["document_id"]
        if document_id not in seen:
            seen.add(document_id)
            result.append(document_id)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--storage", type=Path, required=True)
    parser.add_argument("--queries", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()
    run_benchmark(
        args.model,
        args.storage,
        args.queries,
        args.output,
        device=args.device,
    )


if __name__ == "__main__":
    main()
