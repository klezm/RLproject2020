import tkinter as tk

from ParameterFrame import ParameterFrame


class CheckbuttonFrame(ParameterFrame):
    def make_var(self):
        self.variable = tk.BooleanVar()

    def make_prompt(self):
        kwargs = self.get_prompt_kwargs()
        self.dataPrompt = tk.Checkbutton(self, variable=self.variable, **kwargs)
