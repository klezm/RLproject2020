import tkinter as tk
from ParameterFrame import ParameterFrame
from TypedStringVar import TypedStringVar


class EntryFrame(ParameterFrame):
    def __init__(self, *args, targetType=None, **kwargs):
        self.targetType = targetType
        super().__init__(*args, **kwargs)

    def make_var_widget(self):
        if self.targetType:
            self.tkVar = TypedStringVar(self.targetType)
        else:
            self.tkVar = tk.StringVar()
        self.varWidget = tk.Entry(self, textvariable=self.tkVar, width=10)
