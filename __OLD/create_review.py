#%% Import Libraries
import os
import json
import sys
import uuid
print(os.getcwd())
# Add the root directory to the sys.path
sys.path.append(os.getcwd())
from src.utils.load_sample import *
from src.prompts.json_to_html import *
from src.evaluation.utils import *

#%% import config
configPath =sys.argv[1]
config_json = load_config(configPath)
dataFolder = config_json["evaldefinition"]["folder"]

#%% Check for optional argument (this will define the "day")
if len(sys.argv) > 2:
    day = int(sys.argv[2])
else:
    day = None
#%% Load Article Data (using Oliver's Code)
if config_json['evaldefinition']['type'] == 'matrix-events' or config_json['evaldefinition']['type'] == 'multirowselect_header':
    days = load_events(configPath)
    events = days[day][0]['events']
    all_articles = days[day][0]['article_pool'].articles
elif config_json['evaldefinition']['type'] == 'multiselect_row_single' or config_json['evaldefinition']['type'] == 'multirowselect_fm':
    days = load_events(configPath)
    events = [json.loads(event) for event in days[0][0]['events']]
else:
    all_articles = load_sample(configPath)

#%% load the relevant data from the articles
# What we want here depends on the type of evaluation we're doing. 
if config_json["evaldefinition"]["type"]=="matrix":
    tabs = []
    for article in all_articles:
        tab = {
            "compoundID": article.id,
            "text": article.content,
            "header": config_json["evaldefinition"]["tab_header"]
        }
        tabs.append(tab)
    
    questions = config_json["evaldefinition"]["questions"]
    options = config_json["evaldefinition"]["options"]
    data = {
        "questions": questions,
        "options": options,
        "tabs": tabs,
    }

    list_of_instructions = []
    ## Get the instructions for the Auditor
    for super_key, super_steps in config_json["instructions"].items():
        for key, value in super_steps.items():
            # Create path, navigate to folder (which is given by key), then use "prompt_" + value +".json"
            path = os.path.join("prompts", super_key, key, "prompt_" + value + ".json") ## seems like needs fixing.
            with open(path, 'r') as f:
                instructions = json.load(f)
                to_append = json_to_html(instructions, ' ', key, viewer_type="human", save = False)
                list_of_instructions.append(to_append)

elif config_json["evaldefinition"]["type"]=="matrix-sum":
    tabs = []
    for article in all_articles:
        try:
            tab = {
                "compoundID": article.id,
                "text": article.content,
                "summary_text": article.get_summary(prompt_version=config_json['pipeline']['summarize']),
                "header": config_json["evaldefinition"]["tab_header"]
            }
            tabs.append(tab)
        except Exception as e:
            print(f"Error processing article {article.id}: {e}")
            continue    
    questions = config_json["evaldefinition"]["questions"]
    options = config_json["evaldefinition"]["options"]
    data = {
        "questions": questions,
        "options": options,
        "tabs": tabs,
    }

    list_of_instructions = []
    ## Get the instructions for the Auditor
    for key, value in config_json["instructions"].items():
        path = os.path.join("prompts", key, "prompt_" + value + ".json") ## seems like needs fixing.
        with open(path, 'r') as f:
            instructions = json.load(f)
            to_append = json_to_html(instructions, ' ', key, viewer_type="human", save = False)
            list_of_instructions.append(to_append)

