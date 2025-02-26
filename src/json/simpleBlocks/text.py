class Text:

    def __init__(self, title: str,titleSize: int, body: list[str],scrollable : bool = False):
        self.type="text"
        self.content={
                "scrollable" : scrollable,
                "title" : {
                    "text": title,
                    "size" : titleSize
                },
                "body":{
                    "text": body
                }
        }
    
