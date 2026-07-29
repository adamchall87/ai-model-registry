---
name: ai-model-registry
description: 'Live AI model registry MCP server — polls OpenRouter, HuggingFace, and Ollama Cloud hourly + static commercial models file. Covers ALL GenAI modalities: LLMs, image gen, video gen, audio/TTS, vision, 3D. Query before ANY model recommendation to avoid referencing outdated models from training data.'
version: 2.3.0
author:
  name: Adam Hall + Hermes
  identity: did:web:github.com/adamchall87
  url: https://adamdoesai.com
  signing_key: ed25519:fd17baa163256592308e5e18e1a1637ede20a0cb8c3d78c6a880a8cd21cda816ff9c7772f93dbd43ec8f90eca1a7e4ec88678c5b92864d9fe57b3bf65c895602
license: All Rights Reserved
platforms:
- hermes
- openclaw
- claude
- cursor
- vscode
- codex
- chatgpt
metadata:
  hermes:
    tags:
    - models
    - registry
    - reference
    - mcp
    - llm
    - image
    - video
    - audio
    - vision
    - openrouter
    - huggingface
    - ollama
    - commercial
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
    deny: '*'
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
signing_key: ed25519:LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUNvd0JRWURLMlZ3QXlFQVJ3Tys2RENBTitkdHV4WUlPS1MxSjNYZ1R5ZkEyR28zMVVOK0ZqbVd5YVU9Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo=
content_hash: e446d5a29ff1b39ace7e4e32dbc769c5957e707dce3a09f8dfeacd6b70a80a9b
signature: ed25519:ab1f74669d4ebdd0f9dd732bf94b04b78bf07b0b55b2a0b4cd98f9354ee137cc4fae4f1c5a1b27e736050333fcbccb432caf47da1d32880c486e3186e2342301
---
# AI Model Registry

Live AI model registry that polls OpenRouter, HuggingFace, and Ollama Cloud every hour,
plus a static commercial models file for closed-source models (Veo, Kling, Seedance, Midjourney, etc.).
Covers ALL GenAI modalities: LLMs, image gen, video gen, audio/TTS, vision, and 3D.
Provides agents with up-to-date model information so they never recommend stale models from training data.

## CRITICAL RULE (Non-Negotiable)

**Before recommending, naming, or referencing ANY AI model, query the registry first.**

LLM training data is stale. Models release and retire monthly. AJ has corrected this behavior repeatedly — naming old models like "GPT-4o" when GPT 5.6 SOL is the current meta is a top frustration trigger. The registry exists to solve this.

If the registry MCP tools are available (`mcp_model_registry_*`), USE THEM before any model reference.
If the registry is NOT connected, say so explicitly — do NOT fall back to training data and do NOT guess model names.

## When This Skill Activates

