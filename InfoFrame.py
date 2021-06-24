import tkinter as tk
from SafeVarFrame import SafeVarFrame


class InfoFrame(SafeVarFrame):
    highlightAttributes = ["fg"]

    def make_varWidget(self):
        return tk.Label(self, font=self.font, textvariable=self.tkVar, width=self.varWidgetWidth, fg=self.varWidgetFg, justify=self.varWidgetJustify)
