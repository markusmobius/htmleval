import json

class ReviewJSON:
 
    def __init__(self,root):
        self.root=root

    def get_json(self):
        return json.dumps(self.root,default=lambda x: x.__dict__)
        