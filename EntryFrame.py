import tkinter as tk
from ParameterFrame import ParameterFrame
from TypedStringVar import TypedStringVar


class EntryFrame(ParameterFrame):
    # TODO: Init for exclusive params
    def make_var_widget(self):
        if self.targetType:
            self.tkVar = TypedStringVar(self.targetType, self.formatSpecifier, value=self.defaultValue)
        else:
            self.tkVar = tk.StringVar(value=self.defaultValue)
        self.varWidget = tk.Entry(self, textvariable=self.tkVar, width=10)
