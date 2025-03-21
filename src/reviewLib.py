import os
import json
import uuid
import requests

class Review:

    def __init__(self,serverURL):
        self.serverURL=serverURL

    #create new review
    def create(self, targetFolder : str, evalTitle : str, blockJSON : str, reviewers : list[str], reviewerIds : dict = {}):
        for reviewer in reviewers: 
            htmlFileName=f"{reviewer}.html"
            htmlFileName = os.path.join(targetFolder,htmlFileName)
            if os.path.exists(htmlFileName):
                print(f"ignoring {htmlFileName}: already exists. Would you like to overwrite?")
                overwrite = input("y/n: ")
                if overwrite.lower() != "y":
                    continue
    
            #read HTML template
            with open(os.path.join("src","html","template.html"), 'r') as f:
                html = f.read()
            
            #replace reviewer and evaltitle
            html=html.replace("REVIEWERNAME",reviewer)
            html=html.replace("EVALTITLE",evalTitle)
            if reviewer not in reviewerIds:
                reviewerID = str(uuid.uuid4())
                # Update the dictionary with the reviewer name and ID
                reviewerIds[reviewer] = reviewerID
            else:
                reviewerID=reviewerIds[reviewer]
            html=html.replace("REVIEWERID",reviewerID)


            #replace BLOCKDATA in template
            html=html.replace("BLOCKDATA", blockJSON)

            #include all javascript
            js=[]
            #cycle over the compound blocks
            compoundDir=os.path.join("src","js","compoundBlocks")
            for fname in os.listdir(compoundDir):
                if os.path.isfile(os.path.join(compoundDir, fname)):
                    with open(os.path.join(compoundDir,fname)) as f:
                        js.append(f.read())
            #cycle over the simple blocks
            simpleDir=os.path.join("src","js","simpleBlocks")
            for fname in os.listdir(simpleDir):
                if os.path.isfile(os.path.join(simpleDir, fname)):
                    with open(os.path.join(simpleDir,fname)) as f:
                        js.append(f.read())            
            #add the main build script
            with open(os.path.join("src","js","build.js"), 'r') as f:
                js.append(f.read())
            #insert the JS scripts
            html=html.replace("BUILDJS", '\n'.join(js))            
            html=html.replace("SERVERURL",self.serverURL)

            #save the HTML file
            with open(htmlFileName, 'w') as f:
                f.write(html)

        #now save reviewer IDs
        reviewerFileName=os.path.join(targetFolder, "reviewer_ids.json")
        with open(reviewerFileName, 'w') as f:
           json.dump(reviewerIds, f, indent=4)

        print(f"Reviewer IDs saved to {reviewerFileName}")

        def close(self, reviewerIds : dict):
            for reviewer, reviewerID in reviewerIds:
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
                    #with open(os.path.join("evaluations", dataFolder, key + "_closed.json"), "w") as file:
                    #    json.dump(data, file, indent=4)        
                else:
                    print(f"Failed to download data. HTTP Status code: {response.status_code}")
