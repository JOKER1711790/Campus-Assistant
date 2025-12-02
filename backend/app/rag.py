"""
Very small RAG (Retrieval-Augmented Generation) skeleton.

For the MVP we:
- Build a FAISS index over campus documents (once, at startup or via a script)
- Expose a simple `retrieve_relevant_chunks` function for the chatbot

You can later plug in an actual LLM (OpenAI, local, etc.) in `generate_answer`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import faiss  # type: ignore
import numpy as np
from sentence_transformers import SentenceTransformer

from .config import get_settings


settings = get_settings()


@dataclass
class RetrievedChunk:
    text: str
    score: float
    source: str


class RAGEngine:
    """
    Minimal in-process RAG engine.

    This keeps everything on disk in the `embedding_cache_dir`:
    - `index.faiss` – FAISS index
    - `texts.txt` – newline-separated text chunks
    - `sources.txt` – matching source identifiers per line
    """

    def __init__(self) -> None:
        self.model = SentenceTransformer(
            settings.embedding_model_name,
            cache_folder=settings.embedding_cache_dir,
        )
        self.index_dir = Path(settings.embedding_cache_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.index_path = self.index_dir / "index.faiss"
        self.texts_path = self.index_dir / "texts.txt"
        self.sources_path = self.index_dir / "sources.txt"

        self.index: faiss.Index | None = None
        self.texts: list[str] = []
        self.sources: list[str] = []

        if self.index_path.exists():
            self._load_index()

    def _load_index(self) -> None:
        self.index = faiss.read_index(str(self.index_path))
        if self.texts_path.exists():
            self.texts = self.texts_path.read_text(encoding="utf-8").splitlines()
        if self.sources_path.exists():
            self.sources = self.sources_path.read_text(encoding="utf-8").splitlines()

    def build_index(self, documents: list[tuple[str, str]]) -> None:
        """
        Build a FAISS index from a list of (text, source_id) tuples.

        Intended to be called from an offline script (not on every request).
        """

        if not documents:
            raise ValueError("No documents provided for indexing.")

        texts, sources = zip(*documents)
        embeddings = self.model.encode(
            list(texts), show_progress_bar=True, convert_to_numpy=True
        )

        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings.astype(np.float32))

        # Persist to disk
        faiss.write_index(index, str(self.index_path))
        self.texts_path.write_text("\n".join(texts), encoding="utf-8")
        self.sources_path.write_text("\n".join(sources), encoding="utf-8")

        self.index = index
        self.texts = list(texts)
        self.sources = list(sources)

    def retrieve_relevant_chunks(
        self, query: str, top_k: int = 5
    ) -> List[RetrievedChunk]:
        if self.index is None:
            # No index yet – return empty list instead of failing the whole request
            return []

        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(
            query_embedding.astype(np.float32), top_k
        )

        results: list[RetrievedChunk] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.texts):
                continue
            results.append(
                RetrievedChunk(
                    text=self.texts[idx],
                    score=float(dist),
                    source=self.sources[idx] if idx < len(self.sources) else "",
                )
            )
        return results


rag_engine = RAGEngine()


def generate_answer(query: str) -> str:
    """
    Concise answer generator - returns only the most relevant information.
    """

    chunks = rag_engine.retrieve_relevant_chunks(query, top_k=3)
    if not chunks:
        return "I don't have enough information to answer this. Please check the campus portal."

    # Take only the top result for efficiency
    top_chunk = chunks[0].text
    
    # Extract clean answer from FAQ format
    if "FAQ:" in top_chunk and "Answer:" in top_chunk:
        parts = top_chunk.split("Answer:", 1)
        if len(parts) == 2:
            answer = parts[1].strip()
            return answer
    
    # Extract clean answer from Event format
    if "Event:" in top_chunk and "Description:" in top_chunk:
        parts = top_chunk.split("Description:", 1)
        if len(parts) == 2:
            title = parts[0].replace("Event:", "").strip()
            desc = parts[1].strip()
            return f"{title}: {desc}"
    
    # Clean up and return the most relevant part
    cleaned = top_chunk.replace("FAQ:", "").replace("Event:", "").replace("Description:", "").replace("Answer:", "").strip()
    # Take first sentence or first 150 chars
    if "." in cleaned:
        return cleaned.split(".")[0] + "."
    return cleaned[:150] + ("..." if len(cleaned) > 150 else "")



