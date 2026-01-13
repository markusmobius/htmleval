import os

from src.reviewLib import Review
from src.json.reviewJsonLib import ReviewJSON
from src.json.compoundBlocks.tabs import Tabs
from src.json.compoundBlocks.column import Column
from src.json.compoundBlocks.thread import Thread

# Create the demo.json file from scratch
# Root block are tabs
root = Tabs()
demo = ReviewJSON(root)

# Create a tab for the threads
col = Column()
root.add_tab(tabName="Thread Demo", block=col)

# Create the Parent Thread
parent_thread = Thread(
    title="Parent Thread", 
    titleSize=3, 
    body=["This is the start of the conversation.", "It acts as the root of the discussion tree."]
)

# Child 1: Direct response to parent
child1 = Thread(
    title="Child 1", 
    titleSize=4, 
    body=["I am the first response to the parent."]
)
parent_thread.addThread(child1)

# Child 2: Direct response to parent, with its own child
child2 = Thread(
    title="Child 2", 
    titleSize=4, 
    body=["I am the second response. I have a follow-up comment below me."]
)

# Grandchild: Response to Child 2
grandchild = Thread(
    title="Grandchild", 
    titleSize=5, 
    body=["I am a reply to Child 2.", "This shows the nesting capability."]
)
child2.addThread(grandchild)

parent_thread.addThread(child2)

# Child 3: Direct response to parent
child3 = Thread(
    title="Child 3", 
    titleSize=4, 
    body=["I am the third response to the parent."]
)
parent_thread.addThread(child3)

# Add the parent thread (which contains all children) to the column
col.add_column([parent_thread])


# Now we create the JSON
json_data = demo.get_json()

# Create target directory if it doesn't exist
target_dir = os.path.join(".", "__demo", "demo3")
os.makedirs(target_dir, exist_ok=True)

# Save demo json
with open(os.path.join(target_dir, "demo.json"), 'w') as f:
    f.write(json_data)

# Now we create the HTML files
review = Review(block=json_data, evalTitle="Thread Demo", serverURL="https://www.kv.econlabs.org/")
review.create(targetFolder=target_dir, defaults=None, reviewers=["reviewer1", "reviewer2"])

print(f"Thread demo created in {target_dir}")
