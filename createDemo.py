import os
import json
from src.evaluation.reviewLib import Review

#load demo tabs
with open(os.path.join("src","evaluation","demo","demoTabs.json"), 'r') as f:
    demo = json.loads(f.read())

#create review instance
review=Review("",demo,"Demo")

review.create(["Reviewer1","Reviewer2"])
