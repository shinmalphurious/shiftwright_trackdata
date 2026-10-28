"""Minimal client for a local Ollama server (no extra dependencies).

OLLAMA_URL overrides the address (default http://localhost:11434) and OLLAMA_MODEL the
default model.
"""
import json
import os
import urllib.error
import urllib.request

URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:14b")


class OllamaError(RuntimeError):
    pass


def _post(path, body, timeout):
    req = urllib.request.Request(f"{URL}{path}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as ex:
        raise OllamaError(f"Ollama {ex.code}: {ex.read()[:300].decode(errors='replace')}") from ex
    except (urllib.error.URLError, OSError) as ex:
        raise OllamaError(f"Ollama not reachable at {URL}: {ex}") from ex


def chat_json(system, user, schema, model=MODEL, num_ctx=16384, timeout=900):
    """One chat turn whose reply must match the JSON schema. Returns the parsed object."""
    reply = _post("/api/chat", {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "format": schema,
        "stream": False,
        "keep_alive": "10m",
        "options": {"temperature": 0, "num_ctx": num_ctx},
    }, timeout)
    content = (reply.get("message") or {}).get("content") or ""
    try:
        return json.loads(content)
    except json.JSONDecodeError as ex:
        raise OllamaError(f"reply is not JSON: {content[:200]}") from ex


def available_models():
    req = urllib.request.Request(f"{URL}/api/tags")
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return [m["name"] for m in json.loads(res.read()).get("models", [])]
    except (urllib.error.URLError, OSError) as ex:
        raise OllamaError(f"Ollama not reachable at {URL}: {ex}") from ex
