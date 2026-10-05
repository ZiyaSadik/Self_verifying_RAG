"""Simple dense retriever over HotpotQA context passages.

Uses Sentence Transformers for embeddings and FAISS for cosine-similarity search.
"""

from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Project root: .../Self_verifying_RAG (two levels above this file)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "evaluation" / "hotpotqa_100.json"
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Retriever:
    """Embed HotpotQA context sentences and retrieve the nearest neighbours for a query."""

    def __init__(
        self,
        data_path: Path | str = DEFAULT_DATA_PATH,
        model_name: str = DEFAULT_MODEL_NAME,
    ) -> None:
        self.data_path = Path(data_path)
        self.model_name = model_name

        # Embedding model (loaded once; reused for indexing and queries)
        self.model = SentenceTransformer(model_name)

        # Flat list of passages aligned with FAISS / embedding rows
        # Each passage: {sample_id, title, sent_id, sentence, text_for_embedding}
        self.passages: list[dict] = []

        # L2-normalised passage embeddings (same row order as self.passages)
        self.embeddings: np.ndarray | None = None

        # FAISS index using inner product; cosine similarity after L2 normalisation
        self.index: faiss.IndexFlatIP | None = None

    def _load_samples(self) -> list[dict]:
        """Load the HotpotQA evaluation JSON file."""
        with self.data_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _build_passages(self, samples: list[dict]) -> list[dict]:
        """Turn each context sentence into a retrievable passage.

        HotpotQA context is two parallel lists:
          - context["title"][i]      -> document title
          - context["sentences"][i]  -> list of sentences for that document

        ``sent_id`` is the original zero-based index of the sentence within its
        document list, matching HotpotQA ``supporting_facts.sent_id``. Empty
        sentences are skipped but do not renumber later sentences.
        """
        passages: list[dict] = []

        for sample in samples:
            sample_id = sample["id"]
            titles = sample["context"]["title"]
            sentence_lists = sample["context"]["sentences"]

            for title, sentences in zip(titles, sentence_lists):
                for sent_id, sentence in enumerate(sentences):
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    passages.append(
                        {
                            "sample_id": sample_id,
                            "title": title,
                            "sent_id": sent_id,
                            "sentence": sentence,
                            # Text actually embedded for retrieval
                            "text_for_embedding": f"{title}: {sentence}",
                        }
                    )

        return passages

    def build_index(self) -> None:
        """Load data, embed all passages, and build a FAISS cosine-similarity index."""
        samples = self._load_samples()
        self.passages = self._build_passages(samples)

        texts = [p["text_for_embedding"] for p in self.passages]

        # 1) Encode passages into dense vectors
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
        ).astype("float32")

        # 2) L2-normalise so inner product == cosine similarity
        faiss.normalize_L2(embeddings)
        self.embeddings = embeddings

        # 3) IndexFlatIP: exact search with inner product (cosine after step 2)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        print(
            f"Built FAISS index with {self.index.ntotal} passages "
            f"(dim={dimension}) from {self.data_path.name}."
        )

    def _encode_query(self, query: str) -> np.ndarray:
        """Embed and L2-normalise a query (shape: 1 x dim)."""
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
        ).astype("float32")
        faiss.normalize_L2(query_embedding)
        return query_embedding

    @staticmethod
    def _format_hit(passage: dict, score: float) -> dict:
        """Standardise one retrieval hit for callers and evaluation."""
        return {
            "sample_id": passage["sample_id"],
            "title": passage["title"],
            "sent_id": passage["sent_id"],
            "sentence": passage["sentence"],
            "score": float(score),
        }

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Return the top-k passages from the shared corpus (all samples).

        Each result includes sample_id, title, sent_id, sentence, and score.
        """
        if self.index is None:
            raise RuntimeError("Index is empty. Call build_index() before retrieve().")

        query_embedding = self._encode_query(query)

        # FAISS returns (scores, indices); scores are cosine similarities in [-1, 1]
        scores, indices = self.index.search(query_embedding, top_k)

        results: list[dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                # FAISS can return -1 when fewer than top_k vectors exist
                continue
            results.append(self._format_hit(self.passages[idx], score))

        return results

    def retrieve_within_sample(
        self,
        query: str,
        sample_id: str,
        top_k: int = 5,
    ) -> list[dict]:
        """Return the top-k passages from one HotpotQA sample's context only.

        Used for primary dissertation evaluation so distractors from other
        questions cannot leak into the ranking. Shared-corpus search remains
        available via :meth:`retrieve`.
        """
        if self.embeddings is None:
            raise RuntimeError(
                "Embeddings are empty. Call build_index() before retrieve_within_sample()."
            )

        candidate_idxs = [
            i for i, passage in enumerate(self.passages) if passage["sample_id"] == sample_id
        ]
        if not candidate_idxs:
            return []

        query_embedding = self._encode_query(query)  # (1, dim)
        candidate_embeddings = self.embeddings[candidate_idxs]  # (n, dim)

        # Cosine similarity via inner product of L2-normalised vectors
        similarities = candidate_embeddings @ query_embedding.T  # (n, 1)
        similarities = similarities.ravel()

        # Rank high → low and take top_k
        ranked_local = np.argsort(-similarities)[:top_k]

        results: list[dict] = []
        for local_idx in ranked_local:
            global_idx = candidate_idxs[int(local_idx)]
            results.append(
                self._format_hit(self.passages[global_idx], similarities[local_idx])
            )

        return results


if __name__ == "__main__":
    # Small smoke test: build the index and retrieve for the first question
    retriever = Retriever()
    retriever.build_index()

    with DEFAULT_DATA_PATH.open("r", encoding="utf-8") as f:
        first = json.load(f)[0]

    hits = retriever.retrieve(first["question"], top_k=5)
    print(f"\nShared-corpus query: {first['question']}\n")
    for i, hit in enumerate(hits, start=1):
        print(f"{i}. [{hit['score']:.4f}] {hit['title']} (sent_id={hit['sent_id']})")
        print(f"   {hit['sentence']}")
        print(f"   sample_id={hit['sample_id']}\n")

    scoped = retriever.retrieve_within_sample(
        first["question"], sample_id=first["id"], top_k=5
    )
    print(f"Within-sample ({first['id']}) top hits:")
    for i, hit in enumerate(scoped, start=1):
        print(f"{i}. [{hit['score']:.4f}] {hit['title']} (sent_id={hit['sent_id']})")
