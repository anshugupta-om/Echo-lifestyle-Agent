"""
scripts/ingest_documents.py
---------------------------
Document ingestion script — loads JSON datasets and PDFs,
chunks them, and stores embeddings in ChromaDB.

Run from the project root:
    python scripts/ingest_documents.py
    python scripts/ingest_documents.py --source pdf --path datasets/my_doc.pdf
    python scripts/ingest_documents.py --reset   # Clears and re-ingests everything
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path so relative imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from rag.embeddings import get_embedding_model
from rag.vector_store import VectorStore
from utils.logger import logger
from utils.helpers import clean_text, hash_text


# ── Text chunking ────────────────────────────────────────────

def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[str]:
    """
    Split text into overlapping chunks by word count.
    Simple and fast — no tokeniser dependency.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - chunk_overlap
    return chunks


# ── JSON Dataset Ingestion ───────────────────────────────────

def ingest_json_dataset(
    json_path: Path,
    vector_store: VectorStore,
    chunk_size: int,
    chunk_overlap: int,
) -> int:
    """Ingest the eco_knowledge_base.json dataset. Returns number of chunks added."""
    logger.info(f"Ingesting JSON dataset: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    documents, metadatas, ids = [], [], []

    for record in records:
        doc_id = record.get("id", hash_text(record.get("title", "")))
        title = record.get("title", "")
        content = clean_text(record.get("content", ""))
        category = record.get("category", "general")
        source = record.get("source", "")
        tags = ", ".join(record.get("tags", []))

        # Chunk the content
        chunks = chunk_text(content, chunk_size, chunk_overlap)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            documents.append(chunk)
            metadatas.append({
                "doc_id": doc_id,
                "title": title,
                "category": category,
                "source": source,
                "tags": tags,
                "chunk_index": i,
                "total_chunks": len(chunks),
            })
            ids.append(chunk_id)

    vector_store.add_documents(documents, metadatas, ids)
    logger.info(f"Ingested {len(records)} records → {len(documents)} chunks from JSON.")
    return len(documents)


# ── PDF Ingestion ────────────────────────────────────────────

def ingest_pdf(
    pdf_path: Path,
    vector_store: VectorStore,
    chunk_size: int,
    chunk_overlap: int,
) -> int:
    """Ingest a PDF file. Returns number of chunks added."""
    try:
        from pypdf import PdfReader
    except ImportError:
        logger.error("pypdf not installed. Run: pip install pypdf")
        return 0

    logger.info(f"Ingesting PDF: {pdf_path}")
    reader = PdfReader(str(pdf_path))
    full_text = ""
    for page in reader.pages:
        full_text += (page.extract_text() or "") + "\n"

    full_text = clean_text(full_text)
    if not full_text.strip():
        logger.warning(f"No text extracted from {pdf_path}")
        return 0

    chunks = chunk_text(full_text, chunk_size, chunk_overlap)
    doc_base_id = hash_text(str(pdf_path))
    documents, metadatas, ids = [], [], []

    for i, chunk in enumerate(chunks):
        documents.append(chunk)
        metadatas.append({
            "doc_id": doc_base_id,
            "title": pdf_path.stem,
            "category": "pdf_upload",
            "source": pdf_path.name,
            "tags": "pdf",
            "chunk_index": i,
            "total_chunks": len(chunks),
        })
        ids.append(f"{doc_base_id}_chunk_{i}")

    vector_store.add_documents(documents, metadatas, ids)
    logger.info(f"Ingested PDF '{pdf_path.name}' → {len(documents)} chunks.")
    return len(documents)


# ── Text File Ingestion ──────────────────────────────────────

def ingest_text_file(
    txt_path: Path,
    vector_store: VectorStore,
    chunk_size: int,
    chunk_overlap: int,
) -> int:
    """Ingest a plain .txt file."""
    logger.info(f"Ingesting text file: {txt_path}")
    content = clean_text(txt_path.read_text(encoding="utf-8", errors="ignore"))
    if not content.strip():
        return 0

    chunks = chunk_text(content, chunk_size, chunk_overlap)
    doc_id = hash_text(str(txt_path))
    documents = chunks
    metadatas = [
        {
            "doc_id": doc_id,
            "title": txt_path.stem,
            "category": "text_upload",
            "source": txt_path.name,
            "tags": "text",
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        for i in range(len(chunks))
    ]
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

    vector_store.add_documents(documents, metadatas, ids)
    logger.info(f"Ingested '{txt_path.name}' → {len(documents)} chunks.")
    return len(documents)


# ── Main ─────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Eco Lifestyle Agent — Document Ingestion")
    parser.add_argument("--source", choices=["json", "pdf", "txt", "all"], default="all",
                        help="Source type to ingest (default: all)")
    parser.add_argument("--path", type=str, default=None,
                        help="Specific file path to ingest (optional)")
    parser.add_argument("--reset", action="store_true",
                        help="Reset the vector store before ingesting")
    parser.add_argument("--chunk-size", type=int, default=settings.chunk_size)
    parser.add_argument("--chunk-overlap", type=int, default=settings.chunk_overlap)
    args = parser.parse_args()

    logger.info("=== Eco Lifestyle Agent — Document Ingestion ===")

    # Initialise embedding model and vector store
    embedding_fn = get_embedding_model(settings)
    vector_store = VectorStore(
        persist_dir=settings.chroma_persist_path,
        collection_name=settings.chroma_collection_name,
        embedding_fn=embedding_fn,
    )

    if args.reset:
        logger.warning("Resetting vector store…")
        vector_store.delete_collection()

    total_chunks = 0

    if args.path:
        p = Path(args.path)
        if not p.exists():
            logger.error(f"File not found: {p}")
            sys.exit(1)
        ext = p.suffix.lower()
        if ext == ".json":
            total_chunks += ingest_json_dataset(p, vector_store, args.chunk_size, args.chunk_overlap)
        elif ext == ".pdf":
            total_chunks += ingest_pdf(p, vector_store, args.chunk_size, args.chunk_overlap)
        elif ext == ".txt":
            total_chunks += ingest_text_file(p, vector_store, args.chunk_size, args.chunk_overlap)
        else:
            logger.error(f"Unsupported file type: {ext}")
    else:
        datasets_dir = PROJECT_ROOT / "datasets"
        if args.source in ("json", "all"):
            for json_file in datasets_dir.glob("*.json"):
                total_chunks += ingest_json_dataset(
                    json_file, vector_store, args.chunk_size, args.chunk_overlap
                )
        if args.source in ("pdf", "all"):
            for pdf_file in datasets_dir.glob("*.pdf"):
                total_chunks += ingest_pdf(
                    pdf_file, vector_store, args.chunk_size, args.chunk_overlap
                )
        if args.source in ("txt", "all"):
            for txt_file in datasets_dir.glob("*.txt"):
                total_chunks += ingest_text_file(
                    txt_file, vector_store, args.chunk_size, args.chunk_overlap
                )

    logger.info(
        f"Ingestion complete. Total chunks added: {total_chunks}. "
        f"Vector store size: {vector_store.document_count} documents."
    )


if __name__ == "__main__":
    main()
