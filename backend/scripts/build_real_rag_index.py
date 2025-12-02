"""
Build RAG index from real documents (PDFs, text files, notices).

Usage:
1. Extract text from your PDFs/notices
2. Add them to the `documents` list below
3. Run: python -m scripts.build_real_rag_index
"""

from pathlib import Path

from app.rag import RAGEngine

# ============================================
# ADD YOUR DOCUMENTS HERE
# ============================================
# Format: (text_content, source_id)
# source_id can be any identifier like "notice_2025_01", "handbook_ch1", etc.

documents = [
    # Example 1: Notice text
    (
        "Notice: Library will be closed on March 15th for maintenance. "
        "All books due on that date will have their due date extended by one day.",
        "notice_2025_03_15"
    ),
    
    # Example 2: Campus policy
    (
        "Campus Wi-Fi Policy: Students can access Wi-Fi using their student ID. "
        "Network name: CampusWiFi. Password: student_id@campus",
        "policy_wifi"
    ),
    
    # Add more documents here...
    # (
    #     "Your document text here...",
    #     "source_identifier"
    # ),
]


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Helper function to extract text from a PDF file.
    
    Usage:
        text = extract_text_from_pdf(Path("datasets/notices/notice1.pdf"))
        documents.append((text, "notice_1"))
    """
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(str(pdf_path))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except ImportError:
        print("Error: pypdf not installed. Install it with: pip install pypdf")
        return ""
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""


def load_text_files(directory: Path) -> list[tuple[str, str]]:
    """
    Load all .txt files from a directory.
    
    Usage:
        docs = load_text_files(Path("datasets/notices"))
        documents.extend(docs)
    """
    docs = []
    if not directory.exists():
        return docs
    
    for txt_file in directory.glob("*.txt"):
        try:
            text = txt_file.read_text(encoding="utf-8")
            source_id = txt_file.stem  # filename without extension
            docs.append((text, source_id))
        except Exception as e:
            print(f"Error reading {txt_file}: {e}")
    
    return docs


def main():
    # Option 1: Load from text files in a directory
    # Uncomment and modify the path:
    # notices_dir = Path(__file__).resolve().parents[2] / "datasets" / "notices"
    # documents.extend(load_text_files(notices_dir))
    
    # Option 2: Load from PDFs
    # Uncomment and modify:
    # pdf_path = Path(__file__).resolve().parents[2] / "datasets" / "notices" / "notice1.pdf"
    # if pdf_path.exists():
    #     text = extract_text_from_pdf(pdf_path)
    #     documents.append((text, "notice_1"))
    
    if not documents:
        print("No documents found. Add documents to the 'documents' list in this script.")
        return
    
    print(f"Building RAG index from {len(documents)} documents...")
    engine = RAGEngine()
    engine.build_index(documents)
    print(f"✅ RAG index built successfully with {len(documents)} documents!")


if __name__ == "__main__":
    main()

