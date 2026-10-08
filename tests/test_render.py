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
        self.assertEqual(rows, [{"pid": "s1", "row_id": "s1", "question_id": "kept", "key": '["s1","kept"]', "options": {"yes": "Yes", "no": "No"}}])
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
        self.assertEqual(mr._options([["3:1", "1"], ["3:2", "2"]]), '3:1 ("1") | 3:2 ("2")')     # a wordless label is shown
        self.assertEqual(mr._options([["1", "1"]]), "1")

    def test_a_row_with_several_questions_gets_one_prompt_id_per_question(self):
        root = Tabs(model={"page": {"format": "htmleval-model/1"}})
        unit = Column(model={"unit": "U", "text": ["M"]})
        q = MultiRowSelect(rowLabels=["Arg"], questions=[MultiRowSelectQuestion("Present?", id={1: "present"}, options=YN),
                                                         MultiRowSelectQuestion("Valid?", id={1: "valid"}, options=YN)])
        q.add_row(["arg one"], id={0: "arg1"})
        single = MultiRowSelect(rowLabels=["Q"], questions=[MultiRowSelectQuestion("Ok?", id={1: "ok"}, options=YN)])
        single.add_row(["x"], id={0: "s1"})
        unit.add_column([q, single]); root.add_tab("U", unit)
        out, rows = mr.render_unit(ReviewJSON(root).get_json(), "U")
        self.assertEqual([r["pid"] for r in rows], ["arg1#present", "arg1#valid", "s1"])
        self.assertIn("arg1#present: Present? [yes | no]", lines_of(out))
        self.assertEqual([r["key"] for r in rows], ['["arg1","present"]', '["arg1","valid"]', '["s1","ok"]'])

    def test_a_unit_nested_in_a_unit_is_its_own_unit(self):
        root = Tabs(model={"page": {"format": "htmleval-model/1"}})
        outer = Column(model={"unit": "Doc 1"})
        q1 = MultiRowSelect(rowLabels=["Q"], questions=[MultiRowSelectQuestion("Ok?", id={1: "ok"}, options=YN)]); q1.add_row(["a"], id={0: "d1"})
        inner = Column(model={"unit": "Doc 1 / Claims", "text": ["claims material"]})
        q2 = MultiRowSelect(rowLabels=["Q"], questions=[MultiRowSelectQuestion("Ok?", id={1: "ok"}, options=YN)]); q2.add_row(["b"], id={0: "c1"})
        inner.add_column([q2]); outer.add_column([Text(body=["outer material"]), q1, inner]); root.add_tab("D", outer)
        js = ReviewJSON(root).get_json()
        self.assertEqual([lab for lab, _ in mr.units(js)], ["Doc 1", "Doc 1 / Claims"])
        o_lines, o_rows = mr.render_unit(js, "Doc 1")
        i_lines, i_rows = mr.render_unit(js, "Doc 1 / Claims")
        self.assertEqual(([r["pid"] for r in o_rows], [r["pid"] for r in i_rows]), (["d1"], ["c1"]))
        self.assertNotIn("claims material", lines_of(o_lines))
        self.assertIn("claims material", lines_of(i_lines))


if __name__ == "__main__":
    unittest.main()
