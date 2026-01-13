import json

class Column:

    def __init__(self, signal: str = None, listeners: list[str] = None):
        self.type="column"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content=[]
    
    def add_column(self,blocks):
        self.content.append(blocks)



