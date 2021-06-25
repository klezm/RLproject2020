import tkinter as tk

from ParameterFrame import ParameterFrame


class CheckbuttonFrame(ParameterFrame):
    widgetWidthDefault = 1

    def make_var(self):
        self.tkVar = tk.BooleanVar()

    def make_varWidget(self):
        kwargs = self.get_widget_kwargs()
        print(kwargs)
        kwargs["width"] = 4
        self.varWidget = tk.Checkbutton(self, variable=self.tkVar, **kwargs)
