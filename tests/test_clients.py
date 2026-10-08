"""Unit of analysis: one model request. The OpenAI adapter must send a strict JSON-schema request and parse the reply."""
import asyncio
import json
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from src.modelReview.clients import OpenAIAdapter, make_client  # noqa: E402
from src.modelReview.fill import SCHEMA  # noqa: E402


class LlmClientPool(unittest.TestCase):
    def test_concurrent_first_asks_build_one_pool(self):
        """20 asks arriving at once must open `workers` connections, not 20 x workers."""
        import types
        from src.modelReview.clients import LlmClientAdapter
        created = []

        class FakeClient:
            async def Ask(self, chat, tags=None):
                await asyncio.sleep(0)
                return types.SimpleNamespace(answer=types.SimpleNamespace(ChatAnswer='{"answers": []}'))

        class FakeFactory:
            async def create_client(self):
                await asyncio.sleep(0)          # yield, so the other asks get their chance to race
                created.append(1)
                return FakeClient()

        class FakeChat:
            def __init__(self, responseSchema=None, model=None): pass
            def AddSystemMessage(self, s): pass
            def AddUserMessage(self, u): pass

        adapter = LlmClientAdapter.__new__(LlmClientAdapter)
        adapter._factory, adapter._Chat = FakeFactory, FakeChat
        adapter.model, adapter.workers, adapter._pool, adapter._lock = "m", 6, None, asyncio.Lock()

        async def run():
            return await asyncio.gather(*(adapter.ask("s", f"u{i}", SCHEMA) for i in range(20)))
        out = asyncio.run(run())
        self.assertEqual(len(out), 20)
        self.assertEqual(len(created), 6)


class LlmClientCancel(unittest.TestCase):
    def test_a_timed_out_client_is_dropped_and_its_slot_reconnected(self):
        """A request cut off by the timeout may still get its reply; that client must never serve the next call."""
        import types
        from src.modelReview.clients import LlmClientAdapter
        created, served = [], []

        class SlowClient:
            def __init__(self, n): self.n = n
            async def Ask(self, chat, tags=None):
                served.append(self.n)
                if self.n == 0:
                    await asyncio.sleep(10)                   # the first client hangs
                return types.SimpleNamespace(answer=types.SimpleNamespace(ChatAnswer='{"answers": []}'))

        class Factory:
            async def create_client(self):
                created.append(len(created)); return SlowClient(len(created) - 1)

        class FakeChat:
            def __init__(self, responseSchema=None, model=None): pass
            def AddSystemMessage(self, s): pass
            def AddUserMessage(self, u): pass

        a = LlmClientAdapter.__new__(LlmClientAdapter)
        a._factory, a._Chat, a.model, a.workers, a._pool, a._lock = Factory, FakeChat, "m", 1, None, asyncio.Lock()

        async def run():
            with self.assertRaises(asyncio.TimeoutError):
                await a.ask("s", "u", SCHEMA, timeout=0.01)
            return await a.ask("s", "u2", SCHEMA, timeout=1)
        out = asyncio.run(run())
        self.assertEqual(out, {"answers": []})
        self.assertEqual(created, [0, 1])                     # the hung client was replaced, not recycled
        self.assertEqual(served, [0, 1])


class OpenAI(unittest.TestCase):
    def test_request_shape_and_reply_parsing(self):
        sent = {}

        def post(url, json=None, headers=None, timeout=None):
            sent.update(url=url, body=json, headers=headers)
            reply = {"choices": [{"message": {"content": '{"answers": [{"row_id": "r", "value": "yes", "reason": "ok"}]}'}}]}
            return mock.Mock(raise_for_status=lambda: None, json=lambda: reply)

        client = OpenAIAdapter("gpt-x", api_key="sk-test", base_url="https://api.example/v1/")
        with mock.patch("requests.post", post):
            out = asyncio.run(client.ask("SYS", "USER", SCHEMA, ["t"]))
        self.assertEqual(out, {"answers": [{"row_id": "r", "value": "yes", "reason": "ok"}]})
        self.assertEqual(sent["url"], "https://api.example/v1/chat/completions")
        self.assertEqual(sent["headers"]["Authorization"], "Bearer sk-test")
        body = sent["body"]
        self.assertEqual(body["model"], "gpt-x")
        self.assertEqual(body["messages"], [{"role": "system", "content": "SYS"}, {"role": "user", "content": "USER"}])
        self.assertEqual(body["response_format"]["type"], "json_schema")
        self.assertTrue(body["response_format"]["json_schema"]["strict"])
        self.assertEqual(body["response_format"]["json_schema"]["schema"], SCHEMA)

    def test_needs_a_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                OpenAIAdapter("gpt-x")

    def test_make_client_rejects_unknown_kinds(self):
        with self.assertRaises(ValueError):
            make_client("other", "m")


if __name__ == "__main__":
    unittest.main()