Load this skill whenever you need to:
- Recommend an AI model for a task (ANY modality — LLM, image, video, audio, vision, 3D)
- Reference a model by name
- Compare models side-by-side
- Answer "what model should I use for X?"
- Build a config that references a model name
- Discuss model pricing, context length, or capabilities

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              AI Model Registry (FastAPI, port 9847)            │
│                                                               │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────────────┐   │
│  │OpenRouter│ │HuggingFace│ │Ollama  │ │Commercial Models │   │
│  │  poller  │ │  poller  │ │poller  │ │ (static JSON)     │   │
│  └──────────┘ └──────────┘ └────────┘ └──────────────────┘   │
│       (live polled hourly)          (loaded at startup)       │
│                  In-Memory Cache (hourly refresh)             │
│         ┌────────────┬─────────────┬─────────┐                │
│         ▼            ▼             ▼         ▼               │
│    REST API    MCP Server    Hermes Skill                     │
│  (port 9847)  (stdio)       (this file)                      │
│      │                                                    │
│      ▼                                                    │
│  nginx reverse proxy → HTTPS → public domain                │
│  Any agent anywhere queries the REST API via HTTP GET        │
└──────────────────────────────────────────────────────────────┘
```

Port 9847 is the default (non-standard to avoid conflicts on shared VPS).
The deploy script (`deploy/deploy.sh`) accepts a custom port as the second argument.

This is a **public service** — any agent anywhere can query the REST API. No auth, no MCP client required. Just HTTP GET.

- **GitHub repo**: https://github.com/adamchall87/ai-model-registry
- **Project source**: `/mnt/c/Users/Adam/projects/ai-model-registry/`

## MCP Tools (when connected via Hermes MCP client)

5 tools registered as `mcp_model_registry_*`:

| Tool | Description |
|------|-------------|
| `mcp_model_registry_list_models` | List models with filters (source, modality, capability, min_context, max_price, limit) |
| `mcp_model_registry_search_models` | Search by name/id/description, optional modality filter |
| `mcp_model_registry_best_models` | Best models for a capability (coding, vision, tools, reasoning, agent, image_gen, video_gen, audio_tts, cheapest, largest_context) |
| `mcp_model_registry_compare_models` | Compare specific models side-by-side with winners per dimension + summary |
| `mcp_model_registry_registry_stats` | Registry statistics (total models, by source, by modality, capability counts) |

## Modalities Covered

| Modality | Examples | Sources |
|----------|----------|--------|
| **llm** | GPT 5.6, GLM 5.2, Kimi K3, Qwen 3.5 | OpenRouter, HuggingFace, Ollama |
| **image** | Stable Diffusion, FLUX, Z-Image-Turbo, SDXL, GPT Image 2, Nano Banana 2, Midjourney v8.1, Seedream 5 Pro | HuggingFace, Commercial |
| **video** | LTX-2.3, Veo 3.1, Kling 3 Pro, Seedance 2.5, Runway Gen-4.5 | HuggingFace, Commercial |
| **audio** | Kokoro, XTTS-v2, Whisper, MusicGen, ElevenLabs, Suno, OpenAI TTS | HuggingFace, Commercial |
| **vision** | VLMs, OCR models | HuggingFace, OpenRouter |
| **3d** | Text-to-3D, Image-to-3D | HuggingFace |

## Common Usage Patterns

### Verify a model exists before naming it
```
mcp_model_registry_search_models(q="gpt")
→ Returns: gpt-5.6-luna-pro, gpt-5.6-sol, gpt-5.6-terra, etc.
```

### Best for a capability (ANY modality)
```
mcp_model_registry_best_models(capability="coding")
mcp_model_registry_best_models(capability="vision")
mcp_model_registry_best_models(capability="agent")
mcp_model_registry_best_models(capability="image_gen")
mcp_model_registry_best_models(capability="video_gen")
mcp_model_registry_best_models(capability="audio_tts")
```

### Compare models side-by-side
```
mcp_model_registry_compare_models(models="openai/gpt-5.6-sol,z-ai/glm-5.2,kimi-k3")
→ Returns: pricing per model, context, capabilities, winner per dimension, summary
```

### Filter by source + modality + capability + price
```
mcp_model_registry_list_models(modality="image", capability="free", limit=20)
mcp_model_registry_list_models(source="openrouter", capability="tools", min_context=128000)
```

## REST API (when deployed on VPS)

| Endpoint | Description |
|----------|-------------|
| `GET /` | Health check + cache info (includes modality breakdown) |
| `GET /models` | List with filters (source, modality, capability, min_context, max_input_price, limit, offset) |
| `GET /models/search?q=X` | Search by name/id/description, optional modality filter |
| `GET /models/best?capability=X` | Best models for capability |
| `GET /models/compare?models=A,B,C` | Side-by-side comparison with winners |
| `GET /models/by-source/{source}` | Filter by provider |
| `GET /models/by-modality/{modality}` | Filter by modality |
| `GET /stats` | Registry statistics (by source AND modality) |

## Deployment

### Local test
```bash
cd /mnt/c/Users/Adam/projects/ai-model-registry
uv venv .venv --clear
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m uvicorn src.server:app --port 9847
```

### VPS deployment (one-shot script)
```bash
# Clone and deploy with domain + default port (9847)
git clone https://github.com/adamchall87/ai-model-registry.git
cd ai-model-registry
bash deploy/deploy.sh registry.yourdomain.com

