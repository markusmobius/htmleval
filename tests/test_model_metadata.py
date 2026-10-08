"""Unit of analysis: one block tree. The ``model`` metadata must ride along in the page JSON without changing
anything a page without it serializes, and ``page_questions`` must list exactly the answers a browser can write."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from src.json.answerKeys import page_keys  # noqa: E402
from src.json.model import check_declared_keys, html_to_text, page_meta, page_questions, strip_model  # noqa: E402
from src.json.reviewJsonLib import ReviewJSON  # noqa: E402
from src.json.compoundBlocks.tabs import Tabs  # noqa: E402
from src.json.compoundBlocks.column import Column  # noqa: E402
from src.json.simpleBlocks.text import Text  # noqa: E402
from src.json.simpleBlocks.customComponent import CustomComponent  # noqa: E402
from src.json.simpleBlocks.multiRowSelect import MultiRowSelect, MultiRowSelectQuestion  # noqa: E402
from src.json.simpleBlocks.multiRowChecked import MultiRowChecked  # noqa: E402
from src.json.simpleBlocks.multiRowOption import MultiRowOption  # noqa: E402

DEMO5 = os.path.join(ROOT, "__demo", "demo5")
YN = [MultiRowOption("Yes", "yes"), MultiRowOption("No", "no")]


def demo5_json():
    """The demo5 page exactly as createDemo5.py builds it (its block-building part, executed without writing files)."""
    src = open(os.path.join(ROOT, "createDemo5.py"), encoding="utf-8").read()
    src = src[:src.index("json_data = demo.get_json()")]
    ns = {}
    exec(compile(src, "createDemo5.py", "exec"), ns)
    return ns["demo"].get_json()


def page(model_page=True):
    root = Tabs(model={"page": {"format": "htmleval-model/1", "task": "a test"}} if model_page else None)
    instr = Column()
    instr.add_column([Text(title="How to", body=["Read <b>each</b> item.", "Click the tick."],
                           model={"role": "instructions", "text": ["Read each item."]})])
    root.add_tab("Instructions", instr)
    ex = Column(model={"audience": "human"})
    exq = MultiRowSelect(rowLabels=["Q"], questions=[MultiRowSelectQuestion("Kept?", id={1: "kept"}, options=YN)])
    exq.add_row(["example"], id={0: "ex_1"})
    ex.add_column([exq])
    root.add_tab("Example", ex)
    unit = Column(model={"unit": "Item 1", "text": "The item's text."})
    q = MultiRowSelect(rowLabels=["Sentence"], questions=[MultiRowSelectQuestion("", id={1: "kept"}, options=YN)],
                       model={"note": "A note."})
    q.add_row(["Is it fine?"], id={0: "s1"}, rowData={"kind": "a"}, model={"question": "Keep this sentence?", "about": "Sentence 1"})
    q.add_row(["Second"], id={0: "s2"}, model={"question": "Keep this sentence?", "about": "Sentence 2", "skip": True})
    unit.add_column([q])
    root.add_tab("Item 1", unit)
    return root


class Serialization(unittest.TestCase):
    def test_a_page_without_metadata_serializes_exactly_as_before(self):
        self.assertEqual(demo5_json(), open(os.path.join(DEMO5, "demo.json"), encoding="utf-8").read())

    def test_metadata_rides_along_and_strips_cleanly(self):
        with_meta = ReviewJSON(page()).get_json()
        self.assertIn('"model"', with_meta)
        stripped = strip_model(with_meta)
        self.assertNotIn("model", json.dumps(stripped))
        self.assertEqual(stripped["content"][2]["block"]["content"][0][0]["content"]["rows"][0],
                         {"text": ["Is it fine?"], "id": {"0": "s1"}, "rowData": {"kind": "a"}})
        self.assertEqual(page_meta(with_meta), {"format": "htmleval-model/1", "task": "a test"})
        self.assertIsNone(page_meta(ReviewJSON(page(model_page=False)).get_json()))


class Questions(unittest.TestCase):
    def test_page_keys_is_unchanged_for_demo5(self):
        keys = {q["key"] for q in page_keys(demo5_json())}
        closed = json.load(open(os.path.join(DEMO5, "closed_reviewer1.json")))["variables"]
        self.assertEqual(keys, set(closed))

    def test_questions_carry_wording_unit_about_and_hiding(self):
        qs = page_questions(ReviewJSON(page()).get_json())
        self.assertEqual([(q["row_id"], q["hidden"], q["skip"], q["unit"]) for q in qs],
                         [("ex_1", True, False, None), ("s1", False, False, "Item 1"), ("s2", False, True, "Item 1")])
        s1 = qs[1]
        self.assertEqual((s1["text"], s1["about"], s1["note"], s1["options"]),
                         ("Keep this sentence?", "Sentence 1", "A note.", [["yes", "Yes"], ["no", "No"]]))
        self.assertEqual(qs[0]["text"], "Kept?")                    # falls back to the question label

    def test_question_level_wording_and_checked_blocks(self):
        chk = MultiRowChecked(rowLabel="Claim", id={1: "ok"}, options=YN, model={"question": "Is the claim right?"})
        chk.add_row(id={0: "c1"}, text="Earth orbits the Sun")
        qs = page_questions(ReviewJSON(chk).get_json())
        self.assertEqual((qs[0]["key"], qs[0]["text"], qs[0]["block_type"]), ('["c1","ok"]', "Is the claim right?", "multi_row_checked"))

    def test_custom_component_declares_its_answers(self):
        cc = CustomComponent(html="<my-sort data-cards='[]'></my-sort>", model={
            "text": "Card 1: a. Card 2: b.",
            "questions": [{"row_id": "k1", "question_id": "group", "question": "Group for card 1",
                           "options": [["3:1", "1"], ["3:2", "2"]], "options_text": "1-2"}]})
        qs = page_questions(ReviewJSON(cc).get_json())
        self.assertEqual([(q["key"], q["text"], q["options_text"]) for q in qs], [('["k1","group"]', "Group for card 1", "1-2")])
        self.assertEqual([q["key"] for q in page_keys(ReviewJSON(cc).get_json())], ['["k1","group"]'])


class Checks(unittest.TestCase):
    def test_counts_only_what_the_model_is_asked(self):
        self.assertEqual(check_declared_keys(ReviewJSON(page()).get_json()), 1)

    def test_duplicate_keys_raise_on_any_page(self):
        q = MultiRowSelect(rowLabels=["Q"], questions=[MultiRowSelectQuestion("Kept?", id={1: "kept"}, options=YN)])
        q.add_row(["a"], id={0: "s1"}); q.add_row(["b"], id={0: "s1"})
        with self.assertRaises(ValueError):
            check_declared_keys(ReviewJSON(q).get_json())

    def test_empty_wording_raises_only_on_a_model_ready_page(self):
        def build(ready):
            root = Tabs(model={"page": {"format": "htmleval-model/1"}} if ready else None)
            q = MultiRowSelect(rowLabels=["Q"], questions=[MultiRowSelectQuestion("", id={1: "kept"}, options=YN)])
            q.add_row(["a"], id={0: "s1"})
            col = Column(); col.add_column([q]); root.add_tab("T", col)
            return ReviewJSON(root).get_json()
        self.assertEqual(check_declared_keys(build(False)), 1)
        with self.assertRaises(ValueError):
            check_declared_keys(build(True))

    def test_html_to_text(self):
        self.assertEqual(html_to_text('<p>One &amp; <b>two</b></p><script>x()</script><p>Three<br>four</p>'),
                         "One & two\nThree\nfour")
        self.assertEqual(html_to_text("rates < 2% and inflation > 5% <b>mattered</b>"), "rates < 2% and inflation > 5% mattered")


if __name__ == "__main__":
    unittest.main()
