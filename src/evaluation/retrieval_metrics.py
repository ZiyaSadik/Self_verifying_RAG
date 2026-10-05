"""Supporting-fact retrieval metrics for HotpotQA.

Methodology
-----------
HotpotQA marks gold evidence as ``(title, sent_id)`` pairs in
``supporting_facts``. After dense retrieval we treat each returned passage as
the same kind of pair and score:

* **Recall@k** — of the gold supporting facts, what fraction appear in the
  top-k retrieved passages?
* **Precision@k** — of the top-k retrieved passages, what fraction are gold
  supporting facts?

Matching is exact on ``(title, sent_id)``. No fuzzy text matching is used.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence


GoldFact = tuple[str, int]
RetrievedPassage = Mapping[str, object]


def extract_gold_supporting_facts(sample: Mapping[str, object]) -> set[GoldFact]:
    """Convert a HotpotQA sample's supporting_facts into a set of (title, sent_id)."""
    supporting_facts = sample["supporting_facts"]
    titles = supporting_facts["title"]
    sent_ids = supporting_facts["sent_id"]
    return {(title, int(sent_id)) for title, sent_id in zip(titles, sent_ids)}


def _as_fact(passage: RetrievedPassage) -> GoldFact:
    return (str(passage["title"]), int(passage["sent_id"]))


def supporting_fact_recall_at_k(
    gold_facts: Iterable[GoldFact],
    retrieved: Sequence[RetrievedPassage],
    k: int,
) -> float:
    """Fraction of gold supporting facts found in the top-k retrieved passages.

    ``recall@k = |pred_k ∩ gold| / |gold|``

    Returns 0.0 when there are no gold facts.
    """
    gold_set = {(str(title), int(sent_id)) for title, sent_id in gold_facts}
    if not gold_set or k <= 0:
        return 0.0

    predicted = {_as_fact(passage) for passage in retrieved[:k]}
    return len(predicted & gold_set) / len(gold_set)


def supporting_fact_precision_at_k(
    gold_facts: Iterable[GoldFact],
    retrieved: Sequence[RetrievedPassage],
    k: int,
) -> float:
    """Fraction of the top-k retrieved passages that are gold supporting facts.

    ``precision@k = (# of top-k hits in gold) / k``

    Uses denominator ``k`` (standard P@k). Returns 0.0 when ``k <= 0``.
    Passages beyond the available retrieved list count as non-hits.
    """
    if k <= 0:
        return 0.0

    gold_set = {(str(title), int(sent_id)) for title, sent_id in gold_facts}
    top_k = list(retrieved[:k])
    hits = sum(1 for passage in top_k if _as_fact(passage) in gold_set)
    return hits / k
