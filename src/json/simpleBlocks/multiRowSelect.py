from .multiRowOption import MultiRowOption

class MultiRowSelectQuestion:

    def __init__(self,label: str, id: dict, options : list[MultiRowOption], correctValue: str = None):
        self.label=label
        self.id=id
        self.options=options
        if correctValue is not None:
            self.correctValue=correctValue

class MultiRowSelect:

    def __init__(self,rowLabels: list[str],questions: list[MultiRowSelectQuestion], signal: str = None, listeners: list[str] = None, highlight = False):
        self.type="multi_row_select"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content={
                "rowLabels" : rowLabels,
                "questions": questions,
                "rows": [],
                "highlight": highlight
        }

    def add_row(self,text:list[str], id: dict, default_values: dict = None, correctValues: dict = None, rowData: dict = None):
        row = {
            "text" : text,
            "id" : id
        }
        if correctValues is not None:
            row["correctValues"] = correctValues
        if rowData is not None:
            row["rowData"] = rowData
        self.content["rows"].append(row)
    
