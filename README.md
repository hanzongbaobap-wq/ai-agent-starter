# AI Agent Starter (Python)

A minimal but production-shaped AI agent: a tool-calling loop with real tools (calculator + web page reader), structured messages, and clean error handling.

Not a toy chatbot — this is the same architecture used for real automation agents (content ops, monitoring, reporting).

Built by a senior engineer (ex-IBM / Accenture). Available for custom AI agent work on Upwork.

## Architecture

```
User task ──► Agent loop ──► LLM decides: answer OR call a tool
                    ▲                      │
                    └──── tool result ─────┘
```

- **Tools** are plain Python functions registered in a dict — swap in your own (DB queries, APIs, scrapers)
- **Loop guard**: max iterations to prevent runaway runs
- **Structured output**: final answer printed clean, tool calls logged

## Quick Start

```bash
pip install openai requests beautifulsoup4
export OPENAI_API_KEY=sk-...
python agent.py "Read https://example.com and tell me the main heading, then compute 1234*5678"
```

## Add your own tool

```python
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    ...  # call your API, return a string

TOOLS["get_weather"] = get_weather
TOOL_SPECS.append({"type": "function", "function": {
    "name": "get_weather",
    "description": "Get current weather for a city",
    "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}
}})
```

## Production notes

- Swap `openai` client base_url for any OpenAI-compatible endpoint (local models, DeepSeek, etc.)
- Add a cost counter per run before deploying unattended
- Log every tool call — you will need the audit trail

## License

MIT
