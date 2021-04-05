import tkinter as tk

class ParameterFrame(tk.Frame):
    def __init__(self, mother, name, defaultValue, targetType=None, fontsize=14, textColor="black", **kwargs):
        super().__init__(mother, **kwargs)
        self.font = f"calibri {fontsize} bold"
        self.nameLabel = tk.Label(self, text=name, fg=textColor, width=20, anchor=tk.W, font=self.font)
        self.nameLabel.grid(row=0, column=0)
        self.tkVar = None
        self.defaultValue = defaultValue
        self.targetType = targetType
        self.varWidget = None
        self.make_var_widget()
        self.varWidget.config(font=self.font)
        self.varWidget.grid(row=0, column=1)

    def get_var(self):
        return self.tkVar

    def make_var_widget(self):
        pass
