import tkinter as tk

from ParameterFrame import ParameterFrame


class CheckbuttonFrame(ParameterFrame):
    def _make_var(self):
        self.variable = tk.BooleanVar()

    def _make_prompt(self):
        kwargs = self.get_prompt_kwargs()
        self.dataPrompt = tk.Checkbutton(self, variable=self.variable, **kwargs)
