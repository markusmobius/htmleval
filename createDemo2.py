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

# ### Example Data
example = [
    {
        "event_summary": "Here maybe we can include the one-sentence-summary of the event",
        "event_action_argument_pairs": [
                                            {'action': "Giuliani's interaction and subsequent handling of the situation depicted in the Borat film",
                                            'argument': 'The action was justified as a simple adjustment of clothing after removing recording equipment.',
                                            'actor': 'Rudy Giuliani',
                                            'pro_or_con': 'Pro'},
                                            {'action': "Giuliani's interaction and subsequent handling of the situation depicted in the Borat film",
                                            'argument': 'The action is seen as inappropriate and controversial, leading to negative perceptions and ridicule.',
                                            'actor': 'Rudy Giuliani',
                                            'pro_or_con': 'Con'}
                                        ],
        "articles": [
            {
                "compound_id": {"publisher": "the_publisher", "link": "the_link"},
                "paragraphs": [
                    {
                        "text": "Here we have some article text. Each sentence here will either be associated with no argument or with some argument. Let's try and make the first and third associated and the second not associated.",
                        "fragments": [
                            {
                                "start": 0,
                                "end": 31
                            },
                            {
                                "start": 32,
                                "end": 116
                            },
                            {
                                "start": 117,
                                "end": 197
                            }
                        ]
                    },
                    {
                        "text": "This is a second paragraph. It should be seperated by a linebreak.",
                        "fragments": [
                            {
                                "start": 0,
                                "end": 66
                            }
                        ]
                    }
                ]
            },
            {
                "compound_id": {"publisher": "the_publisher2", "link": "the_link2"},
                "paragraphs": [
                    {
                        "text": "This is the first and only paragraph in this article.",
                        "fragments": [
                            {
                                "start": 0,
                                "end": 53
                            }
                        ]
                    }
                ]
            }
        ]
    },
    {
        "event_summary": "Here maybe we can include the one-sentence-summary of the event",
        "event_action_argument_pairs":[
                                            {'action': "Joe's interaction and subsequent handling of the situation depicted in the Borat film",
                                            'argument': 'The action was justified as a simple adjustment of clothing after removing recording equipment.',
                                            'actor': 'Joe',
                                            'pro_or_con': 'Pro'},
                                            {'action': "Joe's interaction and subsequent handling of the situation depicted in the Borat film",
                                            'argument': 'The action is seen as inappropriate and controversial, leading to negative perceptions and ridicule.',
                                            'actor': 'Joe',
                                            'pro_or_con': 'Con'}
                                        ],
        "articles": [
            {
                "compound_id": {"publisher": "the_publisher3", "link": "the_link3"},
                "paragraphs": [
                    {
                        "text": "Here we have some article text. Each sentence here will either be associated with no argument or with some argument. Let's try and make the first and third associated and the second not associated.",
                        "fragments": [
                            {
                                "start": 0,
                                "end": 31
                            },
                            {
                                "start": 32,
                                "end": 116
                            },
                            {
                                "start": 117,
                                "end": 197
                            }
                        ]
                    }
                ]
            }
        ]
    }
]

#%% Now we need to create a a review json that includes a bunch of interactive tabs. 

root=Tabs()
demo = ReviewJSON(root)
## Skip the instructions tab for now
for i, event in enumerate(example):
    ## Add the event summary at the top.
    event_summary = Text(title="Event Sentence Summary", titleSize=2, body=[event["event_summary"]])
    ## Now want to create subtabs. There will be one subtab for each article.
    MainCol = Column()
    root.add_tab(tabName=f"Event {i+1}",block=MainCol)
    subTabs = Tabs()
    ## Add event summary and subtabs to column
    MainCol.add_column([event_summary, subTabs])
    ## Now create the subtabs for each article 
    for j, article in enumerate(event["articles"]):
        ## Create interactive element
        interactive=Interactive()
        subTabs.add_tab(tabName=f"Article {j+1}",block=interactive)
        ## Loop through paragraphs
        for k, paragraph in enumerate(article["paragraphs"]):
            if paragraph["text"] == "":
                continue
            else:
                p = InteractiveParagraph()
                interactive.addParagraph(p)
                fragment_count = 0
                for h, fragment in enumerate(paragraph["fragments"]):
                    ## Skip if empty text:
                        fragment_count += 1
                        ## Create the text for the fragment
                        fragment_text = paragraph["text"][fragment["start"]:fragment["end"]]
                        ## Print the arguments in a table, then under ask to confirm that there is no association. 
                        ## Create table. Columns are "Action", "Argument", multirowcheck if it is included. 
                        options=[
                        MultiRowOption(label="Yes",value ="yes",color="success"),
                        MultiRowOption(label='No', value  = 'no', color="success")
                        ]
                        LeftCol = Column()
                        action_argument_questions=MultiRowSelect(rowLabels=["Action","Argument"],questions=[
                            MultiRowSelectQuestion(label="Does Fragment Support Argument?",id={1:"arg_present"},options=options),
                        ])
                        for l, act_arg in enumerate(event["event_action_argument_pairs"]):
                            action = act_arg['action']
                            arg = act_arg['argument']
                            action_argument_questions.add_row([action, arg], id= {0:{"compound_id":article["compound_id"], "fragment_id": fragment_count, "act_argument_id": l}})
                        
                        ## Add the single question about other actions. 
                        options=[
                            MultiRowOption(label="No",value ="no",color="success"),
                            MultiRowOption(label="Yes",value ="yes",color="danger")
                        ]
                        multi=MultiRowChecked(rowLabel="Question",id={1:"other_actions"},options=options)
                        multi.add_row(id={0:{"compound_id":article["compound_id"], "fragment_id": fragment_count}},text="Does this fragment present an argument for an unlisted action?")
                        ## Add to the interactive tab
                        LeftCol.add_column([action_argument_questions, multi])
                        p.addFragment(InteractiveFragment(
                            text=fragment_text,
                            block=LeftCol
                        ))


#now we create the JSON
json=demo.get_json()

#save demo json
with open(os.path.join("__demo","demo2.json"), 'w') as f:
    f.write(json)

#now we create the HTML files
review=Review("https://www.kv.econlabs.org/")
review.create(targetFolder="__demo2",blockJSON=json,evalTitle="Demo2",reviewers=["reviewer1","reviewer2"])