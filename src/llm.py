"""Thin, cached wrappers around the OpenAI chat + embedding APIs.

Caching is keyed on the full request payload, so a re-run of the same config
reuses prior generations verbatim. That makes a given run reproducible and cheap
to re-render, even though the generating temperature is > 0.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np
from openai import OpenAI

_CACHE_DIR = Path(__file__).resolve().parent.parent / "results" / "_cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_client: OpenAI | None = None
_anthropic = None


def client() -> OpenAI:
    global _client
    if _client is None:
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set (source seoul-2026-forecast/.env)")
        _client = OpenAI(api_key=key)
    return _client


def anthropic_client():
    global _anthropic
    if _anthropic is None:
        import anthropic  # local import so OpenAI-only runs don't need it
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set (source seoul-2026-forecast/.env)")
        _anthropic = anthropic.Anthropic(api_key=key)
    return _anthropic


def _cache_path(kind: str, payload: dict) -> Path:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    h = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:24]
    return _CACHE_DIR / f"{kind}_{h}.json"


def chat(messages: list[dict], model: str, temperature: float, max_tokens: int = 300, salt: str = "") -> str:
    # `salt` enters the cache key but is NOT sent to the API. It lets identical
    # prompts (e.g. SOLO across generations) draw fresh independent samples while
    # staying reproducible: the salt is deterministic in (condition, gen, creator).
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "salt": salt}
    cp = _cache_path("chat", payload)
    if cp.exists():
        return json.loads(cp.read_text())["text"]
    for attempt in range(6):
        try:
            r = client().chat.completions.create(
                model=model, messages=messages, temperature=temperature, max_tokens=max_tokens
            )
            text = r.choices[0].message.content.strip()
            cp.write_text(json.dumps({"text": text, "payload": payload}, ensure_ascii=False))
            return text
        except Exception as e:  # noqa: BLE001 - transient API errors
            wait = 2 ** attempt
            print(f"  [chat retry {attempt+1}: {type(e).__name__}; sleep {wait}s]")
            time.sleep(wait)
    raise RuntimeError("chat failed after retries")


def claude_judge(prompt: str, model: str = "claude-haiku-4-5-20251001", max_tokens: int = 8) -> str:
    """Cross-family judge (Anthropic) so the rater is not the same family as the generator.
    Cached by prompt; returns the raw text response."""
    payload = {"model": model, "prompt": prompt, "max_tokens": max_tokens}
    cp = _cache_path("judge", payload)
    if cp.exists():
        return json.loads(cp.read_text())["text"]
    for attempt in range(6):
        try:
            r = anthropic_client().messages.create(
                model=model, max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            text = r.content[0].text.strip()
            cp.write_text(json.dumps({"text": text, "payload": payload}, ensure_ascii=False))
            return text
        except Exception as e:  # noqa: BLE001
            wait = 2 ** attempt
            print(f"  [judge retry {attempt+1}: {type(e).__name__}; sleep {wait}s]")
            time.sleep(wait)
    raise RuntimeError("judge failed after retries")


def embed(texts: list[str], model: str = "text-embedding-3-small") -> np.ndarray:
    out: list[list[float]] = []
    to_fetch: list[str] = []
    fetch_idx: list[int] = []
    cached: dict[int, list[float]] = {}
    for i, t in enumerate(texts):
        cp = _cache_path("emb", {"model": model, "text": t})
        if cp.exists():
            cached[i] = json.loads(cp.read_text())["vec"]
        else:
            to_fetch.append(t)
            fetch_idx.append(i)
    if to_fetch:
        for attempt in range(6):
            try:
                r = client().embeddings.create(model=model, input=to_fetch)
                for j, item in enumerate(r.data):
                    vec = item.embedding
                    cached[fetch_idx[j]] = vec
                    cp = _cache_path("emb", {"model": model, "text": to_fetch[j]})
                    cp.write_text(json.dumps({"vec": vec}))
                break
            except Exception as e:  # noqa: BLE001
                wait = 2 ** attempt
                print(f"  [embed retry {attempt+1}: {type(e).__name__}; sleep {wait}s]")
                time.sleep(wait)
        else:
            raise RuntimeError("embed failed after retries")
    for i in range(len(texts)):
        out.append(cached[i])
    return np.array(out, dtype=np.float64)
