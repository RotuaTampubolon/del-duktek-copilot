import pytest

from del_duktek_copilot.knowledge_base.semantic_search import (
    SemanticRetriever,
    cosine_similarity_from_distance,
    format_results,
)


class FakeStore:
    def query(self, embedding, *, n_results=5):
        assert embedding == [0.1, 0.2]
        assert n_results == 2
        return {
            "ids": [["chunk-1", "chunk-2"]],
            "documents": [["teks satu", "teks dua"]],
            "metadatas": [[
                {"source_file": "sop.pdf", "page_number": 3},
                {"source_file": "sop.pdf", "page_number": 4},
            ]],
            "distances": [[0.2, 0.8]],
        }


def test_search_preserves_provenance_and_converts_distance():
    retriever = SemanticRetriever(FakeStore(), lambda query: [0.1, 0.2])

    results = retriever.search("gangguan jaringan", top_k=2)

    assert results[0].similarity == pytest.approx(0.8)
    assert results[0].distance == pytest.approx(0.2)
    assert results[0].source_file == "sop.pdf"
    assert results[0].page_number == 3
    assert format_results(results)[0]["cosine_similarity"] == pytest.approx(0.8)


@pytest.mark.parametrize("distance, expected", [(0.0, 1.0), (1.0, 0.0), (2.0, -1.0)])
def test_cosine_conversion(distance, expected):
    assert cosine_similarity_from_distance(distance) == expected


def test_search_validates_input():
    retriever = SemanticRetriever(FakeStore(), lambda query: [0.1, 0.2])
    with pytest.raises(ValueError):
        retriever.search(" ")
    with pytest.raises(ValueError):
        retriever.search("query", top_k=0)
