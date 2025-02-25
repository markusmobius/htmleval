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

#%% read config, get filepath

configPath =sys.argv[1]
suffix = sys.argv[2]
config_json = load_config(configPath)
dataFolder = config_json["evaldefinition"]["folder"]
included_reviewers = list(sys.argv[3:])
print(included_reviewers)

#%% Load reviewer_ids.json
with open(os.path.join("evaluations", dataFolder, "reviewer_ids.json"), 'r') as f:
    reviewer_ids = json.load(f)
    reviewer_ids = {key: value for key, value in reviewer_ids.items() if key in included_reviewers}

if "gpt" in included_reviewers:
    reviewer_ids["gpt"] = "na"

#%% Create a dictionary which takes all reviewer_ids and keeps "data". 

fullData = {}
fullData["active"] = 0

# Iterate through available reviewers, add their data:
for key, server_address in reviewer_ids.items():
    print(key, server_address)
    # find the reviewer file, should of format key + "_closed.json"
    with open(os.path.join("evaluations", dataFolder, key + "_" + suffix + ".json"), "r") as file:
          reviewer_data = json.load(file)
    fullData[key] = reviewer_data["data"]

#%% Load Article Data (using Oliver's Code)
all_articles = load_sample(configPath)

#%% Construct Matrix and Instructions List
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
        "single": "yes"
    }

    list_of_instructions = []
    ## Get the instructions for the Auditor
    for key, value in config_json["instructions"].items():
        path = os.path.join("prompts", key, "prompt_" + value + ".json") ## seems like needs fixing.
        with open(path, 'r') as f:
            instructions = json.load(f)
            to_append = json_to_html(instructions, ' ', key, viewer_type="human", save = False)
            list_of_instructions.append(to_append)

elif config_json["evaldefinition"]["type"]=="multirowselect":
    tabs = []
    for i, article in enumerate(all_articles):
        if i == 37:
            pass
        else:
            try:
                tab = {
                    "name": config_json["evaldefinition"]["tab_prefix"] + str(i+1),
                    "compoundID": article.id,
                }
                rows = []
                #article.clean(config_json['pipeline']['clean'])
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

#%% Use appropriate JS file and replace relevant variables: 

htmlFileName= "comparison.html"
htmlFileName = os.path.join("evaluations", dataFolder,htmlFileName)
    
#read template and replace EVALTITLE
with open(os.path.join("src","evaluation","html","template_comparison.html"), 'r') as f:
    html = f.read()

html=html.replace("EVALTITLE","Comparison")

#choose correct script
if config_json["evaldefinition"]["type"]=="matrix" or config_json["evaldefinition"]["type"]=="matrix-sum":
    with open(os.path.join("src","evaluation", "js","buildComparisonMatrix.js"), 'r') as f:
        script = f.read()
    script=script.replace("FULLDATA", json.dumps(fullData))
    script=script.replace("MATRIXDATA",json.dumps(data))
    script=script.replace("INSTRUCTIONS",json.dumps(list_of_instructions))
elif config_json["evaldefinition"]["type"]=="multirowselect":
    with open(os.path.join("src","evaluation", "js","buildComparison.js"), 'r') as f:
        script = f.read()
    script=script.replace("FULLDATA", json.dumps(fullData))
    script=script.replace("MULTIROWDATA",json.dumps(data))
    script=script.replace("INSTRUCTIONS",json.dumps(list_of_instructions))
else:
    print(f"evaltype {config_json["evaldefinition"]["type"]} does not exist")


html=html.replace("JAVASCRIPT",script)

with open(htmlFileName, 'w') as f:
    f.write(html)


# #%% Construct the HTML
# with open(os.path.join("src","evaluation","html","template_comparison.html"), 'r') as f:
#     html = f.read()
# #replace reviewer and evaltitle
# html=html.replace("EVALTITLE","Test Evaluation")

# with open(os.path.join("src","evaluation", "js","buildComparison.js"), 'r') as f:
#             script = f.read()

# html=html.replace("JAVASCRIPT", script)

# with open("test1.html", 'w') as f:
#     f.write(html)