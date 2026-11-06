"""Semantic retrieval over the project's persistent ChromaDB collection."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol


class VectorStore(Protocol):
    def query(
        self, embedding: Sequence[float], *, n_results: int = 5
    ) -> dict[str, Any]:
        """Return the ChromaDB query response."""


@dataclass(frozen=True)
class RetrievalResult:
    """A ranked chunk with its complete provenance and measured scores."""

    rank: int
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    distance: float
    similarity: float

    @property
    def source_file(self) -> str | None:
        value = self.metadata.get("source_file")
        return value if isinstance(value, str) else None

    @property
    def page_number(self) -> int | None:
        value = self.metadata.get("page_number")
        return value if isinstance(value, int) else None


def cosine_similarity_from_distance(distance: float) -> float:
    """Convert ChromaDB cosine distance to cosine similarity.

    ChromaDB's ``cosine`` space reports ``1 - cosine_similarity``.  The
    conversion is intentionally kept in one place to prevent score
    interpretation from differing between retrieval and evaluation.
    """
    if not isinstance(distance, (int, float)):
        raise TypeError("distance must be numeric")
    if distance < 0 or distance > 2:
        raise ValueError("cosine distance must be in the inclusive range [0, 2]")
    return 1.0 - float(distance)


class SemanticRetriever:
    """Encode a query and retrieve provenance-preserving ChromaDB results."""

    def __init__(
        self,
        store: VectorStore,
        encode_query: Callable[[str], Sequence[float]],
    ) -> None:
        self._store = store
        self._encode_query = encode_query

    def search(self, query: str, *, top_k: int = 5) -> list[RetrievalResult]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
            raise ValueError("top_k must be a positive integer")

        embedding = self._encode_query(query)
        response = self._store.query(embedding, n_results=top_k)
        return _parse_chroma_response(response)


def from_embedding_pipeline(
    storage_path: str,
    *,
    model_name: str = "intfloat/multilingual-e5-base",
    collection_name: str = "duktek-corpus",
    device: str | None = None,
) -> SemanticRetriever:
    """Build a retriever from the existing embedding and ChromaDB components.

    Imports are intentionally lazy: callers that use a fake store for unit
    tests do not need to install the heavyweight embedding dependencies.
    """
    try:
        from sentence_transformers import SentenceTransformer
        from ..embedding.vector_store import PersistentVectorStore
    except ImportError as error:
        raise RuntimeError(
            "embedding pipeline dependencies are required for ChromaDB retrieval"
        ) from error

    model_kwargs = {} if device is None else {"device": device}
    model = SentenceTransformer(model_name, **model_kwargs)
    store = PersistentVectorStore(storage_path, collection_name)

    def encode_query(query: str) -> Sequence[float]:
        text = f"query: {query}" if model_name.startswith("intfloat/multilingual-e5") else query
        embedding = model.encode(
            [text],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0]
        return embedding.tolist()

    return SemanticRetriever(store, encode_query)


def _parse_chroma_response(response: Mapping[str, Any]) -> list[RetrievalResult]:
    """Normalize ChromaDB's one-query nested response into typed results."""
    try:
        ids = response["ids"][0]
        documents = response["documents"][0]
        metadatas = response["metadatas"][0]
        distances = response["distances"][0]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("ChromaDB response is missing ranked query fields") from error

    lengths = {len(ids), len(documents), len(metadatas), len(distances)}
    if len(lengths) != 1:
        raise ValueError("ChromaDB response fields must have equal lengths")

    results: list[RetrievalResult] = []
    for rank, (chunk_id, text, metadata, distance) in enumerate(
        zip(ids, documents, metadatas, distances), 1
    ):
        if not isinstance(chunk_id, str) or not isinstance(text, str):
            raise ValueError("ChromaDB result ids and documents must be strings")
        if not isinstance(metadata, dict):
            raise ValueError("ChromaDB result metadata must be an object")
        similarity = cosine_similarity_from_distance(distance)
        results.append(
            RetrievalResult(
                rank=rank,
                chunk_id=chunk_id,
                text=text,
                metadata=dict(metadata),
                distance=float(distance),
                similarity=similarity,
            )
        )
    return results


def format_results(results: Sequence[RetrievalResult]) -> list[dict[str, Any]]:
    """Create a JSON-serializable presentation shape for CLI/API callers."""
    return [
        {
            "rank": result.rank,
            "chunk_id": result.chunk_id,
            "text": result.text,
            "source_file": result.source_file,
            "page_number": result.page_number,
            "metadata": result.metadata,
            "cosine_distance": result.distance,
            "cosine_similarity": result.similarity,
        }
        for result in results
    ]
