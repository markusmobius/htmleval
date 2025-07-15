class InteractiveFragment:
    
    def __init__(self, text: str, block, color=None):
        self.text=text
        self.block=block
        # Add color attribute support
        if color:
            self.color = color

class InteractiveParagraph:
    
    def __init__(self):
        self.fragments=[]

    def addFragment(self,f : InteractiveFragment):
        self.fragments.append(f)

class Interactive:

    def __init__(self):
        self.type="interactive"
        self.content=[]

    def addParagraph(self,p : InteractiveParagraph):
        self.content.append(p)
    


