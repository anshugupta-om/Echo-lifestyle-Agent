"""
config/settings.py
------------------
Centralised application settings loaded from environment variables via
pydantic-settings.  Import `settings` anywhere in the project.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root (one level above this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """All configuration values with sensible defaults."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── IBM watsonx.ai ─────────────────────────────────────
    # Default to empty string so the app starts in local/demo mode when
    # credentials are absent; get_embedding_model() and get_llm() check
    # for empty / placeholder values and fall back gracefully.
    ibm_api_key: str = Field("", alias="IBM_API_KEY")
    ibm_watsonx_url: str = Field(
        "https://us-south.ml.cloud.ibm.com", alias="IBM_WATSONX_URL"
    )
    ibm_project_id: str = Field("", alias="IBM_PROJECT_ID")

    # ── IBM Granite Model IDs ───────────────────────────────
    granite_llm_model: str = Field(
        "ibm/granite-13b-chat-v2", alias="GRANITE_LLM_MODEL"
    )
    granite_embed_model: str = Field(
        "ibm/slate-125m-english-rtrvr", alias="GRANITE_EMBED_MODEL"
    )

    # ── FastAPI Backend ─────────────────────────────────────
    backend_host: str = Field("0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(8000, alias="BACKEND_PORT")
    backend_reload: bool = Field(False, alias="BACKEND_RELOAD")

    # ── ChromaDB ────────────────────────────────────────────
    chroma_persist_dir: str = Field(
        "./vectordb/chroma_store", alias="CHROMA_PERSIST_DIR"
    )
    chroma_collection_name: str = Field(
        "eco_knowledge_base", alias="CHROMA_COLLECTION_NAME"
    )

    # ── RAG Pipeline ────────────────────────────────────────
    chunk_size: int = Field(512, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(64, alias="CHUNK_OVERLAP")
    top_k_results: int = Field(5, alias="TOP_K_RESULTS")
    max_tokens: int = Field(1024, alias="MAX_TOKENS")
    temperature: float = Field(0.3, alias="TEMPERATURE")

    # ── App Settings ────────────────────────────────────────
    app_env: str = Field("development", alias="APP_ENV")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    secret_key: str = Field("change_me", alias="SECRET_KEY")

    # ── Derived helpers (not from env) ──────────────────────
    @property
    def chroma_persist_path(self) -> Path:
        p = Path(self.chroma_persist_dir)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        return p

    @property
    def datasets_dir(self) -> Path:
        return PROJECT_ROOT / "datasets"

    @property
    def logs_dir(self) -> Path:
        return PROJECT_ROOT / "logs"

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()


# Convenience alias
settings = get_settings()
