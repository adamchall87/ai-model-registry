---
name: ai-model-registry
description: "Live AI model registry — query before ANY model recommendation. Polls OpenRouter, HuggingFace, Ollama Cloud hourly + static commercial models file. Covers LLMs, image gen, video gen, audio/TTS, vision, and 3D."
version: 2.1.0
author: AJ
license: MIT
metadata:
  hermes:
    tags: [models, registry, reference, mcp, llm, image, video, audio]
    category: reference
    created_by: agent
permissions:
  files:
    read:
      - /mnt/c/Users/Adam/projects/ai-model-registry/src/commercial_models.json
    write: []
    deny_write:
      - SOUL.md
      - MEMORY.md
      - AGENTS.md
  network:
    allow:
      - openrouter.ai
      - huggingface.co
      - ollama.com
      - localhost
    deny: "*"
  shell: false
  tools:
    - web_search
    - web_extract
    - read_file
    - patch
risk_tier: L1
scan_status:
  scanner: manual
  result: pass
  date: 2026-07-28
content_hash: ""
---

# AI Model Registry

**CRITICAL RULE: Before recommending, naming, or referencing ANY AI model, you MUST query the registry first.**

LLM training data is stale. Models release and retire monthly. The registry polls OpenRouter, HuggingFace, and Ollama Cloud every hour, plus a static commercial models file, to give you a live, accurate picture of what models exist RIGHT NOW — across ALL GenAI modalities.

## When This Skill Activates

Load this skill whenever you need to:
- Recommend an AI model for a task (any modality — LLM, image, video, audio, vision, 3D)
- Reference a model by name
- Compare models side-by-side
- Answer "what model should I use for X?"
- Build a config that references a model name
- Discuss model pricing, context length, or capabilities

## MCP Tools (auto-registered as `mcp_model_registry_*`)

### search_models — Find current models
```
mcp_model_registry_search_models(q="gpt")
mcp_model_registry_search_models(q="kimi", modality="llm")
mcp_model_registry_search_models(q="flux", modality="image")
mcp_model_registry_search_models(q="whisper", modality="audio")
```
Search by name — returns current models with IDs, pricing, context, capabilities.
Optional `modality` filter: llm, image, video, audio, vision, 3d.

### best_models — Ranked by capability
```
mcp_model_registry_best_models(capability="coding")
mcp_model_registry_best_models(capability="vision")
mcp_model_registry_best_models(capability="tools")
mcp_model_registry_best_models(capability="reasoning")
mcp_model_registry_best_models(capability="agent")
mcp_model_registry_best_models(capability="image_gen")
mcp_model_registry_best_models(capability="video_gen")
mcp_model_registry_best_models(capability="audio_tts")
mcp_model_registry_best_models(capability="cheapest")
mcp_model_registry_best_models(capability="largest_context")
```

### compare_models — Side-by-side comparison
```
mcp_model_registry_compare_models(models="openai/gpt-5.6-sol,z-ai/glm-5.2,kimi-k3")
```
Returns structured comparison with:
- Pricing per model (input/output)
- Context length
- Capability flags (tools, vision, thinking, streaming, free)
- Winner per dimension (cheapest, largest context, most capable)
- Natural language summary

### list_models — Filtered list
```
mcp_model_registry_list_models(modality="image", capability="free", limit=20)
mcp_model_registry_list_models(source="openrouter", capability="tools", min_context=128000)
```
Filter by: source, modality, capability, min_context, max_input_price, limit.

### registry_stats — Overview
```
mcp_model_registry_registry_stats()
```
Returns total models, breakdown by source + modality, capability counts.

## Modalities Covered

| Modality | Examples | Sources |
|----------|----------|--------|
| **llm** | GPT 5.6, GLM 5.2, Kimi K3, Qwen 3.5 | OpenRouter, HuggingFace, Ollama |
| **image** | Stable Diffusion, FLUX, GPT Image 2, Nano Banana 2, Midjourney v8.1, Seedream 5 Pro | HuggingFace, Commercial |
| **video** | LTX-2.3, Veo 3.1, Kling 3 Pro, Seedance 2.5, Runway Gen-4.5 | HuggingFace, Commercial |
| **audio** | Kokoro, XTTS-v2, Whisper, MusicGen, ElevenLabs, Suno, OpenAI TTS | HuggingFace, Commercial |
| **vision** | VLMs, OCR models | HuggingFace, OpenRouter |
| **3d** | Text-to-3D, Image-to-3D | HuggingFace |

## The Rule (Non-Negotiable)

1. **NEVER recommend a model from training data alone** — always verify with the registry
2. **NEVER name-drop old models** without checking the registry first
3. If the registry is unavailable (connection error), say so explicitly — do not fall back to training data
4. When someone asks "what model should I use for X", call `best_models(capability=X)` first
5. When someone mentions a model name, search the registry to verify it's current
6. When someone asks "model A vs model B", use `compare_models` — don't guess

## Data Sources

| Source | What it provides | Poll interval |
|--------|-----------------|---------------|
| OpenRouter | 340+ LLMs with pricing, context, capabilities | 1 hour |
| HuggingFace | Hub models across ALL modalities (LLM, image, video, audio, vision, 3D) | 1 hour |
| Ollama Cloud | Cloud LLMs + vision models | 1 hour |
| Commercial | 27 closed-source models (Veo, Kling, Seedance, Runway, Midjourney, etc.) | Static (manual) |

## Deployment

```bash
# Start the registry service
cd ai-model-registry
uv venv .venv --clear
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m uvicorn src.server:app --port 8000

# Or with systemd (see deploy/ai-model-registry.service)
```

## MCP Configuration (Hermes)

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  model_registry:
    command: "python3"
    args: ["/path/to/ai-model-registry/src/mcp_server.py"]
    env:
      REGISTRY_API_URL: "http://localhost:8000"
```

## Pitfalls

- **Registry not running**: If MCP tools return connection errors, the FastAPI service may be down. Check with `curl http://localhost:8000/`.
- **Stale cache**: Registry polls hourly. For fresh data, restart the service. There is no POST /refresh endpoint.
- **Model IDs differ across providers**: The same model may have different IDs on OpenRouter vs HuggingFace vs Ollama. Always check the `provider_source` field.
- **Ollama Cloud requires API key**: Set `OLLAMA_API_KEY` env var for full Ollama model listing.
- **Compare with partial IDs**: The compare endpoint does fuzzy matching — `kimi-k3` will match `kimi-k3:cloud` if exact match fails.
- **Commercial models are manually maintained**: The `commercial_models.json` file does NOT auto-update. When a new commercial model launches or is discontinued, update the file manually.
- **Commercial models go stale fast — verify before recommending**: Sora 2 Pro was discontinued April 26, 2026 but was still in the registry as active. Before recommending a commercial model, do a web_search to confirm it's still active and current.
- **Security: read-only public deployment**: The server has NO CORS middleware and NO POST endpoints. All GET endpoints are public. Safe to deploy on 0.0.0.0 for public agent access.