from htmleval.src.json.simpleBlocks.multiRowOption import MultiRowOption

class MultiRowChecked:

    def __init__(self,rowLabel: str, variableName: str, options : list[MultiRowOption]):
        self.type="multi_row_checked"
        self.content={
                "rowLabel" : rowLabel,
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
    
