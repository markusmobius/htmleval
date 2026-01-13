import json

class Thread:

    def __init__(self, title: str = None, titleSize: int = None, body: list[str] = None):
        self.type = "thread"
        self.content = {}
        
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
    
    def addThread(self, block):
        self.threads.append(block)
