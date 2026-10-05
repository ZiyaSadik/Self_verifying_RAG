"""Evaluate dense retrieval against HotpotQA supporting facts.

Primary protocol (Review 02)
----------------------------
For each of the 100 HotpotQA questions we retrieve only within that question's
own distractor context (``retrieve_within_sample``). Gold labels are the
HotpotQA ``supporting_facts`` pairs ``(title, sent_id)``.

We report mean supporting-fact Recall@k and Precision@k for k in {1, 3, 5, 10}.

This script needs the local embedding model already cached; it does not call
an LLM API.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.retrieval_metrics import (
    extract_gold_supporting_facts,
    supporting_fact_precision_at_k,
    supporting_fact_recall_at_k,
)
from src.retrieval.retriever import Retriever

DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "evaluation" / "hotpotqa_100.json"
K_VALUES = (1, 3, 5, 10)


def load_samples(data_path: Path = DEFAULT_DATA_PATH) -> list[dict]:
    """Load the saved HotpotQA evaluation subset."""
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_retrieval(
    samples: list[dict],
    retriever: Retriever,
    k_values: tuple[int, ...] = K_VALUES,
) -> dict[str, float | int]:
    """Run within-sample retrieval evaluation over all questions.

    Returns a flat dict of mean metrics plus ``n_questions``.
    """
    recall_sums: dict[int, float] = defaultdict(float)
    precision_sums: dict[int, float] = defaultdict(float)
    max_k = max(k_values)

    for sample in samples:
        gold = extract_gold_supporting_facts(sample)
        retrieved = retriever.retrieve_within_sample(
            query=sample["question"],
            sample_id=sample["id"],
            top_k=max_k,
        )

        for k in k_values:
            recall_sums[k] += supporting_fact_recall_at_k(gold, retrieved, k)
            precision_sums[k] += supporting_fact_precision_at_k(gold, retrieved, k)

    n_questions = len(samples)
    results: dict[str, float | int] = {"n_questions": n_questions}
    if n_questions == 0:
        return results

    for k in k_values:
        results[f"recall@{k}"] = recall_sums[k] / n_questions
        results[f"precision@{k}"] = precision_sums[k] / n_questions

    return results


def print_summary(results: dict[str, float | int], k_values: tuple[int, ...] = K_VALUES) -> None:
    """Print a compact mean-metrics table for the dissertation log."""
    n_questions = int(results["n_questions"])
    print("=" * 56)
    print("HotpotQA within-sample supporting-fact retrieval")
    print("=" * 56)
    print(f"Evaluated questions: {n_questions}")
    print("-" * 56)
    print(f"{'k':>4}  {'Recall@k':>10}  {'Precision@k':>12}")
    print("-" * 56)
    for k in k_values:
        recall = float(results[f"recall@{k}"])
        precision = float(results[f"precision@{k}"])
        print(f"{k:>4}  {recall:>10.4f}  {precision:>12.4f}")
    print("=" * 56)


def main() -> None:
    samples = load_samples()
    retriever = Retriever(data_path=DEFAULT_DATA_PATH)
    retriever.build_index()
    results = evaluate_retrieval(samples, retriever)
    print_summary(results)


if __name__ == "__main__":
    main()
