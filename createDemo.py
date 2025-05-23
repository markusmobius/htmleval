import os
from src.reviewLib import Review
from src.json.reviewJsonLib import ReviewJSON
from src.json.compoundBlocks.tabs import Tabs
from src.json.compoundBlocks.column import Column
from src.json.compoundBlocks.interactive import Interactive
from src.json.compoundBlocks.interactive import InteractiveParagraph
from src.json.compoundBlocks.interactive import InteractiveFragment
from src.json.simpleBlocks.multiRowSelect import MultiRowSelect
from src.json.simpleBlocks.multiRowSelect import MultiRowSelectQuestion
from src.json.simpleBlocks.multiRowChecked import MultiRowChecked
from src.json.simpleBlocks.multiRowOption import MultiRowOption
from src.json.simpleBlocks.text import Text


#create the demo.json file from scratch
#root block are tabs
root=Tabs()
demo = ReviewJSON(root)

#add the first tab (a pure text tab)
col=Column()
root.add_tab(tabName="Tab 1",block=col)
col.add_column([
    Text(title= "This is the first text block",titleSize=3,body=["This is the first paragraph. Life is good.", "This is the second paragraph. Life is still good."]),
    Text(title="This is the second text block",titleSize=3,body=["This is the first paragraph. Life is good.", "This is the second paragraph. Life is still good."])
])


#add the second tab (a pure text tab with side by side columns)
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
questions=[
    MultiRowSelectQuestion("Correct?",id={1:"correct"},options=options)
]
multi=MultiRowSelect(rowLabels=["Fragment"],questions=questions)
multi.add_row(id={0:"frag1"},text=["Stocks, bonds and commodities are heading for their strongest simultaneous four-month rise on record, highlighting the breadth of the market recovery during the 2020 economic slowdown."])
multi.add_row(id={0:"frag2"},text=["Through Thursday, the"])
root.add_tab(tabName="Tab 3",block=multi)


#add the fourth tab
col=Column()
#add a nested side-by-side Column
nestedCol=Column()
nestedCol.add_column([
    Text(title= "Article",titleSize=4,body=[
        "The Department of Justice is expected Tuesday to charge Google with violating federal antitrust law, according to two people familiar with the matter, finding after a year-long investigation that the tech giant wrongfully wielded its digital dominance to the detriment of corporate rivals and consumers.",
        "The federal government's imminent lawsuit will touch off a landmark and lengthy legal war between Washington and Silicon Valley, one that could have vast implications not only for Google but the entirety of a tech industry that has faced new, unprecedented scrutiny in recent years for the unrivaled power, money and data it has amassed.",
        "Neither the Justice Department nor Google responded to a request for comment.",
        "A federal antitrust lawsuit marks the start, not the end, of the government's gambit against Google. It could take years for a federal court to resolve whether the company violated the country's competition laws and, if so, what punishments it should may face. Only Republican state attorneys general are expected to sign onto the DOJ's complaint, the Post has previously reported. Other states later may choose to join the Justice Department suit, or they still yet may bring their own lawsuits against the tech giant, widening the legal ground Google must cover to defend its business from serious, potentially far-reaching changes.",
        "But the filing alone still serves as a stunning turn of events for Google, roughly seven years after the federal government last probed the company for potential antitrust violations -- an inquiry that regulators concluded without suing Google or seeking significant penalties, including its breakup. The inaction in Washington for years has stood in stark contrast to the withering antitrust scrutiny Google has faced in Europe, where competition regulators over the past decade have slapped the Mountain View, California-based tech behemoth with $9 billion in fines and sought to secure major changes to the way it offers search, advertising and Android, its smartphone operating system.",
        "The Justice Department began scrutinizing Google as part of a broad review of big tech announced last summer, as federal officials sought to respond to what they described then as widespread concerns that consumers, businesses, and entrepreneurs have expressed about search, social media, and some retail services online. That September, Google started turning over key, sensitive documents to DOJ for its investigation, the company acknowledged in a securities filing at the time.",
        "Initially, DOJ officials signaled an interest in probing the company's advertising business, which contributed the lion's share of the company's total $162 billion in 2019 revenue. Quickly, though, the probe expanded to touch on a wider array of issues in response to a flurry of complaints from rival companies -- from news publishers to travel review websites -- that say Google wields its powerful search engine in myriad ways to entrench its dominance.",
        "At times, the federal probe has proven acrimonious. The DOJ and Google have warred over the company's apparent unwillingness to turn over documents that federal investigators describe as critical to their work. Within DOJ, meanwhile, government lawyers have sparred among themselves over the timeline for bringing a case particularly in the weeks before the 2020 presidential election. Dozens of agency staff signaled this summer they did not feel they were ready to bring charges against Google, but Attorney General William P. Barr ultimately overruled them -- and set the Justice Department on a course to file this month.",
        "The federal investigation has proceeded in parallel with state probes commenced last September by nearly every Democratic and Republican attorney general. The investigations have broadened to encompass more than advertising -- touching on search and the extent to which Google further enhances its dominance through the Android smartphone operating system.",
        "A handful of states including Colorado, Iowa, Nebraska and New York are preparing to issue a joint public statement as soon as Tuesday indicating they are still scrutinizing a wide array of Google's business practices and may instead opt to join any federal case later, according to four people familiar with their thinking, who spoke on the condition of anonymity to discuss a law-enforcement matter. The Post first reported the news last week."
    ],scrollable=True)
])
nestedCol.add_column([
    Text(title= "Summary", titleSize=4,body=["The U.S. Department of Justice (DOJ) is set to file an antitrust lawsuit against Google, alleging the tech giant abused its digital dominance to undermine competition and harm consumers. This legal action marks the commencement of a significant court battle that could have extensive consequences not only for Google but also for the broader technology industry, which has already been under heightened scrutiny for its considerable influence and data accumulation. The lawsuit could take years to conclude whether Google actually breached competition laws and determine the appropriate penalties. This development follows a lengthy period of inactivity in the U.S., contrasting the intense antitrust scrutiny Google has faced in Europe, resulting in $9 billion in fines. This legal action originates from a wider DOJ review that began last summer into major tech companies, with Google's advertising dominance being a major focal point that later expanded to include complaints from various competitor sectors."], scrollable=True),
])
options=[
    MultiRowOption(label="No",value ="no",color="danger"),
    MultiRowOption(label="Yes",value ="yes",color="success")
]
multi=MultiRowChecked(rowLabel="Question",id={1:"goodsummary"},options=options)
multi.add_row(id={0:"article1"},text="Is the summary good?")
col.add_column([nestedCol, multi])
root.add_tab(tabName="Tab 4",block=col)


