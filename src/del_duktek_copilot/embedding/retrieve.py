"""Retrieve source chunks from a persistent Duktek vector store."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .evaluate import MODEL_NAMES, _prefix
from .vector_store import PersistentVectorStore


def retrieve(
    query: str,
    storage_path: Path,
    *,
    model_name: str = MODEL_NAMES[0],
    collection_name: str = "duktek-corpus",
    n_results: int = 5,
    device: str | None = None,
) -> dict[str, Any]:
    """Encode a query and return ranked documents with metadata and distances."""
    if not query.strip():
        raise ValueError("query must be non-empty")
    if model_name not in MODEL_NAMES:
        raise ValueError(f"unsupported model: {model_name}")
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise RuntimeError(
            "sentence-transformers is required for retrieval"
        ) from error
    model_kwargs = {} if device is None else {"device": device}
    model = SentenceTransformer(model_name, **model_kwargs)
    embedding = model.encode(
        [_prefix(model_name, query, "query")],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )[0]
    return PersistentVectorStore(storage_path, collection_name).query(
        embedding.tolist(),
        n_results=n_results,
    )
