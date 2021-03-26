import tkinter as tk
from InformationFrame import InformationFrame


class CheckbuttonFrame(InformationFrame):
    def make_var_widget(self):
        self.tkVar = tk.BooleanVar(value=self.defaultValue)
        self.varWidget = tk.Checkbutton(self, variable=self.tkVar)