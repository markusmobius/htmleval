"""Demo 5: Summary reviewer feature with correctValue.

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

# Tab 1: Sentiment classification (MultiRowSelect with correctValue)
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
    correctValue="positive",
)
sentiment_table = MultiRowSelect(rowLabels=["Headline"], questions=[sentiment_q])
sentiment_table.add_row(["Economy grows 5% in Q1"], id={0: "headline_1"})
sentiment_table.add_row(["New park opens downtown"], id={0: "headline_2"})
sentiment_table.add_row(["Stock market hits record high"], id={0: "headline_3"})

col1.add_column([
    Text(title="Classify headline sentiment", titleSize=3, body=["Select the sentiment for each headline."]),
    sentiment_table,
])

# Tab 2: Fact-check (MultiRowChecked with correctValue)
col2 = Column()
root.add_tab(tabName="Fact Check", block=col2)

fc_options = [
    MultiRowOption(label="True",  value="true",  color="success"),
    MultiRowOption(label="False", value="false", color="danger"),
]
fact_check = MultiRowChecked(
    rowLabel="Claim",
    id={1: "fact_check"},
    options=fc_options,
    correctValue="true",
)
fact_check.add_row(id={0: "claim_1"}, text="The Earth orbits the Sun.")
fact_check.add_row(id={0: "claim_2"}, text="Water boils at 100°C at sea level.")

col2.add_column([
    Text(title="Verify each claim", titleSize=3, body=["Mark each claim as true or false."]),
    fact_check,
])

# Generate JSON and create review
json_data = demo.get_json()
target_dir = os.path.join(".", "__demo", "demo5")
os.makedirs(target_dir, exist_ok=True)

with open(os.path.join(target_dir, "demo.json"), "w") as f:
    f.write(json_data)

review = Review(block=json_data, evalTitle="Summary Demo", serverURL="https://www.kv.econlabs.org/")
review.create(targetFolder=target_dir, defaults=None, reviewers=["reviewer1", "reviewer2"], metadata={
    "pipeline": "demo-pipeline-v1",
    "model": "gpt-4o",
    "prompt_version": "2026-05-07",
    "config": {"temperature": 0.0, "max_tokens": 512},
})

print(f"Review created in {target_dir}")
print("Open review_reviewer1.html and review_reviewer2.html in a browser, fill them out,")
print("then run createDemo5_summary.py to close and generate the summary.")
