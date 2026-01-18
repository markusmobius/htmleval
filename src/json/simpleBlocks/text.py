class Text:

    def __init__(self, title: str =None,titleSize: int = None, body: list[str] = None, verticalHeight : int = None,is_table : bool = False, signal: str = None, listeners: list[str] = None, highlight = False):
        self.type="text"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        if (verticalHeight ==None):
            self.content={
                "highlight" : highlight
            }
        else:
            self.content={
                "verticalHeight" : verticalHeight,
                "highlight" : highlight 
            }
        if title is not None:
            self.content["title"]={
                "text": title,
                "size" : titleSize
            }
        if body is not None:
            self.content["body"]={
                    "is_table" : is_table,
                    "text": body
                }
    
