from .multiRowOption import MultiRowOption

class MultiRowChecked:

    def __init__(self, rowLabel: str, id: dict, options: list[MultiRowOption], signal: str = None, listeners: list[str] = None, highlight = False, correctValue: str = None):
        self.type = "multi_row_checked"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content = {
            "rowLabel": rowLabel,
            "id": id,
            "rows": [],
            "options": options,
            "highlight": highlight
        }
        if correctValue is not None:
            self.content["correctValue"] = correctValue

    def add_row(self, id: dict, text: str, options: list[MultiRowOption] = None, highlight: str = None, correctValues: dict = None, rowData: dict = None):
        row = {
            "id": id,
            "text": text
        }
        if correctValues is not None:
            row["correctValues"] = correctValues
        if rowData is not None:
            row["rowData"] = rowData
        self.content["rows"].append(row)
