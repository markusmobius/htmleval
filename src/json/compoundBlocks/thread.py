import json

class Thread:

    def __init__(self, title: str = None, titleSize: int = None, body: list[str] = None, signal: str = None, listeners: list[str] = None, highlight = False, model: dict = None):
        self.type = "thread"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content = {
            "highlight": highlight
        }
        
        # Store text content structure similar to Text block
        if title is not None:
            self.content["title"] = {
                "text": title,
                "size": titleSize
            }
        
        if body is not None:
            self.content["body"] = {
                "text": body
            }
            
        self.threads = []
        if model is not None:
            self.model = model
    
    def addThread(self, block):
        self.threads.append(block)
