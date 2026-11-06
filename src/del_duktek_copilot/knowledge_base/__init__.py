"""Enterprise knowledge-base retrieval components."""

from .semantic_search import (
    RetrievalResult,
    SemanticRetriever,
    cosine_similarity_from_distance,
    from_embedding_pipeline,
)

__all__ = [
    "RetrievalResult",
    "SemanticRetriever",
    "cosine_similarity_from_distance",
    "from_embedding_pipeline",
]
