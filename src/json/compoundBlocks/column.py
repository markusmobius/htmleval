import json

class Column:

    def __init__(self):
        self.type="column"
        self.content=[]
    
    def add_column(self,blocks):
        self.content.append(blocks)



