import tkinter as tk
from ParameterFrame import ParameterFrame


class InformationFrame(ParameterFrame):
    def __init__(self, *args, TkVarType=tk.StringVar, informationWidth=8, **kwargs):
        self.TkVarType = TkVarType
        self.informationWidth = informationWidth
        super().__init__(*args, **kwargs)
        self.varWidget.config(font=self.font)

    def make_var_widget(self):
        self.tkVar = self.TkVarType()
        self.varWidget = tk.Label(self, textvariable=self.tkVar, width=self.informationWidth)
