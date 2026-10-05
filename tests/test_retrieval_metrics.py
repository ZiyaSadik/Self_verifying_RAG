"""Unit tests for supporting-fact retrieval metrics (no model / network)."""

from __future__ import annotations

import unittest

from src.evaluation.retrieval_metrics import (
    extract_gold_supporting_facts,
    supporting_fact_precision_at_k,
    supporting_fact_recall_at_k,
)


def _hit(title: str, sent_id: int) -> dict:
    return {"title": title, "sent_id": sent_id, "sentence": "unused"}


class TestSupportingFactMetrics(unittest.TestCase):
    def test_extract_gold_supporting_facts(self) -> None:
        sample = {
            "supporting_facts": {
                "title": ["Doc A", "Doc B", "Doc A"],
                "sent_id": [0, 1, 2],
            }
        }
        gold = extract_gold_supporting_facts(sample)
        self.assertEqual(gold, {("Doc A", 0), ("Doc B", 1), ("Doc A", 2)})

    def test_perfect_recall_and_precision_at_2(self) -> None:
        gold = {("A", 0), ("B", 1)}
        retrieved = [_hit("A", 0), _hit("B", 1), _hit("C", 0)]

        self.assertEqual(supporting_fact_recall_at_k(gold, retrieved, k=2), 1.0)
        self.assertEqual(supporting_fact_precision_at_k(gold, retrieved, k=2), 1.0)

    def test_partial_recall_at_1(self) -> None:
        gold = {("A", 0), ("B", 1)}
        retrieved = [_hit("A", 0), _hit("C", 9)]

        # One of two gold facts found in top-1
        self.assertAlmostEqual(supporting_fact_recall_at_k(gold, retrieved, k=1), 0.5)
        # Top-1 hit is relevant → P@1 = 1/1
        self.assertAlmostEqual(supporting_fact_precision_at_k(gold, retrieved, k=1), 1.0)

    def test_precision_uses_k_even_if_fewer_hits_returned(self) -> None:
        gold = {("A", 0)}
        retrieved = [_hit("A", 0)]  # only one passage available

        # One relevant hit in top-3 slots → 1/3
        self.assertAlmostEqual(supporting_fact_precision_at_k(gold, retrieved, k=3), 1 / 3)
        self.assertAlmostEqual(supporting_fact_recall_at_k(gold, retrieved, k=3), 1.0)

    def test_duplicate_retrieved_facts_count_once_for_recall(self) -> None:
        gold = {("A", 0), ("B", 1)}
        retrieved = [_hit("A", 0), _hit("A", 0), _hit("A", 0)]

        self.assertAlmostEqual(supporting_fact_recall_at_k(gold, retrieved, k=3), 0.5)
        # Precision counts each ranked slot: all three are gold → 3/3
        self.assertAlmostEqual(supporting_fact_precision_at_k(gold, retrieved, k=3), 1.0)

    def test_no_overlap_is_zero(self) -> None:
        gold = {("A", 0)}
        retrieved = [_hit("Z", 9), _hit("Y", 8)]

        self.assertEqual(supporting_fact_recall_at_k(gold, retrieved, k=2), 0.0)
        self.assertEqual(supporting_fact_precision_at_k(gold, retrieved, k=2), 0.0)

    def test_empty_gold_or_k(self) -> None:
        retrieved = [_hit("A", 0)]
        self.assertEqual(supporting_fact_recall_at_k(set(), retrieved, k=1), 0.0)
        self.assertEqual(supporting_fact_precision_at_k({("A", 0)}, retrieved, k=0), 0.0)
        self.assertEqual(supporting_fact_recall_at_k({("A", 0)}, retrieved, k=0), 0.0)


if __name__ == "__main__":
    unittest.main()
