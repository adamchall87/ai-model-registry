"""
AI Model Registry — Pollers for OpenRouter, HuggingFace, Ollama Cloud.
Each poller fetches the provider's model list and normalizes to a common schema.
Covers ALL GenAI modalities: LLMs, image gen, video gen, audio/TTS, vision, multimodal.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(val: Any) -> float | None:
    try:
        if val is None:
            return None
        return float(val)
    except (TypeError, ValueError):
        return None


def _safe_int(val: Any) -> int | None:
    try:
        if val is None:
            return None
        return int(val)
    except (TypeError, ValueError):
        return None


# Modality classification — maps pipeline_tag/source to our unified modality field
MODALITY_MAP = {
    "text-generation": "llm",
    "text2text-generation": "llm",
    "image-text-to-text": "llm",
    "text-to-image": "image",
    "text-to-video": "video",
    "image-to-video": "video",
    "text-to-speech": "audio",
    "automatic-speech-recognition": "audio",
    "image-to-text": "vision",
    "object-detection": "vision",
    "image-classification": "vision",
    "text-to-3d": "3d",
    "image-to-3d": "3d",
}

def _classify_modality(pipeline_tag: str, tags: list = None) -> str:
    """Classify a model into a modality category."""
    if pipeline_tag in MODALITY_MAP:
        return MODALITY_MAP[pipeline_tag]
    tag_str = " ".join(tags or []).lower()
    if any(k in tag_str for k in ["text-to-image", "stable-diffusion", "flux", "imagen"]):
        return "image"
    if any(k in tag_str for k in ["text-to-video", "video-generation"]):
        return "video"
    if any(k in tag_str for k in ["text-to-speech", "tts", "musicgen", "audiogen"]):
        return "audio"
    if any(k in tag_str for k in ["whisper", "asr", "speech-recognition"]):
        return "audio"
    if any(k in tag_str for k in ["vision", "vlm", "image-text"]):
        return "vision"
    return "llm"  # default


# ── OpenRouter (LLMs only, but includes vision/tool models) ──────────────

OPENROUTER_URL = "https://openrouter.ai/api/v1/models"

async def poll_openrouter(client: httpx.AsyncClient) -> list[dict]:
    """Poll OpenRouter's public model list. No auth required."""
    try:
        resp = await client.get(OPENROUTER_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            raw_models = data
        else:
            raw_models = data.get("data", [])
        models = []
        for m in raw_models:
            pricing = m.get("pricing", {})
            arch = m.get("architecture", {})
            sp = m.get("supported_parameters", [])
            if isinstance(sp, dict):
                supports_tools = sp.get("tools", False) or "tool_use" in str(sp)
                supports_streaming = sp.get("stream", True) if "stream" in str(sp) else True
                supports_thinking = "reasoning" in str(sp)
            else:
                sp_str = str(sp)
                supports_tools = "tools" in sp_str or "tool_use" in sp_str
                supports_streaming = "stream" in sp_str
                supports_thinking = "reasoning" in sp_str
            # Detect vision from modality field
            modality_str = str(arch.get("modality", "text")).lower()
            has_vision = "image" in modality_str or "vision" in modality_str
            models.append({
                "id": m.get("id", ""),
                "name": m.get("name", m.get("id", "")),
                "provider_source": "openrouter",
                "modality": "llm",
                "description": m.get("description", ""),
                "context_length": _safe_int(m.get("context_length")),
                "input_price_per_1m": _safe_float(pricing.get("prompt")),
                "output_price_per_1m": _safe_float(pricing.get("completion")),
                "cached_price_per_1m": _safe_float(pricing.get("prompt_cache", pricing.get("image"))),
                "input_modalities": arch.get("input_modalities", ["text"]),
                "output_modalities": arch.get("output_modalities", ["text"]),
                "supports_tools": supports_tools,
                "supports_streaming": supports_streaming,
                "supports_thinking": supports_thinking,
                "supports_vision": has_vision,
                "is_free": _safe_float(pricing.get("prompt")) == 0 and _safe_float(pricing.get("completion")) == 0,
                "architecture": {
                    "family": arch.get("tokenizer", ""),
                    "parameters": arch.get("parameters", ""),
                    "modality": arch.get("modality", "text"),
                },
                "raw_id": m.get("id", ""),
                "polled_at": _now_iso(),
            })
        logger.info(f"OpenRouter: fetched {len(models)} models")
        return models
    except Exception as e:
        logger.error(f"OpenRouter poll failed: {e}")
        return []


# ── HuggingFace (ALL modalities) ────────────────────────────────────────

HF_MODELS_URL = "https://huggingface.co/api/models"

# Pipeline tags for all GenAI modalities
HF_PIPELINE_FILTERS = {
    "llm": "text-generation,text2text-generation,image-text-to-text",
    "image": "text-to-image,diffusers",
    "video": "text-to-video,image-to-video",
    "audio_tts": "text-to-speech",
    "audio_asr": "automatic-speech-recognition",
    "vision": "image-to-text,image-classification,object-detection",
    "3d": "text-to-3d,image-to-3d",
}

async def poll_huggingface(client: httpx.AsyncClient) -> list[dict]:
    """Poll HuggingFace Hub models API across ALL modalities. No auth required."""
    models = []

    for modality, filter_str in HF_PIPELINE_FILTERS.items():
        try:
            resp = await client.get(
                HF_MODELS_URL,
                params={
                    "filter": filter_str,
                    "sort": "downloads",
                    "direction": "-1",
                    "limit": 100,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            for m in data:
                mid = m.get("id", m.get("modelId", ""))
                tags = m.get("tags", [])
                pipeline_tag = m.get("pipeline_tag", "")
                models.append({
                    "id": mid,
                    "name": mid.split("/")[-1],
                    "provider_source": "huggingface",
                    "modality": _classify_modality(pipeline_tag, tags),
                    "description": "",
                    "downloads": _safe_int(m.get("downloads")),
                    "likes": _safe_int(m.get("likes")),
                    "pipeline_tag": pipeline_tag,
                    "tags": tags,
                    "last_modified": m.get("lastModified", ""),
                    "library_name": m.get("library_name", ""),
                    "context_length": None,
                    "input_price_per_1m": None,
                    "output_price_per_1m": None,
                    "supports_vision": modality == "vision" or "vision" in str(tags).lower() or "image" in str(tags).lower(),
                    "is_free": True,
                    "local_capable": True,
                    "raw_id": mid,
                    "polled_at": _now_iso(),
                })
            logger.info(f"HuggingFace {modality}: fetched {len(data)} models")
        except Exception as e:
            logger.error(f"HuggingFace {modality} poll failed: {e}")

    logger.info(f"HuggingFace total: {len(models)} models across all modalities")
    return models


# ── Ollama Cloud ────────────────────────────────────────────────────────

OLLAMA_TAGS_URL = "https://ollama.com/api/tags"

async def poll_ollama(client: httpx.AsyncClient, api_key: str | None = None) -> list[dict]:
    """Poll Ollama Cloud's model list. API key optional but gives more models."""
    try:
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        resp = await client.get(OLLAMA_TAGS_URL, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        models = []
        for m in data.get("models", []):
            details = m.get("details", {})
            family = details.get("family", "")
            # Ollama models can be LLMs, vision models, or embedding models
            has_vision = "vision" in family.lower() or "clip" in family.lower()
            models.append({
                "id": m.get("name", ""),
                "name": m.get("name", ""),
                "provider_source": "ollama",
                "modality": "vision" if has_vision else "llm",
                "description": family,
                "size_bytes": _safe_int(m.get("size")),
                "quantization": details.get("quantization_level", ""),
                "parameter_size": details.get("parameter_size", ""),
                "family": family,
                "families": details.get("families", []),
                "context_length": None,
                "input_price_per_1m": None,
                "output_price_per_1m": None,
                "supports_vision": has_vision,
                "is_free": False,
                "local_capable": ":cloud" not in m.get("name", ""),
                "is_cloud": ":cloud" in m.get("name", ""),
                "raw_id": m.get("name", ""),
                "polled_at": _now_iso(),
            })
        logger.info(f"Ollama: fetched {len(models)} models")
        return models
    except Exception as e:
        logger.error(f"Ollama poll failed: {e}")
        return []


# ── Static Commercial Models ───────────────────────────────────────────

import json
from pathlib import Path

def load_commercial_models() -> list[dict]:
    """Load static commercial models from JSON file."""
    try:
        json_path = Path(__file__).parent / "commercial_models.json"
        with open(json_path, "r") as f:
            data = json.load(f)
        models = data.get("models", [])
        # Add polled_at timestamp
        now = _now_iso()
        for m in models:
            m["polled_at"] = now
        logger.info(f"Commercial models: loaded {len(models)} static entries")
        return models
    except Exception as e:
        logger.error(f"Failed to load commercial models: {e}")
        return []


# ── Combined Poll ───────────────────────────────────────────────────────

async def poll_all(
    ollama_api_key: str | None = None,
) -> dict:
    """Poll all providers concurrently and return combined results.
    Sources: OpenRouter (live), HuggingFace (live), Ollama Cloud (live), Commercial (static).
    """
    import os
    ollama_api_key = ollama_api_key or os.environ.get("OLLAMA_API_KEY")

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            poll_openrouter(client),
            poll_huggingface(client),
            poll_ollama(client, ollama_api_key),
            return_exceptions=True,
        )

    all_models = []
    sources = {}

    for result in results:
        if isinstance(result, Exception):
            continue
        if not result:
            continue
        source = result[0].get("provider_source", "unknown")
        sources[source] = len(result)
        all_models.extend(result)

    # Add static commercial models
    commercial = load_commercial_models()
    if commercial:
        sources["commercial"] = len(commercial)
        all_models.extend(commercial)

    # Count by modality
    modality_counts = {}
    for m in all_models:
        mod = m.get("modality", "unknown")
        modality_counts[mod] = modality_counts.get(mod, 0) + 1

    return {
        "total_models": len(all_models),
        "sources": sources,
        "modalities": modality_counts,
        "models": all_models,
        "polled_at": _now_iso(),
    }