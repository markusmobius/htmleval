from htmleval.src.json.simpleBlocks.multiRowOption import MultiRowOption

class MultiRowChecked:

    def __init__(self, rowLabel: str, id: dict, options: list[MultiRowOption] = None, custom_colours: bool = False):
        self.type = "multi_row_checked"
        self.content = {
            "rowLabel": rowLabel,
            "id": id,
            "rows": [],
            "custom_colours": custom_colours
        }
        if not custom_colours:
            self.content["options"] = options if options is not None else []

    def add_row(self, id: dict, text: str, options: list[MultiRowOption] = None, highlight: str = None, default_value: str = None):
        row = {
            "id": id,
            "text": text
        }
        if self.content.get("custom_colours", False) and options is not None:
            row["options"] = options
        if highlight is not None:
            row["highlight"] = highlight
        if default_value is not None:
            row["default_value"] = default_value
        self.content["rows"].append(row)
