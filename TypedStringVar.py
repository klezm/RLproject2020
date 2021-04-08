import tkinter as tk


class TypedStringVar(tk.StringVar):
    def __init__(self, targetType, formatSpecifier="", **kwargs):
        super().__init__(**kwargs)
        self.targetType = targetType
        #template = "{:" + formatSpecifier + "}"
        #self.trace_add("write", lambda *argDump, newString=template.format(self.get()): self.set(newString))

    def get(self):
        return self.targetType(super().get())
