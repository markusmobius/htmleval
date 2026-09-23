"""Unit of analysis: one block tree. The keys listed for a page must equal the keys a browser writes for it."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from src.json.answerKeys import page_keys, variable_key  # noqa: E402
from src.json.reviewJsonLib import ReviewJSON  # noqa: E402
from src.json.compoundBlocks.tabs import Tabs  # noqa: E402
from src.json.compoundBlocks.column import Column  # noqa: E402
from src.json.compoundBlocks.interactive import Interactive, InteractiveFragment, InteractiveParagraph  # noqa: E402
from src.json.simpleBlocks.multiRowSelect import MultiRowSelect, MultiRowSelectQuestion  # noqa: E402
from src.json.simpleBlocks.multiRowOption import MultiRowOption  # noqa: E402

DEMO5 = os.path.join(os.path.dirname(HERE), "__demo", "demo5")


class AnswerKeys(unittest.TestCase):
    def test_demo5_keys_match_browser_written_keys(self):
        keys = {q["key"] for q in page_keys(open(os.path.join(DEMO5, "demo.json")).read())}
        closed = json.load(open(os.path.join(DEMO5, "closed_reviewer1.json")))["variables"]
        self.assertEqual(keys, set(closed))

    def test_variable_key_slot_merge(self):
        self.assertEqual(variable_key({0: "r"}, {1: "q"}), '["r","q"]')
        self.assertEqual(variable_key({"0": "r"}, {"1": "q"}), '["r","q"]')
        self.assertEqual(variable_key("r", "q"), '["r","q"]')
        self.assertEqual(variable_key({0: "ü"}, {1: "q"}), '["ü","q"]')   # JS keeps non-ASCII

    def test_rows_inside_interactive_spans_and_row_data(self):
        yn = [MultiRowOption("Yes", "yes"), MultiRowOption("No", "no")]
        q = MultiRowSelect(rowLabels=[""], questions=[MultiRowSelectQuestion("Kept?", id={1: "kept"}, options=yn),
                                                      MultiRowSelectQuestion("Cleaned?", id={1: "cleaned"}, options=yn)])
        q.add_row(text=[""], id={0: "s0"}, rowData={"state": "removed"})
        par = InteractiveParagraph(); par.addFragment(InteractiveFragment("<s>Copyright</s>", q))
        inter = Interactive(); inter.addParagraph(par)
        root = Tabs(); col = Column(); col.add_column([inter]); root.add_tab("A", col)
        got = page_keys(ReviewJSON(root).get_json())
        self.assertEqual([(g["row_id"], g["question_id"], g["key"]) for g in got],
                         [("s0", "kept", '["s0","kept"]'), ("s0", "cleaned", '["s0","cleaned"]')])
        self.assertEqual(got[0]["row_data"], {"state": "removed"})


if __name__ == "__main__":
    unittest.main()
