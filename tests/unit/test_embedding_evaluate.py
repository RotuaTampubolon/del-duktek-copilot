import json

import pytest

from del_duktek_copilot.embedding.evaluate import (
    load_chunks,
    load_relevance,
    ndcg_at_k,
    reciprocal_rank_at_k,
    recall_at_k,
)


def test_load_chunks_validates_ids_and_metadata(tmp_path):
    path = tmp_path / "chunks.jsonl"
    record = {
        "text": "Prosedur jaringan.",
        "metadata": {
            "document_id": "doc",
            "source": "source",
            "category": "network",
            "source_status": "Layak",
            "authority_status": "external",
            "source_file": "source.pdf",
            "document_title": "Title",
            "page_number": 1,
            "chunk_index": 1,
            "chunk_id": "doc-p001-c0001",
        },
    }
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    chunks = load_chunks(path)

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "doc-p001-c0001"


def test_load_relevance_rejects_unknown_chunk_id(tmp_path):
    path = tmp_path / "relevance.jsonl"
    path.write_text(
        json.dumps(
            {
                "query_id": "q1",
                "query": "gangguan jaringan",
                "relevant_chunk_ids": ["unknown"],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown relevant chunk IDs"):
        load_relevance(path, {"known"})


def test_binary_retrieval_metrics():
    ranked = ["a", "b", "c", "d"]
    relevant = frozenset({"c"})

    assert recall_at_k(ranked, relevant, 2) == 0.0
    assert recall_at_k(ranked, relevant, 5) == 1.0
    assert reciprocal_rank_at_k(ranked, relevant, 10) == pytest.approx(1 / 3)
    assert ndcg_at_k(ranked, relevant, 10) == pytest.approx(0.5)
