"""Persistent ChromaDB storage for validated Duktek embeddings."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence


class PersistentVectorStore:
    """Store normalized embeddings and scalar chunk metadata in ChromaDB."""

    def __init__(
        self,
        path: Path,
        collection_name: str = "duktek-corpus",
    ) -> None:
        try:
            import chromadb
        except ImportError as error:
            raise RuntimeError(
                "chromadb is required for persistent vector storage"
            ) from error
        if chromadb is None:
            raise RuntimeError("chromadb is required for persistent vector storage")
        self._client = chromadb.PersistentClient(path=str(path))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            configuration={"hnsw": {"space": "cosine"}},
        )

    @property
    def count(self) -> int:
        return int(self._collection.count())

    def upsert(
        self,
        ids: Sequence[str],
        embeddings: Sequence[Sequence[float]],
        documents: Sequence[str],
        metadatas: Sequence[dict[str, Any]],
    ) -> None:
        if not ids:
            return
        lengths = {len(ids), len(embeddings), len(documents), len(metadatas)}
        if len(lengths) != 1:
            raise ValueError("ids, embeddings, documents, and metadatas must align")
        if len(set(ids)) != len(ids):
            raise ValueError("ids must be unique within an upsert")
        if any(not isinstance(item, str) or not item.strip() for item in ids):
            raise ValueError("ids must be non-empty strings")
        dimensions = {len(vector) for vector in embeddings}
        if len(dimensions) != 1 or 0 in dimensions:
            raise ValueError("embeddings must have one consistent positive dimension")
        if any(
            not isinstance(value, (str, int, float, bool))
            for metadata in metadatas
            for value in metadata.values()
        ):
            raise ValueError("Chroma metadata values must be scalar")
        self._collection.upsert(
            ids=list(ids),
            embeddings=[list(vector) for vector in embeddings],
            documents=list(documents),
            metadatas=[dict(metadata) for metadata in metadatas],
        )

    def query(
        self,
        embedding: Sequence[float],
        *,
        n_results: int = 5,
    ) -> dict[str, Any]:
        if n_results < 1:
            raise ValueError("n_results must be positive")
        return self._collection.query(
            query_embeddings=[list(embedding)],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
