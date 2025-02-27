from src.json.simpleBlocks.multiRowOption import MultiRowOption

class MultiRowSelect:

    def __init__(self,rowLabel: str,questionLabel: str, id: dict, options : list[MultiRowOption]):
        self.type="multi_row_select"
        self.content={
                "rowLabel" : rowLabel,
                "questionLabel": questionLabel,
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
    
