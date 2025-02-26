import os
from src.reviewLib import Review
from src.json.reviewJsonLib import ReviewJSON
from src.json.compoundBlocks.tabs import Tabs
from src.json.compoundBlocks.column import Column
from src.json.simpleBlocks.multiRowSelect import MultiRowSelect
from src.json.simpleBlocks.multiRowChecked import MultiRowChecked
from src.json.simpleBlocks.multiRowOption import MultiRowOption
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
multi=MultiRowSelect(rowLabel="Fragment",questionLabel="Correct?",variableName="correct",options=options)
multi.add_row(id="multiselect1",text="Stocks, bonds and commodities are heading for their strongest simultaneous four-month rise on record, highlighting the breadth of the market recovery during the 2020 economic slowdown.")
multi.add_row(id="multiselect2",text="Through Thursday, the")
root.add_tab(tabName="Tab 3",block=multi)

#add the fourth tab
col=Column()
#add a nested side-by-side Column
nestedCol=Column()
nestedCol.add_column([
    Text(title= "Article",titleSize=4,body=[
        "The Department of Justice is expected Tuesday to charge Google with violating federal antitrust law, according to two people familiar with the matter, finding after a year-long investigation that the tech giant wrongfully wielded its digital dominance to the detriment of corporate rivals and consumers.",
        "The federal government’s imminent lawsuit will touch off a landmark and lengthy legal war between Washington and Silicon Valley, one that could have vast implications not only for Google but the entirety of a tech industry that has faced new, unprecedented scrutiny in recent years for the unrivaled power, money and data it has amassed.",
        "Neither the Justice Department nor Google responded to a request for comment.",
        "A federal antitrust lawsuit marks the start, not the end, of the government’s gambit against Google. It could take years for a federal court to resolve whether the company violated the country’s competition laws and, if so, what punishments it should may face. Only Republican state attorneys general are expected to sign onto the DOJ’s complaint, the Post has previously reported. Other states later may choose to join the Justice Department suit, or they still yet may bring their own lawsuits against the tech giant, widening the legal ground Google must cover to defend its business from serious, potentially far-reaching changes.",
        "But the filing alone still serves as a stunning turn of events for Google, roughly seven years after the federal government last probed the company for potential antitrust violations -- an inquiry that regulators concluded without suing Google or seeking significant penalties, including its breakup. The inaction in Washington for years has stood in stark contrast to the withering antitrust scrutiny Google has faced in Europe, where competition regulators over the past decade have slapped the Mountain View, California-based tech behemoth with $9 billion in fines and sought to secure major changes to the way it offers search, advertising and Android, its smartphone operating system.",
        "The Justice Department began scrutinizing Google as part of a broad review of big tech announced last summer, as federal officials sought to respond to what they described then as widespread concerns that consumers, businesses, and entrepreneurs have expressed about search, social media, and some retail services online. That September, Google started turning over key, sensitive documents to DOJ for its investigation, the company acknowledged in a securities filing at the time.",
        "Initially, DOJ officials signaled an interest in probing the company’s advertising business, which contributed the lion’s share of the company’s total $162 billion in 2019 revenue. Quickly, though, the probe expanded to touch on a wider array of issues in response to a flurry of complaints from rival companies -- from news publishers to travel review websites -- that say Google wields its powerful search engine in myriad ways to entrench its dominance.",
        "At times, the federal probe has proven acrimonious. The DOJ and Google have warred over the company’s apparent unwillingness to turn over documents that federal investigators describe as critical to their work. Within DOJ, meanwhile, government lawyers have sparred among themselves over the timeline for bringing a case particularly in the weeks before the 2020 presidential election. Dozens of agency staff signaled this summer they did not feel they were ready to bring charges against Google, but Attorney General William P. Barr ultimately overruled them -- and set the Justice Department on a course to file this month.",
        "The federal investigation has proceeded in parallel with state probes commenced last September by nearly every Democratic and Republican attorney general. The investigations have broadened to encompass more than advertising -- touching on search and the extent to which Google further enhances its dominance through the Android smartphone operating system.",
        "A handful of states including Colorado, Iowa, Nebraska and New York are preparing to issue a joint public statement as soon as Tuesday indicating they are still scrutinizing a wide array of Google’s business practices and may instead opt to join any federal case later, according to four people familiar with their thinking, who spoke on the condition of anonymity to discuss a law-enforcement matter. The Post first reported the news last week."
    ],scrollable=True)
])
nestedCol.add_column([
    Text(title= "Summary", titleSize=4,body=["The U.S. Department of Justice (DOJ) is set to file an antitrust lawsuit against Google, alleging the tech giant abused its digital dominance to undermine competition and harm consumers. This legal action marks the commencement of a significant court battle that could have extensive consequences not only for Google but also for the broader technology industry, which has already been under heightened scrutiny for its considerable influence and data accumulation. The lawsuit could take years to conclude whether Google actually breached competition laws and determine the appropriate penalties. This development follows a lengthy period of inactivity in the U.S., contrasting the intense antitrust scrutiny Google has faced in Europe, resulting in $9 billion in fines. This legal action originates from a wider DOJ review that began last summer into major tech companies, with Google's advertising dominance being a major focal point that later expanded to include complaints from various competitor sectors."], scrollable=True),
])
options=[
    MultiRowOption(label="No",value ="no",color="danger"),
    MultiRowOption(label="Yes",value ="yes",color="success")
]
multi=MultiRowChecked(rowLabel="Question",variableName="goodsummary",options=options)
multi.add_row(id="multichecked1",text="Is the summary good?")
col.add_column([nestedCol, multi])
root.add_tab(tabName="Tab 4",block=col)

#now we create the JSON
json=demo.get_json()

#save demo json
with open(os.path.join("__demo","demo.json"), 'w') as f:
    f.write(json)

#now we create the HTML files
review=Review("__demo",json,"Demo")
review.create(["reviewer1","reviewer2"])
