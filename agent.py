#!/usr/bin/env python3
"""ai-agent-starter — minimal production-shaped tool-calling agent.

Swap the demo tools for your own (DB queries, APIs, scrapers) to build
real automation agents. Uses any OpenAI-compatible endpoint.
"""
import argparse
import json
import sys

import requests
from openai import OpenAI

DEFAULT_MODEL = "deepseek-v4-pro"
MAX_ITERATIONS = 6

# ---------- tools ----------

def calculate(expression: str) -> str:
    """Safely evaluate a simple arithmetic expression."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Error: invalid characters in expression"
    try:
        return str(eval(expression, {"__builtins__": {}}))  # noqa: S307 — input sanitized above
    except Exception as exc:  # noqa: BLE001
        return f"Error: {exc}"


def read_webpage(url: str) -> str:
    """Fetch a webpage and return its readable text (first 3000 chars)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; agent-demo/1.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return f"Error fetching page: {exc}"
    try:
        from bs4 import BeautifulSoup
        text = BeautifulSoup(resp.text, "html.parser").get_text(" ", strip=True)
    except ImportError:
        text = resp.text
    return text[:3000]


TOOLS = {"calculate": calculate, "read_webpage": read_webpage}

TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate an arithmetic expression like '1234*5678' or '(100+50)/3'",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "Arithmetic expression"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_webpage",
            "description": "Fetch a URL and return its readable text content (first 3000 chars)",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "Full https:// URL"}},
                "required": ["url"],
            },
        },
    },
]

# ---------- agent loop ----------

def run_agent(task: str, model: str) -> str:
    client = OpenAI()  # uses OPENAI_API_KEY; set base_url for compatible endpoints
    messages = [
        {"role": "system", "content": "You are a precise assistant. Use tools when they help. Think step by step, then give a final concise answer."},
        {"role": "user", "content": task},
    ]
    for i in range(1, MAX_ITERATIONS + 1):
        resp = client.chat.completions.create(model=model, messages=messages, tools=TOOL_SPECS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content or ""
        messages.append(msg)
        for call in msg.tool_calls:
            fn_name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            print(f"[tool {i}] {fn_name}({args})")
            result = TOOLS.get(fn_name, lambda **_: f"Unknown tool: {fn_name}")(**args)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result[:4000]})
    return "Stopped: max iterations reached."


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Minimal tool-calling agent")
    ap.add_argument("task", help="Task for the agent")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="Model name on your OpenAI-compatible endpoint")
    args = ap.parse_args()
    print(run_agent(args.task, args.model))