elif config_json["evaldefinition"]["type"]=="matrix-event":
    tabs = []

    # ## For now just read the file, in future should somehow be in the config file
    # with open("data/derived/event_example.json") as f:
    #     events = json.load(f)
    
    # events = events['events']

    ## Create a list of tabs
    for event in events:
        try:
            tab = {}
            ## Unique ID for the event
            event = json.loads(event)
            tab["compoundID"] = event['uid']
            tab["header"] = ""
            ## One sentence summary of the event
            label = json.loads(event['label'])
            one_sentence_summary = label['one sentence summary']
            tab["text"] = one_sentence_summary

            ## Get the list of articles in the event
            uids = get_uids(event)
            matched_articles = find_matched_articles_info(uids, all_articles)

            ## Only need the "title" of those articles
            article_titles = [article.meta['title'] for article in matched_articles]
            tab["articles"] = article_titles

            tabs.append(tab)
        except Exception as e:
            print(f"Error processing event {event['uid']}: {e}")
            continue

    questions = config_json["evaldefinition"]["questions"]
    options = config_json["evaldefinition"]["options"]
    data = {
        "questions": questions,
        "options": options,
        "tabs": tabs,
    }

    list_of_instructions = []
    ## Get the instructions for the Auditor
    for super_key, super_steps in config_json["instructions"].items():
        for key, value in super_steps.items():
            # Create path, navigate to folder (which is given by key), then use "prompt_" + value +".json"
            path = os.path.join("prompts", super_key, key, "prompt_" + value + ".json") ## seems like needs fixing.
            with open(path, 'r') as f:
                instructions = json.load(f)
                to_append = json_to_html(instructions, ' ', key, viewer_type="human", save = False)
                list_of_instructions.append(to_append)

elif config_json["evaldefinition"]["type"]=="multirowselect":
    tabs = []
    for i, article in enumerate(all_articles):
        try:
            tab = {
                "name": config_json["evaldefinition"]["tab_prefix"] + str(i+1),
                "compoundID": article.id,
            }
            rows = []
            # article.clean(config_json['pipeline']['clean'])
            article.save()
            article.markup_cleaning_positions(config_file_path=configPath)
            for j, segment in enumerate(article.return_classified_segments(config_file_path=configPath)):
                compoundID = article.id.copy()
                compoundID["fragment"] = j
                row = {
                    "compoundID": compoundID,
                    "text": segment["text"],
                    "css": segment["classification"] ## Need to fix this
                }
                rows.append(row)
            tab["rows"] = rows
            tabs.append(tab)
        except Exception as e:
            print(f"Error processing article {article.id}: {e}")
            continue  
    
    questions = config_json["evaldefinition"]["questions"]

    data = {
        "questions": questions,
        "tabs": tabs,
    }
    print("_____")
    print(data)
    print("_____")

    list_of_instructions = []
    ## Get the instructions for the Auditor
    for super_key, super_steps in config_json["instructions"].items():
        for key, value in super_steps.items():
            # Create path, navigate to folder (which is given by key), then use "prompt_" + value +".json"
            path = os.path.join("prompts", super_key, key, "prompt_" + value + ".json")
            with open(path, 'r') as f:
                instructions = json.load(f)
                to_append = json_to_html(instructions, ' ', key, viewer_type="human", save = False)
                list_of_instructions.append(to_append)

elif config_json["evaldefinition"]["type"]=="multirowselect_header":
    tabs = []

    # ## For now just read the file, in future should somehow be in the config file
    # with open("data/derived/event_example.json") as f:
    #     events = json.load(f)
    
    # events = events['events']

    ## Create a list of tabs
    for i, event in enumerate(events):
        try:
            tab = {}
            ## Unique ID for the event
            event = json.loads(event)
            tab["compoundID"] = event['uid']
            tab["header"] = "Cluster Summary"
            ## One sentence summary of the event
            label = json.loads(event['label'])
            one_sentence_summary = label['one sentence summary']
            tab["text"] = one_sentence_summary
            tab["table_header"] = config_json["evaldefinition"]["table_header"]
            tab["name"] = config_json["evaldefinition"]["tab_prefix"] + str(i+1)

            ## Get rows
            rows = []
            ## Get the list of articles in the event
            uids = get_uids(event)
            matched_articles = find_matched_articles_info(uids, all_articles)

            ## Only need the "title" of those articles
            for j, article in enumerate(matched_articles):
                row = {
                    "compoundID": article.id.copy(),
                    "text": article.meta['title'],
                    "css": ""
                }
                rows.append(row)
            
            tab["rows"] = rows
            tabs.append(tab)
        except Exception as e:
            print(f"Error processing event {event['uid']}: {e}")
            continue

    questions = config_json["evaldefinition"]["questions"]

    data = {
        "questions": questions,
        "tabs": tabs,
    }
    print("_____")
    print(data)
    print("_____")

    list_of_instructions = []
    ## Get the instructions for the Auditor
    for super_key, super_steps in config_json["instructions"].items():
        for key, value in super_steps.items():
            # Create path, navigate to folder (which is given by key), then use "prompt_" + value +".json"
            path = os.path.join("prompts", super_key, key, "prompt_" + value + ".json") ## seems like needs fixing.
            with open(path, 'r') as f:
                instructions = json.load(f)
                to_append = json_to_html(instructions, ' ', key, viewer_type="human", save = False)
                list_of_instructions.append(to_append)