# Custom port (if 9847 is taken)
bash deploy/deploy.sh registry.yourdomain.com 12345
```
The script handles: system packages, clone, venv, deps, systemd service, nginx reverse proxy, Let's Encrypt SSL, and API verification.
See `references/deployment-guide.md` for full step-by-step manual deploy.

### Deployed instance
- **URL**: `http://registry.adamdoesai.com:9847`
- **VPS**: Hostinger Ubuntu `148.230.80.163`
- **Service**: systemd `ai-model-registry` (runs as user `registry`, `/home/registry/ai-model-registry/`)
- **Port**: 9847 (direct, no nginx — Traefik/Docker owns 80/443)
- **SSL**: Not configured (read-only GET API, acceptable for now)
- **Model count**: 895 (OpenRouter 367, HuggingFace 482, Ollama 19, Commercial 27)
- **Poll interval**: Hourly refresh via scheduled timer (model data refreshes, skill content is static)

### Hermes MCP config (local MCP server → remote REST API)
Add to `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  model_registry:
    command: "python3"
    args: ["/path/to/ai-model-registry/src/mcp_server.py"]
    env:
      REGISTRY_API_URL: "https://registry.yourdomain.com"
```

### Public REST API (for external agents)
Any agent can query the REST API directly — no MCP client needed:
```
GET https://registry.yourdomain.com/models/best?capability=video_gen
GET https://registry.yourdomain.com/models/search?q=seedance
GET https://registry.yourdomain.com/stats
```

## Data Sources

| Source | API | Auth | What it provides |
|--------|-----|------|-----------------|
| OpenRouter | `GET https://openrouter.ai/api/v1/models` | None | 340+ LLMs with pricing, context, capabilities |
| HuggingFace | `GET https://huggingface.co/api/models` | None | Hub models across ALL modalities (LLM, image, video, audio, vision, 3D) |
| Ollama Cloud | `GET https://ollama.com/api/tags` | Bearer (optional) | Cloud LLMs + vision models |
| Commercial | Static JSON file (`src/commercial_models.json`) | None | 27 closed-source models: Veo, Kling, Seedance, Runway, Midjourney, Nano Banana, Seedream, ElevenLabs, Suno, etc. |

## Capabilities Supported

- `coding` — code/coder/devstral models
- `vision` — models with image input (VLMs) or supports_vision flag
- `tools` — models that support tool/function calling
- `reasoning` — models with thinking/reasoning capability
- `free` — zero-cost models
- `local` — models that can run locally
- `cloud` — cloud-routed models
- `agent` — best for agent use (tools + 32K+ context + reasonable price)
- `image_gen` — image generation models (modality=image)
- `video_gen` — video generation models (modality=video)
- `audio_tts` — audio/TTS models (modality=audio)
- `cheapest` — sorted by input price
- `largest_context` — sorted by context length

## Pitfalls

