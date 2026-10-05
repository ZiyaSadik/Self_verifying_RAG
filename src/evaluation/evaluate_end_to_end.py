"""Rev 2 deterministic end-to-end baseline evaluation.

Pipeline
--------
HotpotQA sample
  → within-sample dense retrieval (top-10)
  → extractive generation (top-3 of those hits)
  → sentence-level claim extraction
  → lexical claim–evidence verification against ALL top-10 hits

Verifier label
--------------
This script reports **lexical claim–evidence verification; not factual-truth
verification**. Support rates measure token coverage of generated claims by
retrieved evidence, not HotpotQA answer correctness or objective truth.

No LLM or external API is used.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.generation.generator import ExtractiveGenerator
from src.retrieval.retriever import Retriever
from src.verification.claim_extractor import ClaimExtractor
from src.verification.claim_verifier import ClaimEvidenceVerifier

DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "evaluation" / "hotpotqa_100.json"

# Calibrated on HotpotQA lexical supporting-fact proxies (Rev 2).
# Development default in ClaimEvidenceVerifier is 0.7; end-to-end uses τ*.
VERIFIER_THRESHOLD = 1.0

RETRIEVE_TOP_K = 10
GENERATE_TOP_K = 3


def load_samples(data_path: Path = DEFAULT_DATA_PATH) -> list[dict[str, Any]]:
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def gold_supporting_facts(sample: dict[str, Any]) -> set[tuple[str, int]]:
    """HotpotQA gold evidence as (title, sent_id) pairs."""
    sf = sample["supporting_facts"]
    return {
        (str(title), int(sent_id))
        for title, sent_id in zip(sf["title"], sf["sent_id"])
    }


def format_gold_supporting_facts(sample: dict[str, Any]) -> list[str]:
    """Human-readable gold supporting facts with sentence text when available."""
    titles = sample["context"]["title"]
    sentence_lists = sample["context"]["sentences"]
    title_to_sentences = {
        title: sentences for title, sentences in zip(titles, sentence_lists)
    }

    lines: list[str] = []
    sf = sample["supporting_facts"]
    for title, sent_id in zip(sf["title"], sf["sent_id"]):
        sent_id = int(sent_id)
        sentences = title_to_sentences.get(title, [])
        text = ""
        if 0 <= sent_id < len(sentences):
            text = str(sentences[sent_id]).strip()
        lines.append(f"  - ({title!r}, sent_id={sent_id}): {text}")
    return lines


def evaluate_sample(
    sample: dict[str, Any],
    retriever: Retriever,
    generator: ExtractiveGenerator,
    extractor: ClaimExtractor,
    verifier: ClaimEvidenceVerifier,
) -> dict[str, Any]:
    """Run the full Rev 2 pipeline for one HotpotQA sample."""
    gold_facts = gold_supporting_facts(sample)

    retrieved = retriever.retrieve_within_sample(
        query=sample["question"],
        sample_id=sample["id"],
        top_k=RETRIEVE_TOP_K,
    )

    generation = generator.generate(
        question=sample["question"],
        passages=retrieved[:GENERATE_TOP_K],
    )

    claims = extractor.extract(generation["answer"])
    # Verify against ALL top-10 retrieved evidence, not only generation evidence.
    verification = verifier.verify(claims, retrieved)
    aggregate = ClaimEvidenceVerifier.aggregate(verification)

    claim_rows: list[dict[str, Any]] = []
    n_matched_gold = 0
    n_supported_matched_gold = 0

    for result in verification:
        matched = result["matched_evidence"]
        if matched:
            m = matched[0]
            matched_title = m["title"]
            matched_sent_id = int(m["sent_id"])
            matched_sentence = m["sentence"]
            matched_overlap = float(m["overlap_score"])
            is_gold = (matched_title, matched_sent_id) in gold_facts
        else:
            matched_title = ""
            matched_sent_id = -1
            matched_sentence = ""
            matched_overlap = 0.0
            is_gold = False

        if is_gold:
            n_matched_gold += 1
            if result["decision"] == "supported":
                n_supported_matched_gold += 1

        claim_rows.append(
            {
                "claim_id": result["claim_id"],
                "claim": result["claim"],
                "support_score": result["support_score"],
                "decision": result["decision"],
                "matched_evidence_title": matched_title,
                "matched_evidence_sent_id": matched_sent_id,
                "matched_evidence_sentence": matched_sentence,
                "matched_overlap_score": matched_overlap,
                "matched_is_gold_supporting_fact": is_gold,
            }
        )

    return {
        "sample_id": sample["id"],
        "question": sample["question"],
        "gold_answer": sample["answer"],
        "generated_answer": generation["answer"],
        "n_retrieved": len(retrieved),
        "n_claims": int(aggregate["n_claims"]),
        "n_supported": int(aggregate["n_supported"]),
        "n_unsupported": int(aggregate["n_unsupported"]),
        "support_rate": float(aggregate["support_rate"]),
        "claims": claim_rows,
        "n_claims_matched_gold_sf": n_matched_gold,
        "n_supported_matched_gold_sf": n_supported_matched_gold,
        "gold_supporting_facts": list(gold_facts),
        "gold_supporting_fact_lines": format_gold_supporting_facts(sample),
    }


def summarise(results: list[dict[str, Any]]) -> dict[str, float | int]:
    """Dataset-level aggregates for the dissertation log."""
    n_samples = len(results)
    total_claims = sum(r["n_claims"] for r in results)
    supported = sum(r["n_supported"] for r in results)
    unsupported = sum(r["n_unsupported"] for r in results)
    matched_gold = sum(r["n_claims_matched_gold_sf"] for r in results)
    supported_matched_gold = sum(r["n_supported_matched_gold_sf"] for r in results)

    overall_support_rate = supported / total_claims if total_claims else 0.0
    # Gold-support match rate among supported claims only.
    gold_match_rate_among_supported = (
        supported_matched_gold / supported if supported else 0.0
    )

    return {
        "n_samples": n_samples,
        "total_claims": total_claims,
        "supported_claims": supported,
        "unsupported_claims": unsupported,
        "overall_claim_support_rate": overall_support_rate,
        "claims_matched_gold_supporting_fact": matched_gold,
        "supported_claims_matched_gold_sf": supported_matched_gold,
        "gold_support_match_rate_among_supported": gold_match_rate_among_supported,
    }


def choose_examples(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pick three representative samples for terminal display."""
    all_supported = next(
        (r for r in results if r["n_claims"] > 0 and r["n_unsupported"] == 0),
        None,
    )
    has_unsupported = next(
        (r for r in results if r["n_unsupported"] > 0),
        None,
    )

    chosen: list[dict[str, Any]] = []
    chosen_ids: set[str] = set()

    for candidate in (all_supported, has_unsupported):
        if candidate is not None and candidate["sample_id"] not in chosen_ids:
            chosen.append(candidate)
            chosen_ids.add(candidate["sample_id"])

    for r in results:
        if r["sample_id"] not in chosen_ids:
            chosen.append(r)
            chosen_ids.add(r["sample_id"])
        if len(chosen) >= 3:
            break

    return chosen[:3]