elif config_json["evaldefinition"]["type"]=="multirowselect_header_fragment":
    tabs = []

    ## For now just read the file, in future we'll remove this from here and have it be loaded from config. 
    data = json.load(open('data/derived/temp_events_with_fragments.json'))
    event = json.loads(data['events'][0])

    ## Given event, obtain a dictionary of action and fragments
    actions_dict = get_actions_dict(event)

    ## Now, for each action create a tab
    for i, action in enumerate(actions_dict.keys()):
        try:
            tab = {}
            tab["compoundID"] = {}
            ## Unique ID for the action
            tab["compoundID"]["event"] = event['uid']
            tab["compoundID"]["action"] = i

            ## Create the head for the Tab
            tab["header"] = "Pertinent Action:"
            
            ## Get the action itself
            tab["text"] = action
            tab["table_header"] = config_json["evaldefinition"]["table_header"]
            tab["name"] = config_json["evaldefinition"]["tab_prefix"] + str(i+1)

            ## Create the relevant rows
            rows = []

            ## Go through the list of fragments
            for j, fragment in enumerate(actions_dict[action]):
                compoundID = tab["compoundID"].copy()
                compoundID["fragment"] = j
                row = {
                    "compoundID": compoundID,
                    "text": fragment,
                    "css": ""
                }
                rows.append(row)
            
            tab["rows"] = rows
            tabs.append(tab)
        except Exception as e:
            print(f"Error processing event {action}: {e}")
            continue

    questions = config_json["evaldefinition"]["questions"]

    data = {
        "questions": questions,
        "tabs": tabs,
    }
    print("_____")
    print(data)
    print("_____")

    list_of_instructions = []
    ## Get the instructions for the Auditor
    for key, value in config_json["instructions"].items():
        path = os.path.join("prompts", key, "prompt_" + value + ".json") ## seems like needs fixing.
        with open(path, 'r') as f:
            instructions = json.load(f)
            to_append = json_to_html(instructions, ' ', key, viewer_type="human", save = False)
            list_of_instructions.append(to_append)

elif config_json["evaldefinition"]["type"]=="multiselect_row_single":

    ## For now just read the file, in future we'll remove this from here and have it be loaded from config. 
    # data = json.load(open('data/derived/temp_events_with_fragments.json'))
    # event = json.loads(data['events'][0])
    
    # We now have a list of events

    tabs = []
    for i, event in enumerate(events):
        tab = {}

    ## Given event, obtain a dictionary of action and fragments

        actions_dict = get_actions_dict(event)
        if len(actions_dict) == 0:
            continue
        ## I think in this case we only have the one tab... 
        
        tab["compoundID"] = {}
        ## Unique ID for the action
        tab["compoundID"]["event"] = event['uid']
        tab["table_header"] = config_json["evaldefinition"]["table_header"]
        tab["header"] = "Event Summary"
        ## One sentence summary of the event
        label = json.loads(event['label'])
        one_sentence_summary = label['one sentence summary']
        tab["text"] = one_sentence_summary
        ## Sort the actions by the number of fragments associated with each:
        actions_dict = dict(sorted(actions_dict.items(), key=lambda item: len(item[1]), reverse=True))

        ## Create a list, stored in tab["column"] which gives the number of fragments associated with each action
        tab["column"] = [len(actions_dict[action]) for action in actions_dict.keys()]
        tab["column_header"] = "# Associated Fragments"
        tab["name"] = i+1
        print(tab["column"])

        ## Create a list of actions, stored in tab["rows"]

        rows = []

        for j, action in enumerate(actions_dict.keys()):
            compoundID = tab["compoundID"].copy()
            compoundID["action"] = j
            row = {
                "compoundID": compoundID,
                "text": action,
                "css": ""
            }
            rows.append(row)

        tab["rows"] = rows
        tabs.append(tab)
        # except Exception as e:
        #     print(f"Error processing event {event}: {e}")
        #     continue

    questions = config_json["evaldefinition"]["question"]

    data = {
        "question": questions,
        "tabs": tabs,
    }

    list_of_instructions = []
    ## Get the instructions for the Auditor
    for key, value in config_json["instructions"].items():
        path = os.path.join("prompts", key, "prompt_" + value + ".json") ## seems like needs fixing.
        with open(path, 'r') as f:
            instructions = json.load(f)
            to_append = json_to_html(instructions, ' ', key, viewer_type="human", save = False)
            list_of_instructions.append(to_append)
            print(list_of_instructions)

