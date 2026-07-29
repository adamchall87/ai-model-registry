"""
AI Model Registry — MCP Server (stdio transport).
Exposes registry tools to any MCP-compatible agent (Hermes, OpenClaw, Claude Code, etc.)

Tools exposed:
  - list_models: List models with optional filters (source, modality, capability, min_context, max_price)
  - search_models: Search by name/id/description
  - best_models: Get best models for a capability (coding, vision, tools, reasoning, agent, image_gen, video_gen, audio_tts, cheapest, largest_context)
  - compare_models: Compare specific models side-by-side with winners per dimension
  - registry_stats: Get registry statistics

Usage:
  Configure in Hermes config.yaml:
    mcp_servers:
      model_registry:
        command: "python3"
        args: ["/path/to/ai-model-registry/src/mcp_server.py"]
        env:
          REGISTRY_API_URL: "http://localhost:8000"
"""

import json
import os
import sys

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, ListToolsResult

REGISTRY_URL = os.environ.get("REGISTRY_API_URL", "http://localhost:8000")

app = Server("ai-model-registry")


@app.list_tools()
async def list_tools() -> ListToolsResult:
    return ListToolsResult(tools=[
        Tool(
            name="list_models",
            description="List AI models from the registry with optional filters. Use this BEFORE recommending any AI model to ensure you're referencing current models, not outdated training data. Supports filtering by modality (llm, image, video, audio, vision, 3d).",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Filter by provider: openrouter, huggingface, ollama, commercial",
                    },
                    "modality": {
                        "type": "string",
                        "description": "Filter by modality: llm, image, video, audio, vision, 3d, other",
                    },
                    "capability": {
                        "type": "string",
                        "description": "Filter by capability: coding, vision, tools, reasoning, free, local, cloud, image_gen, video_gen, tts",
                    },
                    "min_context": {
                        "type": "integer",
                        "description": "Minimum context length in tokens",
                    },
                    "max_input_price": {
                        "type": "number",
                        "description": "Maximum input price per 1M tokens",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 50, max 500)",
                        "default": 50,
                    },
                },
            },
        ),
        Tool(
            name="search_models",
            description="Search AI models by name, ID, or description. Use this to find the current version of a model (e.g. search 'gpt' to see what GPT models are available NOW, not what was available when your training data was cut). Can filter by modality.",
            inputSchema={
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "modality": {
                        "type": "string",
                        "description": "Filter by modality: llm, image, video, audio, vision, 3d",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 20)",
                        "default": 20,
                    },
                },
                "required": ["q"],
            },
        ),
        Tool(
            name="best_models",
            description="Get the best/current models for a given capability. Use this when someone asks 'what model should I use for X' — returns ranked list of current models. Capabilities: coding, vision, tools, reasoning, agent, general, cheapest, largest_context, image_gen, video_gen, audio_tts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "capability": {
                        "type": "string",
                        "description": "Capability to rank by: general, llm, coding, vision, tools, reasoning, agent, general, cheapest, largest_context, image_gen, video_gen, audio_tts",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 10)",
                        "default": 10,
                    },
                },
                "required": ["capability"],
            },
        ),
        Tool(
            name="compare_models",
            description="Compare specific AI models side-by-side. Pass 2+ model IDs and get a structured comparison with pricing, context, capabilities, and winners per dimension. Use when someone asks 'model A vs model B' or 'compare these models'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "models": {
                        "type": "string",
                        "description": "Comma-separated model IDs to compare (e.g. 'openai/gpt-5.6-sol,kimi-k3:cloud,zai-org/GLM-5.2')",
                    },
                },
                "required": ["models"],
            },
        ),
        Tool(
            name="registry_stats",
            description="Get statistics about the AI Model Registry — total models, breakdown by source and modality, counts of free/tool-capable/vision/thinking models, and when the registry was last polled.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ])


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        async with httpx.AsyncClient() as client:
            if name == "list_models":
                params = {}
                for k in ("source", "modality", "capability", "min_context", "max_input_price", "limit"):
                    if k in arguments:
                        params[k] = arguments[k]
                resp = await client.get(f"{REGISTRY_URL}/models", params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()

            elif name == "search_models":
                params = {"q": arguments["q"], "limit": arguments.get("limit", 20)}
                if "modality" in arguments:
                    params["modality"] = arguments["modality"]
                resp = await client.get(f"{REGISTRY_URL}/models/search", params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()

            elif name == "best_models":
                resp = await client.get(f"{REGISTRY_URL}/models/best", params={"capability": arguments["capability"], "limit": arguments.get("limit", 10)}, timeout=30)
                resp.raise_for_status()
                data = resp.json()

            elif name == "compare_models":
                resp = await client.get(f"{REGISTRY_URL}/models/compare", params={"models": arguments["models"]}, timeout=30)
                resp.raise_for_status()
                data = resp.json()

            elif name == "registry_stats":
                resp = await client.get(f"{REGISTRY_URL}/stats", timeout=10)
                resp.raise_for_status()
                data = resp.json()

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

            return [TextContent(type="text", text=json.dumps(data, indent=2))]

    except httpx.ConnectError:
        return [TextContent(type="text", text=f"Error: Could not connect to AI Model Registry at {REGISTRY_URL}. The service may not be running. Start it with: cd ai-model-registry && python -m uvicorn src.server:app --port 8000")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())