- **Registry not running**: If MCP tools return connection errors, the FastAPI service may be down. Check with `curl http://localhost:8000/`.
- **Stale cache**: Registry polls hourly. For fresh data, restart the service.
- **Model IDs differ across providers**: Same model may have different IDs on OpenRouter vs HuggingFace vs Ollama. Check `provider_source`.
- **OpenRouter `supported_parameters` can be list OR dict**: The poller handles both, but if you write custom queries, account for this.
- **Compare endpoint does fuzzy matching**: `kimi-k3` will match `kimi-k3:cloud` if exact match fails. Pass partial IDs if unsure of the full ID.
- **Model pricing is per-token, not per-request**: OpenRouter returns prices per 1M tokens. Some providers return scientific notation (e.g. `5e-06` = $0.000005/1M).
- **Commercial models are manually maintained**: The `commercial_models.json` file is updated manually by the skill author. When a new commercial model launches (e.g. Seedance 3.0, Veo 4), the file must be updated manually. A scheduled job to check for new model announcements is planned but not yet implemented.
- **Do NOT add providers the user didn't ask for**: In the original session, I added Replicate and Fal.ai pollers without being asked. AJ called this out — he has a 4090 with ComfyUI for local generation and OpenArt.ai for cloud. Stick to the 3 live sources + commercial static file unless AJ explicitly requests a new source.
- **Commercial models go stale fast — verify before recommending**: Sora 2 Pro was discontinued April 26, 2026 (web app) / September 24, 2026 (API) but was still in the registry as an active model. Seedance 2.0 was superseded by 2.5 (June 23, 2026 announcement) but the file still had 2.0. The `commercial_models.json` file is manually maintained and can lag reality by weeks. Before recommending a commercial model, do a web_search to confirm it's still active and current version. If you find a model has been discontinued or updated, patch the JSON file immediately.
- **Security: read-only public deployment**: The FastAPI server has NO CORS middleware (pure JSON API for agents, not browsers) and NO POST endpoints. All endpoints are GET-only — the server refreshes its cache on a scheduled timer, no external write surface exists. Safe to deploy on 0.0.0.0 for public agent access.
- **Governance**: Skill maintained by Adam Hall (adamdoesai.com). Changes reviewed and re-audited before deployment. Commercial models file updates follow a defined release cadence.
- **HTML report design — no emoji, no stock icons, no AI slop**: When building premium HTML deliverables (audit reports, dashboards, templates), use custom SVG illustrations and real visual design language — not emoji icons or generic stock elements. AJ explicitly rejected emoji icons (shield, magnifying glass, etc.) and demanded Snyk/Vercel-quality design. Use: custom SVG logo marks, proper type hierarchy (Inter + JetBrains Mono), SVG ring charts, color-coded accent bars, subtle grid backgrounds. This applies to ALL client-facing deliverables, not just security reports.
- **Understand project scope before framing**: AJ repeatedly corrected me for framing the registry as his personal Hermes tool when he had been saying all along it's a PUBLIC service for any agent. Before discussing architecture, deployment, or usage, understand whether the project is personal or public. If the user says "this will be public" or "any agent can use it," STOP framing it as their local setup. This is a first-class correction — don't default to "how does this fit in YOUR workflow" when the user is building for everyone.
- **Don't hardcode port 8000 on shared VPS**: Standard ports are likely taken when a user has multiple apps on one VPS. Default to non-standard ports (9847) and make port configurable via deploy script argument. Always ask or use non-standard defaults when deploying to shared infrastructure.
- **Version string sync trap**: The FastAPI app version (`app = FastAPI(version="X")`) and the health check endpoint's `"version"` field are separate values. If the health endpoint hardcodes a version string instead of referencing `app.version`, bumping the app version won't update the API response. Always use `"version": app.version` in the health check — never hardcode it. This caused a confusing debug session where the source clearly showed 2.1.0 but the API kept returning 2.0.0 across multiple server restarts and cache clears. The root cause was a hardcoded string on line 73 that shadowed the app version on line 26.
- **Public service architecture**: The registry is designed as a public API that ANY agent can query via HTTP GET. No auth, no MCP client required. The MCP server is just a local bridge for Hermes — external agents use the REST API directly. Deploy behind nginx with HTTPS for public access.
- **VPS port conflict with existing Traefik/Docker**: If the VPS already runs Docker apps with Traefik on ports 80/443 (e.g. n8n stack), system nginx CANNOT bind those ports. The deploy script will fail at the nginx step with `bind() to 0.0.0.0:80 failed (98: Address already in use)`. The registry service itself (port 9847) will still start fine — only the nginx reverse proxy fails. Solutions: (a) use port 9847 directly without nginx (no SSL, acceptable for read-only API), (b) route through the existing Traefik by adding a file provider config or docker label, (c) move docker off 80/443. Check for existing port usage BEFORE running deploy: `ss -tlnp | grep -E ':80|:443'`. If docker-proxy is there, the deploy script's nginx step will fail — the service still works on its internal port.
- **Firewall port opening for direct access**: If bypassing nginx and using the registry on its raw port (e.g. 9847), the port must be opened in BOTH the OS firewall AND the cloud provider firewall. On Ubuntu: `ufw allow 9847/tcp`. On Hostinger VPS, there's a separate cloud firewall panel that also needs the port opened — ufw alone is not enough. If `curl http://registry.domain:9847/stats` times out from outside but works from localhost, it's a firewall issue, not a service issue.
- **Deploy script hardcoded 127.0.0.1 — service won't be externally reachable**: The deploy script's systemd ExecStart line had `--host 127.0.0.1` which binds to localhost only. The service works fine internally (`curl localhost:9847/stats` succeeds) but times out from outside the VPS. Check with `ss -tlnp | grep 9847` — if it shows `127.0.0.1:9847`, the bind is wrong. Fix: change to `--host 0.0.0.0` in the deploy script (deploy/deploy.sh), commit, push to GitHub, then pull on the VPS and restart. NEVER sed the service file directly on the VPS — AJ explicitly corrected this: fix at the source in GitHub, then pull.
- **Fix at the source, not on the server**: When a deployment file needs changing (service config, deploy script, etc.), ALWAYS fix it in the GitHub repo, commit, push, then pull on the VPS. Do NOT patch files directly on the VPS with sed/echo. AJ's exact correction: "why would I modify it outside of the source code on gh". This is a hard workflow rule — the repo is the source of truth, the VPS is a deployment target.
- **Don't suggest touching existing infrastructure casually**: When the deploy script's nginx failed because Docker Traefik held ports 80/443, I suggested `systemctl disable nginx`. AJ's immediate concern was "wont that break my n8n". Even when the suggestion is technically correct (system nginx is separate from Docker Traefik), don't casually suggest disabling/removing services on a shared VPS — the user has production apps running. Explain what IS and ISN'T affected, and let the user decide. Prefer leaving dead services disabled-but-present over suggesting removal.
- **Security-conscious user — opening ports is a real concern**: AJ is a security professional. When the registry went live on a raw port (9847) without SSL, he immediately flagged it: "but I am a security guy, I just opened a port to the public...". Document the trade-off explicitly: read-only GET API with no auth surface is low-risk, but every open port is attack surface. The proper hardening path is routing through the existing Traefik on 443 (SSL, no extra port) and closing 9847 externally. Don't dismiss the concern — acknowledge it and provide the fix path.
- **DNS A record vs CNAME/ALIAS conflict**: When creating a subdomain A record in Hostinger's DNS Zone Editor, any existing CNAME or ALIAS record for the same hostname must be deleted first. DNS doesn't allow mixing A and CNAME/ALIAS on the same name. Error: `RRset registry.adamdoesai.com IN ALIAS must not be used with A on the same name`. Delete the old record, then add the A record. Verify propagation with `ping -c1 registry.yourdomain.com` — IP should match VPS IP, not a Hostinger parked page IP. DNS propagation can take a few minutes.
- **`best_models` sorts by HuggingFace downloads**: Open-source models always dominate `best_models` rankings because HuggingFace returns download counts and commercial models don't have that field. When recommending a commercial model, use `search_models` by name instead of `best_models` by capability — the ranking heuristic doesn't apply to closed-source models.
- **Compare endpoint lacks commercial-specific fields**: The compare endpoint only compares standard fields (input_price, context_length, supports_tools, etc.). Commercial model fields like `max_resolution`, `supports_audio`, `max_duration`, and `max_reference_inputs` are NOT included in comparison dimensions. This is a feature gap, not a bug — if comparing two commercial video models, the winner is determined by `most_capable` (count of standard capability flags), not video-specific capabilities.

