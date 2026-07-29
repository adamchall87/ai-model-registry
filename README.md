# AI Model Registry

A live AI model registry for every major GenAI modality. Polls OpenRouter, HuggingFace, and Ollama Cloud hourly, plus a manually maintained commercial models file. Built so AI agents never recommend outdated models from stale training data.

895 models. Hourly updates. Read-only public API. No auth, no database, no moving parts.

## Live Endpoint

```
http://registry.adamdoesai.com:9847
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /stats` | Total model count, breakdown by source and modality |
| `GET /search?q=<query>` | Full-text search across all models |
| `GET /best_models?modality=video` | Top models by modality, sorted by downloads |
| `GET /compare?models=veo-3.1,kling-3-pro` | Side-by-side model comparison |
| `GET /health` | Health check |

## Model Sources

| Source | Count | Method | Coverage |
|--------|-------|--------|----------|
| OpenRouter | 367 | Live API (hourly) | LLMs with pricing |
| HuggingFace | 482 | Live API (hourly) | All modalities |
| Ollama Cloud | 19 | Live API (hourly) | LLMs + vision |
| Commercial | 27 | Manual updates | Closed-source video, image, audio |

**Total: 895 models across all GenAI modalities.**

## Platforms

Hermes, OpenClaw, Claude Code, Cursor, VS Code, Codex, ChatGPT.

## Quick Start

```bash
git clone <repo-url> && cd ai-model-registry
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.server:app --host 0.0.0.0 --port 9847
```

Or deploy with systemd:

```bash
bash deploy/deploy.sh your-domain.com
```

---

## About the Author

Built by **Adam Hall**, founder of [Adam Does AI](https://adamdoesai.com).

I build practical AI tools and integrations — whether you're running a small business, working on a personal project, or just trying to get something useful out of AI without the hype. No buzzwords, no "prompt engineering" courses, no AI slop. Just real software and real results.

This registry is one of the tools I use in my own work and offer to anyone who needs reliable, current model data. If you need custom AI infrastructure, a model registry configured for your stack, or help making AI actually useful, reach out.

[adamdoesai.com](https://adamdoesai.com)

---

## License — All Rights Reserved

Copyright (c) 2026 Adam Hall. All Rights Reserved.

### End User License Agreement (EULA)

**1. Grant of License.** Adam Hall ("Licensor") grants you ("Licensee") a non-exclusive, non-transferable, revocable license to use this Software for your personal or internal business use.

**2. Restrictions.** Licensee shall NOT: (a) Redistribute, resell, sublicense, or transfer the Software; (b) Reverse engineer or decompile; (c) Remove copyright or attribution notices; (d) Use to build a competing product; (e) Include in any open-source project or public repository.

**3. Updates.** The commercial models file is manually maintained and updated regularly. Licensees receive updates as part of their license.

**4. No Warranty.** Provided "AS IS" without warranty. Model data may change.

**5. Liability.** Licensor not liable for damages from use or inability to use.

**6. Termination.** License terminates on breach. Cease use, destroy copies.

For licensing: [adamdoesai.com](https://adamdoesai.com)