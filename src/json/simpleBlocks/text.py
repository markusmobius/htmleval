class Text:

    def __init__(self, title: str,titleSize: int, body: list[str] = None,scrollable : bool = False,is_table : bool = False):
        self.type="text"
        self.content={
                "scrollable" : scrollable
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
    
