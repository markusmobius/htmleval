class Tabs:

    def __init__(self, signal: str = None, listeners: list[str] = None):
        self.type="tabs";
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content=[]
    
    def add_tab(self,tabName: str, block):
        self.content.append({
            "tabName": tabName,
            "block" : block
        })



