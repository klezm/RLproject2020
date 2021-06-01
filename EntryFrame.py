import tkinter as tk
from ParameterFrame import ParameterFrame


class EntryFrame(ParameterFrame):
    def __init__(self, *args, TkVarType=tk.StringVar, entryWidth=8, entryColor="black", **kwargs):
        self.TkVarType = TkVarType
        self.entryWidth = entryWidth
        self.entryColor = entryColor
        super().__init__(*args, **kwargs)
        self.varWidget.config(font=self.font)

    def make_var_widget(self):
        self.tkVar = self.TkVarType()
        self.varWidget = tk.Entry(self, textvariable=self.tkVar, width=self.entryWidth, fg=self.entryColor)
