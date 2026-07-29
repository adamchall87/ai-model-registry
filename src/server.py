"""
AI Model Registry — FastAPI server with in-memory cache.
Polls OpenRouter, HuggingFace, and Ollama Cloud on a schedule.
Covers ALL GenAI modalities: LLMs, image gen, video gen, audio/TTS, vision, 3D.
Serves a clean JSON API for agents to query current model availability.
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Query
from pydantic import BaseModel

from .pollers import poll_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL", "3600"))  # 1 hour default
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")

app = FastAPI(title="AI Model Registry", version="2.1.0")
# No CORS middleware — this is a pure JSON API for agents, not a browser frontend.

# In-memory cache
_cache: dict[str, Any] = {
    "total_models": 0,
    "sources": {},
    "modalities": {},
    "models": [],
    "polled_at": None,
    "last_poll_duration_s": None,
}


async def refresh_cache():
    """Poll all providers and update the cache."""
    start = time.time()
    logger.info("Starting model poll...")
    result = await poll_all(
        ollama_api_key=OLLAMA_API_KEY or None,
    )
    elapsed = time.time() - start
    result["last_poll_duration_s"] = round(elapsed, 2)
    _cache.update(result)
    logger.info(f"Poll complete: {result['total_models']} models from {result['sources']} ({result.get('modalities', {})}) in {elapsed:.1f}s")


async def poll_loop():
    """Background polling loop."""
    await refresh_cache()
    while True:
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
        await refresh_cache()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poll_loop())


# ── API Endpoints ──────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Health check + cache info."""
    return {
        "service": "AI Model Registry",
        "version": app.version,
        "status": "ok" if _cache["polled_at"] else "initializing",
        "total_models": _cache["total_models"],
        "sources": _cache["sources"],
        "modalities": _cache.get("modalities", {}),
        "polled_at": _cache["polled_at"],
        "last_poll_duration_s": _cache.get("last_poll_duration_s"),
        "poll_interval_seconds": POLL_INTERVAL_SECONDS,
        "endpoints": {
            "/models": "List all models (with optional filters including modality)",
            "/models/search": "Search models by name, tag, or description",
            "/models/best": "Get best models for a given capability",
            "/models/compare": "Compare specific models side-by-side",
            "/models/by-source/{source}": "Filter by provider source",
            "/models/by-modality/{modality}": "Filter by modality (llm, image, video, audio, vision, 3d)",
            "/stats": "Registry statistics",
        },
    }


@app.get("/models")
async def list_models(
    source: str | None = Query(None, description="Filter by provider: openrouter, huggingface, ollama, commercial"),
    modality: str | None = Query(None, description="Filter by modality: llm, image, video, audio, vision, 3d, other"),
    capability: str | None = Query(None, description="Filter by capability: coding, vision, tools, reasoning, free, local, cloud"),
    min_context: int | None = Query(None, description="Minimum context length"),
    max_input_price: float | None = Query(None, description="Max input price per 1M tokens"),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
):
    """List models with optional filters. Returns JSON array."""
    models = _cache["models"]

    if source:
        models = [m for m in models if m.get("provider_source") == source]

    if modality:
        models = [m for m in models if m.get("modality") == modality]

    if capability:
        cap = capability.lower()
        if cap == "coding":
            models = [m for m in models if any(k in m.get("id", "").lower() + " " + m.get("description", "").lower() for k in ["code", "coder", "coding", "devstral"])]
        elif cap == "vision":
            models = [m for m in models if m.get("supports_vision") is True or "vision" in str(m.get("modality", "")).lower() or "image" in str(m.get("input_modalities", [])).lower() or "vlm" in m.get("id", "").lower()]
        elif cap == "tools":
            models = [m for m in models if m.get("supports_tools") is True]
        elif cap == "reasoning":
            models = [m for m in models if m.get("supports_thinking") is True or "reason" in m.get("id", "").lower()]
        elif cap == "free":
            models = [m for m in models if m.get("is_free") is True]
        elif cap == "local":
            models = [m for m in models if m.get("local_capable") is True]
        elif cap == "cloud":
            models = [m for m in models if m.get("is_cloud") is True or m.get("provider_source") in ("openrouter", "ollama")]
        elif cap == "tts":
            models = [m for m in models if m.get("modality") == "audio" and "tts" in m.get("id", "").lower()]
        elif cap == "image_gen":
            models = [m for m in models if m.get("modality") == "image"]
        elif cap == "video_gen":
            models = [m for m in models if m.get("modality") == "video"]

    if min_context:
        models = [m for m in models if m.get("context_length") and m["context_length"] >= min_context]

    if max_input_price is not None:
        models = [m for m in models if m.get("input_price_per_1m") is not None and m["input_price_per_1m"] <= max_input_price]

    total = len(models)
    models = models[offset:offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "models": models,
        "polled_at": _cache["polled_at"],
    }


