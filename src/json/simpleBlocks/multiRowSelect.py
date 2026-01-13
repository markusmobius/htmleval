from src.json.simpleBlocks.multiRowOption import MultiRowOption

class MultiRowSelectQuestion:

    def __init__(self,label: str, id: dict, options : list[MultiRowOption]):
        self.label=label
        self.id=id
        self.options=options

class MultiRowSelect:

    def __init__(self,rowLabels: list[str],questions: list[MultiRowSelectQuestion], signal: str = None, listeners: list[str] = None):
        self.type="multi_row_select"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content={
                "rowLabels" : rowLabels,
                "questions": questions,
                "rows": []
        }

    def add_row(self,text:list[str], id: dict, default_values: dict = None):
        row = {
            "text" : text,
            "id" : id
        }
        self.content["rows"].append(row)
    
