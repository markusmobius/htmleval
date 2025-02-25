class Tabs:

    def __init__(self):
        self.type="tabs";
        self.content=[]
    
    def add_tab(self,tabName: str, block):
        self.content.append({
            "tabName": tabName,
            "block" : block
        })