## Debugging Lesson — Check Logs Before Speculating

When a model provider fails, do NOT guess about config issues, endpoint URLs, or API keys. Check the actual error:

```bash
grep -i "error\\|fail\\|401\\|402\\|403\\|429\\|500\\|timeout" ~/.hermes/logs/errors.log | tail -20
```

In this session, I wasted several minutes speculating about Ollama Cloud endpoint URLs and model name formats. The actual error was HTTP 402 (Payment Required) — the extra usage credits were empty. The config, endpoint, API key, and model name were all correct. Always check logs FIRST.

**AJ's exact words**: "You are not being that intelligent. You are running Ollama Cloud right now you have a valid API key dummy." — The agent was literally running on the provider it was speculating about. Check the environment you're in before guessing.

## Model Reference Discipline

AJ has repeatedly corrected the behavior of naming old/outdated AI models from training data (e.g. referencing GPT-4o when GPT 5.6 SOL is current). This is a FIRST-CLASS frustration trigger. The rules:

1. NEVER name a specific AI model without checking the registry first
2. If the registry is not connected, say so explicitly — do NOT fall back to training data
3. When someone mentions a model, search the registry to verify it's the current version
4. When someone asks "what model should I use for X", call `best_models(capability=X)`
5. Commercial models (closed-source) are in the static file — search by name to find current version
6. **ALWAYS web_search to verify a commercial model is still active before recommending it.** The commercial_models.json file is manually maintained and can lag reality by weeks. Sora 2 Pro was discontinued April 26, 2026 but was still in the registry as an active model — AJ caught this. The registry is a starting point, not a source of truth for commercial model lifecycle status. Verify, then recommend.
7. **When you discover a model has been discontinued or updated, patch the JSON file immediately.** Don't just note it — fix the registry so the next agent doesn't make the same mistake.
8. **AJ refuses Google AI products**: Do not recommend Veo, Gemini, Nano Banana, Imagen, or any Google AI product unless AJ explicitly asks. This is a hard preference, not a suggestion. When AJ says "fuck Google" or similar, filter Google products from all recommendations immediately.

