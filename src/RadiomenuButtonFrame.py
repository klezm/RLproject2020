from ParameterFrame import ParameterFrame
from RadiomenuButton import RadiomenuButton


class RadiomenuButtonFrame(ParameterFrame):
    promptBdDefault = 3
    arrowSymbolDefault = "⮛"
    
    def __init__(self, *args, choices, promptBd=None, promptWidth=None, arrowSymbol=None, **kwargs):
        self.choices = choices
        self.arrowSymbol = self.arrowSymbolDefault if arrowSymbol is None else arrowSymbol
        self.promptBd = self.promptBdDefault if promptBd is None else promptBd
        self.promptWidth = promptWidth  # setting promptWidth to None makes the RadiomenuButton width the largest of its choices
        super().__init__(*args, **kwargs)

    # If self.make_variable() is called, self.variable was None anyway beforehand, so the super().make_variable() can easily be used.

    def make_prompt(self):
        self.dataPrompt = RadiomenuButton(self, choices=self.choices, choiceVariable=self.variable, arrowSymbol=self.arrowSymbol, **self.get_prompt_kwargs())
        self.variable = self.dataPrompt.get_choiceVar()  # if self.variable was None before, because it is meant to be taken after the RadiomenuButton construction, the self.variable must be updated now.
