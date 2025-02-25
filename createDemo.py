import os
from src.reviewLib import Review
from src.json.reviewJsonLib import ReviewJSON
from src.json.compoundBlocks.tabs import Tabs
from src.json.compoundBlocks.column import Column
from src.json.simpleBlocks.multiRow import MultiRow,MultiRowOption
from src.json.simpleBlocks.text import Text


#create the demo.json file from scratch
#root block are tabs
root=Tabs()
demo = ReviewJSON(root)
#add the first tab
col=Column()
root.add_tab(tabName="Tab 1",block=col)
col.add_column([
    Text(title= "This is the first text block",titleSize=3,body=["This is the first paragraph. Life is good.", "This is the second paragraph. Life is still good."]),
    Text(title="This is the second text block",titleSize=3,body=["This is the first paragraph. Life is good.", "This is the second paragraph. Life is still good."])
])
#add the second tab
col=Column()
root.add_tab(tabName="Tab 2",block=col)
col.add_column([
    Text(title= "This is the first left text block",titleSize=3,body=["This is the first left paragraph. Life is good.", "This is the second left paragraph. Life is still good."])
])
col.add_column([
    Text(title= "This is the first right text block",titleSize=3,body=["This is the first paragraph. Life is good.", "This is the second paragraph. Life is still good."]),
    Text(title= "This is the second right text block",titleSize=3,body=["This is the first paragraph. Life is good.", "This is the second paragraph. Life is still good."])
])
#add the third tab
options=[
    MultiRowOption(label="No",value ="no",color="danger"),
    MultiRowOption(label="Yes",value ="yes",color="success")
]
multi=MultiRow(rowLabel="Fragment",questionLabel="Correct?",variableName="correct",options=options)
multi.add_row(id="multi1",text="Stocks, bonds and commodities are heading for their strongest simultaneous four-month rise on record, highlighting the breadth of the market recovery during the 2020 economic slowdown.")
multi.add_row(id="multi2",text="Through Thursday, the")
root.add_tab(tabName="Tab 3",block=multi)

#now we create the JSON
json=demo.get_json()

#save demo json
with open(os.path.join("__demo","demo.json"), 'w') as f:
    f.write(json)

#now we create the HTML files
review=Review("__demo",json,"Demo")
review.create(["reviewer1","reviewer2"])