reviewer_ids = {}
#now build the reviews
for reviewer in config_json["evaldefinition"]["reviewers"]:
    if day != None:
        htmlFileName=f"{reviewer}_{dataFolder}_day_{day}.html"    
    else:
        htmlFileName=f"{reviewer}_{dataFolder}.html"
    htmlFileName = os.path.join("evaluations", dataFolder,htmlFileName)
    if os.path.exists(htmlFileName):
        print(f"ignoring {htmlFileName}: already exists. Would you like to overwrite?")
        overwrite = input("y/n: ")
        if overwrite.lower() != "y":
            continue
        
    #read template
    with open(os.path.join("src","evaluation","html","template.html"), 'r') as f:
        html = f.read()
    #replace reviewer and evaltitle
    html=html.replace("REVIEWERNAME",reviewer)
    html=html.replace("EVALTITLE",dataFolder)

    #choose correct script
    if config_json["evaldefinition"]["type"]=="matrix" or config_json["evaldefinition"]["type"]=="matrix-sum" or config_json["evaldefinition"]["type"]=="matrix-event":
        with open(os.path.join("src","evaluation", "js","buildReviewMatrix.js"), 'r') as f:
            script = f.read()
        script=script.replace("MATRIXDATA",json.dumps(data))
        script=script.replace("INSTRUCTIONS",json.dumps(list_of_instructions))
    elif config_json["evaldefinition"]["type"]=="multirowselect" or config_json["evaldefinition"]["type"]=="multirowselect_header" or config_json["evaldefinition"]["type"]=="multirowselect_header_fragment":
        with open(os.path.join("src","evaluation", "js","buildMultiRowSelect.js"), 'r') as f:
            script = f.read()
        script=script.replace("MULTIROWDATA",json.dumps(data))
        script=script.replace("INSTRUCTIONS",json.dumps(list_of_instructions))
    elif config_json["evaldefinition"]["type"]=="multiselect_row_single":
        with open(os.path.join("src","evaluation", "js","buildMultiRowRadio.js"), 'r') as f:
            script = f.read()
        script=script.replace("MULTIROWDATA",json.dumps(data))
        script=script.replace("INSTRUCTIONS",json.dumps(list_of_instructions))
    else:
        print(f"evaltype {config_json["evaldefinition"]["type"]} does not exist")


    html=html.replace("JAVASCRIPT",script)

    #include server script
    with open(os.path.join("src","evaluation", "js","serverJS.js"), 'r') as f:
        script = f.read()
        html=html.replace("SERVERJS",script)
    reviewerID = str(uuid.uuid4())
    html=html.replace("REVIEWERID",reviewerID)

    with open(htmlFileName, 'w') as f:
        f.write(html)

    # Update the dictionary with the reviewer name and ID
    reviewer_ids[reviewer] = reviewerID

# Save the reviewer IDs to a JSON file
if day != None:
    jsonFileName = os.path.join("evaluations", dataFolder, f"reviewer_ids_day_{day}.json")
else:
    jsonFileName = os.path.join("evaluations", dataFolder, "reviewer_ids.json")
with open(jsonFileName, 'w') as f:
    json.dump(reviewer_ids, f, indent=4)

print(f"Reviewer IDs saved to {jsonFileName}")