@app.get("/models/search")
async def search_models(
    q: str = Query(..., description="Search query — matches model name, id, or description"),
    modality: str | None = Query(None, description="Filter by modality: llm, image, video, audio, vision, 3d"),
    limit: int = Query(20, le=100),
):
    """Search models by name, id, or description. Case-insensitive."""
    query = q.lower()
    models = _cache["models"]

    if modality:
        models = [m for m in models if m.get("modality") == modality]

    scored = []
    for m in models:
        mid = m.get("id", "").lower()
        mname = m.get("name", "").lower()
        desc = m.get("description", "").lower()

        score = 0
        if query in mid:
            score += 10
        if query in mname:
            score += 8
        if query in desc:
            score += 3
        if any(word in mid or word in mname for word in query.split()):
            score += 5

        if score > 0:
            scored.append((score, m))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [m for _, m in scored[:limit]]

    return {
        "query": q,
        "modality_filter": modality,
        "total_matches": len(scored),
        "results": results,
        "polled_at": _cache["polled_at"],
    }


@app.get("/models/best")
async def best_models(
    capability: str = Query(..., description="Capability: coding, vision, tools, reasoning, agent, general, cheapest, largest_context, llm, image_gen, video_gen, audio_tts"),
    limit: int = Query(10, le=50),
):
    """Get best models for a given capability, ranked by heuristics."""
    models = _cache["models"]
    cap = capability.lower()

    if cap == "cheapest":
        ranked = sorted([m for m in models if m.get("input_price_per_1m") is not None], key=lambda m: m["input_price_per_1m"])
    elif cap == "largest_context":
        ranked = sorted([m for m in models if m.get("context_length")], key=lambda m: m["context_length"], reverse=True)
    elif cap == "coding":
        # LLMs with tools support, ranked by context length (newer models have larger context)
        coding = [m for m in models if m.get("modality") == "llm" and m.get("supports_tools") is True]
        ranked = sorted(coding, key=lambda m: (m.get("context_length") or 0), reverse=True)
    elif cap == "vision":
        vision = [m for m in models if m.get("supports_vision") is True or "vision" in str(m.get("modality", "")).lower() or "image" in str(m.get("input_modalities", [])).lower() or "vlm" in m.get("id", "").lower()]
        ranked = sorted(vision, key=lambda m: (m.get("downloads") or 0), reverse=True)
    elif cap == "tools":
        ranked = sorted([m for m in models if m.get("supports_tools") is True], key=lambda m: (m.get("downloads") or 0), reverse=True)
    elif cap == "reasoning":
        ranked = sorted([m for m in models if m.get("supports_thinking") is True or "reason" in m.get("id", "").lower()], key=lambda m: (m.get("downloads") or 0), reverse=True)
    elif cap == "agent":
        agent_models = [m for m in models if m.get("supports_tools") is True and m.get("context_length") and m["context_length"] >= 32000]
        ranked = sorted(agent_models, key=lambda m: (m.get("input_price_per_1m") or 999))
    elif cap == "image_gen":
        ranked = sorted([m for m in models if m.get("modality") == "image"], key=lambda m: (m.get("downloads") or m.get("likes") or 0), reverse=True)
    elif cap == "video_gen":
        ranked = sorted([m for m in models if m.get("modality") == "video"], key=lambda m: (m.get("downloads") or m.get("likes") or 0), reverse=True)
    elif cap == "audio_tts":
        ranked = sorted([m for m in models if m.get("modality") == "audio"], key=lambda m: (m.get("downloads") or m.get("likes") or 0), reverse=True)
    elif cap == "general":
        # LLMs only, ranked by context length (best proxy for recency/capability)
        ranked = sorted([m for m in models if m.get("modality") == "llm"], key=lambda m: (m.get("context_length") or 0), reverse=True)
    elif cap == "llm":
        # All LLMs ranked by context length
        ranked = sorted([m for m in models if m.get("modality") == "llm"], key=lambda m: (m.get("context_length") or 0), reverse=True)
    else:
        ranked = models

    return {
        "capability": cap,
        "results": ranked[:limit],
        "polled_at": _cache["polled_at"],
    }


