from SafeVarFrame import SafeVarFrame
from SafeVar import MyEntry


class MyEntryFrame(SafeVarFrame):
    highlightAttributes = ["highlightcolor", "highlightbackground"]

    def make_varWidget(self):
        return MyEntry(self, font=self.font, textvariable=self.tkVar, width=self.varWidgetWidth, fg=self.varWidgetFg, justify=self.varWidgetJustify, highlightthickness=2)