## References

- `references/deployment-guide.md` — Full VPS deployment guide: nginx config template, Let's Encrypt setup, systemd service, DNS configuration, and public API architecture
- `references/api-endpoints.md` — Full API endpoint reference with response shapes and curl examples
- `references/provider-quirks.md` — Provider-specific API quirks (OpenRouter parameter shapes, HuggingFace pipeline tags, Ollama model naming)
- `references/commercial-models-maintenance.md` — How to update the static commercial models file, what sources to check for new model launches, and the monthly update workflow
- `references/ast10-audit-remediation-example.md` — Complete real-world AST10 audit-to-remediation cycle: findings, fixes applied, 8/8 test verification, and key lessons (read-only API pattern, CORS removal, port conflicts, version sync, stale references, no emoji in deliverables)
- `references/vps-deployment-realities.md` — Real VPS deployment with existing Traefik/Docker: port conflicts, firewall opening, DNS A record vs CNAME/ALIAS conflicts, non-root deploy, and direct-port-access fallback when nginx can't bind
- `references/auditor-false-positives.md` — How to fix self-detection false positives in security scanners (CORS, 0.0.0.0, web_extract, MEMORY.md in documentation context). Includes the strip_code_noise() pattern and documentation-context filter.
- `references/remediation-knowledge-base.md` — Pattern for building a remediation knowledge base inside security auditors: map finding messages to step-by-step fix instructions with code blocks and reference links.