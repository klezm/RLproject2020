import tkinter as tk
from SafeVarFrame import SafeVarFrame


class MyInfoFrame(SafeVarFrame):
    highlightAttributes = ["bg"]

    def make_varWidget(self):
        return tk.Label(self, font=self.font, textvariable=self.tkVar, width=self.varWidgetWidth, fg=self.varWidgetFg, justify=self.varWidgetJustify)
