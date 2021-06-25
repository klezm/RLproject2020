import tkinter as tk
from SafeVarFrame import SafeVarFrame


class EntryFrame(SafeVarFrame):
    widgetHighlightthicknessDefault = 2
    highlightAttributes = ["highlightcolor", "highlightbackground"]

    def __init__(self, *args, widgetHighlightthickness=None, **kwargs):
        self.widgetHighlightthickness = self.widgetHighlightthicknessDefault if widgetHighlightthickness is None else widgetHighlightthickness
        super().__init__(*args, **kwargs)

    def make_varWidget(self):
        self.varWidget = tk.Entry(self, **self.get_widget_kwargs())
        #self.varWidget = tk.Entry(self, font=self.font, width=self.widgetWidth, fg=self.widgetFg, widgetHighlightthickness=self.widgetHighlightthickness)
        self.connect()
