"""Deterministic sentence-level claim extraction (Review 02 baseline).

The current extractive generator forms answers by concatenating retrieved
sentences. This module therefore treats each sentence in the draft answer as
one candidate claim.

This is intentionally **not** LLM-based semantic claim decomposition. It only
segments text into candidate claims so the pipeline
(Query → Retrieval → Generation → Claim Extraction) can be validated before a
stronger claim-decomposition component is added later.
"""

from __future__ import annotations

import re


class ClaimExtractor:
    """Split a generated answer into sentence-level candidate claims.

    The extractor is deterministic: the same ``answer`` string always yields
    the same ordered list of claim dictionaries. No model, network, or API
    calls are used.
    """

    # Split on sentence-ending punctuation followed by whitespace.
    # Keeps the implementation transparent for dissertation explanation.
    _SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")

    def extract(self, answer: str) -> list[dict]:
        """Extract sentence-level claims from a generated answer.

        Args:
            answer: Draft answer text (typically from ``ExtractiveGenerator``).

        Returns:
            A list of dictionaries, each with:
              - ``claim_id``: deterministic id (``claim_1``, ``claim_2``, ...)
              - ``claim``: the sentence text used as the candidate claim
              - ``source_text``: the same sentence (traceable source span)

            Returns an empty list when ``answer`` is empty or whitespace-only.
        """
        if answer is None:
            return []

        text = str(answer).strip()
        if not text:
            return []

        sentences = [
            sentence.strip()
            for sentence in self._SENTENCE_SPLIT_PATTERN.split(text)
            if sentence.strip()
        ]

        claims: list[dict] = []
        for index, sentence in enumerate(sentences, start=1):
            claims.append(
                {
                    "claim_id": f"claim_{index}",
                    "claim": sentence,
                    "source_text": sentence,
                }
            )

        return claims


if __name__ == "__main__":
    # Offline smoke test (no model / network / API).
    demo_answer = (
        "Arthur's Magazine: Arthur's Magazine (1844–1846) was an American "
        "literary periodical. First for Women: First for Women is a woman's "
        "magazine published in the USA."
    )
    extractor = ClaimExtractor()
    for item in extractor.extract(demo_answer):
        print(item["claim_id"], "->", item["claim"])
    print("empty ->", extractor.extract(""))
