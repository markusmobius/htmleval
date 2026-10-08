"""Model clients behind one protocol, so the filler does not care which service answers.

``ModelClient.ask(system, user, schema, tags)`` sends one structured-output request and returns the parsed JSON
reply (or None when the service gave no answer). Two adapters ship:
  * ``LlmClientAdapter``: the in-house LlmClient (an optional dependency, imported only when used). It keeps a pool
    of connected clients and hands each in-flight call its own, because one LlmClient holds one reply future per
    connection: concurrent asks on a shared client receive each other's answers and the wrong answer lands in its
    local cache.
  * ``OpenAIAdapter``: any OpenAI-compatible chat-completions endpoint reached with an API key, using ``requests``
    only (the library's one dependency).
"""
import asyncio
import json
import os
from typing import Protocol


class ModelClient(Protocol):
    model: str

    async def ask(self, system: str, user: str, schema: dict, tags: list[str] | None = None,
                  timeout: float | None = None) -> dict | None:
        """One structured request. ``timeout`` (seconds) covers the request itself, not the wait for a free worker."""
        ...

    async def close(self) -> None: ...


class LlmClientAdapter:
    """The in-house LlmClient: ``workers`` connected clients, one per in-flight call."""

    def __init__(self, model: str, workers: int = 6):
        from LlmClient.LlmLib import LlmFactory      # optional dependency
        from LlmClient.Models import Chat
        self._factory, self._Chat = LlmFactory, Chat
        self.model = model
        self.workers = max(1, workers)
        self._pool = None
        self._lock = asyncio.Lock()

    async def _pool_ready(self):
        # Built once, under a lock: the first asks arrive concurrently, and without the lock each of them would
        # open its own set of connections (the server caps them, and every call then fails to connect).
        if self._pool is None:
            async with self._lock:
                if self._pool is None:
                    pool = asyncio.Queue()
                    for _ in range(self.workers):
                        pool.put_nowait(await self._factory().create_client())
                    self._pool = pool
        return self._pool

    async def ask(self, system, user, schema, tags=None, timeout=None):
        pool = await self._pool_ready()
        client = await pool.get()
        if client is None:                                  # a slot whose client was dropped: connect a fresh one
            client = await self._factory().create_client()
        keep = True
        try:
            chat = self._Chat(responseSchema=schema, model=self.model)
            chat.AddSystemMessage(system)
            chat.AddUserMessage(user)
            request = client.Ask(chat, tags=list(tags or []))
            out = await (asyncio.wait_for(request, timeout) if timeout else request)
            if out is None or out.answer is None:
                return None
            raw = out.answer.ChatAnswer
            return json.loads(raw) if isinstance(raw, str) else raw
        except BaseException:
            # A timed-out or cancelled request may still be answered by the server; a client with a reply in flight
            # would hand that reply to the next call (and to the local cache). The slot stays, the client is dropped.
            keep = False
            raise
        finally:
            pool.put_nowait(client if keep else None)

    async def close(self):
        return None


class OpenAIAdapter:
    """An OpenAI-compatible ``/chat/completions`` endpoint with an API key (argument or ``OPENAI_API_KEY``).
    Requests run in threads, at most ``workers`` at a time."""

    def __init__(self, model: str, api_key: str | None = None, base_url: str = "https://api.openai.com/v1",
                 workers: int = 6, timeout: float = 900.0):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAIAdapter needs an API key (argument api_key= or the OPENAI_API_KEY environment variable)")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._sem = asyncio.Semaphore(max(1, workers))

    def request_body(self, system, user, schema) -> dict:
        return {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_schema", "json_schema": {"name": "answers", "schema": schema, "strict": True}},
        }

    def _post(self, system, user, schema, timeout=None):
        import requests
        r = requests.post(self.base_url + "/chat/completions", json=self.request_body(system, user, schema),
                          headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                          timeout=timeout or self.timeout)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        return json.loads(content) if isinstance(content, str) else content

    async def ask(self, system, user, schema, tags=None, timeout=None):
        async with self._sem:
            return await asyncio.to_thread(self._post, system, user, schema, timeout)

    async def close(self):
        return None


def make_client(kind: str, model: str, **kw) -> ModelClient:
    """``kind``: "llmclient" or "openai"; the keyword arguments go to the adapter."""
    if kind == "llmclient":
        return LlmClientAdapter(model, workers=kw.get("workers", 6))
    if kind == "openai":
        return OpenAIAdapter(model, api_key=kw.get("api_key"), base_url=kw.get("base_url") or "https://api.openai.com/v1",
                             workers=kw.get("workers", 6))
    raise ValueError(f"unknown client kind {kind!r}: use 'llmclient' or 'openai'")
