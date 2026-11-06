import pytest

from del_duktek_copilot.knowledge_base.evaluation import (
    calibrate_ood_threshold,
    load_queries,
    ndcg_at_k,
    out_of_domain_rejection_precision,
    recall_at_k,
    reciprocal_rank_at_k,
)


def test_retrieval_metrics():
    ranked = ["other", "target", "last"]
    relevant = frozenset({"target"})
    assert recall_at_k(ranked, relevant, 2) == 1.0
    assert reciprocal_rank_at_k(ranked, relevant, 2) == pytest.approx(0.5)
    assert ndcg_at_k(ranked, relevant, 3) == pytest.approx(1 / 1.5849625007)


def test_ood_threshold_is_calibrated_from_scores():
    threshold = calibrate_ood_threshold([0.75, 0.8], [0.05, 0.2])
    assert threshold in {0.05, 0.2, 0.75, 0.8}
    assert out_of_domain_rejection_precision(
        [0.8, 0.2, 0.05], [False, True, True], threshold
    ) == 1.0


def test_loads_ground_truth_queries():
    queries = load_queries("data/evaluation/retrieval_queries.jsonl")
    assert len(queries) >= 5
    assert any(query.out_of_domain for query in queries)