#add the fifth tab
col=Column()
#add a nested side-by-side Column
nestedCol=Column()
nestedCol.add_column([
    Text(title= "Cluster Description",titleSize=4,body=[
        "Democratic presidential candidate Joe Biden visited Kenosha, Wisconsin, on September 3, 2020, to meet with the family of Jacob Blake, a Black man who was shot by a police officer, igniting several days of protests."
    ],scrollable=True)
])
nestedCol.add_column([
    Text(title= "Article Titles", titleSize=4,body=[
        "Biden to call for healing on Kenosha visit",
        "Joe Biden Meets with Blake Family -- Including Antisemitic, Racist Father",
        "Biden to meet with Jacob Blake's family in Kenosha today",
        "Biden says he spoke with Jacob Blake, praises family's 'resilience and optimism' during Kenosha visit",
        "Joe Biden meets Jacob Blake’s family, tours Kenosha days after Trump visit",
        "Joe Biden meets with Jacob Blake's family after arriving in Wisconsin for Kenosha visit"        
        ], scrollable=True, is_table=True),
])
options=[
    MultiRowOption(label="No",value ="no",color="danger"),
    MultiRowOption(label="Yes",value ="yes",color="success")
]
multi=MultiRowChecked(rowLabel="Question",id={1:"appropriate"},options=options)
multi.add_row(id={0:"cluster1"},text="Is this cluster appropriate?")
col.add_column([nestedCol, multi])
root.add_tab(tabName="Tab 5",block=col)


