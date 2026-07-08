"""
rag/retriever.py
----------------
Retrieval logic — given a user query and optional metadata filter, fetches
the most relevant document chunks from ChromaDB and formats them as context
for the LLM prompt.
"""

from __future__ import annotations

from typing import Any

from utils.logger import logger
from utils.helpers import clean_text, format_source_citation
from prompts.agent_instructions import CITATION_PREFIX


# Avoid circular import at module level
def _top_k():
    try:
        from config.settings import settings
        return settings.top_k_results
    except Exception:
        return 5


class EcoRetriever:
    """
    Retrieves relevant document chunks from the vector store
    and formats them as an LLM context block.
    """

    def __init__(self, vector_store, top_k: int | None = None) -> None:
        self.vector_store = vector_store
        self.top_k = top_k or _top_k()

    def retrieve(
        self,
        query: str,
        filter_category: str | None = None,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve top-k relevant chunks for `query`.

        Args:
            query: The user's natural language question.
            filter_category: Optional ChromaDB metadata filter by category.
            top_k: Override default top_k.

        Returns:
            List of result dicts with keys: document, metadata, distance, relevance_score.
        """
        k = top_k or self.top_k
        meta_filter = {"category": filter_category} if filter_category else None

        results = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter_metadata=meta_filter,
        )

        # Convert cosine distance → similarity score (0–1, higher is better)
        for r in results:
            r["relevance_score"] = round(1.0 - r["distance"], 4)

        # Sort by relevance (highest first)
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        logger.debug(
            f"Retrieved {len(results)} chunks; "
            f"top score={results[0]['relevance_score'] if results else 'N/A'}"
        )
        return results

    def format_context(self, results: list[dict[str, Any]]) -> str:
        """
        Format retrieved results into a single context string for the LLM.
        Each chunk includes its title, category, content, and source.
        """
        if not results:
            return "No relevant context found."

        parts = []
        for i, r in enumerate(results, start=1):
            meta = r.get("metadata", {})
            title = meta.get("title", "Unknown")
            source = meta.get("source", "")
            category = meta.get("category", "")
            content = clean_text(r.get("document", ""))
            score = r.get("relevance_score", 0)

            block = (
                f"[{i}] **{title}** (Category: {category} | Relevance: {score:.2f})\n"
                f"{content}\n"
                f"Source: {source}"
            )
            parts.append(block)

        return "\n\n---\n\n".join(parts)

    def get_sources(self, results: list[dict[str, Any]]) -> list[str]:
        """Extract formatted source citations from results."""
        citations = []
        seen = set()
        for r in results:
            meta = r.get("metadata", {})
            source = meta.get("source", "")
            title = meta.get("title", "")
            if source and source not in seen:
                seen.add(source)
                citations.append(format_source_citation(source, title, CITATION_PREFIX))
        return citations

    def retrieve_and_format(
        self,
        query: str,
        filter_category: str | None = None,
    ) -> tuple[str, list[str], list[dict]]:
        """
        Convenience method: retrieve + format context + extract sources.

        Returns:
            (context_string, source_citations, raw_results)
        """
        results = self.retrieve(query, filter_category=filter_category)
        context = self.format_context(results)
        sources = self.get_sources(results)
        return context, sources, results


# ── Singleton factory ────────────────────────────────────────

_retriever_instance: EcoRetriever | None = None


def get_retriever(settings=None) -> EcoRetriever:
    """Return a module-level EcoRetriever singleton."""
    global _retriever_instance
    if _retriever_instance is not None:
        return _retriever_instance

    from rag.vector_store import get_vector_store
    vs = get_vector_store(settings)
    _retriever_instance = EcoRetriever(vector_store=vs)
    return _retriever_instance
