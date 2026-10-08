"""Unit of analysis: one generated review page. The template placeholders must be filled only in the template,
never inside page content, and the non-interactive paths must never call input()."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from src.reviewLib import Review  # noqa: E402
from src.json.reviewJsonLib import ReviewJSON  # noqa: E402
from src.json.simpleBlocks.text import Text  # noqa: E402

SERVER = "https://example.test/kv/"


class TemplateFill(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        sys.stdin = open(os.devnull)        # any input() call fails loudly instead of hanging

    def tearDown(self):
        sys.stdin = sys.__stdin__
        shutil.rmtree(self.dir)

    def test_placeholder_words_inside_page_content_survive(self):
        body = "Set the DEFAULTS before BUILDJS; READONLY and SERVERURL and REVIEWERID are words. BLOCKDATA too."
        block = ReviewJSON(Text(title="EVALTITLE is a word", body=[body], model={"text": "DEFAULTS"})).get_json()
        Review(block=block, evalTitle="My Review", serverURL=SERVER).create(
            targetFolder=self.dir, defaults={"k": "v"}, reviewers=["r1"], reviewerIds={"r1": "id-1"})
        html = open(os.path.join(self.dir, "review_r1.html"), encoding="utf-8").read()
        self.assertIn(json.dumps(body), html)                       # the body is embedded untouched
        self.assertIn('"EVALTITLE is a word"', html)
        self.assertIn('var rootBlock = {"type": "text"', html)
        self.assertIn('var dataDefaults = {"k": "v"};', html)
        self.assertIn('var readOnly = false;', html)
        self.assertIn('var reviewerID = "id-1";', html)
        self.assertIn(f'var serverURL = "{SERVER}";', html)
        self.assertIn(f'fetch("{SERVER}" + reviewerID', html)        # the library's own JS still gets the server
        for token in ("BLOCKDATA", "BUILDJS", "READONLY", "DEFAULTS", "SERVERURL", "REVIEWERID", "REVIEWERNAME"):
            self.assertEqual(html.count(token), body.count(token) + (1 if token == "DEFAULTS" else 0), token)

    def test_overwrite_flag_replaces_or_keeps_without_asking(self):
        block = ReviewJSON(Text(body=["one"])).get_json()
        review = Review(block=block, evalTitle="T", serverURL=SERVER)
        review.create(targetFolder=self.dir, defaults=None, reviewers=["r1"], reviewerIds={"r1": "id-1"})
        path = os.path.join(self.dir, "review_r1.html")
        first = open(path, encoding="utf-8").read()
        Review(block=ReviewJSON(Text(body=["two"])).get_json(), evalTitle="T", serverURL=SERVER).create(
            targetFolder=self.dir, defaults=None, reviewers=["r1"], overwrite=False)
        self.assertEqual(open(path, encoding="utf-8").read(), first)
        Review(block=ReviewJSON(Text(body=["two"])).get_json(), evalTitle="T", serverURL=SERVER).create(
            targetFolder=self.dir, defaults=None, reviewers=["r1"], overwrite=True)
        self.assertIn('"two"', open(path, encoding="utf-8").read())
        self.assertEqual(json.load(open(os.path.join(self.dir, "reviewer_ids.json"))), {"r1": "id-1"})


class ClonedPage(unittest.TestCase):
    def test_a_cloned_page_keeps_the_custom_element_js_and_swaps_the_reviewer(self):
        import tempfile
        from src.reviewLib import addCustomElement, _CUSTOM_ELEMENTS
        d = tempfile.mkdtemp()
        try:
            addCustomElement("x-probe", "customElements.define('x-probe', class extends HTMLElement {});")
            block = ReviewJSON(Text(body=["<x-probe></x-probe>"])).get_json()
            Review(block=block, evalTitle="T", serverURL=SERVER).create(targetFolder=d, defaults=None, reviewers=["henry"], reviewerIds={"henry": "id-h"})
        finally:
            _CUSTOM_ELEMENTS.pop("x-probe", None)
        src = os.path.join(d, "review_henry.html"); dst = os.path.join(d, "review_astra.html")
        Review.clone_reviewer_page(src, dst, "astra", "id-a")
        html = open(dst, encoding="utf-8").read()
        self.assertIn("customElements.define('x-probe'", html)
        self.assertIn('var reviewerID = "id-a";', html)
        self.assertIn('<dd class="col-sm-2">astra</dd>', html)
        self.assertNotIn('"id-h"', html)
        self.assertEqual(Review.page_block(dst), json.loads(block))
        shutil.rmtree(d)


class Reviewers(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.review = Review(block="{}", evalTitle="T", serverURL=SERVER)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_register_reviewer_keeps_existing_ids(self):
        a = self.review.register_reviewer(self.dir, "astra")
        b = self.review.register_reviewer(self.dir, "astra")
        self.assertEqual(a, b)
        self.assertEqual(json.load(open(os.path.join(self.dir, "reviewer_ids.json"))), {"astra": a})

    def test_upload_puts_the_blob_and_verifies_the_round_trip(self):
        blob = {"active": {}, "variables": {'["r","q"]': "yes"}, "timestamps": {}}
        store = {}

        def put(url, data=None, headers=None, timeout=None):
            store[url] = json.loads(data)
            return mock.Mock(raise_for_status=lambda: None)

        def get(url, timeout=None):
            return mock.Mock(raise_for_status=lambda: None, json=lambda: store[url])

        with mock.patch("src.reviewLib.requests.put", put), mock.patch("src.reviewLib.requests.get", get):
            url = self.review.upload(self.dir, "astra", blob)
        rid = json.load(open(os.path.join(self.dir, "reviewer_ids.json")))["astra"]
        self.assertEqual(url, SERVER + rid)
        self.assertEqual(store[url], blob)

    def test_upload_raises_when_the_server_returns_something_else(self):
        blob = {"active": {}, "variables": {'["r","q"]': "yes"}, "timestamps": {}}
        with mock.patch("src.reviewLib.requests.put", lambda *a, **k: mock.Mock(raise_for_status=lambda: None)), \
                mock.patch("src.reviewLib.requests.get", lambda *a, **k: mock.Mock(raise_for_status=lambda: None, json=lambda: {"variables": {}})):
            with self.assertRaises(RuntimeError):
                self.review.upload(self.dir, "astra", blob)


if __name__ == "__main__":
    unittest.main()
