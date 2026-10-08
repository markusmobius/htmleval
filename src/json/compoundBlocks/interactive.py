class InteractiveFragment:
    
    def __init__(self, text: str, block, color=None, border=None, model: dict = None):
        self.text=text
        self.block=block
        if model is not None:
            self.model = model
        # Add color attribute support
        if color:
            self.color = color
        # Add border attribute support
        if border:
            self.border = border

class InteractiveParagraph:
    
    def __init__(self):
        self.fragments=[]

    def addFragment(self,f : InteractiveFragment):
        self.fragments.append(f)

class Interactive:

    def __init__(self, signal: str = None, listeners: list[str] = None, model: dict = None):
        self.type="interactive"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content=[]
        if model is not None:
            self.model = model

    def addParagraph(self,p : InteractiveParagraph):
        self.content.append(p)
    


