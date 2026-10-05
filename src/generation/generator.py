"""Deterministic extractive answer generator (Review 02 baseline).

This module intentionally does **not** call an LLM. It builds a draft answer
by selecting and concatenating the highest-ranked retrieved sentences so that
the Query → Retrieval → Generation path can be validated end-to-end before an
LLM (local or API) is integrated later.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


class ExtractiveGenerator:
    """Baseline generator that forms answers only from retrieved evidence.

    The method is deterministic: given the same ``question`` and the same
    ordered ``passages``, the returned ``answer`` and ``evidence`` are always
    identical. No model weights, network calls, or sampling are involved.
    """

    def __init__(self, max_sentences: int = 3) -> None:
        """
        Args:
            max_sentences: Maximum number of top-ranked retrieved sentences to
                include in the draft answer (and in ``evidence``).
        """
        if max_sentences < 1:
            raise ValueError("max_sentences must be >= 1")
        self.max_sentences = max_sentences

    def generate(
        self,
        question: str,
        passages: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Build a draft extractive answer from ranked retrieval hits.

        Passages are assumed to be ordered by descending retrieval score
        (as returned by the project's retriever). The generator takes the
        first ``max_sentences`` passages, preserves their metadata as
        ``evidence``, and concatenates their sentence texts into ``answer``.

        Args:
            question: The user / HotpotQA question string.
            passages: Retrieval results with keys such as
                ``sample_id``, ``title``, ``sent_id``, ``sentence``, ``score``.

        Returns:
            A dictionary with:
              - ``question``: echoed input question
              - ``answer``: concatenated extractive draft
              - ``evidence``: list of the passages actually used
              - ``method``: always ``\"extractive\"``
        """
        selected = [dict(passage) for passage in passages[: self.max_sentences]]

        if not selected:
            answer = ""
        else:
            # Sentence text only: titles stay in evidence metadata for provenance.
            parts = [str(passage["sentence"]).strip() for passage in selected]
            answer = " ".join(parts)

        return {
            "question": question,
            "answer": answer,
            "evidence": selected,
            "method": "extractive",
        }


if __name__ == "__main__":
    # Offline smoke test: hardcoded passages only (no model / network / API).
    demo_question = "Which magazine was started first Arthur's Magazine or First for Women?"
    demo_passages = [
        {
            "sample_id": "demo",
            "title": "Arthur's Magazine",
            "sent_id": 0,
            "sentence": "Arthur's Magazine (1844–1846) was an American literary periodical.",
            "score": 0.91,
        },
        {
            "sample_id": "demo",
            "title": "First for Women",
            "sent_id": 0,
            "sentence": "First for Women is a woman's magazine published in the USA.",
            "score": 0.87,
        },
        {
            "sample_id": "demo",
            "title": "Unrelated",
            "sent_id": 1,
            "sentence": "This lower-ranked sentence should be ignored when max_sentences=2.",
            "score": 0.10,
        },
    ]

    result = ExtractiveGenerator(max_sentences=2).generate(demo_question, demo_passages)
    print("method:", result["method"])
    print("question:", result["question"])
    print("answer:", result["answer"])
    print("evidence_count:", len(result["evidence"]))
    for i, ev in enumerate(result["evidence"], start=1):
        print(f"  {i}. {ev['title']} (sent_id={ev['sent_id']}, score={ev['score']})")
