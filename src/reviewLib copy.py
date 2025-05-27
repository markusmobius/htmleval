import os
import json
import uuid

class Review:

    targetFolder=""
    block=None
    evalTitle=""
 
    def __init__(self,targetFolder,block,evalTitle):
        self.block=block
        self.targetFolder=targetFolder
        self.evalTitle=evalTitle
 
    #provide list of reviewers
    def create(self,reviewers,reviewerIds={}):
        for reviewer in reviewers: 
            htmlFileName=f"{reviewer}.html"
            htmlFileName = os.path.join(self.targetFolder,htmlFileName)
            if os.path.exists(htmlFileName):
                print(f"ignoring {htmlFileName}: already exists. Would you like to overwrite?")
                overwrite = input("y/n: ")
                if overwrite.lower() != "y":
                    continue
    
            #read HTML template
            with open(os.path.join("htmleval", "src","html","template.html"), 'r') as f:
                html = f.read()
            
            #replace reviewer and evaltitle
            html=html.replace("REVIEWERNAME",reviewer)
            html=html.replace("EVALTITLE",self.evalTitle)
            if reviewer not in reviewerIds:
                reviewerID = str(uuid.uuid4())
                # Update the dictionary with the reviewer name and ID
                reviewerIds[reviewer] = reviewerID
            else:
                reviewerID=reviewerIds[reviewer]
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

            #save the HTML file
            with open(htmlFileName, 'w') as f:
                f.write(html)

        #now save reviewer IDs
        reviewerFileName=os.path.join(self.targetFolder, "reviewer_ids.json")
        with open(reviewerFileName, 'w') as f:
           json.dump(reviewerIds, f, indent=4)

        print(f"Reviewer IDs saved to {reviewerFileName}")
