import tkinter as tk

import myFuncs


class ParameterFrame(tk.Frame):
    def __init__(self, *args, text="", defaultValue=None, font="calibri 14 bold", textColor="black", labelWidth=20, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = font
        self.nameLabel = tk.Label(self, text=text, fg=textColor, width=labelWidth, anchor=tk.W, font=self.font)
        self.nameLabel.grid(row=0, column=0)
        self.tkVar = None
        self.varWidget = None
        self.make_var_widget()
        self.varWidgetDefaultBg = self.varWidget.cget("bg")
        self.varWidget.grid(row=0, column=1)
        if defaultValue is not None:
            self.set_value(defaultValue)

    def set_and_call_trace(self, inputFunc):
        myFuncs.set_and_call_trace(self.get_var(), inputFunc)

    def freeze(self, includeText=True):
        self.varWidget.config(state=tk.DISABLED)
        if includeText:
            self.nameLabel.config(state=tk.DISABLED)

    def unfreeze(self):
        self.varWidget.config(state=tk.NORMAL)
        self.nameLabel.config(state=tk.NORMAL)

    def highlight(self, color):
        self.varWidget.config(bg=color)
        self.nameLabel.config(fg=color)

    def normalize(self):
        self.varWidget.config(bg=self.varWidgetDefaultBg)
        self.nameLabel.config(fg="black")

    def get_text(self):
        return self.nameLabel.cget("text")

    def get_var(self):
        return self.tkVar

    def get_value(self):
        return self.get_var().get()

    def set_value(self, value):
        return self.get_var().set(value)

    def make_var_widget(self):
        pass
