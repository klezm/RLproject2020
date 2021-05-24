import tkinter as tk


class ParameterFrame(tk.Frame):
    def __init__(self, *args, text="", defaultValue=None, font="calibri 14 bold", textColor="black", labelWidth=20, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = font
        self.nameLabel = tk.Label(self, text=text, fg=textColor, width=labelWidth, anchor=tk.W, font=self.font)
        self.nameLabel.grid(row=0, column=0)
        self.tkVar = None
        self.varWidget= None
        self.make_var_widget()
        self.varWidget.grid(row=0, column=1)
        if defaultValue is not None:
            self.set_value(defaultValue)

    def set_and_call_trace(self, inputFunc):
        def traceFunc(*traceArgsDump):
            if self.get_value() is None:
                return
            inputFunc()
        self.tkVar.trace_add("write", traceFunc)
        traceFunc()

    def freeze(self, includeText=True):
        self.varWidget.config(state=tk.DISABLED)
        if includeText:
            self.nameLabel.config(state=tk.DISABLED)

    def unfreeze(self):
        self.varWidget.config(state=tk.NORMAL)
        self.nameLabel.config(state=tk.NORMAL)

    def get_text(self):
        return self.nameLabel.cget("text")

    def get_var(self):
        return self.tkVar

    def get_value(self):
        return self.get_var().get()

    def set_value(self, value):
        return self.get_var().set(value)

    def set_color(self, color):
        self.nameLabel.config(fg=color)

    def make_var_widget(self):
        pass
