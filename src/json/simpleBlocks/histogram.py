class Histogram:
    def __init__(self, title, width=400, height=200, data=None, labels=None, barColor="#2196F3", yLabel="y-axis", xLabel="x-axis", titleSize=3):
        self.title = title
        self.width = width
        self.height = height
        self.data = data or []
        self.labels = labels or []
        self.barColor = barColor
        self.type = "histogram"
        self.yLabel = yLabel
        self.xLabel = xLabel
        self.content = {
            "width": width,
            "height": height,
            "data": self.data,
            "labels": self.labels,
            "barColor": barColor,
            "yLabel": yLabel,
            "xLabel": xLabel
        }
        if title is not None:
            self.content["title"] = {
                "text": title,
                "size": titleSize
            }

