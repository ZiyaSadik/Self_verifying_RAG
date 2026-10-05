"""Calibrate the claim–evidence verifier threshold on HotpotQA proxies.

This script does **not** measure factual truth. It only finds an empirical
operating threshold for lexical token-coverage decisions using HotpotQA
``supporting_facts`` annotations as a proxy for “supported” vs “unsupported”
lexical pairs.

Protocol
--------
* Split the 100 samples by sorted ``id`` into 70 calibration + 30 validation
  samples (no pair-level leakage across the split).
* Positive pair: claim = gold supporting-fact sentence; evidence = same text.
* Negative pair: claim = gold supporting-fact sentence; evidence = a
  non-supporting context sentence from the same sample when possible.
* Sweep thresholds 0.0, 0.1, ..., 1.0 on the calibration set; select the
  threshold with highest F1 (ties → higher threshold); report validation
  precision / recall / F1 at that threshold.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.verification.claim_verifier import ClaimEvidenceVerifier

DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "evaluation" / "hotpotqa_100.json"
THRESHOLDS = [i / 10 for i in range(0, 11)]  # 0.0 ... 1.0
CALIBRATION_COUNT = 70


def load_samples(data_path: Path = DEFAULT_DATA_PATH) -> list[dict[str, Any]]:
    with data_path.open("r", encoding="utf-8") as f:
        samples = json.load(f)
    return sorted(samples, key=lambda s: s["id"])


def gold_supporting_sentences(sample: dict[str, Any]) -> list[tuple[str, int, str]]:
    """Return (title, sent_id, sentence) for each gold supporting fact."""
    titles = sample["context"]["title"]
    sentence_lists = sample["context"]["sentences"]
    title_to_sentences = {
        title: sentences for title, sentences in zip(titles, sentence_lists)
    }

    results: list[tuple[str, int, str]] = []
    sf = sample["supporting_facts"]
    for title, sent_id in zip(sf["title"], sf["sent_id"]):
        sent_id = int(sent_id)
        sentences = title_to_sentences.get(title)
        if not sentences or sent_id < 0 or sent_id >= len(sentences):
            continue
        text = str(sentences[sent_id]).strip()
        if text:
            results.append((title, sent_id, text))
    return results


def non_supporting_sentences(sample: dict[str, Any]) -> list[tuple[str, int, str]]:
    """Return context sentences that are not gold supporting facts."""
    gold_keys = {
        (title, int(sent_id))
        for title, sent_id in zip(
            sample["supporting_facts"]["title"],
            sample["supporting_facts"]["sent_id"],
        )
    }
    results: list[tuple[str, int, str]] = []
    for title, sentences in zip(
        sample["context"]["title"], sample["context"]["sentences"]
    ):
        for sent_id, sentence in enumerate(sentences):
            text = str(sentence).strip()
            if not text:
                continue
            if (title, sent_id) in gold_keys:
                continue
            results.append((title, sent_id, text))
    # Deterministic order for reproducible negative selection
    results.sort(key=lambda x: (x[0], x[1]))
    return results


def build_pairs_for_sample(
    sample: dict[str, Any],
    fallback_evidence_text: str | None = None,
) -> list[tuple[str, str, int]]:
    """Build (claim_text, evidence_text, gold_label) pairs for one sample."""
    pairs: list[tuple[str, str, int]] = []
    gold = gold_supporting_sentences(sample)
    negatives = non_supporting_sentences(sample)

    for _title, _sent_id, claim_text in gold:
        # Positive: identical gold supporting-fact sentence
        pairs.append((claim_text, claim_text, 1))

        # Negative: same claim against a non-supporting sentence
        if negatives:
            _n_title, _n_sid, neg_text = negatives[0]
            pairs.append((claim_text, neg_text, 0))
        elif fallback_evidence_text and fallback_evidence_text != claim_text:
            pairs.append((claim_text, fallback_evidence_text, 0))

    return pairs


def build_pairs(samples: list[dict[str, Any]]) -> list[tuple[str, str, int]]:
    """Build all proxy pairs for a list of samples."""
    # Fallback evidence: first non-empty sentence from the last sample, if needed
    fallback: str | None = None
    for sample in reversed(samples):
        for sentences in sample["context"]["sentences"]:
            for sentence in sentences:
                text = str(sentence).strip()
                if text:
                    fallback = text
                    break
            if fallback:
                break
        if fallback:
            break

    pairs: list[tuple[str, str, int]] = []
    for sample in samples:
        pairs.extend(build_pairs_for_sample(sample, fallback_evidence_text=fallback))
    return pairs


def predict_label(claim_text: str, evidence_text: str, threshold: float) -> int:
    verifier = ClaimEvidenceVerifier(threshold=threshold)
    result = verifier.verify_claim(
        {"claim_id": "proxy", "claim": claim_text},
        [
            {
                "sample_id": "proxy",
                "title": "proxy",
                "sent_id": 0,
                "sentence": evidence_text,
                "score": 1.0,
            }
        ],
    )
    return 1 if result["decision"] == "supported" else 0


def classification_metrics(
    pairs: list[tuple[str, str, int]],
    threshold: float,
) -> dict[str, float]:
    """Precision / recall / F1 for binary support decisions on proxy pairs."""
    tp = fp = tn = fn = 0
    for claim_text, evidence_text, gold in pairs:
        pred = predict_label(claim_text, evidence_text, threshold)
        if gold == 1 and pred == 1:
            tp += 1
        elif gold == 0 and pred == 1:
            fp += 1
        elif gold == 0 and pred == 0:
            tn += 1
        else:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    if precision + recall == 0.0:
        f1 = 0.0
    else:
        f1 = 2.0 * precision * recall / (precision + recall)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": float(tp),
        "fp": float(fp),
        "tn": float(tn),
        "fn": float(fn),
    }


def select_threshold(calibration_pairs: list[tuple[str, str, int]]) -> tuple[float, dict[str, float], list[dict[str, float]]]:
    """Sweep thresholds; return best threshold, its metrics, and the full table."""
    table: list[dict[str, float]] = []
    best_threshold = 0.0
    best_metrics: dict[str, float] | None = None

    for threshold in THRESHOLDS:
        metrics = classification_metrics(calibration_pairs, threshold)
        row = {"threshold": threshold, **metrics}
        table.append(row)

        if best_metrics is None:
            best_threshold, best_metrics = threshold, metrics
            continue

        # Highest F1; ties → higher threshold
        if metrics["f1"] > best_metrics["f1"] or (
            metrics["f1"] == best_metrics["f1"] and threshold > best_threshold
        ):
            best_threshold, best_metrics = threshold, metrics

    assert best_metrics is not None
    return best_threshold, best_metrics, table


def print_table(table: list[dict[str, float]]) -> None:
    print("-" * 64)
    print(f"{'tau':>6}  {'P':>8}  {'R':>8}  {'F1':>8}")
    print("-" * 64)
    for row in table:
        print(
            f"{row['threshold']:>6.1f}  "
            f"{row['precision']:>8.4f}  "
            f"{row['recall']:>8.4f}  "
            f"{row['f1']:>8.4f}"
        )
    print("-" * 64)


def main() -> None:
    samples = load_samples()
    if len(samples) < CALIBRATION_COUNT:
        raise RuntimeError(
            f"Expected at least {CALIBRATION_COUNT} samples, found {len(samples)}"
        )

    calibration_samples = samples[:CALIBRATION_COUNT]
    validation_samples = samples[CALIBRATION_COUNT:]

    calibration_pairs = build_pairs(calibration_samples)
    validation_pairs = build_pairs(validation_samples)

    selected, calib_metrics, table = select_threshold(calibration_pairs)
    val_metrics = classification_metrics(validation_pairs, selected)

    print("=" * 64)
    print("Claim–evidence verifier threshold calibration")
    print("(lexical HotpotQA supporting-fact proxies; not factual truth)")
    print("=" * 64)
    print(f"Calibration samples: {len(calibration_samples)}")
    print(f"Validation samples:  {len(validation_samples)}")
    print(f"Calibration pairs:   {len(calibration_pairs)}")
    print(f"Validation pairs:    {len(validation_pairs)}")
    print()
    print("Calibration threshold sweep:")
    print_table(table)
    print()
    print(f"Selected threshold:  {selected:.1f}")
    print(
        "Calibration  P/R/F1: "
        f"{calib_metrics['precision']:.4f} / "
        f"{calib_metrics['recall']:.4f} / "
        f"{calib_metrics['f1']:.4f}"
    )
    print(
        "Validation   P/R/F1: "
        f"{val_metrics['precision']:.4f} / "
        f"{val_metrics['recall']:.4f} / "
        f"{val_metrics['f1']:.4f}"
    )
    print("=" * 64)


if __name__ == "__main__":
    main()
