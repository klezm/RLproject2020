import tkinter as tk
from ParameterFrame import ParameterFrame


class CheckbuttonFrame(ParameterFrame):
    def make_var_widget(self):
        self.tkVar = tk.BooleanVar(value=self.defaultValue)
        self.varWidget = tk.Checkbutton(self, variable=self.tkVar)