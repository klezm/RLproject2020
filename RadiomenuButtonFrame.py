from ParameterFrame import ParameterFrame
from RadiomenuButton import RadiomenuButton


class RadiomenuButtonFrame(ParameterFrame):
    highlightAttributes = ["fg"]

    def __init__(self, *args, choices, buttonWidth=None, buttonBd=None, buttonArrowSymbol=None, **kwargs):
        self._choices = choices
        self._buttonWidth = buttonWidth
        self._buttonBd = buttonBd
        self._buttonArrowSymbol = buttonArrowSymbol
        super().__init__(*args, **kwargs)

    def make_tkVar(self):
        return None  # If this is called, self.tkVar was None anyway beforehand

    def make_varWidget(self):
        button = RadiomenuButton(self, choices=self._choices, choiceVariable=self.tkVar, width=self._buttonWidth, bd=self._buttonBd, arrowSymbol=self._buttonArrowSymbol, font=self.font)
        self.tkVar = button.get_choiceVar()  # if self.tkVar was None before, because it is meant to be taken after the RadiomenuButton construction, the self.tkVar must be updated now.
        return button
