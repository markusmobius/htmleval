# Usage Guide

You can use `htmleval` to programmaticly generate survey evaluations. Below is a simplified example based on the logic in `createDemo.py`.

## Basic Workflow
1. **Define Structure**: Create a Root block (usually `Tabs`).
2. **Add Content**: Add `Column` blocks to tabs, and populate columns with `Text` or Question blocks.
3. **Generate**: Use `ReviewJSON` to compile the structure into JSON, and `Review` to generate the HTML assets.

## Example Script

```python
import os
from htmleval.reviewLib import Review
from htmleval.json.reviewJsonLib import ReviewJSON
from htmleval.json.compoundBlocks.tabs import Tabs
from htmleval.json.compoundBlocks.column import Column
from htmleval.json.simpleBlocks.text import Text
from htmleval.json.simpleBlocks.multiRowOption import MultiRowOption
from htmleval.json.simpleBlocks.multiRowChecked import MultiRowChecked

# 1. Initialize the root layout (Tabs) and ReviewJSON wrapper
root = Tabs()
demo = ReviewJSON(root)

# 2. Create the first tab with some text content
col = Column()
root.add_tab(tabName="Welcome", block=col)

# Add a text block to the column
col.add_column([
    Text(
        title="Welcome to the Survey", 
        titleSize=3, 
        body=[
            "This is a paragraph of text.",
            "You can add multiple paragraphs like this."
        ]
    )
])

# 3. Create a second tab with a question
col2 = Column()
root.add_tab(tabName="Questions", block=col2)

# Define options for the question
options = [
    MultiRowOption(label="No", value="no", color="danger"),
    MultiRowOption(label="Yes", value="yes", color="success")
]

# Create a MultiRowChecked question block
# This creates a question where rows can be checked against the options
question_block = MultiRowChecked(rowLabel="Is this correct?", id={1: "correctness_check"}, options=options)
question_block.add_row(id={0: "q1"}, text="Is the sky blue?")
question_block.add_row(id={0: "q2"}, text="Is water dry?")

col2.add_column([question_block])

# 4. Generate the JSON structure
json_data = demo.get_json()

# 5. Generate the HTML files
# This creates the necessary HTML/JS files in the target folder
target_folder = "./my_demo_survey"
review = Review(block=json_data, evalTitle="My Demo", serverURL="https://www.kv.econlabs.org/")
# reviewers list generates unique links for each reviewer if needed
# metadata is saved to metadata.json for use by generate_summary
review.create(targetFolder=target_folder, defaults=None, reviewers=["reviewer1", "reviewer2"], metadata={
    "pipeline": "my-pipeline-v1",
    "model": "gpt-4o",
    "config": {"temperature": 0.0},
})

print(f"Survey generated in {target_folder}")
```

## Correct Values

Questions can optionally include a `correctValue` for computing error rates during aggregation. This can be set at the question level (applies to all rows) or per-row (overrides the question-level value). When no `correctValue` is set, the summary shows a response distribution instead.

```python
from htmleval.json.simpleBlocks.multiRowSelect import MultiRowSelect, MultiRowSelectQuestion

# Question-level correctValue (same expected answer for all rows)
question_block = MultiRowChecked(
    rowLabel="Claim", id={1: "fact_check"}, options=options,
    correctValue="true"
)

# Per-row correctValues (each row has its own expected answer)
q = MultiRowSelectQuestion(label="Correct?", id={1: "fact_check"}, options=options)
table = MultiRowSelect(rowLabels=["Claim"], questions=[q])
table.add_row(["Earth orbits the Sun"], id={0: "c1"}, correctValues={"fact_check": "true"})
table.add_row(["Water boils at 50°C"], id={0: "c2"}, correctValues={"fact_check": "false"})
```

Per-row `correctValues` take priority over question-level `correctValue` during aggregation.

## Row Data (Tags)

Rows can carry arbitrary metadata via `rowData` — a dict of key-value pairs attached to each row. This data is **not displayed** in the review UI but is included in the flat `records` output during aggregation, and used by `group_by` to break down summary statistics.