def print_header() -> None:
    print("=" * 72)
    print("Rev 2 deterministic end-to-end baseline")
    print("=" * 72)
    print("Pipeline:")
    print("  HotpotQA → within-sample retrieval (top-10)")
    print("           → extractive generation (top-3)")
    print("           → claim extraction")
    print("           → claim–evidence verification vs ALL top-10 evidence")
    print()
    print(
        "Verifier: lexical claim-evidence verification; "
        "not factual-truth verification"
    )
    print(f"Verifier threshold τ = {VERIFIER_THRESHOLD:.1f} (Rev 2 calibration)")
    print("No LLM / API calls.")
    print("=" * 72)


def print_summary(summary: dict[str, float | int]) -> None:
    print()
    print("-" * 72)
    print("DATASET SUMMARY")
    print("-" * 72)
    print(f"Evaluated samples:                         {summary['n_samples']}")
    print(f"Total claims:                              {summary['total_claims']}")
    print(f"Supported claims:                          {summary['supported_claims']}")
    print(f"Unsupported claims:                        {summary['unsupported_claims']}")
    print(
        f"Overall claim support rate:                 "
        f"{float(summary['overall_claim_support_rate']):.4f}"
    )
    print(
        f"Claims whose matched evidence is gold SF:   "
        f"{summary['claims_matched_gold_supporting_fact']}"
    )
    print(
        f"Supported claims matched to gold SF:        "
        f"{summary['supported_claims_matched_gold_sf']}"
    )
    print(
        f"Gold-support match rate among supported:    "
        f"{float(summary['gold_support_match_rate_among_supported']):.4f}"
    )
    print()
    print(
        "Note: support rates are lexical claim–evidence coverage, "
        "not factual answer accuracy."
    )
    print("-" * 72)


