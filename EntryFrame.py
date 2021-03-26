import tkinter as tk
from InformationFrame import InformationFrame


class EntryFrame(InformationFrame):
    def make_var_widget(self):
        self.tkVar = tk.StringVar(value=self.defaultValue)
        self.varWidget = tk.Entry(self, textvariable=self.tkVar, width=10)
