import os
from src.reviewLib import Review
from src.json.reviewJsonLib import ReviewJSON
from src.json.compoundBlocks.column import Column
from src.json.simpleBlocks.text import Text

# Root block logic can be anything, let's use a Column for main layout
root = Column()
demo = ReviewJSON(root)

# Create two columns side by side
layout_col = Column()
root.add_column([layout_col])

# Left side: Menu (Emitters)
menu_col = Column()

# Right side: Content (Listeners)
content_col = Column()

layout_col.add_column([menu_col])
layout_col.add_column([content_col])

# Menu Items
menu_item_1 = Text(title="Click Me for Info A", titleSize=4, body=["Emits Signal A"], signal="A")
menu_item_2 = Text(title="Click Me for Info B", titleSize=4, body=["Emits Signal B"], signal="B")
menu_item_3 = Text(title="Click Me for Info C", titleSize=4, body=["Emits Signal C"], signal="C")

menu_col.add_column([menu_item_1, menu_item_2, menu_item_3])

# Content Items
# Info A: Listens to A
info_a = Text(title="Information A", titleSize=3, body=["This is details for A.", "Visible only when A is signalled (or default)."], listeners=["A"])
# Info B: Listens to B
info_b = Text(title="Information B", titleSize=3, body=["This is details for B."], listeners=["B"])
# Info C: Listens to C
info_c = Text(title="Information C", titleSize=3, body=["This is details for C."], listeners=["C"])

content_col.add_column([info_a, info_b, info_c])

# Generate
json_data = demo.get_json()
target_dir = os.path.join(".", "__demo", "demo4")
os.makedirs(target_dir, exist_ok=True)

with open(os.path.join(target_dir, "demo.json"), 'w') as f:
    f.write(json_data)

review = Review(block=json_data, evalTitle="Signal Demo", serverURL="https://www.kv.econlabs.org/")
review.create(targetFolder=target_dir, defaults=None, reviewers=["reviewer1"])

print(f"Signal demo created in {target_dir}")
