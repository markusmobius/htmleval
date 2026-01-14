from .multiRowOption import MultiRowOption

class MultiRowChecked:

    def __init__(self, rowLabel: str, id: dict, options: list[MultiRowOption], signal: str = None, listeners: list[str] = None):
        self.type = "multi_row_checked"
        self.signal = signal
        self.listeners = listeners if listeners is not None else []
        self.content = {
            "rowLabel": rowLabel,
            "id": id,
            "rows": [],
            "options": options
        }

    def add_row(self, id: dict, text: str, options: list[MultiRowOption] = None, highlight: str = None):
        row = {
            "id": id,
            "text": text
        }
        self.content["rows"].append(row)
