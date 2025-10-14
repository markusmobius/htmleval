import os
import json
import sys

  
# Add the root directory (parent of htmleval) to Python path so 'htmleval' module can be found
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)  # Go up one level from htmleval to the root
sys.path.insert(0, root_dir)
from htmleval.src.reviewLib import Review 
# Ensure project root is on path so we can import htmleval
PROJECT_ROOT = os.getcwd()
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
EVAL_FOLDER = os.path.join("__demo","academicnews","classification_review")
REVIEWER_IDS_PATH = os.path.join(os.getcwd(), EVAL_FOLDER, "reviewer_ids.json")
SERVER_URL = "https://www.kv.econlabs.org/"  # Trailing slash expected
EVAL_TITLE = "Science Evaluation"

def load_reviewer_ids(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Could not find reviewer_ids.json at {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {str(k): v for k, v in data.items()}

def main():
    print(f"Loading reviewer IDs from {REVIEWER_IDS_PATH}")
    reviewer_ids = load_reviewer_ids(REVIEWER_IDS_PATH)

    if "reviewer1" not in reviewer_ids:
        print("reviewer1 not found in reviewer_ids.json. Nothing to close.")
        return

    reviewer_ids = {"reviewer1": reviewer_ids["reviewer1"]}
    print(f"Closing evaluation for reviewer1 -> {reviewer_ids['reviewer1']}")

    review = Review(EVAL_FOLDER, '', EVAL_TITLE, SERVER_URL)
    review.close_eval(reviewerIds=reviewer_ids)
    print("Done. Saved file: reviewer1_closed.json (if server returned data)")

if __name__ == "__main__":
    main()