def print_example(result: dict[str, Any], index: int) -> None:
    print()
    print("=" * 72)
    print(f"REPRESENTATIVE EXAMPLE {index}")
    print("=" * 72)
    print(f"Sample ID:          {result['sample_id']}")
    print(f"Question:           {result['question']}")
    print(f"Gold answer:        {result['gold_answer']}")
    print(f"Generated answer:   {result['generated_answer']}")
    print(f"Retrieved passages: {result['n_retrieved']}")
    print(
        f"Claims: {result['n_claims']}  "
        f"(supported={result['n_supported']}, "
        f"unsupported={result['n_unsupported']}, "
        f"support_rate={result['support_rate']:.4f})"
    )
    print()
    print("Gold supporting facts:")
    for line in result["gold_supporting_fact_lines"]:
        print(line)
    print()
    print("Claims and verification:")
    for claim in result["claims"]:
        gold_flag = "yes" if claim["matched_is_gold_supporting_fact"] else "no"
        print(f"  [{claim['claim_id']}] decision={claim['decision']}  "
              f"score={claim['support_score']:.4f}")
        print(f"      claim: {claim['claim']}")
        print(
            f"      matched: title={claim['matched_evidence_title']!r}  "
            f"sent_id={claim['matched_evidence_sent_id']}  "
            f"gold_SF={gold_flag}"
        )
        print(f"      evidence: {claim['matched_evidence_sentence']}")
    print("=" * 72)


def print_compact_sample_table(results: list[dict[str, Any]], limit: int = 10) -> None:
    """Optional short per-sample preview (first N) for terminal readability."""
    print()
    print("-" * 72)
    print(f"PER-SAMPLE PREVIEW (first {min(limit, len(results))} of {len(results)})")
    print("-" * 72)
    for i, r in enumerate(results[:limit], start=1):
        print(
            f"{i:>3}. id={r['sample_id']}  "
            f"claims={r['n_claims']}  "
            f"supp={r['n_supported']}  "
            f"unsupp={r['n_unsupported']}  "
            f"rate={r['support_rate']:.2f}  "
            f"Q={r['question'][:60]}..."
        )


def run_evaluation(
    data_path: Path = DEFAULT_DATA_PATH,
    threshold: float = VERIFIER_THRESHOLD,
) -> tuple[list[dict[str, Any]], dict[str, float | int]]:
    samples = load_samples(data_path)

    retriever = Retriever(data_path=data_path)
    retriever.build_index()

    generator = ExtractiveGenerator(max_sentences=GENERATE_TOP_K)
    extractor = ClaimExtractor()
    verifier = ClaimEvidenceVerifier(threshold=threshold)

    results: list[dict[str, Any]] = []
    for sample in samples:
        results.append(
            evaluate_sample(sample, retriever, generator, extractor, verifier)
        )

    return results, summarise(results)


def main() -> None:
    print_header()
    results, summary = run_evaluation()
    print_summary(summary)
    print_compact_sample_table(results, limit=10)

    examples = choose_examples(results)
    labels = []
    for ex in examples:
        if ex["n_claims"] > 0 and ex["n_unsupported"] == 0:
            labels.append("all claims supported")
        elif ex["n_unsupported"] > 0:
            labels.append("has unsupported claim(s)")
        else:
            labels.append("additional example")

    print()
    print("Representative examples selected:")
    for i, (ex, label) in enumerate(zip(examples, labels), start=1):
        print(f"  {i}. {label} (sample_id={ex['sample_id']})")

    for i, ex in enumerate(examples, start=1):
        print_example(ex, index=i)


if __name__ == "__main__":
    main()
