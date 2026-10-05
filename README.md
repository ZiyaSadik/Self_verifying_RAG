# Self-Verifying RAG

A Self-Verifying Multi-Agent Framework for Trustworthy Retrieval-Augmented Generation

## Overview

Retrieval-Augmented Generation (RAG) can improve factual grounding by conditioning language-model answers on external evidence. In practice, however, retrieval errors, irrelevant passages, unsupported claims, and hallucinations can still undermine reliability.

This dissertation project investigates a **self-verifying multi-agent RAG framework** that integrates:

- retrieval
- evidence verification
- generation
- claim-level verification
- iterative correction
- multi-agent coordination

The long-term goal is to improve the trustworthiness of RAG responses while accounting for the additional computational and verification cost introduced by these checks.

## Research Objective

To investigate whether an integrated multi-agent framework with evidence-level verification, claim-level verification, and iterative correction can improve the trustworthiness of RAG responses while managing verification cost.

## Proposed Framework

```
User Query
    ↓
Query Planner Agent
    ↓
Retrieval Agent
    ↓
Evidence Verification Agent
    ↓
Generation Agent
    ↓
Claim Verification Agent
    ↓
All claims supported?
    ├── Yes → Final Answer
    └── No → Critic / Revision Agent
                    ↓
              Re-retrieve / Revise
                    ↓
              Generate Again
                    ↓
             Claim Verification
                    ↺
```

| Component | Role |
|---|---|
| Query Planner Agent | Interprets the user question and prepares retrieval-ready sub-queries |
| Retrieval Agent | Retrieves candidate evidence from the knowledge corpus |
| Evidence Verification Agent | Filters or ranks retrieved passages for relevance and usefulness |
| Generation Agent | Produces an answer conditioned on verified evidence |
| Claim Verification Agent | Checks whether individual answer claims are supported by evidence |
| Critic / Revision Agent | Triggers revision, re-retrieval, or regeneration when claims are unsupported |

Some pipeline stages are currently implemented as deterministic research prototypes (dense retrieval, extractive generation, lexical claim–evidence checking). The full LLM-based multi-agent system is under active development.

## Current Progress

| Component | Status |
|---|---|
| Problem formulation & literature review | Completed |
| HotpotQA evaluation dataset (100-sample subset) | Completed |
| Dense retrieval pipeline (SentenceTransformers + FAISS) | Completed |
| Retrieval evaluation (supporting-fact Recall / Precision) | Completed |
| Initial extractive generation | Completed |
| Claim extraction prototype | Completed |
| Claim–evidence verification prototype | Completed |
| Initial end-to-end evaluation | Completed |
| Semantic / entailment-based verification | Planned |
| Evidence-level verification agent | Planned |
| Multi-agent orchestration | Planned |
| Iterative correction loop | Planned |
| LLM-based generation | Planned |
| Final comparative evaluation | Planned |

## Current Experimental Results

Early experiments are run on a **100-sample HotpotQA distractor** subset.

| Result | Value |
|---|---:|
| Retrieval Recall@5 | 68.08% |
| Retrieval Recall@10 | 77.53% |
| End-to-end samples evaluated | 100 |

Additional observations from the initial end-to-end run:

- The lexical claim–evidence verifier produces a high **lexical support** rate.
- Lexical support is **not** answer accuracy and must not be treated as factual correctness.
- Comparison with HotpotQA gold supporting facts shows that lexical support does not necessarily align with gold evidence.

**Methodological note:** Current verification is lexical / token-coverage based and is therefore treated as a baseline consistency signal rather than a factual-truth guarantee.

## Technology Stack

- Python
- SentenceTransformers
- FAISS
- Hugging Face Datasets
- PyTorch
- Transformers
- HotpotQA
- Git / GitHub

The current implementation supports **CPU-only** execution.

## Repository Structure

```
Self_verifying_RAG/
├── data/
│   └── evaluation/          # HotpotQA evaluation subset
├── src/
│   ├── ingestion/           # Dataset loading utilities
│   ├── retrieval/           # Dense retrieval
│   ├── generation/          # Answer generation prototypes
│   ├── verification/        # Claim extraction and verification
│   ├── agents/              # Multi-agent orchestration (in development)
│   └── evaluation/          # Metrics and experiment runners
├── tests/                   # Unit tests
├── notebooks/               # Exploratory analysis
├── config/                  # Experiment configuration
├── requirements.txt
└── README.md
```

## Getting Started

```powershell
git clone https://github.com/ZiyaSadik/Self_verifying_RAG.git
cd Self_verifying_RAG

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Main evaluation commands:

```powershell
python src/evaluation/evaluate_retrieval.py
python src/evaluation/calibrate_verifier.py
python src/evaluation/evaluate_end_to_end.py
```

Unit tests:

```powershell
python -m unittest tests.test_retrieval_metrics -v
python -m unittest tests.test_claim_verifier -v
```

No API key is required for the current deterministic components. The first retrieval run may download the local embedding model into the Hugging Face cache.

## Research Roadmap

1. Establish retrieval and evidence-quality baselines
2. Develop evidence-level verification
3. Introduce semantic claim verification
4. Implement specialized RAG agents
5. Add iterative correction / re-retrieval
6. Introduce LLM-based generation and verification
7. Compare baseline RAG against progressively stronger verification configurations
8. Evaluate trustworthiness, factuality, retrieval quality, and verification cost

## Research Questions / Evaluation Direction

Future experiments will compare configurations such as:

- Standard RAG
- RAG + evidence verification
- RAG + claim verification
- RAG + iterative correction
- Full self-verifying multi-agent RAG

Evaluation dimensions under consideration:

- retrieval quality
- answer correctness
- faithfulness / groundedness
- unsupported claim rate
- evidence quality
- correction success
- verification cost / latency

## Limitations of the Current Implementation

- Generation is currently deterministic and extractive.
- Claim extraction is rule-based (sentence segmentation).
- Claim–evidence verification uses lexical token coverage.
- Semantic entailment / NLI is not yet part of the active pipeline.
- Full multi-agent orchestration remains under development.
- Lexical support is a consistency signal, not a factual-truth guarantee.

## Disclaimer

This repository is an evolving research implementation developed for postgraduate dissertation work. Architecture details and experimental results may change as the framework is extended and more thoroughly evaluated.