# ── Compare Endpoint ───────────────────────────────────────────────────

@app.get("/models/compare")
async def compare_models(
    models: str = Query(..., description="Comma-separated model IDs to compare (e.g. openai/gpt-5.6-sol,kimi-k3:cloud)"),
):
    """Compare specific models side-by-side. Returns structured comparison with winners."""
    requested_ids = [m.strip() for m in models.split(",")]
    all_models = _cache["models"]

    # Find each requested model — try exact match first, then fuzzy
    found = {}
    not_found = []
    for rid in requested_ids:
        # Exact match
        match = next((m for m in all_models if m.get("id") == rid), None)
        if not match:
            # Try case-insensitive
            match = next((m for m in all_models if m.get("id", "").lower() == rid.lower()), None)
        if not match:
            # Try partial match
            match = next((m for m in all_models if rid.lower() in m.get("id", "").lower()), None)
        if match:
            found[rid] = match
        else:
            not_found.append(rid)

    if not found:
        return {
            "error": "No models found",
            "requested": requested_ids,
            "not_found": not_found,
            "polled_at": _cache["polled_at"],
        }

    model_ids = list(found.keys())

    # Build comparison dimensions
    dimensions = {}
    winners = {}

    # Price dimensions (lower is better)
    for price_key in ["input_price_per_1m", "output_price_per_1m"]:
        dim = {}
        values = {}
        for mid, m in found.items():
            val = m.get(price_key)
            dim[mid] = val
            if val is not None:
                values[mid] = val
        dimensions[price_key] = dim
        if values:
            winners[price_key] = min(values, key=values.get)

    # Context length (higher is better)
    dim = {}
    values = {}
    for mid, m in found.items():
        val = m.get("context_length")
        dim[mid] = val
        if val is not None:
            values[mid] = val
    dimensions["context_length"] = dim
    if values:
        winners["context_length"] = max(values, key=values.get)

    # Capability flags (true is better)
    for cap_key in ["supports_tools", "supports_vision", "supports_thinking", "supports_streaming", "is_free"]:
        dim = {}
        true_ids = []
        for mid, m in found.items():
            val = m.get(cap_key)
            dim[mid] = val
            if val is True:
                true_ids.append(mid)
        dimensions[cap_key] = dim
        if true_ids:
            if len(true_ids) == 1:
                winners[cap_key] = true_ids[0]
            elif cap_key == "is_free":
                # For free, having it is better
                winners[cap_key] = true_ids[0]

    # Modality
    dimensions["modality"] = {mid: m.get("modality") for mid, m in found.items()}
    dimensions["provider_source"] = {mid: m.get("provider_source") for mid, m in found.items()}
    dimensions["input_modalities"] = {mid: m.get("input_modalities", []) for mid, m in found.items()}
    dimensions["output_modalities"] = {mid: m.get("output_modalities", []) for mid, m in found.items()}
    dimensions["downloads"] = {mid: m.get("downloads") for mid, m in found.items()}
    dimensions["parameter_size"] = {mid: m.get("parameter_size") or m.get("architecture", {}).get("parameters") for mid, m in found.items()}

    # Most capable (most capability flags = True)
    cap_count = {}
    for mid, m in found.items():
        count = sum(1 for k in ["supports_tools", "supports_vision", "supports_thinking"] if m.get(k) is True)
        cap_count[mid] = count
    if cap_count:
        winners["most_capable"] = max(cap_count, key=cap_count.get)

    # Generate summary
    summaries = []
    for mid, m in found.items():
        parts = [m.get("name", mid)]
        if m.get("modality"):
            parts.append(f"({m['modality']})")
        if m.get("input_price_per_1m") is not None:
            parts.append(f"${m['input_price_per_1m']}/1M input")
        if m.get("context_length"):
            parts.append(f"{m['context_length']:,} ctx")
        caps = []
        if m.get("supports_tools"): caps.append("tools")
        if m.get("supports_vision"): caps.append("vision")
        if m.get("supports_thinking"): caps.append("thinking")
        if caps:
            parts.append(f"[{'+'.join(caps)}]")
        summaries.append(" ".join(parts))

    summary = " | ".join(summaries)

    return {
        "comparison": {
            "models": model_ids,
            "not_found": not_found,
            "dimensions": dimensions,
            "winner_by_dimension": winners,
            "capability_counts": cap_count,
            "summary": summary,
            "full_data": found,
        },
        "polled_at": _cache["polled_at"],
    }


