from htmleval.src.json.simpleBlocks.multiRowOption import MultiRowOption

class MultiRowSelectQuestion:

    def __init__(self,label: str, id: dict, options : list[MultiRowOption]):
        self.label=label
        self.id=id
        self.options=options

class MultiRowSelect:

    def __init__(self,rowLabels: list[str],questions: list[MultiRowSelectQuestion]):
        self.type="multi_row_select"
        self.content={
                "rowLabels" : rowLabels,
                "questions": questions,
                "rows": []
        }

    def add_row(self,text:list[str], id: dict):
        self.content["rows"].append(
            {
                "text" : text,
                "id" : id
            }
        )
    
