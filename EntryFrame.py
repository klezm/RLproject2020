import tkinter as tk
from ParameterFrame import ParameterFrame
from TypedStringVar import TypedStringVar


class EntryFrame(ParameterFrame):
    def __init__(self, *args, targetType=None, entryWidth=8, entryColor="black", **kwargs):
        self.targetType = targetType
        self.entryWidth = entryWidth
        self.entryColor = entryColor
        super().__init__(*args, **kwargs)
        self.varWidget.config(font=self.font)

    def make_var_widget(self):
        if self.targetType:
            self.tkVar = TypedStringVar(self.targetType)
        else:
            self.tkVar = tk.StringVar()
        self.varWidget = tk.Entry(self, textvariable=self.tkVar, width=self.entryWidth, fg=self.entryColor)
