import requests
import json
import sys

#%% Load the JSON data from the URL
# URL of the JSON data
survey_id = sys.argv[1]
to_put_path = sys.argv[2]
url = "https://www.kv.econlabs.org//" + survey_id

#%% Clear the server of old data
# Clear the server of old data
delete_response = requests.delete(url)
if delete_response.status_code == 200:
    print("Successfully cleared old data.")
else:
    print(f"Failed to clear old data. HTTP Status code: {delete_response.status_code}")

# Load the new JSON data from the file
with open(to_put_path, 'r') as file:
    new_data = json.load(file)

# Upload the new JSON data to the server
put_response = requests.put(url, json=new_data)
if put_response.status_code == 200:
    print("Successfully uploaded new data.")
else:
    print(f"Failed to upload new data. HTTP Status code: {put_response.status_code}")