# Self-Verifying RAG

A Self-Verifying Multi-Agent Framework for Trustworthy Retrieval-Augmented Generation

## Current Status

This repository currently contains the **Review 02 (Rev 2) deterministic / offline baseline**.

It includes HotpotQA subset loading, dense retrieval, extractive generation, claim extraction, lexical claim–evidence verification, and evaluation scripts.

It does **not** yet contain the final multi-agent LLM framework, LLM-based generation, NLI entailment, LLM judges, or iterative LLM correction.

## Rev 2 Pipeline

```
HotpotQA (100 samples)
  → within-sample dense retrieval using SentenceTransformers + FAISS
  → top-10 retrieved evidence
  → extractive generation from top-3 evidence
  → deterministic claim extraction
  → lexical claim–evidence verification against all top-10 evidence
  → comparison with HotpotQA gold supporting facts
```

Important clarifications:

- **No LLM / API is required for Rev 2.** The baseline runs offline after dependencies and the embedding model are available locally.
- **Lexical claim–evidence support is NOT factual-truth verification.** The verifier measures token-coverage consistency between claims and retrieved evidence.
- **The current claim extractor is a deterministic sentence splitter.** It is not semantic claim decomposition.

## Project Structure

```
Self_verifying_RAG/
├── data/
│   ├── documents/                 # Reserved for future document corpora
│   └── evaluation/
│       └── hotpotqa_100.json      # 100 HotpotQA distractor samples (Rev 2)
├── src/
│   ├── ingestion/
│   │   └── load_hotpotqa.py       # Optional regenerator for hotpotqa_100.json
│   ├── retrieval/
│   │   └── retriever.py           # MiniLM + FAISS dense retriever
│   ├── generation/
│   │   └── generator.py           # Deterministic extractive generator
│   ├── verification/
│   │   ├── claim_extractor.py     # Sentence-level claim splitter
│   │   └── claim_verifier.py      # Lexical token-coverage verifier
│   ├── evaluation/
│   │   ├── retrieval_metrics.py   # Supporting-fact Recall@k / Precision@k
│   │   ├── evaluate_retrieval.py  # Retrieval evaluation runner
│   │   ├── calibrate_verifier.py  # Threshold calibration on HotpotQA proxies
│   │   └── evaluate_end_to_end.py # Full Rev 2 end-to-end evaluation
│   ├── agents/                    # Stub only (future multi-agent orchestration)
│   └── ...
├── tests/
│   ├── test_retrieval_metrics.py
│   └── test_claim_verifier.py
├── config/                        # Reserved for future experiment configs
├── notebooks/                     # Reserved for exploratory analysis
├── .env.example                   # Placeholder env vars only (no secrets)
├── .gitignore
├── requirements.txt
└── README.md
```

| Path | Purpose |
|---|---|
| `data/evaluation/hotpotqa_100.json` | Saved 100-sample HotpotQA distractor subset used by all Rev 2 evaluations |
| `src/ingestion/load_hotpotqa.py` | Downloads/saves the 100-sample subset if regeneration is needed |
| `src/retrieval/retriever.py` | Dense retrieval with within-sample and shared-corpus modes |
| `src/generation/generator.py` | Concatenates top retrieved sentences into a draft answer |
| `src/verification/claim_extractor.py` | Splits the answer into sentence-level candidate claims |
| `src/verification/claim_verifier.py` | Max token-coverage claim–evidence verifier |
| `src/evaluation/retrieval_metrics.py` | Pure-Python supporting-fact metrics |
| `src/evaluation/evaluate_retrieval.py` | Reports mean Recall@k / Precision@k |
| `src/evaluation/calibrate_verifier.py` | Threshold sweep on lexical HotpotQA proxies |
| `src/evaluation/evaluate_end_to_end.py` | End-to-end Rev 2 pipeline evaluation |
| `tests/` | Offline unit tests (no model / network required for metric/verifier tests) |

## Requirements

- Python **3.13.9** was used for the current Rev 2 environment.
- CPU-only execution is supported.
- No NVIDIA GPU / CUDA is required.
- Main packages include: `datasets`, `sentence-transformers`, `faiss-cpu`, `numpy`, `torch`, `transformers`, and `requests`.
- Install dependencies with `requirements.txt` (see Setup).

Package versions are not pinned in this repository; install the current compatible releases via pip.

## Setup

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No API key is required for Rev 2.

Notes:

- First retrieval / end-to-end run may download the SentenceTransformer model `sentence-transformers/all-MiniLM-L6-v2` into the local Hugging Face cache if it is not already present.
- Regenerating the HotpotQA subset with `load_hotpotqa.py` requires network access to Hugging Face Datasets. The included `hotpotqa_100.json` is enough for Rev 2 evaluation without regenerating.

## Dataset

This repository includes:

```text
data/evaluation/hotpotqa_100.json
```

It contains **100 HotpotQA distractor training examples** used for the Rev 2 evaluation.

To regenerate the dataset if needed:

```powershell
python src/ingestion/load_hotpotqa.py
```

## Running Rev 2

Retrieval evaluation:

```powershell
python src/evaluation/evaluate_retrieval.py
```

Verifier threshold calibration:

```powershell
python src/evaluation/calibrate_verifier.py
```

End-to-end Rev 2 baseline:

```powershell
python src/evaluation/evaluate_end_to_end.py
```

Unit tests:

```powershell
python -m unittest tests.test_retrieval_metrics -v
python -m unittest tests.test_claim_verifier -v
```

## Expected Rev 2 Results

### Retrieval (within-sample supporting-fact metrics)

| Metric | Value |
|---|---:|
| Recall@1 | 0.2848 |
| Precision@1 | 0.6700 |
| Recall@3 | 0.5483 |
| Precision@3 | 0.4400 |
| Recall@5 | 0.6808 |
| Precision@5 | 0.3280 |
| Recall@10 | 0.7753 |
| Precision@10 | 0.1860 |

### End-to-end lexical claim–evidence evaluation

| Quantity | Value |
|---|---:|
| Evaluated samples | 100 |
| Total claims | 318 |
| Supported claims | 316 |
| Unsupported claims | 2 |
| Overall lexical claim support rate | 0.9937 |
| Claims whose matched evidence is gold supporting fact | 140 |
| Supported claims matched to gold supporting fact | 139 |
| Gold-support match rate among supported claims | 0.4399 |

Interpretation (critical):

- The **0.9937** overall claim support rate **must not** be interpreted as factual accuracy. The verifier is lexical token-coverage based and checks whether generated claims are covered by retrieved evidence text.
- The **0.4399** gold-support match rate is a **separate** comparison of matched evidence against HotpotQA gold supporting-fact pairs. It is also **not** the verifier’s factual accuracy.

## Important Rev 2 Limitations

- Deterministic extractive generator (not an LLM)
- Deterministic sentence-based claim extraction (not semantic claim decomposition)
- Lexical token-coverage verifier
- No semantic entailment / NLI
- No LLM judge
- No multi-agent orchestration yet
- No iterative LLM-based correction yet
- Lexical support does not establish factual truth
- Current threshold calibration uses HotpotQA supporting-fact lexical proxies and is a **sanity check**, not a factual-truth benchmark

## Next Phase

Intended future architecture (not implemented yet):

```
User Query
  → Query Planner Agent
  → Retrieval Agent
  → Evidence Verification Agent
  → Generation Agent
  → Claim Verification Agent
  → Critic / Revision Agent
  → Re-retrieval / Revision
  → Re-verification
  → Final Answer
```

This multi-agent LLM pipeline is planned for later dissertation stages and is **not** present in the current Rev 2 codebase.
