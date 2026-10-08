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
