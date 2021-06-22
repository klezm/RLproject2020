import tkinter as tk


class ParameterFrame(tk.Frame):
    highlightAttributes = []

    def __init__(self, master, *args, tkVar=None, nameLabel=None, defaultValue=None, font="calibri 14 bold", textColor="black", labelWidth=20, inverse=False, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.font = font
        self.defaultFrameBg = master.cget("bg")
        self.nameLabel = nameLabel  # allows connecting labels of external Frames as nameLabels, if given as nameLabel arg
        if isinstance(self.nameLabel, str):
            self.nameLabel = tk.Label(self, text=nameLabel, fg=textColor, width=labelWidth, anchor=tk.W, font=self.font)
        if self.nameLabel:  # argument None allows ParameterFrame without description
            self.nameLabel.grid(row=0, column=int(inverse))
        self.tkVar = tkVar
        if tkVar is None:
            self.tkVar = self.make_tkVar()
        self.varWidget = self.make_varWidget()
        self.varWidget.grid(row=0, column=int(not inverse))
        self.normalize()
        if defaultValue is not None:
            self.set_value(defaultValue)

    def set_and_call_trace(self, input_Func):
        self.tkVar.trace_add("write", lambda *traceArgs: input_Func())
        input_Func()

    def freeze(self, includeText=True):
        if includeText and self.nameLabel:
            self.nameLabel.config(state=tk.DISABLED)
        self.varWidget.config(state=tk.DISABLED)

    def unfreeze(self):
        if self.nameLabel:
            self.nameLabel.config(state=tk.NORMAL)
        self.varWidget.config(state=tk.NORMAL)

    def highlight(self, color):
        if self.nameLabel:
            self.nameLabel.config(fg=color)
        for attribute in self.highlightAttributes:
            self.varWidget[attribute] = color

    def normalize(self):
        if self.nameLabel:
            self.nameLabel.config(fg="black")
        for attribute in self.highlightAttributes:
            self.varWidget[attribute] = self.defaultFrameBg

    def get_text(self):
        if self.nameLabel:
            return self.nameLabel.cget("text")
        else:
            return ""

    def get_var(self):
        return self.tkVar

    def get_value(self):
        return self.get_var().get()

    def get_font(self):
        return self.font

    def set_value(self, value):
        return self.get_var().set(value)

    def make_tkVar(self) -> tk.Variable:
        pass

    def make_varWidget(self) -> tk.Widget:
        pass
