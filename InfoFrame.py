import tkinter as tk
from SafeVarFrame import SafeVarFrame


class InfoFrame(SafeVarFrame):
    def make_varWidget(self):
        self.varWidget = tk.Label(self, **self.get_widget_kwargs())
        self.connect()
