"""Unit of analysis: one call. Slicing, follow-ups and parsing must keep every answer on the page's own keys."""
import asyncio
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from src.modelReview import fill as F  # noqa: E402
from src.modelReview import render as mr  # noqa: E402
from src.json.reviewJsonLib import ReviewJSON  # noqa: E402
from src.json.compoundBlocks.tabs import Tabs  # noqa: E402
from src.json.compoundBlocks.column import Column  # noqa: E402
from src.json.simpleBlocks.multiRowSelect import MultiRowSelect, MultiRowSelectQuestion  # noqa: E402
from src.json.simpleBlocks.multiRowOption import MultiRowOption  # noqa: E402

YN = [MultiRowOption("Yes", "yes"), MultiRowOption("No", "no")]


def big_page(n_units=2, n_rows=13):
    root = Tabs(model={"page": {"format": "htmleval-model/1", "task": "a test form"}})
    for u in range(n_units):
        unit = Column(model={"unit": f"Item {u}", "text": ["Material line.", "Another line."]})
        q = MultiRowSelect(rowLabels=["Q"], questions=[MultiRowSelectQuestion("Fine?", id={1: "fine"}, options=YN)])
        for i in range(n_rows):
            q.add_row([f"row {i}"], id={0: f"{u}_r{i}"}, model={"about": f"About thing {i // 4}"})
        unit.add_column([q]); root.add_tab(f"Item {u}", unit)
    return ReviewJSON(root).get_json()


class FakeClient:
    model = "fake-model"

    def __init__(self, answer_fn):
        self.answer_fn = answer_fn; self.calls = []

    async def ask(self, system, user, schema, tags=None):
        self.calls.append((system, user))
        return self.answer_fn(user)

    async def close(self):
        return None


def answer_all(user, value="yes", skip=()):
    ids = [ln.split(": ", 1)[0] for ln in user.split("\n") if ": " in ln and ln.endswith("]")]
    return {"answers": [{"row_id": i, "value": value, "reason": "because"} for i in ids if i not in skip]}


