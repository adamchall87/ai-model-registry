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
| `GET /stats` | Total model count, breakdown by source and modality (also serves as health check) |
| `GET /models` | List all models, optionally filtered by source |
| `GET /models?source=commercial` | Filter by source (openrouter, huggingface, ollama, commercial) |
| `GET /models/search?q=<query>` | Full-text search across all models |
| `GET /models/search?q=video&modality=video` | Filter by modality (llm, image, video, audio, vision, 3d) |
| `GET /models/best?capability=video_gen` | Top models by capability (video_gen, image_gen, audio_tts, coding, vision, tools, agent) |
| `GET /models/compare?models=google/veo-3.1,kling/kling-3-pro` | Side-by-side model comparison |
| `GET /models/by-modality/video` | All models for a given modality |
| `GET /models/by-source/commercial` | All models from a given source |

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
curl "http://registry.adamdoesai.com:9847/models/search?q=video"

# Get best video generation models
curl "http://registry.adamdoesai.com:9847/models/best?capability=video_gen"

# Compare two models
curl "http://registry.adamdoesai.com:9847/models/compare?models=google/veo-3.1,kling/kling-3-pro"

# List commercial models
curl "http://registry.adamdoesai.com:9847/models?source=commercial"
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

---

## Built by Adam Hall — Adam Does AI

This registry is part of **[Adam Does AI](https://adamdoesai.com)** — practical AI integration and automation for small businesses. I build systems that help businesses book more jobs, handle more work without adding payroll, and stop losing time to disconnected tools and repetitive manual work.

**What I do:**
- **AI-Powered Booking & Reception** — AI voice receptionists, missed-call text-back, lead qualification, and after-hours call handling
- **Custom AI Integration** — connect CRM, inbox, documents, scheduling, and business tools into systems that automate handoffs, follow-up, estimates, and invoicing
- **Standard Packages** — proven setups for calls, booking, follow-up, and customer pipeline, configured for your business with ongoing support
- **Open-Source AI Infrastructure** — tools like this model registry, agent skill frameworks, and MCP servers that make AI agents actually useful

**Why this registry exists:** AI agents running on stale training data will recommend GPT-4o like it's still 2024. This registry gives agents a live, accurate view of what models actually exist right now — across every modality. It's the kind of infrastructure that separates toy demos from production workflows.

[adamdoesai.com](https://adamdoesai.com)

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
