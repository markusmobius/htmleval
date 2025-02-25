class Text:

    def __init__(self,title: str,titleSize: int, body: list[str]):
        self.type="text"
        self.content={
                "title" : {
                    "text": title,
                    "size" : titleSize
                },
                "body":{
                    "text": body
                }
        }
    
