class MultiRowOption:

    def __init__(self,label : str,value : str,color :str =None):
        self.label=label
        self.value=value
        if color is not None:
            self.color=color

class MultiRow:

    def __init__(self,rowLabel: str,questionLabel: str, variableName: str, options : list[MultiRowOption]):
        self.type="multi_row"
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
    
