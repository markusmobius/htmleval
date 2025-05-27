class Chart:

    def __init__(self,label : str,value : str,color :str =None):
        self.label=label
        self.value=value
        if color is not None:
            self.color=color