@app.get("/models/by-source/{source}")
async def models_by_source(source: str):
    """Get all models from a specific provider source."""
    models = [m for m in _cache["models"] if m.get("provider_source") == source]
    return {
        "source": source,
        "total": len(models),
        "models": models,
        "polled_at": _cache["polled_at"],
    }


@app.get("/models/by-modality/{modality}")
async def models_by_modality(modality: str):
    """Get all models for a specific modality (llm, image, video, audio, vision, 3d, other)."""
    models = [m for m in _cache["models"] if m.get("modality") == modality]
    return {
        "modality": modality,
        "total": len(models),
        "models": models,
        "polled_at": _cache["polled_at"],
    }


@app.get("/stats")
async def stats():
    """Registry statistics."""
    models = _cache["models"]
    by_source = {}
    by_modality = {}
    free_count = 0
    tools_count = 0
    vision_count = 0
    thinking_count = 0
    with_pricing = 0
    with_context = 0

    for m in models:
        src = m.get("provider_source", "unknown")
        by_source[src] = by_source.get(src, 0) + 1
        mod = m.get("modality", "unknown")
        by_modality[mod] = by_modality.get(mod, 0) + 1
        if m.get("is_free"):
            free_count += 1
        if m.get("supports_tools"):
            tools_count += 1
        if m.get("supports_vision") or "vision" in str(m.get("modality", "")).lower():
            vision_count += 1
        if m.get("supports_thinking"):
            thinking_count += 1
        if m.get("input_price_per_1m") is not None:
            with_pricing += 1
        if m.get("context_length"):
            with_context += 1

    return {
        "total_models": len(models),
        "by_source": by_source,
        "by_modality": by_modality,
        "free_models": free_count,
        "tool_capable": tools_count,
        "vision_capable": vision_count,
        "thinking_capable": thinking_count,
        "with_pricing": with_pricing,
        "with_context_length": with_context,
        "polled_at": _cache["polled_at"],
        "poll_interval_seconds": POLL_INTERVAL_SECONDS,
    }