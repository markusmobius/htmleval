class Tabs:

    def __init__(self, signal: str = None, listeners: list[str] = None, model: dict = None):
        self.type="tabs";
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content=[]
        if model is not None:
            self.model = model
    
    def add_tab(self,tabName: str, block):
        self.content.append({
            "tabName": tabName,
            "block" : block
        })



