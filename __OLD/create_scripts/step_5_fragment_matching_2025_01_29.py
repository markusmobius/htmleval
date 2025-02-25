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

days = load_events(configPath)
events = [json.loads(event) for event in days[0][0]['events']]
classified_fragments = [event['classified_fragments'] for event in events]
print(classified_fragments)

### Organised by action. 
classified_fragments = create_list_of_all_actions(classified_fragments)
print(classified_fragments)


list_of_instructions = []
## Get the instructions for the Auditor
for key, value in config_json["instructions"].items():
    path = os.path.join("prompts", key, "prompt_" + value + ".json") ## seems like needs fixing.
    with open(path, 'r') as f:
        instructions = json.load(f)
        to_append = json_to_html(instructions, ' ', key, viewer_type="human", save = False)
        list_of_instructions.append(to_append)


overall_data = []

## Instructions Tab
outer_tab = {}
outer_tab["tab_id"] = "instructions"
outer_tab["nav_tab_name"] = "Instructions"
outer_tab["header"] = {"text":"Instructions", "size":1}
outer_tab["content"] = []

## Create Instructions Text
text = {}
text["type"] = "text"
text["header"] = None
## Get all items from list of instructions, seperated by <br>
text["text"] = "<br>".join(list_of_instructions)
outer_tab["content"].append(text)
overall_data.append(outer_tab)

for i, action in enumerate(classified_fragments):
    ## Get the basics
    outer_tab = {}
    outer_tab["tab_id"] = "id"+str(i)
    outer_tab["content"] = []

    ## Create a "text" with the one sentence summary
    text = {}
    text["type"] = "text"
    text["header"] = {"text":"Action and Actor", "size":2}
    text["text"] = "<b> Action: </b>"+action['action'] + "<br>" + "<b> Actor: </b>"+action['actor']

    outer_tab["content"].append(text)

    ## Create Inner Tabs
    inner = {}
    inner["type"] = "inner_tabs"
    inner["inner_tab_id"] = "id" + str(i) + "_inner"
    inner["content"] = []

    ## arguments_list

    arguments_list = action['arguments']

    if len(arguments_list) == 0:
        ## Single Question Checkbox
        question = {}
        question["type"] = "single-question-checkbox"
        question["varname"] = "no_controversial_actions"
        question["question"] = "Are there no controversial actions in this event?"
        question["options"] = [{"opt_name": "yes", "text": "Yes"}, {"opt_name": "no", "text": "No"}]
        outer_tab["content"].append(question)
    else:
        for j, argument in enumerate(arguments_list):
            inner_tab = {}
            inner_tab["inner_tab_id"] = "id" + str(i)+"_argument" + str(j)
            inner_tab["content"] = []

            ## Create the text at the top, which gives the argument text
            text = {}
            text["type"] = "text"
            text["header"] = {"text":"Argument", "size":2}
            text["text"] = f"<b> Argument:</b> {argument['argument']}"
            inner_tab["content"].append(text)
            

            ## Create a table_row_unique_select this time. This will just ask if the arguments are valid. 
            table_row = {}
            table_row["type"] = "table_row_unique_select"
            table_row["header"] = {"text":"Associated Fragments", "size":2}
            table_row["col_names"] = ["Fragment"]
            table_row["questions"] = [{"varname": "fragment_associated", "text": "Is this fragment associated with the fragment?"}]
            table_row["options"] = [[{"opt_name": "yes", "text": "Yes", "css": "success"}, {"opt_name": "no", "text": "No", "css": "danger"}]]
            table_row["rows"] = [{"text_columns": [sentence]} for sentence in argument['sentences']]
            inner_tab["content"].append(table_row)


            ## That's everything. Append the inner_tab to the inner_tab list
            inner["content"].append(inner_tab)
        outer_tab["content"].append(inner)
    overall_data.append(outer_tab)

#%% Save overall_data as json
jsonFileName = os.path.join("evaluations", dataFolder, "overall_data.json")

reviewer_ids = {}
#now build the reviews
for reviewer in config_json["evaldefinition"]["reviewers"]:
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
    with open(os.path.join("src","evaluation", "js","buildGeneral.js"), 'r') as f:
        script = f.read()
        script=script.replace("OVERALL_DATA", json.dumps(overall_data))
    html=html.replace("JAVASCRIPT",script)


    #include server script
    with open(os.path.join("src","evaluation", "js","serverJS_mod.js"), 'r') as f:
        script = f.read()
        html=html.replace("SERVERJS",script)
    
    reviewerID = str(uuid.uuid4())
    html=html.replace("REVIEWERID",reviewerID)

    with open(htmlFileName, 'w') as f:
        f.write(html)

    # Update the dictionary with the reviewer name and ID
    reviewer_ids[reviewer] = reviewerID

jsonFileName = os.path.join("evaluations", dataFolder, "reviewer_ids.json")
with open(jsonFileName, 'w') as f:
    json.dump(reviewer_ids, f, indent=4)

print(f"Reviewer IDs saved to {jsonFileName}")