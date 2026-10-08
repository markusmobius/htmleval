"""Unit of analysis: one call unit of a page. The prompt text is a pure function of the page JSON and its metadata."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from src.modelReview import render as mr  # noqa: E402
from src.json.reviewJsonLib import ReviewJSON  # noqa: E402
from src.json.compoundBlocks.tabs import Tabs  # noqa: E402
from src.json.compoundBlocks.column import Column  # noqa: E402
from src.json.compoundBlocks.thread import Thread  # noqa: E402
from src.json.simpleBlocks.text import Text  # noqa: E402
from src.json.simpleBlocks.customComponent import CustomComponent  # noqa: E402
from src.json.simpleBlocks.multiRowSelect import MultiRowSelect, MultiRowSelectQuestion  # noqa: E402
from src.json.simpleBlocks.multiRowOption import MultiRowOption  # noqa: E402
from tests.test_model_metadata import page  # noqa: E402

YN = [MultiRowOption("Yes", "yes"), MultiRowOption("No", "no")]


def lines_of(out):
    return [line for line, _ in out]


class Units(unittest.TestCase):
    def test_units_skip_hidden_subtrees_and_name_the_page_unit_when_needed(self):
        js = ReviewJSON(page()).get_json()
        self.assertEqual([lab for lab, _ in mr.units(js)], ["Item 1"])
        q = MultiRowSelect(rowLabels=["Q"], questions=[MultiRowSelectQuestion("Kept?", id={1: "kept"}, options=YN)])
        q.add_row(["a"], id={0: "s1"})
        root = Tabs(model={"page": {"format": "htmleval-model/1"}}); col = Column(); col.add_column([Text(body=["Intro"]), q])
        root.add_tab("Only", col)
        self.assertEqual([lab for lab, _ in mr.units(ReviewJSON(root).get_json())], ["Page"])

    def test_system_text_uses_the_page_preamble_and_the_instruction_blocks(self):
        js = ReviewJSON(page()).get_json()
        self.assertEqual(mr.system_text(js, "HEAD"), "HEAD\n\n" + mr.MODEL_PREAMBLE + "\n\nTHE REVIEWER INSTRUCTIONS:\nRead each item.")
        root = page(); root.model["page"]["preamble"] = "Custom preamble."
        self.assertTrue(mr.system_text(ReviewJSON(root).get_json(), "HEAD").startswith("HEAD\n\nCustom preamble.\n\n"))


class Rendering(unittest.TestCase):
    def test_unit_text_then_questions_with_note_about_and_options(self):
        js = ReviewJSON(page()).get_json()
        out, rows = mr.render_unit(js, "Item 1")
        self.assertEqual(lines_of(out), ["The item's text.", mr.QUESTIONS_HEAD, "A note.", "", "Sentence 1",
                                         "s1: Keep this sentence? [yes | no]"])
        self.assertEqual(rows, [{"row_id": "s1", "question_id": "kept", "key": '["s1","kept"]', "options": {"yes": "Yes", "no": "No"}}])
        tags = [t for _, t in out]
        self.assertEqual(tags[4], ("group", [rows[0]]))             # the About line travels with its rows
        self.assertIs(tags[5], rows[0])

    def test_options_text_overrides_the_bracket_and_groups_shuffle_deterministically(self):
        root = Tabs(model={"page": {"format": "htmleval-model/1"}})
        unit = Column(model={"unit": "U", "text": ["M"]})
        q = MultiRowSelect(rowLabels=["Q"], questions=[MultiRowSelectQuestion("Q?", id={1: "g"}, options=[MultiRowOption("1", "3:1"), MultiRowOption("2", "3:2")])])
        for i in range(4):
            q.add_row([f"card {i}"], id={0: f"k{i}"}, model={"about": f"Card {i}", "options_text": "1-2; same number = same group"})
        unit.add_column([q]); root.add_tab("U", unit)
        js = ReviewJSON(root).get_json()
        out, rows = mr.render_unit(js, "U")
        self.assertIn("k0: Q? [1-2; same number = same group]", lines_of(out))
        self.assertEqual([r["row_id"] for r in rows], ["k0", "k1", "k2", "k3"])
        a = [r["row_id"] for r in mr.render_unit(js, "U", shuffle_seed="1:U")[1]]
        b = [r["row_id"] for r in mr.render_unit(js, "U", shuffle_seed="1:U")[1]]
        c = [r["row_id"] for r in mr.render_unit(js, "U", shuffle_seed="2:U")[1]]
        self.assertEqual(a, b)
        self.assertEqual(sorted(a), ["k0", "k1", "k2", "k3"])
        self.assertTrue(a != c or a != ["k0", "k1", "k2", "k3"])

    def test_material_without_model_text_is_the_blocks_as_plain_text(self):
        unit = Column(model={"unit": "U"})
        th = Thread(title="<b>Head</b>", body=["One &amp; two"])
        th.addThread(Thread(body=["Reply"]))
        unit.add_column([Text(title="T", body=[["a", "b"], "<p>para</p>"]), th, CustomComponent(html="<x-y>raw</x-y>", model={"text": "Cards: 1, 2"}),
                         Text(body=["secret"], model={"audience": "human"})])
        root = Tabs(model={"page": {"format": "htmleval-model/1"}}); root.add_tab("U", unit)
        out, rows = mr.render_unit(ReviewJSON(root).get_json(), "U")
        self.assertEqual(lines_of(out)[:7], ["T", "a | b", "para", "Head", "One & two", "Reply", "Cards: 1, 2"])
        self.assertNotIn("secret", lines_of(out))
        self.assertEqual(rows, [])

    def test_option_labels_only_when_they_add_words(self):
        self.assertEqual(mr._options([["news", "NEWS action (grey)"], ["commentary", "COMMENTARY action (yellow)"]]), "news | commentary")
        self.assertEqual(mr._options([["not_claim", "Not a claim"]]), "not_claim")
        self.assertIn('yes ("Yes — a detail', mr._options([["yes", "Yes &mdash; a detail is missing"]]))


if __name__ == "__main__":
    unittest.main()
