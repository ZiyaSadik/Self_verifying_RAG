"""Load a small HotpotQA subset and save it for evaluation."""

from __future__ import annotations

import json
from pathlib import Path

from datasets import load_dataset

# Project root: .../Self_verifying_RAG (two levels above this file)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "data" / "evaluation" / "hotpotqa_100.json"

FIELDS = (
    "id",
    "question",
    "answer",
    "type",
    "level",
    "supporting_facts",
    "context",
)


def load_hotpotqa_samples(split: str = "train[:100]") -> list[dict]:
    """Load HotpotQA distractor split and return selected fields for each sample."""
    dataset = load_dataset("hotpotqa/hotpot_qa", "distractor", split=split)

    samples = []
    for row in dataset:
        sample = {field: row[field] for field in FIELDS}
        samples.append(sample)
    return samples


def save_samples(samples: list[dict], output_path: Path = OUTPUT_PATH) -> Path:
    """Write samples to JSON, creating the parent directory if needed."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    samples = load_hotpotqa_samples()
    path = save_samples(samples)
    print(f"Saved {len(samples)} samples to {path}")


if __name__ == "__main__":
    main()
