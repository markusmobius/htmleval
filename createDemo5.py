"""Demo 5: Summary reviewer feature — three summary patterns.

Tab 1: Sentiment (no correctValue) — summary shows response distribution by category.
Tab 2: Fact Check (correctValue per row) — error rate overall + by category.
Tab 3: Grammar Check (correctValue at question level) — error rate overall + by category.

Step 1: Run this script to create the review HTML files.
Step 2: Open review_reviewer1.html and review_reviewer2.html in a browser and fill them out.
Step 3: Run createDemo5_summary.py to close evals, aggregate, and generate the summary.
"""
import os

from src.reviewLib import Review
from src.json.reviewJsonLib import ReviewJSON
from src.json.compoundBlocks.tabs import Tabs
from src.json.compoundBlocks.column import Column
from src.json.simpleBlocks.text import Text
from src.json.simpleBlocks.multiRowSelect import MultiRowSelect, MultiRowSelectQuestion
from src.json.simpleBlocks.multiRowChecked import MultiRowChecked
from src.json.simpleBlocks.multiRowOption import MultiRowOption

# Root block: tabs
root = Tabs()
demo = ReviewJSON(root)

# ---------------------------------------------------------------------------
# Tab 1: Sentiment — NO correctValue
#   Summary will show response distribution (positive/negative/neutral counts)
#   broken down by category via rowData.
# ---------------------------------------------------------------------------
col1 = Column()
root.add_tab(tabName="Sentiment", block=col1)

sentiment_options = [
    MultiRowOption(label="Positive", value="positive", color="success"),
    MultiRowOption(label="Negative", value="negative", color="danger"),
    MultiRowOption(label="Neutral",  value="neutral",  color="warning"),
]
sentiment_q = MultiRowSelectQuestion(
    label="Sentiment",
    id={1: "sentiment"},
    options=sentiment_options,
)
sentiment_table = MultiRowSelect(rowLabels=["Headline"], questions=[sentiment_q])
sentiment_table.add_row(
    ["Economy grows 5% in Q1"], id={0: "headline_1"},
    rowData={"category": "economics"}
)
sentiment_table.add_row(
    ["Unemployment rises sharply"], id={0: "headline_2"},
    rowData={"category": "economics"}
)
sentiment_table.add_row(
    ["New park opens downtown"], id={0: "headline_3"},
    rowData={"category": "local"}
)
sentiment_table.add_row(
    ["Mayor announces infrastructure plan"], id={0: "headline_4"},
    rowData={"category": "local"}
)

col1.add_column([
    Text(title="Classify headline sentiment", titleSize=3, body=["Select the sentiment for each headline."]),
    sentiment_table,
])

# ---------------------------------------------------------------------------
# Tab 2: Fact Check — correctValue PER ROW (correctValues on each row)
#   Each claim has its own known correct answer.
#   Summary will show error rate overall + by category.
# ---------------------------------------------------------------------------
col2 = Column()
root.add_tab(tabName="Fact Check", block=col2)

tf_options = [
    MultiRowOption(label="True",  value="true",  color="success"),
    MultiRowOption(label="False", value="false", color="danger"),
]
fact_q = MultiRowSelectQuestion(
    label="Correct?",
    id={1: "fact_check"},
    options=tf_options,
)
fact_table = MultiRowSelect(rowLabels=["Claim"], questions=[fact_q])
fact_table.add_row(
    ["The Earth orbits the Sun."], id={0: "claim_1"},
    correctValues={"fact_check": "true"},
    rowData={"category": "science"}
)
fact_table.add_row(
    ["Water boils at 50°C at sea level."], id={0: "claim_2"},
    correctValues={"fact_check": "false"},
    rowData={"category": "science"}
)
fact_table.add_row(
    ["France is in Europe."], id={0: "claim_3"},
    correctValues={"fact_check": "true"},
    rowData={"category": "geography"}
)
fact_table.add_row(
    ["Tokyo is the capital of China."], id={0: "claim_4"},
    correctValues={"fact_check": "false"},
    rowData={"category": "geography"}
)

col2.add_column([
    Text(title="Verify each claim", titleSize=3, body=["Mark each claim as true or false."]),
    fact_table,
])

# ---------------------------------------------------------------------------
# Tab 3: Grammar Check — correctValue AT QUESTION LEVEL
#   All rows share the same expected answer ("yes") — was the correction correct?
#   Summary will show error rate overall + by category.
# ---------------------------------------------------------------------------
col3 = Column()
root.add_tab(tabName="Grammar Check", block=col3)

yn_options = [
    MultiRowOption(label="Yes", value="yes", color="success"),
    MultiRowOption(label="No",  value="no",  color="danger"),
]
grammar_check = MultiRowChecked(
    rowLabel="Correction",
    id={1: "grammar_check"},
    options=yn_options,
    correctValue="yes",
)
grammar_check.add_row(id={0: "gram_1"}, text="\"Their going to the store\" → \"They're going to the store\"",
    rowData={"category": "homophones"})
grammar_check.add_row(id={0: "gram_2"}, text="\"The cat chased it's tail\" → \"The cat chased its tail\"",
    rowData={"category": "homophones"})
grammar_check.add_row(id={0: "gram_3"}, text="\"Him and me went\" → \"He and I went\"",
    rowData={"category": "pronouns"})
grammar_check.add_row(id={0: "gram_4"}, text="\"She don't like it\" → \"She doesn't like it\"",
    rowData={"category": "subject-verb"})

col3.add_column([
    Text(title="Was the grammar correction correct?", titleSize=3,
         body=["For each sentence, mark whether the automated correction was applied correctly."]),
    grammar_check,
])

# ---------------------------------------------------------------------------
# Generate JSON and create review
# ---------------------------------------------------------------------------
json_data = demo.get_json()
target_dir = os.path.join(".", "__demo", "demo5")
os.makedirs(target_dir, exist_ok=True)

with open(os.path.join(target_dir, "demo.json"), "w") as f:
    f.write(json_data)

review = Review(block=json_data, evalTitle="Summary Demo", serverURL="https://www.kv.econlabs.org/")
review.create(targetFolder=target_dir, defaults=None, reviewers=["reviewer1", "reviewer2"], metadata={
    "pipeline_name": "demo-pipeline-v1",
    "date_run": "2026-05-07",
    "config": {"temperature": 0.0, "max_tokens": 512},
})

print(f"Review created in {target_dir}")
print("Open review_reviewer1.html and review_reviewer2.html in a browser, fill them out,")
print("then run createDemo5_summary.py to close and generate the summary.")
