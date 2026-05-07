"""Demo 5 Step 2: Close evals, aggregate, and generate summary.

Run this after reviewers have filled out their evaluations in the browser.
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

# Generate read-only summary (metadata loaded from metadata.json)
review.generate_summary(target_dir)

print(f"Summary generated in {target_dir}")