class Slicing(unittest.TestCase):
    def test_slices_carry_their_about_lines_and_rejoin(self):
        js = big_page(1)
        lines, rows = mr.render_unit(js, "Item 0")
        with mock.patch.object(F, "MIN_ROWS_PER_CALL", 1):
            calls = F.slice_calls("u", lines, rows, max_rows=5, max_chars=10**9)
        self.assertGreater(len(calls), 1)
        self.assertEqual([r["row_id"] for _, _, rs in calls for r in rs], [r["row_id"] for r in rows])
        for _label, call_lines, call_rows in calls:
            text = F.prompt_text(call_lines)
            self.assertIn("Material line.", text)
            for r in call_rows:
                self.assertIn(f"\n{r['row_id']}: ", text)
            abouts = [ln for ln in text.split("\n") if ln.startswith("About thing")]
            self.assertEqual(len(abouts), len({r["row_id"].split("r")[1] and int(r["row_id"].split("r")[1]) // 4 for r in call_rows}))

    def test_followup_keeps_only_unanswered_questions(self):
        lines, rows = mr.render_unit(big_page(1), "Item 0")
        answered = {r["key"]: "yes" for r in rows if not r["row_id"].endswith(("r1", "r2"))}
        _label, kept, missing = F.followup("u", lines, rows, answered)
        text = F.prompt_text(kept)
        self.assertEqual(sorted(r["row_id"] for r in missing), ["0_r1", "0_r2"])
        self.assertIn("Material line.", text)
        self.assertIn("About thing 0", text)
        self.assertNotIn("About thing 2", text)
        self.assertNotIn("0_r3: ", text)


class Parsing(unittest.TestCase):
    def test_values_labels_and_repaired_ids(self):
        rows = [{"row_id": "12_action_9_categorized", "question_id": "q", "key": "k9", "options": {"yes": "Yes", "no_neither": "No — neither"}},
                {"row_id": "12_action_1_categorized", "question_id": "q", "key": "k1", "options": {"yes": "Yes", "no_neither": "No — neither"}}]
        raw = {"answers": [{"row_id": "12_action_9_categorated", "value": "YES", "reason": "a"},
                           {"row_id": "12_action_1_categorized", "value": "no — neither", "reason": "b"},
                           {"row_id": "nope", "value": "yes", "reason": "c"},
                           {"row_id": "12_action_1_categorized", "value": "maybe", "reason": "d"}]}
        variables, reasons, rejected = F.parse_answers(raw, rows)
        self.assertEqual(variables, {"k9": "yes", "k1": "no_neither"})
        self.assertEqual(reasons, {"12_action_9_categorized": "a", "12_action_1_categorized": "b"})
        self.assertEqual([why for _, why in rejected], ["repaired to 12_action_9_categorized", "unknown row_id", "value 'maybe' not an option"])

    def test_timestamp_key_and_blob(self):
        self.assertEqual(F.timestamp_key('["r","q"]'), '["r","timestamp"]')
        blob = F.answer_blob({'["r","q"]': "yes"})
        self.assertEqual(set(blob), {"active", "variables", "timestamps"})
        self.assertEqual(list(blob["timestamps"]), ['["r","timestamp"]'])


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        with open(os.path.join(self.dir, "eval.json"), "w", encoding="utf-8") as f:
            f.write(big_page(2))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_fill_writes_the_closed_file_in_the_human_shape_and_follows_up(self):
        skipped_once = set()

        def answer(user):
            # the first time row 0_r5 is asked it is left out, so the filler must re-ask it (task start order
            # is not deterministic, so the skip is keyed on the row, not on the call count)
            skip = () if "0_r5" in skipped_once else ("0_r5",)
            if "0_r5: " in user:
                skipped_once.add("0_r5")
            return answer_all(user, skip=skip)
        client = FakeClient(answer)
        import contextlib
        import io
        with mock.patch.object(F.asyncio, "sleep", mock.AsyncMock()), contextlib.redirect_stdout(io.StringIO()):
            result = asyncio.run(F.fill(self.dir, "fake", client, no_upload=True))
        self.assertEqual((result["answered"], result["total"], result["rejected"]), (26, 26, 0))
        closed = json.load(open(os.path.join(self.dir, "closed_fake.json")))
        self.assertEqual(set(closed), {"active", "variables", "timestamps"})
        self.assertEqual(len(closed["variables"]), 26)
        self.assertEqual(closed["variables"]['["0_r5","fine"]'], "yes")
        self.assertEqual(len(client.calls), 3)                                             # 2 units + 1 follow-up
        reasons = json.load(open(os.path.join(self.dir, "reasons_fake.json")))
        self.assertEqual(reasons["model"], "fake-model")
        self.assertIn("because", reasons["reasons"]["0_r0"])
        self.assertTrue(os.path.exists(os.path.join(self.dir, "fill_log_fake.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "reviewer_ids.json")))     # no upload, no registration
        self.assertIn("a test form", client.calls[0][0])                                   # the page's task in the system text

    def test_refuses_a_page_without_model_metadata(self):
        with open(os.path.join(self.dir, "plain.json"), "w", encoding="utf-8") as f:
            f.write(ReviewJSON(Tabs()).get_json())
        with self.assertRaises(ValueError):
            asyncio.run(F.fill(self.dir, "fake", FakeClient(answer_all), page="plain.json", no_upload=True))

    def test_dump_and_dry_run_make_no_calls(self):
        import contextlib
        import io
        client = FakeClient(answer_all)
        dump = os.path.join(self.dir, "dump")
        with contextlib.redirect_stdout(io.StringIO()):
            result = asyncio.run(F.fill(self.dir, "fake", client, dry_run=True, dump_dir=dump, no_upload=True))
        self.assertEqual(client.calls, [])
        self.assertEqual(result["total"], 26)
        self.assertEqual(sorted(os.listdir(dump)), ["0000.txt", "0001.txt", "system.txt"])
        self.assertTrue(open(os.path.join(dump, "0000.txt")).read().startswith("LABEL Item 0\nROWS 13\n\n"))


if __name__ == "__main__":
    unittest.main()
