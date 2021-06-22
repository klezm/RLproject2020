import tkinter as tk

from ParameterFrame import ParameterFrame


class CheckbuttonFrame(ParameterFrame):
    highlightAttributes = ["bg"]

    def make_tkVar(self):
        return tk.BooleanVar()

    def make_varWidget(self):
        return tk.Checkbutton(self, variable=self.tkVar)
