"""
rag/pipeline.py
---------------
End-to-end RAG pipeline:
  1. Receive user question + conversation history
  2. Retrieve relevant chunks from ChromaDB
  3. Build system prompt + user message (SEPARATE — required by Granite chat format)
  4. Call IBM Granite LLM via _build_granite_chat_prompt()
  5. Return response + sources + metadata
"""

from __future__ import annotations

from typing import Any

from prompts.agent_instructions import (
    AGENT_NAME,
    AGENT_TAGLINE,
    RESPONSE_TONE,
    RESPONSE_LENGTH,
    USE_MARKDOWN,
    SAFETY_GUIDELINES,
    SUPPORTED_LANGUAGES,
    CITATION_PREFIX,
    ALWAYS_CITE,
)
from utils.logger import logger
from utils.helpers import build_user_context_string


# ── System prompt (injected into <|system|> token) ────────────
_SYSTEM_TEMPLATE = """\
You are {agent_name}, {agent_tagline}.

You are a world-class sustainability expert specialising in eco-friendly living, \
waste management, renewable energy, water conservation, sustainable transport, \
carbon footprint reduction, and India's environmental policies and government schemes.

TONE: Be {tone} and solution-focused.
RESPONSE LENGTH: {response_length} responses.
FORMATTING: {markdown_instruction}
LANGUAGE: Respond in the same language the user writes in. Supported: {languages}.

SAFETY RULES:
{safety_guidelines}

KNOWLEDGE BASE CONTEXT:
Use ONLY the following retrieved context to answer. If the context lacks \
sufficient detail, say so briefly and give general sustainability guidance.

{context}

CITATIONS: {citation_instruction}"""

# ── Fallback system prompt (no context retrieved) ─────────────
_FALLBACK_SYSTEM = """\
You are {agent_name}, {agent_tagline}.

You are a sustainability expert. Answer based on well-established environmental \
science. Be honest that your answer is general knowledge, not from a specific \
knowledge base.

SAFETY RULES:
{safety_guidelines}"""


def _markdown_instruction() -> str:
    if USE_MARKDOWN:
        return "Use markdown: **bold**, bullet lists, ### headers."
    return "Plain text only — no markdown."


def _citation_instruction() -> str:
    if ALWAYS_CITE:
        return f"End your answer with a '{CITATION_PREFIX}:' list of the sources you used."
    return "Include sources only when asked."


class RAGPipeline:
    """
    Orchestrates the full RAG flow: retrieve → prompt → generate → respond.
    Prompts are split into system / user parts so GraniteLLM can wrap them
    in the required <|system|>…<|user|>…<|assistant|> chat tokens.
    """

    def __init__(self, retriever, llm) -> None:
        self.retriever = retriever
        self.llm = llm

    # ── Public API ───────────────────────────────────────────

    def query(
        self,
        question: str,
        conversation_history: list[dict] | None = None,
        user_preferences: dict[str, Any] | None = None,
        filter_category: str | None = None,
    ) -> dict[str, Any]:
        """
        Run the complete RAG pipeline for a single user question.

        Returns:
            {
              "answer": str,
              "sources": list[str],
              "retrieved_chunks": int,
              "retrieval_scores": list[float],
              "prompt_tokens_estimate": int,
            }
        """
        logger.info(f"RAG query: {question[:80]!r}")

        # 1. Retrieve
        context, sources, results = self.retriever.retrieve_and_format(
            query=question,
            filter_category=filter_category,
        )
        retrieved_count = len(results)
        scores = [r.get("relevance_score", 0) for r in results]

        # 2. Build system and user strings separately
        system, user = self._build_system_user(
            question=question,
            context=context,
            retrieved_count=retrieved_count,
            conversation_history=conversation_history or [],
            user_preferences=user_preferences or {},
        )

        # 3. Generate (LLM handles Granite chat token wrapping)
        answer = self.llm.generate(system, user)

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": retrieved_count,
            "retrieval_scores": scores,
            "prompt_tokens_estimate": (len(system) + len(user)) // 4,
        }

    def stream_query(
        self,
        question: str,
        conversation_history: list[dict] | None = None,
        user_preferences: dict[str, Any] | None = None,
    ):
        """Streaming version — yields text tokens, then a metadata dict."""
        context, sources, results = self.retriever.retrieve_and_format(question)
        system, user = self._build_system_user(
            question=question,
            context=context,
            retrieved_count=len(results),
            conversation_history=conversation_history or [],
            user_preferences=user_preferences or {},
        )
        for token in self.llm.stream(system, user):
            yield token
        yield {"__meta__": True, "sources": sources, "retrieved_chunks": len(results)}

    # ── Private helpers ──────────────────────────────────────

    def _build_system_user(
        self,
        question: str,
        context: str,
        retrieved_count: int,
        conversation_history: list[dict],
        user_preferences: dict,
    ) -> tuple[str, str]:
        """
        Returns (system_prompt, user_message) as separate strings.
        The LLM wraps these in Granite's <|system|>/<|user|>/<|assistant|> tokens.
        """
        profile_str = build_user_context_string(user_preferences)
        history_str = self._format_history(conversation_history)

        # ── System string ─────────────────────────────────────
        if retrieved_count > 0:
            system = _SYSTEM_TEMPLATE.format(
                agent_name=AGENT_NAME,
                agent_tagline=AGENT_TAGLINE,
                tone=RESPONSE_TONE,
                response_length=RESPONSE_LENGTH,
                markdown_instruction=_markdown_instruction(),
                languages=", ".join(SUPPORTED_LANGUAGES),
                safety_guidelines=SAFETY_GUIDELINES.strip(),
                context=context,
                citation_instruction=_citation_instruction(),
            )
        else:
            system = _FALLBACK_SYSTEM.format(
                agent_name=AGENT_NAME,
                agent_tagline=AGENT_TAGLINE,
                safety_guidelines=SAFETY_GUIDELINES.strip(),
            )

        # ── User message ──────────────────────────────────────
        parts = []
        if history_str:
            parts.append(f"Conversation so far:\n{history_str}\n")
        if profile_str:
            parts.append(profile_str)
        parts.append(question)
        user = "\n".join(parts)

        return system, user

    @staticmethod
    def _format_history(history: list[dict]) -> str:
        """Format last 6 turns of conversation history into a compact string."""
        if not history:
            return ""
        lines = []
        for turn in history[-6:]:
            role = turn.get("role", "user").capitalize()
            content = turn.get("content", "")[:400]
            lines.append(f"{role}: {content}")
        return "\n".join(lines)


# ── Singleton factory ────────────────────────────────────────

_pipeline_instance: RAGPipeline | None = None


def get_pipeline(settings=None) -> RAGPipeline:
    """Return a module-level RAGPipeline singleton."""
    global _pipeline_instance
    if _pipeline_instance is not None:
        return _pipeline_instance

    from rag.retriever import get_retriever
    from rag.llm import get_llm
    retriever = get_retriever(settings)
    llm = get_llm(settings)
    _pipeline_instance = RAGPipeline(retriever=retriever, llm=llm)
    logger.info("RAG pipeline initialised")
    return _pipeline_instance
