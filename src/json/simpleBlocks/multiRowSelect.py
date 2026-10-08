from .multiRowOption import MultiRowOption

class MultiRowSelectQuestion:

    def __init__(self,label: str, id: dict, options : list[MultiRowOption], correctValue: str = None, model: dict = None):
        self.label=label
        self.id=id
        self.options=options
        if correctValue is not None:
            self.correctValue=correctValue
        if model is not None:
            self.model = model

class MultiRowSelect:

    def __init__(self,rowLabels: list[str],questions: list[MultiRowSelectQuestion], signal: str = None, listeners: list[str] = None, highlight = False, model: dict = None):
        self.type="multi_row_select"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content={
                "rowLabels" : rowLabels,
                "questions": questions,
                "rows": [],
                "highlight": highlight
        }
        if model is not None:
            self.model = model

    def add_row(self,text:list[str], id: dict, default_values: dict = None, correctValues: dict = None, rowData: dict = None, model: dict = None):
        row = {
            "text" : text,
            "id" : id
        }
        if correctValues is not None:
            row["correctValues"] = correctValues
        if rowData is not None:
            row["rowData"] = rowData
        if model is not None:
            row["model"] = model
        self.content["rows"].append(row)
    
