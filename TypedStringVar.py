import tkinter as tk


class TypedStringVar(tk.StringVar):
    def __init__(self, targetType, **kwargs):
        super().__init__(**kwargs)
        self.targetType = targetType

    def get(self):
        return self.targetType(super().get())
