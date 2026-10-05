"""Deterministic claim–evidence verifier using maximum token coverage.

Review 02 baseline
------------------
For a claim ``c`` and an evidence sentence ``e``:

    score(c, e) = |T(c) ∩ T(e)| / |T(c)|

where ``T()`` returns the normalised token **set**.

This score measures **lexical coverage / evidence consistency** only. It does
**not** measure semantic entailment and does **not** measure objective
factual truth. A claim may be lexically supported by incorrect evidence, or
factually true yet lexically unsupported (e.g. paraphrase).
"""

from __future__ import annotations

import re
import string
from typing import Any, Mapping, Sequence


# Small fixed English stopword set (frozen for reproducibility).
_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "being",
        "by",
        "for",
        "from",
        "has",
        "have",
        "had",
        "he",
        "her",
        "him",
        "his",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "she",
        "that",
        "the",
        "their",
        "them",
        "then",
        "there",
        "these",
        "they",
        "this",
        "to",
        "was",
        "were",
        "will",
        "with",
    }
)

_PUNCT_TABLE = str.maketrans({ch: " " for ch in string.punctuation})
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_tokens(text: str) -> set[str]:
    """Lowercase, strip punctuation, tokenise, drop stopwords. No stemming."""
    if text is None:
        return set()
    lowered = str(text).lower().translate(_PUNCT_TABLE)
    tokens = _WHITESPACE_RE.split(lowered.strip())
    return {tok for tok in tokens if tok and tok not in _STOPWORDS}


class ClaimEvidenceVerifier:
    """Max claim–evidence token-coverage verifier.

    Default ``threshold=0.7`` is a **development placeholder only**. Prefer a
    value selected by ``src/evaluation/calibrate_verifier.py``.
    """

    def __init__(self, threshold: float = 0.7) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                f"threshold must be in [0, 1], got {threshold!r}"
            )
        self.threshold = float(threshold)

    def coverage_score(self, claim: str, evidence_text: str) -> float:
        """Return lexical coverage of ``claim`` by ``evidence_text`` in [0, 1]."""
        claim_tokens = normalize_tokens(claim)
        if not claim_tokens:
            return 0.0
        evidence_tokens = normalize_tokens(evidence_text)
        return len(claim_tokens & evidence_tokens) / len(claim_tokens)

    def verify_claim(
        self,
        claim: Mapping[str, Any],
        evidence: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Verify one claim against all evidence passages."""
        claim_id = str(claim.get("claim_id", ""))
        claim_text = str(claim.get("claim", ""))

        best: dict[str, Any] | None = None
        best_overlap = -1.0

        for passage in evidence:
            overlap = self.coverage_score(claim_text, str(passage.get("sentence", "")))
            candidate = {
                "sample_id": str(passage.get("sample_id", "")),
                "title": str(passage.get("title", "")),
                "sent_id": int(passage.get("sent_id", 0)),
                "sentence": str(passage.get("sentence", "")),
                "score": float(passage.get("score", 0.0)),
                "overlap_score": float(overlap),
            }

            if best is None or self._is_better_match(candidate, best):
                best = candidate
                best_overlap = overlap

        if best is None:
            support_score = 0.0
            matched: list[dict[str, Any]] = []
        else:
            support_score = float(best_overlap)
            matched = [best]

        decision = "supported" if support_score >= self.threshold else "unsupported"

        return {
            "claim_id": claim_id,
            "claim": claim_text,
            "support_score": support_score,
            "decision": decision,
            "matched_evidence": matched,
            "method": "token_coverage",
        }

    def verify(
        self,
        claims: Sequence[Mapping[str, Any]],
        evidence: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        """Verify every claim; returns one result dict per claim."""
        return [self.verify_claim(claim, evidence) for claim in claims]

    @staticmethod
    def aggregate(results: Sequence[Mapping[str, Any]]) -> dict[str, float | int]:
        """Aggregate per-claim decisions into answer-level support statistics."""
        n_claims = len(results)
        if n_claims == 0:
            return {
                "n_claims": 0,
                "n_supported": 0,
                "n_unsupported": 0,
                "support_rate": 0.0,
            }

        n_supported = sum(1 for r in results if r.get("decision") == "supported")
        n_unsupported = n_claims - n_supported
        return {
            "n_claims": n_claims,
            "n_supported": n_supported,
            "n_unsupported": n_unsupported,
            "support_rate": n_supported / n_claims,
        }

    @staticmethod
    def _is_better_match(candidate: Mapping[str, Any], current: Mapping[str, Any]) -> bool:
        """Deterministic tie-break for selecting the best evidence passage."""
        if candidate["overlap_score"] != current["overlap_score"]:
            return candidate["overlap_score"] > current["overlap_score"]
        if candidate["score"] != current["score"]:
            return candidate["score"] > current["score"]
        if candidate["sent_id"] != current["sent_id"]:
            return candidate["sent_id"] < current["sent_id"]
        return candidate["title"] < current["title"]
