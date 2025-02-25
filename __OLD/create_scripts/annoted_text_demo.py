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

#%% Trial
overall_data = []

## Instructions Tab
outer_tab = {}
outer_tab["tab_id"] = "Tab 1"
outer_tab["nav_tab_name"] = "Tab 1 Name"
outer_tab["header"] = {"text":"Tab 1 Header", "size":1}
outer_tab["content"] = []

# Create Paragraphs JSON:
paragraphs = []
paragraph_1 = {}
fragment_11 = {"text": "This is an example text with two fragments.", "id": "fragment1"}
fragment_12 = {"text": "Together they make up one paragraph.", "id": "fragment2"}
paragraph_1["fragments"] = [fragment_11, fragment_12]
paragraph_2 = {}
fragment_21 = {"text": "This is a second paragraph.", "id": "fragment3"}
paragraph_2["fragments"] = [fragment_21]
paragraphs.append(paragraph_1)
paragraphs.append(paragraph_2)

text = {}
text["type"] = "annotated_text"
text["paragraphs"] = paragraphs 

outer_tab["content"].append(text)

#%% MessageDisplay
text = {}
text["type"] = "message_display"
text["content_map"] = {
    "fragment1": [
        { "type": "text", "header": {"text": "Highlight 1 Title", "size": 2}, "text": "This is the content for highlight 1." },
        { "type": "single-question-checkbox", "varname": "question1", "question": "What is your favorite color?", "options": [{"opt_name": "red", "text": "Red"}, {"opt_name": "blue", "text": "Blue"}, {"opt_name": "green", "text": "Green"}] }
    ],
    "fragment2": [
        { "type": "text", "header": {"text": "Highlight 2 Title", "size": 2}, "text": "This is the content for highlight 2." },
        { "type": "single-question-checkbox", "varname": "question2", "question": "What is your favorite animal?", "options": [{"opt_name": "dog", "text": "Dog"}, {"opt_name": "cat", "text": "Cat"}, {"opt_name": "fish", "text": "Fish"}] }
    ],
    "fragment3": [
        { "type": "text", "header": {"text": "Highlight 3 Title", "size": 2}, "text": "This is the content for highlight 3." }
    ]
}
outer_tab["content"].append(text)
overall_data.append(outer_tab)

### Save overall_data as json
with open(os.path.join("demo.json"), 'w') as f:
    json.dump(overall_data, f, indent=4)
#%% Create HTML

reviewer = "Sir Kiran Kiranelton"
htmlFileName = os.path.join("annotated_text_demo.html")
if os.path.exists(htmlFileName):
    print(f"ignoring {htmlFileName}: already exists. Would you like to overwrite?")
    overwrite = input("y/n: ")
    if overwrite.lower() != "y":
        exit()
    
#read template
with open(os.path.join("src","evaluation","html","template_interactive_text.html"), 'r') as f:
    html = f.read()
#replace reviewer and evaltitle
html=html.replace("REVIEWERNAME",reviewer)
html=html.replace("EVALTITLE","a test of annotated text")

#choose correct script
with open(os.path.join("src","evaluation", "js","buildGeneral.js"), 'r') as f:
    script = f.read()
    script=script.replace("OVERALL_DATA", json.dumps(overall_data))
html=html.replace("JAVASCRIPT",script)


#include server script
with open(os.path.join("src","evaluation", "js","serverJS_mod.js"), 'r') as f:
    script = f.read()
    html=html.replace("SERVERJS",script)

#include interactive text class:
with open(os.path.join("src","evaluation", "js","interactivetext.js"), 'r') as f:
    script = f.read()
    html=html.replace("INTERACTIVETEXTJS",script)

#include interactive text class:
with open(os.path.join("src","evaluation", "js","messagedisplay.js"), 'r') as f:
    script = f.read()
    html=html.replace("MESSAGEDISPLAYJS",script)

reviewerID = str(uuid.uuid4())
html=html.replace("REVIEWERID",reviewerID)

with open(htmlFileName, 'w') as f:
    f.write(html)


# %%
