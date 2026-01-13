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
review.create(targetFolder=target_folder, defaults=None, reviewers=["reviewer1", "reviewer2"])

print(f"Survey generated in {target_folder}")
```
