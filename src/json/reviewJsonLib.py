import json

class ReviewJSON:
 
    def __init__(self,root):
        self.root=root
        self.defaults = {}

    def add_default(self, id_json, value):
        self.defaults[id_json] = value

    def get_json(self):
        base = json.dumps(self.root, default=lambda x: x.__dict__)
        
        # If there are defaults, add them to the data.variables section
        if self.defaults:
            data_obj = json.loads(base)
            # Initialize data and variables if they don't exist
            if "data" not in data_obj:
                data_obj["data"] = {}
            if "variables" not in data_obj["data"]:
                data_obj["data"]["variables"] = {}
            data_obj["data"]["variables"].update(self.defaults)
            return json.dumps(data_obj)
        else:
            return base
        
        