"""
rag/embeddings.py
-----------------
IBM Slate Embedding wrapper.
Falls back to sentence-transformers directly when IBM credentials are not
available (works with ibm_watson_machine_learning OR ibm-watsonx-ai SDK).
"""

from __future__ import annotations

from typing import List

from utils.logger import logger

# ── IBM SDK — try both new (ibm-watsonx-ai) and old (ibm_watson_machine_learning) SDKs ──
IBM_AVAILABLE = False
_ibm_sdk = None  # "new" | "old"

try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import Embeddings as WatsonxEmbeddings
    from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
    IBM_AVAILABLE = True
    _ibm_sdk = "new"
except ImportError:
    pass

if not IBM_AVAILABLE:
    try:
        from ibm_watson_machine_learning import APIClient
        from ibm_watson_machine_learning.foundation_models import Embeddings as WMLEmbeddings
        IBM_AVAILABLE = True
        _ibm_sdk = "old"
    except ImportError:
        pass

if not IBM_AVAILABLE:
    logger.warning("No IBM SDK found — will use local sentence-transformers embeddings.")

# ── HuggingFace / sentence-transformers fallback ──────────────────────────────
HF_AVAILABLE = False
try:
    # Try langchain-community wrapper first
    from langchain_community.embeddings import HuggingFaceEmbeddings as _HFEmb
    HF_AVAILABLE = True
    _hf_backend = "langchain"
except ImportError:
    try:
        # Fall back to sentence-transformers directly
        from sentence_transformers import SentenceTransformer as _ST
        HF_AVAILABLE = True
        _hf_backend = "sentence_transformers"
    except ImportError:
        _hf_backend = None


class IBMSlateEmbeddings:
    """
    Wrapper around IBM watsonx.ai Slate embedding model.
    Supports both ibm-watsonx-ai (new) and ibm_watson_machine_learning (old) SDKs.
    """

    def __init__(
        self,
        api_key: str,
        url: str,
        project_id: str,
        model_id: str = "ibm/slate-125m-english-rtrvr-v2",
    ) -> None:
        if not IBM_AVAILABLE:
            raise RuntimeError("No IBM SDK found. Install ibm-watsonx-ai or ibm_watson_machine_learning.")
        self.model_id = model_id

        if _ibm_sdk == "new":
            credentials = Credentials(url=url, api_key=api_key)
            embed_params = {
                EmbedParams.TRUNCATE_INPUT_TOKENS: 512,
                EmbedParams.RETURN_OPTIONS: {"input_text": False},
            }
            self._model = WatsonxEmbeddings(
                model_id=model_id,
                credentials=credentials,
                project_id=project_id,
                params=embed_params,
            )
            self._sdk = "new"
        else:
            # Old SDK: ibm_watson_machine_learning
            wml_credentials = {"url": url, "apikey": api_key}
            client = APIClient(wml_credentials)
            client.set.default_project(project_id)
            self._client = client
            self._wml_model_id = model_id
            self._sdk = "old"

        logger.info(f"IBM Slate embeddings initialised (sdk={self._sdk}): {model_id}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        logger.debug(f"Embedding {len(texts)} document(s) with IBM Slate")
        if self._sdk == "new":
            return self._model.embed_documents(texts)
        # Old SDK: call generate_embeddings in batches of 10
        results = []
        for i in range(0, len(texts), 10):
            batch = texts[i:i + 10]
            resp = WMLEmbeddings(
                model_id=self._wml_model_id,
                api_client=self._client,
            ).generate(inputs=batch)
            for item in resp["results"]:
                results.append(item["embedding"])
        return results

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


class LocalEmbeddings:
    """
    Fallback embedding model using sentence-transformers directly.
    No API key required — CPU-friendly, ~90MB download on first use.
    Works with sentence-transformers>=2.0 regardless of langchain-community.
    """

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self) -> None:
        if not HF_AVAILABLE:
            raise RuntimeError(
                "sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            )
        if _hf_backend == "langchain":
            self._model = _HFEmb(
                model_name=self.MODEL_NAME,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
            self._backend = "langchain"
        else:
            # Direct sentence-transformers usage
            self._st = _ST(self.MODEL_NAME)
            self._backend = "sentence_transformers"
        logger.info(f"Local embeddings initialised (backend={self._backend}): {self.MODEL_NAME}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self._backend == "langchain":
            return self._model.embed_documents(texts)
        vecs = self._st.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [v.tolist() for v in vecs]

    def embed_query(self, text: str) -> List[float]:
        if self._backend == "langchain":
            return self._model.embed_query(text)
        vec = self._st.encode([text], normalize_embeddings=True, show_progress_bar=False)
        return vec[0].tolist()


def get_embedding_model(settings=None):
    """
    Factory — returns IBM Slate embeddings if credentials are available,
    otherwise falls back to local HuggingFace embeddings.
    """
    if settings is None:
        from config.settings import settings as _settings
        settings = _settings

    try:
        if not settings.ibm_api_key or settings.ibm_api_key == "your_ibm_cloud_api_key_here":
            raise ValueError("IBM API key not configured")
        model = IBMSlateEmbeddings(
            api_key=settings.ibm_api_key,
            url=settings.ibm_watsonx_url,
            project_id=settings.ibm_project_id,
            model_id=settings.granite_embed_model,
        )
        logger.info("Using IBM Slate embedding model")
        return model
    except Exception as exc:
        logger.warning(f"IBM embeddings unavailable ({exc}). Falling back to local model.")
        return LocalEmbeddings()
