import os
import json
import uuid
import requests

class Review:

    def __init__(self,targetFolder,block,evalTitle, serverURL):
        self.block=block
        self.targetFolder=targetFolder
        self.evalTitle=evalTitle
        self.serverURL = serverURL

    #create new review
    def create(self, reviewers, reviewerIds=None):
        # Path to the reviewer IDs file
        reviewerFileName = os.path.join(self.targetFolder, "reviewer_ids.json")

        # Initialize / load existing reviewer IDs
        if reviewerIds is None:
            reviewerIds = {}
        # Merge with on-disk file if it exists (disk is authoritative for existing IDs)
        if os.path.exists(reviewerFileName):
            try:
                with open(reviewerFileName, 'r') as f:
                    existing_ids = json.load(f)
                # Update only missing keys so passed-in reviewerIds (if any) can override intentionally
                for k, v in existing_ids.items():
                    reviewerIds.setdefault(k, v)
            except Exception as e:
                print(f"Warning: could not read existing reviewer IDs '{reviewerFileName}': {e}")

        # Track whether we actually add any new reviewer IDs (or overwrite HTML files)
        reviewer_ids_changed = False

        for reviewer in reviewers: 
            htmlFileName=f"{reviewer}.html"
            htmlFileName = os.path.join(self.targetFolder,htmlFileName)
            if os.path.exists(htmlFileName):
                print(f"ignoring {htmlFileName}: already exists. Would you like to overwrite?")
                overwrite = input("y/n: ")
                if overwrite.lower() != "y":
                    continue
    
            #read HTML template
            with open(os.path.join("htmleval","src","html","template.html"), 'r') as f:
                html = f.read()
            
            #replace reviewer and evaltitle
            html=html.replace("REVIEWERNAME",reviewer)
            html=html.replace("EVALTITLE",self.evalTitle)
            if reviewer not in reviewerIds:
                reviewerID = str(uuid.uuid4())
                reviewerIds[reviewer] = reviewerID
                reviewer_ids_changed = True
            else:
                reviewerID = reviewerIds[reviewer]
            html=html.replace("REVIEWERID",reviewerID)


            #replace BLOCKDATA in template
            html=html.replace("BLOCKDATA", self.block)

            #include all javascript
            js=[]
            #cycle over the compound blocks
            compoundDir=os.path.join("htmleval","src","js","compoundBlocks")
            for fname in os.listdir(compoundDir):
                if os.path.isfile(os.path.join(compoundDir, fname)):
                    with open(os.path.join(compoundDir,fname)) as f:
                        js.append(f.read())
            #cycle over the simple blocks
            simpleDir=os.path.join("htmleval","src","js","simpleBlocks")
            for fname in os.listdir(simpleDir):
                if os.path.isfile(os.path.join(simpleDir, fname)):
                    with open(os.path.join(simpleDir,fname)) as f:
                        js.append(f.read())            
            #add the main build script
            with open(os.path.join("htmleval","src","js","build.js"), 'r') as f:
                js.append(f.read())
            #insert the JS scripts
            html=html.replace("BUILDJS", '\n'.join(js))            
            html=html.replace("SERVERURL",self.serverURL)

            #save the HTML file
            with open(htmlFileName, 'w') as f:
                f.write(html)

        # Save reviewer IDs only if any new IDs were added
        if reviewer_ids_changed:
            try:
                with open(reviewerFileName, 'w') as f:
                   json.dump(reviewerIds, f, indent=4)
                print(f"Reviewer IDs updated in {reviewerFileName}")
            except Exception as e:
                print(f"Error writing reviewer IDs file '{reviewerFileName}': {e}")
        else:
            print("No new reviewer IDs added; existing reviewer_ids.json left unchanged.")

    def close_eval(self, reviewerIds : dict):
        for reviewer, reviewerID in reviewerIds.items():
            print(f"Retrieving data for reviewer {reviewer}")
            # Do a get request to pull down the data.
            url = self.serverURL + reviewerID

            # Send a GET request to the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON data
                data = response.json()
    
                # Save the JSON data to a file
                with open(os.path.join(self.targetFolder, reviewer + "_closed.json"), "w") as file:
                    json.dump(data, file, indent=4)        
            else:
                print(f"Failed to download data. HTTP Status code: {response.status_code}")
