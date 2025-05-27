from htmleval.src.json.simpleBlocks.multiRowOption import MultiRowOption

class MultiRowSelect:

    def __init__(self,rowLabel: str,questionLabel: str, variableName: str, options : list[MultiRowOption]):
        self.type="multi_row_select"
        self.content={
                "rowLabel" : rowLabel,
                "questionLabel" : questionLabel,
                "variableName" : variableName,
                "options" : options,
                "rows": []
        }

    def add_row(self,id: str, text: str):
        self.content["rows"].append(
            {
                "id" : id,
                "text" : text
            }
        )
    
