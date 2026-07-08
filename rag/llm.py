"""
rag/llm.py
----------
IBM Granite LLM wrapper.
Falls back to a stub (echo) response when IBM credentials are absent — useful
for UI development and testing without an active IBM Cloud account.
"""

from __future__ import annotations

from typing import Generator

from utils.logger import logger

# ── Try new SDK first, then old SDK ──────────────────────────
IBM_AVAILABLE = False
_llm_sdk = None

try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    IBM_AVAILABLE = True
    _llm_sdk = "new"
except ImportError:
    pass

if not IBM_AVAILABLE:
    try:
        from ibm_watson_machine_learning import APIClient as _WMLClient
        from ibm_watson_machine_learning.foundation_models import Model as _WMLModel
        from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
        IBM_AVAILABLE = True
        _llm_sdk = "old"
    except ImportError:
        pass

if not IBM_AVAILABLE:
    logger.warning("No IBM SDK found — LLM will use stub responses.")


# ── Chat-format prompt builder ────────────────────────────────
def _build_chat_prompt(model_id: str, system: str, user: str) -> str:
    """
    Build the correct chat-token prompt for the given model family.

    - Granite chat models:  <|system|> / <|user|> / <|assistant|>
    - Llama-3 instruct:     <|begin_of_text|><|start_header_id|>…
    - Fallback (base/unknown models): plain text concatenation
    """
    mid = model_id.lower()
    if "llama" in mid:
        return (
            "<|begin_of_text|>"
            "<|start_header_id|>system<|end_header_id|>\n\n"
            f"{system}<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\n"
            f"{user}<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )
    elif "granite" in mid and ("chat" in mid or "instruct" in mid):
        return (
            f"<|system|>\n{system}\n"
            f"<|user|>\n{user}\n"
            f"<|assistant|>\n"
        )
    else:
        # Base models: plain text (no special tokens)
        return f"System: {system}\n\nUser: {user}\n\nAssistant:"


class GraniteLLM:
    """
    Wrapper around IBM Granite language models.
    Supports ibm-watsonx-ai (new) and ibm_watson_machine_learning (old) SDKs.
    Always wraps prompts in Granite chat tokens to prevent prompt-leakage.
    """

    def __init__(
        self,
        api_key: str,
        url: str,
        project_id: str,
        model_id: str = "ibm/granite-13b-chat-v2",
        max_new_tokens: int = 1024,
        temperature: float = 0.3,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
    ) -> None:
        if not IBM_AVAILABLE:
            raise RuntimeError("No IBM SDK found. Install ibm-watsonx-ai.")

        self.model_id = model_id
        self._sdk = _llm_sdk

        gen_params = {
            GenParams.MAX_NEW_TOKENS: max_new_tokens,
            GenParams.TEMPERATURE: temperature,
            GenParams.TOP_P: top_p,
            GenParams.REPETITION_PENALTY: repetition_penalty,
            GenParams.STOP_SEQUENCES: ["<|user|>", "<|system|>", "<|endoftext|>"],
        }

        if self._sdk == "new":
            credentials = Credentials(url=url, api_key=api_key)
            self._model = ModelInference(
                model_id=model_id,
                credentials=credentials,
                project_id=project_id,
                params=gen_params,
            )
        else:
            # Old WML SDK
            wml_creds = {"url": url, "apikey": api_key}
            client = _WMLClient(wml_creds)
            client.set.default_project(project_id)
            self._model = _WMLModel(
                model_id=model_id,
                params=gen_params,
                api_client=client,
            )

        logger.info(f"Granite LLM initialised (sdk={self._sdk}): {model_id}")

    def generate(self, system: str, user: str) -> str:
        """Generate a response given separate system and user strings."""
        prompt = _build_chat_prompt(self.model_id, system, user)
        logger.debug(f"Prompt length: {len(prompt)} chars for model {self.model_id}")
        try:
            response = self._model.generate_text(prompt=prompt)
            return response.strip()
        except Exception as exc:
            logger.error(f"LLM generate error: {exc}")
            raise

    def stream(self, system: str, user: str) -> Generator[str, None, None]:
        """Stream tokens given separate system and user strings."""
        prompt = _build_chat_prompt(self.model_id, system, user)
        try:
            for chunk in self._model.generate_text_stream(prompt=prompt):
                yield chunk
        except Exception as exc:
            logger.error(f"LLM stream error: {exc}")
            raise


class StubLLM:
    """
    Deterministic stub LLM for offline/test use.
    Signature matches GraniteLLM: generate(system, user).
    """

    def generate(self, system: str, user: str) -> str:
        return (
            "🌿 **[Demo Mode — IBM credentials not configured]**\n\n"
            "This is a placeholder response. To get real AI-powered eco advice, "
            "please add your IBM Cloud API key and watsonx Project ID to the `.env` file "
            "and restart the application.\n\n"
            "Once configured, I'll answer your sustainability questions using IBM Granite "
            "and a curated environmental knowledge base.\n\n"
            "*Configure your credentials in `.env` to unlock full functionality.*"
        )

    def stream(self, system: str, user: str) -> Generator[str, None, None]:
        for word in self.generate(system, user).split(" "):
            yield word + " "


def get_llm(settings=None):
    """
    Factory — returns GraniteLLM if IBM credentials are configured,
    otherwise returns StubLLM.
    """
    if settings is None:
        from config.settings import settings as _s
        settings = _s

    try:
        if not settings.ibm_api_key or settings.ibm_api_key == "your_ibm_cloud_api_key_here":
            raise ValueError("IBM API key not set")
        llm = GraniteLLM(
            api_key=settings.ibm_api_key,
            url=settings.ibm_watsonx_url,
            project_id=settings.ibm_project_id,
            model_id=settings.granite_llm_model,
            max_new_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )
        logger.info("Using IBM Granite LLM")
        return llm
    except Exception as exc:
        logger.warning(f"IBM LLM unavailable ({exc}). Using stub LLM.")
        return StubLLM()
