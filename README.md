# AI Model Registry

Live AI model registry that polls OpenRouter, HuggingFace, and Ollama Cloud hourly.
Provides agents (Hermes, OpenClaw, Claude Code) with up-to-date model information so they
never recommend outdated models from stale training data.

## Architecture

```
┌─────────────────────────────────────────────┐
│         AI Model Registry (FastAPI)          │
│                                              │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐ │
│  │OpenRouter│  │HuggingFace│  │Ollama Cloud │ │
│  │  poller  │  │  poller   │  │   poller    │ │
│  └────┬─────┘  └─────┬─────┘  └──────┬──────┘ │
│       └──────────────┼────────────────┘      │
│                      ▼                        │
│              In-Memory Cache                   │
│                      │                        │
│         ┌────────────┼────────────┐           │
│         ▼            ▼            ▼           │
│    REST API    MCP Server    Hermes Skill      │
│  (port 8000)  (stdio)     (SKILL.md)          │
└─────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone
git clone <your-repo> ai-model-registry
cd ai-model-registry

# Install
pip install -r requirements.txt

# Run the API server
python -m uvicorn src.server:app --port 8000

# In another terminal, test it
curl http://localhost:8000/
curl http://localhost:8000/models/best?capability=coding
curl http://localhost:8000/models/search?q=kimi
```

## Deploy on VPS (systemd)

```bash
# Copy to VPS
scp -r ai-model-registry user@vps:/opt/ai-model-registry

# Install deps
cd /opt/ai-model-registry
pip install -r requirements.txt

# Install service
sudo cp deploy/ai-model-registry.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ai-model-registry

# Verify
curl http://localhost:8000/
```

## MCP Integration (Hermes)

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  model_registry:
    command: "python3"
    args: ["/opt/ai-model-registry/src/mcp_server.py"]
    env:
      REGISTRY_API_URL: "http://localhost:8000"
```

Then copy the skill:

```bash
cp -r skill /path/to/.hermes/skills/ai-model-registry
```

Restart Hermes. Tools will appear as:
- `mcp_model_registry_list_models`
- `mcp_model_registry_search_models`
- `mcp_model_registry_best_models`
- `mcp_model_registry_registry_stats`

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Health check + cache info |
| `GET /models` | List models with filters (source, capability, min_context, max_input_price, limit, offset) |
| `GET /models/search?q=X` | Search by name/id/description |
| `GET /models/best?capability=X` | Best models for a capability (coding, vision, tools, reasoning, agent, general, cheapest, largest_context) |
| `GET /models/by-source/{source}` | Filter by provider |
| `POST /refresh` | Manual refresh |
| `GET /stats` | Registry statistics |

## Environment Variables

| Var | Default | Description |
|-----|---------|-------------|
| `POLL_INTERVAL` | `3600` | Seconds between polls (1 hour) |
| `OLLAMA_API_KEY` | (empty) | Ollama Cloud API key for full model listing |
| `REGISTRY_API_URL` | `http://localhost:8000` | URL for MCP server to connect to |

## Data Sources

- **OpenRouter**: `GET https://openrouter.ai/api/v1/models` — 400+ models with pricing
- **HuggingFace**: `GET https://huggingface.co/api/models` — Hub models + inference models
- **Ollama Cloud**: `GET https://ollama.com/api/tags` — Cloud models (API key optional)