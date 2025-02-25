#%% Import Libraries
import os
import json
import sys
import uuid
import requests
print(os.getcwd())
# Add the root directory to the sys.path
sys.path.append(os.getcwd())
from src.utils.load_sample import *
from src.prompts.json_to_html import *

#%% import config
configPath =sys.argv[1]
config_json = load_config(configPath)
dataFolder = config_json["evaldefinition"]["folder"] ## We can find the reviewer_ids in that folder

#%% Find reviewer IDS
with open("evaluations/"+ dataFolder + "/reviewer_ids.json", 'r') as f:
    reviewer_ids = json.load(f)

#%% Combined those IDs with server name, and do a get to pull down data. 

for key, server_address in reviewer_ids.items():
    print(key, server_address)
    # Do a get request to pull down the data.
    url = "https://www.kv.econlabs.org//" + server_address

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()
        
        # Save the JSON data to a file
        with open(os.path.join("evaluations", dataFolder, key + "_closed.json"), "w") as file:
            json.dump(data, file, indent=4)
        
        # print("Data downloaded and saved to data.json")
        # data = list(data.values())[-1]
    else:
        print(f"Failed to download data. HTTP Status code: {response.status_code}")