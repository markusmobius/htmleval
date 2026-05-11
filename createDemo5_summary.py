"""Demo 5 Step 2: Close evals, aggregate, and generate summary.

Run this after reviewers have filled out their evaluations in the browser.

The summary tab will show:
  - Sentiment: response distribution by category (no correctValue)
  - Fact Check: error rate by category (per-row correctValues)
  - Grammar Check: error rate by category (question-level correctValue)
Plus: Data tab (TSV records), Metadata tab.
"""
import os

from src.reviewLib import Review

target_dir = os.path.join(".", "__demo", "demo5")

# Load the block JSON
with open(os.path.join(target_dir, "demo.json"), "r") as f:
    json_data = f.read()

review = Review(block=json_data, evalTitle="Summary Demo", serverURL="https://www.kv.econlabs.org/")

# Pull closed review data from the server
review.close_eval(targetFolder=target_dir)

# Generate summary with grouped breakdown by category
aggregated = review.generate_summary(target_dir, group_by=["category"])

print(f"Summary generated in {target_dir}")
