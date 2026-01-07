from src.json.simpleBlocks.multiRowOption import MultiRowOption

class MultiRowChecked:

    def __init__(self, rowLabel: str, id: dict, options: list[MultiRowOption]):
        self.type = "multi_row_checked"
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
