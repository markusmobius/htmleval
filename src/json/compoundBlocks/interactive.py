class InteractiveFragment:
    
    def __init__(self, text: str, block, color=None, border=None):
        self.text=text
        self.block=block
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

    def __init__(self, signal: str = None, listeners: list[str] = None):
        self.type="interactive"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content=[]

    def addParagraph(self,p : InteractiveParagraph):
        self.content.append(p)
    


