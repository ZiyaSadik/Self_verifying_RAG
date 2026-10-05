"""Unit tests for ClaimEvidenceVerifier (no model / network / LLM)."""

from __future__ import annotations

import unittest

from src.verification.claim_verifier import ClaimEvidenceVerifier, normalize_tokens


def _evidence(
    sentence: str,
    *,
    sample_id: str = "s1",
    title: str = "Doc",
    sent_id: int = 0,
    score: float = 0.5,
) -> dict:
    return {
        "sample_id": sample_id,
        "title": title,
        "sent_id": sent_id,
        "sentence": sentence,
        "score": score,
    }


def _claim(text: str, claim_id: str = "claim_1") -> dict:
    return {"claim_id": claim_id, "claim": text, "source_text": text}


class TestClaimEvidenceVerifier(unittest.TestCase):
    def test_exact_match_score_is_one(self) -> None:
        verifier = ClaimEvidenceVerifier(threshold=0.7)
        score = verifier.coverage_score(
            "Arthur's Magazine began in 1844.",
            "Arthur's Magazine began in 1844.",
        )
        self.assertEqual(score, 1.0)

    def test_partial_overlap_score(self) -> None:
        verifier = ClaimEvidenceVerifier(threshold=0.7)
        # After stopword removal, claim tokens are a predictable set.
        claim = "cats dogs birds"
        evidence = "cats dogs"
        claim_tokens = normalize_tokens(claim)
        evidence_tokens = normalize_tokens(evidence)
        expected = len(claim_tokens & evidence_tokens) / len(claim_tokens)
        self.assertAlmostEqual(verifier.coverage_score(claim, evidence), expected)
        self.assertAlmostEqual(expected, 2 / 3)

    def test_no_overlap_score_is_zero(self) -> None:
        verifier = ClaimEvidenceVerifier(threshold=0.7)
        score = verifier.coverage_score("alpha beta", "gamma delta")
        self.assertEqual(score, 0.0)

    def test_supported_decision_above_threshold(self) -> None:
        verifier = ClaimEvidenceVerifier(threshold=0.5)
        result = verifier.verify_claim(
            _claim("red blue green"),
            [_evidence("red blue green yellow")],
        )
        self.assertEqual(result["decision"], "supported")
        self.assertGreaterEqual(result["support_score"], 0.5)
        self.assertEqual(result["method"], "token_coverage")

    def test_unsupported_decision_below_threshold(self) -> None:
        verifier = ClaimEvidenceVerifier(threshold=0.9)
        result = verifier.verify_claim(
            _claim("red blue green"),
            [_evidence("red only")],
        )
        self.assertEqual(result["decision"], "unsupported")
        self.assertLess(result["support_score"], 0.9)

    def test_deterministic_tie_breaking(self) -> None:
        verifier = ClaimEvidenceVerifier(threshold=0.0)
        claim = _claim("alpha beta")
        # Three passages with identical overlap; tie-break by retrieval score,
        # then sent_id, then title.
        evidence = [
            _evidence("alpha beta", title="Zeta", sent_id=5, score=0.80),
            _evidence("alpha beta", title="Alpha", sent_id=2, score=0.90),
            _evidence("alpha beta", title="Beta", sent_id=1, score=0.90),
        ]
        result = verifier.verify_claim(claim, evidence)
        matched = result["matched_evidence"][0]
        # Highest score (0.90), then lowest sent_id among those → sent_id=1, title=Beta
        self.assertEqual(matched["score"], 0.90)
        self.assertEqual(matched["sent_id"], 1)
        self.assertEqual(matched["title"], "Beta")

        # Equal score and sent_id → lexicographically smallest title
        evidence2 = [
            _evidence("alpha beta", title="Mirror", sent_id=0, score=0.5),
            _evidence("alpha beta", title="Apple", sent_id=0, score=0.5),
        ]
        matched2 = verifier.verify_claim(claim, evidence2)["matched_evidence"][0]
        self.assertEqual(matched2["title"], "Apple")

    def test_empty_claim_handling(self) -> None:
        verifier = ClaimEvidenceVerifier(threshold=0.7)
        self.assertEqual(verifier.coverage_score("", "some evidence"), 0.0)
        self.assertEqual(verifier.coverage_score("the and of", "the and of"), 0.0)

        result = verifier.verify_claim(_claim(""), [_evidence("anything here")])
        self.assertEqual(result["support_score"], 0.0)
        self.assertEqual(result["decision"], "unsupported")

    def test_invalid_threshold_raises(self) -> None:
        with self.assertRaises(ValueError):
            ClaimEvidenceVerifier(threshold=-0.1)
        with self.assertRaises(ValueError):
            ClaimEvidenceVerifier(threshold=1.1)

    def test_answer_level_aggregation(self) -> None:
        verifier = ClaimEvidenceVerifier(threshold=0.5)
        results = verifier.verify(
            [_claim("alpha beta", "claim_1"), _claim("zzzz yyyy", "claim_2")],
            [_evidence("alpha beta gamma")],
        )
        summary = ClaimEvidenceVerifier.aggregate(results)
        self.assertEqual(summary["n_claims"], 2)
        self.assertEqual(summary["n_supported"], 1)
        self.assertEqual(summary["n_unsupported"], 1)
        self.assertAlmostEqual(float(summary["support_rate"]), 0.5)

        empty = ClaimEvidenceVerifier.aggregate([])
        self.assertEqual(empty["n_claims"], 0)
        self.assertEqual(empty["support_rate"], 0.0)

    def test_multiple_claims(self) -> None:
        verifier = ClaimEvidenceVerifier(threshold=0.7)
        claims = [
            _claim("paris france", "claim_1"),
            _claim("berlin germany", "claim_2"),
            _claim("unrelated tokens xx yy", "claim_3"),
        ]
        evidence = [
            _evidence("paris france capital", title="Paris", sent_id=0, score=0.9),
            _evidence("berlin germany capital", title="Berlin", sent_id=0, score=0.8),
        ]
        results = verifier.verify(claims, evidence)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["claim_id"], "claim_1")
        self.assertEqual(results[0]["decision"], "supported")
        self.assertEqual(results[1]["decision"], "supported")
        self.assertEqual(results[2]["decision"], "unsupported")
        self.assertEqual(results[0]["matched_evidence"][0]["title"], "Paris")
        self.assertEqual(results[1]["matched_evidence"][0]["title"], "Berlin")


if __name__ == "__main__":
    unittest.main()
