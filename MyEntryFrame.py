from SafeVarFrame import SafeVarFrame
from SafeVar import MyEntry


class MyEntryFrame(SafeVarFrame):
    highlightAttributes = ["highlightcolor", "highlightbackground"]

    def __init__(self, *args, highlightthickness=2, **kwargs):
        self.highlightthickness = highlightthickness
        super().__init__(*args, **kwargs)

    def make_varWidget(self):
        return MyEntry(self, font=self.font, textvariable=self.tkVar, width=self.varWidgetWidth, fg=self.varWidgetFg, justify=self.varWidgetJustify, highlightthickness=self.highlightthickness)