#add the sixth tab
mainCol=Column()
eventDescription=Text(title="Event Sentence Summary",titleSize=2,body=[
    "In mid-October, vandals targeted former Deputy Mayor Randy Mastro's home on the Upper East Side, New York City, by spraying graffiti and throwing red paint as a protest against his support for closing a local hotel used as a homeless shelter."
])
pertinentArticles=Text(title="Pertinent Articles",titleSize=3)
article1=Text(title="Article 1",titleSize=5,scrollable=True,body=[
    "De Blasio pauses plans to boot disabled from NYC shelter after lawsuit threat",
    "Vandals splattered the front of a prominent Manhattan lawyer’s home with graffiti blaring, “Randy Mastro you can’t displace us” and “F–k you Randy” after he represented a group of residents in their bid to close a West 79th Street hotel that houses homeless men.",
    "Mastro, a former deputy mayor under Rudy Giuliani, was not home at his Upper East Side residence when it was tagged sometime Tuesday night, a source told The Post, but he was alerted by a neighbor whose home was also vandalized and they both reported the incident to the NYPD.",
    "Red paint was splashed on the front door and the words “prick,” “shame,” “Randy Mastro you can’t displace us” and “F–k you Randy” were written on the building’s facade and sidewalk in red and pink.",
    "“This is a very sad day to see a genuine debate about serious issues involving the homeless devolve into vandalism targeting my family’s home. The persons who did this are criminals who should be brought to justice. And if they thought they were going to intimidate me, they picked the wrong guy,” Mastro told The Post.",
    "“I will continue to be a passionate advocate against housing homeless adults in SRO hotels where they don’t get the services [they] need. This vulnerable population requires housing in proper shelters with full services. The City says it is committed to doing just that, and I will continue to advocate for it because that is the right and humane thing to do.”",
    "UWS Hearts Initiative, a group that opposes Mastro’s effort to relocate about 235 homeless men with mental illness or struggling with substance abuse living at the Lucerne Hotel on West 79th Street, tweeted about the incident Wednesday morning."
    "Advertisement",
    "October 21, 2020",
    "“We’ve received reports from one of our faith leaders that Randy Mastro’s home has been vandalized. UWS Open Hearts and Lucerne residents unequivocally condemn this kind of personal attack. Our fight is for human dignity for all, and we extend our support to the Mastro family,” the group tweeted.",
    "A second source said NYPD detectives were interviewing homeless men at the Lucerne about the incident. Police reps did not immediately comment.",
    "Mayor Bill de Blasio announced in early September that he would stop using the Lucerne as a homeless shelter after Mastro threatened a lawsuit."
    "But the men remain in the converted facility after a Manhattan judge blocked their move, following legal challenges both by Lucerne residents and a group of Financial District neighbors who live near a shuttered Radisson Hotel that city officials planned to use as their new shelter."
])
subTabs=Tabs()
mainCol.add_column([eventDescription,pertinentArticles,article1,subTabs])
root.add_tab(tabName="Tab 6",block=mainCol)
#now add the action sub tab 1
actionDescription=Text(title="Action and Actor",titleSize=2,body=[
    "<strong>Action:</strong> Relocating homeless men from the Lucerne Hotel",
    "<strong>Actor:</strong> City officials and Randy Mastro"
])
options=[
    MultiRowOption(label="Yes",value ="yes",color="success"),
    MultiRowOption(label="No",value ="no",color="danger")
]
actionQuestions=MultiRowChecked("Question",id={0:"action1"},options=options)
actionQuestions.add_row(id={1:"contained"},text="Is the action in described in an article?")
actionQuestions.add_row(id={1:"controversial"},text="Is the action controversial?")
actionQuestions.add_row(id={1:"correctactor"},text="Is the correct actor identified in the article?")
argumentFavorDescription = Text(title="Arguments in Favor",titleSize=2)
argumentFavorQuestions=MultiRowSelect(rowLabels=["Argument","Example Fragment"],questions=[
      MultiRowSelectQuestion(label="Is argument present in text?",id={1:"id_present"},options=options),
      MultiRowSelectQuestion(label="Is argument valid?",id={1:"is_valid"},options=options),
])
argumentFavorQuestions.add_row([
    "Homeless adults should not be housed in SRO (Single Room Occupancy) hotels because they cannot provide the necessary services.",
    "I will continue to be a passionate advocate against housing homeless adults in SRO hotels where they don’t get the services [they] need."
],id={0:"tab1_argument_favor1"})
argumentFavorQuestions.add_row([
    "Homeless men at the Lucerne require housing in shelters equipped with full services to address their needs adequately.",
    "This vulnerable population requires housing in proper shelters with full services."
],id={0:"tab1_argument_favor2"})
argumentAgainstDescription = Text(title="Arguments Against",titleSize=2)
argumentAgainstQuestions=MultiRowSelect(rowLabels=["Argument","Example Fragment"],questions=[
      MultiRowSelectQuestion(label="Is argument present in text?",id={1:"id_present"},options=options),
      MultiRowSelectQuestion(label="Is argument valid?",id={1:"is_valid"},options=options),
])
argumentAgainstQuestions.add_row([
    "The relocation efforts are opposed due to the disruption it could cause to the lives of the homeless men involved.",
    "Vandals splattered the front of a prominent Manhattan lawyer’s home with graffiti blaring, “Randy Mastro you can’t displace us”"
],id={0:"tab1_argument_against1"})		
subCol=Column()
subCol.add_column([actionDescription,actionQuestions,argumentFavorDescription,argumentFavorQuestions,argumentAgainstDescription,argumentAgainstQuestions])
subTabs.add_tab(tabName="0",block=subCol)
#now add the action sub tab 2
actionDescription=Text(title="Action and Actor",titleSize=2,body=[
    "<strong>Action:</strong> Threatening or initiating a lawsuit against the city to stop using the Lucerne as a shelter",
    "<strong>Actor:</strong> Randy Mastro"
])
options=[
    MultiRowOption(label="Yes",value ="yes",color="success"),
    MultiRowOption(label="No",value ="no",color="danger")
]
actionQuestions=MultiRowChecked("Question",id={0:"action2"},options=options)
actionQuestions.add_row(id={1:"contained"},text="Is the action in described in an article?")
actionQuestions.add_row(id={1:"controversial"},text="Is the action controversial?")
actionQuestions.add_row(id={1:"correctactor"},text="Is the correct actor identified in the article?")
argumentFavorDescription = Text(title="Arguments in Favor",titleSize=2)
argumentFavorQuestions=MultiRowSelect(rowLabels=["Argument","Example Fragment"],questions=[
      MultiRowSelectQuestion(label="Is argument present in text?",id={1:"id_present"},options=options),
      MultiRowSelectQuestion(label="Is argument valid?",id={1:"is_valid"},options=options),
])
argumentFavorQuestions.add_row([
    "Initiating legal intervention to prevent the inappropriate use of unsuitable facilities for housing vulnerable populations.",
    "Mayor Bill de Blasio announced in early September that he would stop using the Lucerne as a homeless shelter after Mastro threatened a lawsuit."
],id={0:"tab2_argument_favor1"})
argumentAgainstDescription = Text(title="Arguments Against",titleSize=2)
argumentAgainstQuestions=MultiRowSelect(rowLabels=["Argument","Example Fragment"],questions=[
      MultiRowSelectQuestion(label="Is argument present in text?",id={1:"id_present"},options=options),
      MultiRowSelectQuestion(label="Is argument valid?",id={1:"is_valid"},options=options),
])
argumentAgainstQuestions.add_row([
    "The lawsuit causes additional stress and uncertainty for the residents involved, potentially exacerbating their already challenging circumstances.",
    "But the men remain in the converted facility after a Manhattan judge blocked their move, following legal challenges both by Lucerne residents and a group of Financial District neighbors."
],id={0:"tab2_argument_against1"})		
subCol=Column()
subCol.add_column([actionDescription,actionQuestions,argumentFavorDescription,argumentFavorQuestions,argumentAgainstDescription,argumentAgainstQuestions])
subTabs.add_tab(tabName="1",block=subCol)


#add the seventh tab
interactive=Interactive()
#add three paragraph
for i in range(3):
    p=InteractiveParagraph()
    interactive.addParagraph(p)
    #add three fragments per paragraph
    for f in range(2):
        fragmentTab=MultiRowChecked("Question",id={0:f"sentence{i}:{f}"},options=options)
        fragmentTab.add_row(id={1:"like"},text="Do you like this sentence?")
        fragmentTab.add_row(id={1:"grammar"},text="Does it have grammatical errors?")
        fragmentTab.add_row(id={1:"spelling"},text="Are there misspellings?")
        p.addFragment(InteractiveFragment(
            text=f"This is paragraph {i} with sentence {f}.",
            block=fragmentTab
        ))
root.add_tab(tabName="Tab 7",block=interactive)

#now we create the JSON
json=demo.get_json()

#save demo json
with open(os.path.join("__demo","demo.json"), 'w') as f:
    f.write(json)

#now we create the HTML files
review=Review("https://www.kv.econlabs.org/")
review.create(targetFolder="__demo",blockJSON=json,evalTitle="Demo",reviewers=["reviewer1","reviewer2"])

