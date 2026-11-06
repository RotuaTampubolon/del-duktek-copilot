"""Encode the processed corpus and persist it in ChromaDB."""

from __future__ import annotations

import argparse
from pathlib import Path

from .evaluate import MODEL_NAMES, _prefix, load_chunks
from .vector_store import PersistentVectorStore


def index_corpus(
    chunks_path: Path,
    storage_path: Path,
    *,
    model_name: str = MODEL_NAMES[0],
    collection_name: str = "duktek-corpus",
    batch_size: int = 16,
    device: str | None = None,
) -> int:
    """Encode all chunks and idempotently upsert them into persistent storage."""
    if model_name not in MODEL_NAMES:
        raise ValueError(f"unsupported model: {model_name}")
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise RuntimeError(
            "sentence-transformers is required to index the corpus"
        ) from error
    chunks = load_chunks(chunks_path)
    model_kwargs = {} if device is None else {"device": device}
    model = SentenceTransformer(model_name, **model_kwargs)
    embeddings = model.encode(
        [_prefix(model_name, chunk.text, "passage") for chunk in chunks],
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    store = PersistentVectorStore(storage_path, collection_name)
    store.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        embeddings=embeddings.tolist(),
        documents=[chunk.text for chunk in chunks],
        metadatas=[chunk.metadata for chunk in chunks],
    )
    return store.count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, required=True)
    parser.add_argument("--storage", type=Path, required=True)
    parser.add_argument("--model", default=MODEL_NAMES[0], choices=MODEL_NAMES)
    parser.add_argument("--collection", default="duktek-corpus")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()
    count = index_corpus(
        args.chunks,
        args.storage,
        model_name=args.model,
        collection_name=args.collection,
        batch_size=args.batch_size,
        device=args.device,
    )
    print(f"Indexed {count} unique chunks in {args.storage}")


if __name__ == "__main__":
    main()
