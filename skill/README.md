# AI Model Registry

A live AI model registry covering every major GenAI modality — LLMs, image generation, video generation, audio/TTS, vision, and 3D. Polls OpenRouter, HuggingFace, and Ollama Cloud hourly, plus a manually maintained commercial models file for closed-source models (Veo, Kling, Seedance, Midjourney, Sora, Runway, Pika, PixVerse, and more).

Built so AI agents never recommend outdated models from stale training data. Query the registry before naming any model — get current names, pricing, capabilities, and availability in real time.

## Live Endpoint

```
http://registry.adamdoesai.com:9847
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /stats` | Total model count, breakdown by source and modality |
| `GET /search?q=<query>` | Full-text search across all models |
| `GET /search?q=video&modality=video_gen` | Filter by modality (llm, image, video, audio, vision, 3d) |
| `GET /best_models?modality=video` | Top models by modality, sorted by downloads |
| `GET /compare?models=veo-3.1,kling-3-pro` | Side-by-side model comparison |
| `GET /models?source=openrouter` | Filter by source (openrouter, huggingface, ollama, commercial) |
| `GET /health` | Health check |

## Model Sources

| Source | Count | Method | Coverage |
|--------|-------|--------|----------|
| OpenRouter | 367 | Live API poll (hourly) | LLMs with pricing |
| HuggingFace | 482 | Live API poll (hourly) | All modalities — image, video, audio, vision, 3D, LLM |
| Ollama Cloud | 19 | Live API poll (hourly) | LLMs + vision |
| Commercial | 27 | Static JSON (manually maintained) | Video, image, audio — closed-source models |

**Total: 895 models across all GenAI modalities.**

## Monthly Update Service

New AI models release monthly. The commercial models file is manually maintained by Adam Hall and updated on a regular cadence to ensure newly released models are available in the registry as soon as they are announced.

If you purchase a license, updates to the commercial models file are included. You will receive updated JSON files at the defined update frequency, ready to drop into your deployment.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         AI Model Registry (FastAPI, port 9847)      │
│                                                      │
│  ┌──────────┐  ┌───────────┐  ┌─────────────┐        │
│  │OpenRouter│  │HuggingFace│  │Ollama Cloud │        │
│  │  poller  │  │  poller   │  │   poller    │        │
│  └────┬─────┘  └─────┬─────┘  └──────┬──────┘        │
│       └──────────────┼────────────────┘               │
│                      ▼                                │
│              In-Memory Cache (hourly)                 │
│                      │                                │
│         ┌────────────┼────────────┐                  │
│         ▼            ▼            ▼                  │
│    REST API    MCP Server    Hermes Skill             │
│  (port 9847)  (stdio)       (SKILL.md)               │
│                                                      │
│  + Commercial models (static JSON, manual updates)   │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### Self-Host

```bash
git clone <repo-url>
cd ai-model-registry
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.server:app --host 0.0.0.0 --port 9847
```

### Deploy with systemd + nginx

```bash
bash deploy/deploy.sh your-domain.com
```

### Query as an agent

```bash
# Get stats
curl http://registry.adamdoesai.com:9847/stats

# Search for video models
curl http://registry.adamdoesai.com:9847/search?q=video

# Get best models by modality
curl http://registry.adamdoesai.com:9847/best_models?modality=video

# Compare models
curl http://registry.adamdoesai.com:9847/compare?models=veo-3.1,kling-3-pro
```

## Platforms

This skill is compatible with:
- Hermes
- OpenClaw
- Claude Code
- Cursor
- VS Code
- Codex
- ChatGPT

## Security

- Read-only GET API — no POST, no PUT, no DELETE
- No CORS (agents don't need it)
- No authentication required (public read-only)
- No database (in-memory cache)
- No secrets in code
- Pinned dependencies (exact versions, no ranges)
- OWASP AST10 audited and compliant

## About

Built by **Adam Hall** — [adamdoesai.com](https://adamdoesai.com)

AI infrastructure for agents that need accurate, real-time model information across every GenAI modality. Part of the Adam Does AI toolkit.

---

## License — All Rights Reserved

Copyright (c) 2026 Adam Hall. All Rights Reserved.

### End User License Agreement (EULA)

**1. Grant of License.** Adam Hall ("Licensor") grants you ("Licensee") a non-exclusive, non-transferable, revocable license to use the AI Model Registry software ("Software") for your personal or internal business use.

**2. Restrictions.** Licensee shall NOT:
   - (a) Redistribute, resell, sublicense, lease, rent, or otherwise transfer the Software to any third party
   - (b) Reverse engineer, decompile, or disassemble the Software, except as permitted by applicable law
   - (c) Remove or alter any copyright, trademark, or attribution notices within the Software
   - (d) Use the Software to build a competing product or service
   - (e) Include the Software in any open-source project or public repository

**3. Updates.** Licensor may provide updates to the commercial models file on a regular cadence. Updates are available to Licensees who have purchased a license. The frequency of updates is at Licensor's discretion and will be communicated to Licensees.

**4. Commercial Models File.** The `commercial_models.json` file is manually maintained by the Licensor and represents proprietary research. Licensee may use it as part of the Software but may not redistribute it separately.

**5. No Warranty.** The Software is provided "AS IS" without warranty of any kind. Licensor does not guarantee the accuracy, completeness, or timeliness of model information. Model availability and pricing are subject to change by their respective providers.

**6. Liability.** Licensor shall not be liable for any damages arising from the use or inability to use the Software, including but not limited to data loss, business interruption, or incorrect model recommendations.

**7. Termination.** This license terminates automatically if Licensee breaches any term. Upon termination, Licensee must cease all use of the Software and destroy all copies.

**8. Entire Agreement.** This EULA constitutes the entire agreement between Licensor and Licensee regarding the Software.

For licensing inquiries: [adamdoesai.com](https://adamdoesai.com)