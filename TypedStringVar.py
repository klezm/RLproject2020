import tkinter as tk
from tkinter import messagebox


class TypedStringVar(tk.StringVar):
    def __init__(self, targetType, **kwargs):
        super().__init__(**kwargs)
        self.targetType = targetType

    def get(self):
        try:
            return self.targetType(super().get())
        except:
            return None
