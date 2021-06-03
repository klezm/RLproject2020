import tkinter as tk
from random import random


class NonEmptyIntVar(tk.IntVar):
    def __init__(self):
        super().__init__()
        self.save_oldValue()

    def get(self, forUse=False):
        a = super().get()
        if forUse:
            try:
                return super().get()
            except:
                self.restore_oldValue()

        return a

    def set(self, value):
        print("set", value, random())
        try:
            self.save_oldValue()
        except:
            pass
        super().set(value)

    def save_oldValue(self):
        self.oldValue = super().get()
        print(self.oldValue, random())

    def restore_oldValue(self):
        super().set(self.oldValue)
