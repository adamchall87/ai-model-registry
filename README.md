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

## Platforms

Compatible with Hermes, OpenClaw, Claude Code, Cursor, VS Code, Codex, and ChatGPT.

## Security

- Read-only GET API — no POST, no PUT, no DELETE
- No CORS, no authentication, no database, no secrets
- Pinned dependencies, OWASP AST10 audited

## Quick Start

```bash
git clone <repo-url> && cd ai-model-registry
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.server:app --host 0.0.0.0 --port 9847
```

Or deploy with systemd + nginx:

```bash
bash deploy/deploy.sh your-domain.com
```

---

## Built by Adam Hall — Adam Does AI

This registry is part of the **[Adam Does AI](https://adamdoesai.com)** toolkit — hands-on AI engineering, agent infrastructure, and tools for builders who need things that actually work. No hype, no AI slop, no "prompt engineering" courses. Just real software and real deployments.

**What I do:**
- **AI Agent Infrastructure** — custom registries, MCP servers, toolchains that agents can actually query and trust
- **Secure Skill Authoring** — OWASP AST10-compliant skill creation and auditing for the agent skills marketplace
- **Private AI Deployments** — self-hosted LLMs, ComfyUI workflows, GPU-accelerated inference on real hardware
- **Content & Media Production** — video generation tools, HyperFrames compositions, and media pipelines built on open-source tech
- **Consulting & Builds** — custom AI tooling for businesses that need more than a ChatGPT wrapper

**Why this registry exists:** AI agents running on stale training data will recommend GPT-4o like it's still 2024. This registry gives agents a live, accurate view of what models actually exist right now — across every modality. It's the kind of infrastructure that separates toy demos from production workflows.

**Need something built?** [adamdoesai.com](https://adamdoesai.com) — reach out. I build the stuff that makes AI agents actually useful, not just chatty.

---

## License — All Rights Reserved

Copyright (c) 2026 Adam Hall. All Rights Reserved.

### End User License Agreement (EULA)

**1. Grant of License.** Adam Hall ("Licensor") grants you ("Licensee") a non-exclusive, non-transferable, revocable license to use the AI Model Registry software ("Software") for your personal or internal business use.

**2. Restrictions.** Licensee shall NOT: (a) Redistribute, resell, sublicense, lease, rent, or otherwise transfer the Software to any third party; (b) Reverse engineer, decompile, or disassemble the Software; (c) Remove or alter any copyright, trademark, or attribution notices; (d) Use the Software to build a competing product or service; (e) Include the Software in any open-source project or public repository.

**3. Commercial Models Updates.** The `commercial_models.json` file is manually maintained and updated on a regular cadence. Licensees receive updates as part of their license. Frequency of updates is at Licensor's discretion.

**4. No Warranty.** The Software is provided "AS IS" without warranty of any kind. Model availability and pricing are subject to change by their respective providers.

**5. Liability.** Licensor shall not be liable for any damages arising from the use or inability to use the Software.

**6. Termination.** This license terminates automatically if Licensee breaches any term. Upon termination, Licensee must cease all use and destroy all copies.

For licensing inquiries: [adamdoesai.com](https://adamdoesai.com)