```python
table.add_row(
    ["Economy grows 5% in Q1"], id={0: "headline_1"},
    rowData={"category": "economics", "source": "reuters"}
)
```

`rowData` works the same way on `MultiRowChecked`:

```python
relevance_check = MultiRowChecked(
    rowLabel="Search result", id={1: "relevant"}, options=options, correctValue="yes"
)
relevance_check.add_row(
    id={0: "r1"}, text="Python tutorial on loops",
    rowData={"category": "programming"}
)
```

`rowData` is optional — when omitted, you can still use `id_parser` (see below) or rely on the raw `row_id` in the records.

Since `rowData` is stored in the block JSON (`demo.json`) and only read at aggregation time, you can add or modify tags **after** reviews have already been completed. Just update the `rowData` fields in `demo.json` (or regenerate it with updated `add_row` calls) and re-run the summary — the closed review data doesn't need to change.

## Closing and Aggregating Reviews

After reviewers complete their evaluations, pull their answers from the server and aggregate:

```python
# Download closed review data from server
review.close_eval(targetFolder=target_folder)

# Aggregate across reviewers
result = review.aggregate_closed_reviews(target_folder)
# result contains:
#   majority_votes  - {question_key: majority_answer}
#   per_question    - {question_key: {answer: count}}
#   reviewers       - list of reviewer names
#   stats           - agreement_rate, majority_error_rate, per_reviewer_error_rate, etc.
#   records         - flat list of per-(reviewer, row, question) dicts for analysis
```

The `records` list contains one dict per (reviewer, row, question) combination. Each record includes `reviewer`, `row_id`, `question_id`, `answer`, `correct_value`, plus any fields from `rowData`. This makes it easy to load into pandas or other tools for custom analysis.

### Using id_parser instead of rowData

If your rows don't carry `rowData`, you can pass an `id_parser` function to extract metadata from the row ID string:

```python
def parse_id(row_id_str):
    parts = row_id_str.split("_")
    return {"category": parts[0]}

result = review.aggregate_closed_reviews(target_folder, id_parser=parse_id)
```

`rowData` takes priority over `id_parser` when both are available for a given row.

## Generating a Summary

`generate_summary` creates a read-only HTML reviewer showing the original questions with majority answers pre-filled, plus Summary, Data, and Metadata tabs. It also saves `summary.json` with the aggregated data.

```python
review.generate_summary(target_folder, group_by=["question_id", "category"])
```

`group_by` accepts a list of field names (from `rowData`, `id_parser`, or built-in fields like `question_id`). The **first** field splits records into separate tables; **remaining** fields add sub-rows within each table.

The table format depends on whether the question has a `correctValue`:

- **With `correctValue`**: error rate table (Overall + per sub-group)
- **Without `correctValue`**: response distribution table showing counts/percentages for each answer value

For example, with three tabs — Sentiment (no correctValue), Fact Check (per-row correctValues), and Grammar Check (question-level correctValue) — the summary would show:

| **sentiment** | positive | negative | neutral |
|---|---|---|---|
| Overall | 50% (4) | 25% (2) | 25% (2) |
| category=economics | 50% (2) | 50% (2) | 0% (0) |
| category=local | 50% (2) | 0% (0) | 50% (2) |

| **fact_check** | Error Rate | n |
|---|---|---|
| Overall | 25% | 8 |
| category=geography | 25% | 4 |
| category=science | 25% | 4 |

| **grammar_check** | Error Rate | n |
|---|---|---|
| Overall | 25% | 8 |
| category=homophones | 25% | 4 |
| category=pronouns | 0% | 2 |
| category=subject-verb | 50% | 2 |

See `createDemo5.py` for a complete example with all three patterns.

### Summary features

- **Read-only**: dropdowns and checkboxes are disabled; nothing is saved to the server.
- **Metadata tab**: loaded from `metadata.json` (saved by `create()`).
- **Data tab**: contains all records in TSV format with a download button.
- **Overwrite protection**: `review_summary.html` and `summary.json` prompt before overwriting.
- **Tie-breaking**: when votes are tied, the first reviewer's answer is used for the majority.
