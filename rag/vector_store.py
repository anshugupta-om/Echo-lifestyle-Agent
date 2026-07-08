"""
rag/vector_store.py
-------------------
ChromaDB vector store management — initialisation, document upsert, and
semantic similarity search used by the RAG retriever.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from utils.logger import logger


class VectorStore:
    """
    Thin wrapper around ChromaDB that provides:
    - Persistent on-disk storage
    - Document upsert with metadata
    - Semantic similarity search via pre-computed embeddings
    """

    def __init__(
        self,
        persist_dir: str | Path,
        collection_name: str,
        embedding_fn: Any,
    ) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_fn = embedding_fn

        self._client = chromadb.PersistentClient(
            path=str(self.persist_dir),
        )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"ChromaDB collection '{collection_name}' loaded — "
            f"{self._collection.count()} documents."
        )

    # ── Properties ───────────────────────────────────────────

    @property
    def document_count(self) -> int:
        return self._collection.count()

    # ── Write Operations ─────────────────────────────────────

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str],
    ) -> None:
        """
        Embed documents and upsert into the collection.
        Uses upsert so re-running ingestion is idempotent.
        """
        if not documents:
            logger.warning("add_documents called with empty list — skipping.")
            return

        logger.info(f"Embedding and upserting {len(documents)} document(s)…")
        embeddings = self.embedding_fn.embed_documents(documents)

        self._collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info(
            f"Upsert complete. Collection now has {self._collection.count()} documents."
        )

    # ── Read Operations ──────────────────────────────────────

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[dict]:
        """
        Perform semantic similarity search.

        Returns a list of dicts:
          { "document": str, "metadata": dict, "distance": float }
        sorted by relevance (lowest distance first).
        """
        query_embedding = self.embedding_fn.embed_query(query)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, max(self._collection.count(), 1)),
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            hits.append({"document": doc, "metadata": meta, "distance": dist})

        logger.debug(f"similarity_search returned {len(hits)} results for query snippet: {query[:60]!r}")
        return hits

    def delete_collection(self) -> None:
        """Delete and recreate the collection (full reset)."""
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.warning(f"Collection '{self.collection_name}' has been reset.")


# ── Singleton factory ─────────────────────────────────────────

_vector_store_instance: VectorStore | None = None


def get_vector_store(settings=None, embedding_fn=None) -> VectorStore:
    """
    Return a module-level singleton VectorStore.
    Safe to call multiple times — returns the same instance.
    """
    global _vector_store_instance
    if _vector_store_instance is not None:
        return _vector_store_instance

    if settings is None:
        from config.settings import settings as _s
        settings = _s
    if embedding_fn is None:
        from rag.embeddings import get_embedding_model
        embedding_fn = get_embedding_model(settings)

    _vector_store_instance = VectorStore(
        persist_dir=settings.chroma_persist_path,
        collection_name=settings.chroma_collection_name,
        embedding_fn=embedding_fn,
    )
    return _vector_store_instance
