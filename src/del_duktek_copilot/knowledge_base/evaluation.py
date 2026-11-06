"""Ground-truth metrics for semantic retrieval and OOD rejection."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
import json
from math import log2
from pathlib import Path


@dataclass(frozen=True)
class EvaluationQuery:
    """Human-reviewed relevance labels defined before a benchmark run."""

    query_id: str
    query: str
    expected_document_ids: frozenset[str]
    out_of_domain: bool = False


def load_queries(path: Path) -> list[EvaluationQuery]:
    """Load and validate pre-registered ground-truth query labels."""
    path = Path(path)
    queries: list[EvaluationQuery] = []
    seen_ids: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from error
            query_id = record.get("query_id")
            query = record.get("query")
            expected = record.get("expected_document_ids")
            out_of_domain = record.get("out_of_domain", False)
            if (
                not isinstance(query_id, str)
                or not query_id.strip()
                or query_id in seen_ids
            ):
                raise ValueError(f"{path}:{line_number}: query_id must be unique")
            if not isinstance(query, str) or not query.strip():
                raise ValueError(f"{path}:{line_number}: query must be non-empty")
            if not isinstance(expected, list) or not all(
                isinstance(item, str) and item.strip() for item in expected
            ):
                raise ValueError(
                    f"{path}:{line_number}: expected_document_ids must be strings"
                )
            if not isinstance(out_of_domain, bool):
                raise ValueError(f"{path}:{line_number}: out_of_domain must be boolean")
            if out_of_domain != (len(expected) == 0):
                raise ValueError(
                    f"{path}:{line_number}: OOD labels must have no expected documents"
                )
            seen_ids.add(query_id)
            queries.append(
                EvaluationQuery(
                    query_id=query_id,
                    query=query,
                    expected_document_ids=frozenset(expected),
                    out_of_domain=out_of_domain,
                )
            )
    if not queries:
        raise ValueError(f"{path}: no query records found")
    return queries


def recall_at_k(
    ranked_document_ids: Sequence[str],
    relevant_document_ids: frozenset[str],
    k: int,
) -> float:
    _validate_k(k)
    return float(bool(set(ranked_document_ids[:k]) & relevant_document_ids))


def reciprocal_rank_at_k(
    ranked_document_ids: Sequence[str],
    relevant_document_ids: frozenset[str],
    k: int,
) -> float:
    _validate_k(k)
    for rank, document_id in enumerate(ranked_document_ids[:k], 1):
        if document_id in relevant_document_ids:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(
    ranked_document_ids: Sequence[str],
    relevant_document_ids: frozenset[str],
    k: int,
) -> float:
    _validate_k(k)
    if not relevant_document_ids:
        return 0.0
    dcg = sum(
        1.0 / log2(rank + 2)
        for rank, item in enumerate(ranked_document_ids[:k])
        if item in relevant_document_ids
    )
    ideal_count = min(k, len(relevant_document_ids))
    idcg = sum(1.0 / log2(rank + 2) for rank in range(ideal_count))
    return dcg / idcg


def calibrate_ood_threshold(
    in_domain_similarities: Iterable[float],
    out_of_domain_similarities: Iterable[float],
) -> float:
    """Select the threshold with the best measured binary F1 score."""
    in_domain = list(in_domain_similarities)
    out_of_domain = list(out_of_domain_similarities)
    if not in_domain or not out_of_domain:
        raise ValueError("both similarity sets must be non-empty")
    candidates = sorted(set(in_domain + out_of_domain))
    best = (-1.0, candidates[0])
    for threshold in candidates:
        true_positive = sum(score >= threshold for score in in_domain)
        false_positive = sum(score >= threshold for score in out_of_domain)
        false_negative = len(in_domain) - true_positive
        denominator = 2 * true_positive + false_positive + false_negative
        f1 = 0.0 if denominator == 0 else 2 * true_positive / denominator
        if (f1, -threshold) > (best[0], -best[1]):
            best = (f1, threshold)
    return best[1]


def out_of_domain_rejection_precision(
    similarities: Sequence[float],
    out_of_domain: Sequence[bool],
    threshold: float,
) -> float:
    """Measure OOD queries among all queries rejected by the threshold."""
    if len(similarities) != len(out_of_domain):
        raise ValueError("similarities and out_of_domain must align")
    rejected = [is_ood for score, is_ood in zip(similarities, out_of_domain) if score < threshold]
    if not rejected:
        return 0.0
    return sum(rejected) / len(rejected)


def _validate_k(k: int) -> None:
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("k must be a positive integer")
