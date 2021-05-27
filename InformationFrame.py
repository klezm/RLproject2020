import tkinter as tk
from ParameterFrame import ParameterFrame
from TypedStringVar import TypedStringVar


class InformationFrame(ParameterFrame):
    def __init__(self, *args, targetType=None, informationWidth=8, **kwargs):
        self.targetType = targetType
        self.informationWidth = informationWidth
        super().__init__(*args, **kwargs)
        self.varWidget.config(font=self.font)

    def make_var_widget(self):
        if self.targetType:
            self.tkVar = TypedStringVar(self.targetType)
        else:
            self.tkVar = tk.StringVar()
        self.varWidget = tk.Label(self, textvariable=self.tkVar, width=self.informationWidth)
