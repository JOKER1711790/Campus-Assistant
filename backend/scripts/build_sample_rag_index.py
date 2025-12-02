"""
Build a tiny RAG index from the existing sample datasets.

This script:
- Reads FAQs and event descriptions.
- Builds embeddings and writes a FAISS index into the cache directory.

Run from the `backend` directory:

    python -m scripts.build_sample_rag_index
"""

from pathlib import Path

from app.rag import RAGEngine

ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "datasets"


def load_documents() -> list[tuple[str, str]]:
    documents: list[tuple[str, str]] = []

    faqs_path = DATASETS_DIR / "faqs.csv"
    events_path = DATASETS_DIR / "events.csv"

    if faqs_path.exists():
        import csv

        with faqs_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                text = f"FAQ: {row['question']} Answer: {row['answer']}"
                documents.append((text, f"faq_{i}"))

    if events_path.exists():
        import csv

        with events_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                text = f"Event: {row['title']} Description: {row.get('description','')}"
                documents.append((text, f"event_{i}"))

    return documents


def main():
    docs = load_documents()
    if not docs:
        print("No documents found to index.")
        return

    engine = RAGEngine()
    engine.build_index(docs)
    print(f"Built RAG index over {len(docs)} documents.")


if __name__ == "__main__":
    main()



