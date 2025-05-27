from htmleval.src.json.simpleBlocks.multiRowOption import MultiRowOption

class MultiRowChecked:

    def __init__(self,rowLabel: str, id: dict, options : list[MultiRowOption]):
        self.type="multi_row_checked"
        self.content={
                "rowLabel" : rowLabel,
                "id" : id,
                "options" : options,
                "rows": []
        }

    def add_row(self,id: dict, text: str):
        self.content["rows"].append(
            {
                "id" : id,
                "text" : text
            }
        )
    
