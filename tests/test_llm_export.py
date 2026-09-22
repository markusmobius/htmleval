"""Unit of analysis: one block tree. The export's keys must equal the keys a browser writes."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from src.json.llmExport import to_llm_json, iter_questions, variable_key, strip_html  # noqa: E402
from src.json.reviewJsonLib import ReviewJSON  # noqa: E402
from src.json.compoundBlocks.tabs import Tabs  # noqa: E402
from src.json.compoundBlocks.column import Column  # noqa: E402
from src.json.compoundBlocks.thread import Thread  # noqa: E402
from src.json.simpleBlocks.multiRowSelect import MultiRowSelect, MultiRowSelectQuestion  # noqa: E402
from src.json.simpleBlocks.multiRowOption import MultiRowOption  # noqa: E402

DEMO5 = os.path.join(os.path.dirname(HERE), "__demo", "demo5")


class KeyContract(unittest.TestCase):
    def test_demo5_keys_match_browser_written_keys(self):
        export = to_llm_json(open(os.path.join(DEMO5, "demo.json")).read())
        keys = {k for q in iter_questions(export["root"]) for r in q["rows"] for k in r["keys"].values()}
        closed = json.load(open(os.path.join(DEMO5, "closed_reviewer1.json")))["variables"]
        self.assertEqual(keys, set(closed))

    def test_row_data_and_correct_values_survive(self):
        export = to_llm_json(open(os.path.join(DEMO5, "demo.json")).read())
        rows = {r["row_id"]: r for q in iter_questions(export["root"]) for r in q["rows"]}
        self.assertEqual(rows["headline_1"]["row_data"], {"category": "economics"})
        self.assertEqual(rows["claim_2"]["correct_values"], {"fact_check": "false"})

    def test_variable_key_slot_merge(self):
        self.assertEqual(variable_key({0: "r"}, {1: "q"}), '["r","q"]')
        self.assertEqual(variable_key({"0": "r"}, {"1": "q"}), '["r","q"]')
        self.assertEqual(variable_key("r", "q"), '["r","q"]')
        self.assertEqual(variable_key({0: "ü"}, {1: "q"}), '["ü","q"]')   # JS keeps non-ASCII

    def test_subjects_resolve_to_emitting_thread(self):
        root = Tabs(); col = Column(); root.add_tab("Eval", col)
        th = Thread(title="", body=["<b>Action 3</b>: Iran fired a salvo."], signal="act_0_3", listeners=["act_0_3"], highlight=True)
        q = MultiRowSelect(rowLabels=["Question"], questions=[MultiRowSelectQuestion("", id={1: "answer"},
                           options=[MultiRowOption("Yes", "yes"), MultiRowOption("No", "no")])], listeners=["act_0_3"])
        q.add_row(id={0: "0_action_3_categorized"}, text=["Is the action correctly categorized?"], rowData={"question_type": "cat"})
        col.add_column([th, q])
        export = to_llm_json(ReviewJSON(root).get_json())
        qs = list(iter_questions(export["root"]))
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0]["subjects"][0]["text"], ["Action 3: Iran fired a salvo."])
        self.assertEqual(qs[0]["rows"][0]["keys"], {"answer": '["0_action_3_categorized","answer"]'})

    def test_strip_html_keeps_line_structure(self):
        self.assertEqual(strip_html("<p>a &amp; b</p><ul><li>x</li><li>y</li></ul>"), "a & b\nx\ny")


if __name__ == "__main__":
    unittest.main()
