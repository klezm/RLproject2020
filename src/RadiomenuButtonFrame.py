from ParameterFrame import ParameterFrame
from RadiomenuButton import RadiomenuButton
from myFuncs import get_default_kwargs


class RadiomenuButtonFrame(ParameterFrame):
    def __init__(self, *args, choices, promptBd=3, promptWidth=None, arrowSymbol=get_default_kwargs(RadiomenuButton)["arrowSymbol"], **kwargs):
        self.choices = choices
        self.arrowSymbol = arrowSymbol
        self.promptBd = promptBd
        self.promptWidth = promptWidth  # setting promptWidth to None makes the RadiomenuButton width the largest of its choices
        super().__init__(*args, **kwargs)

    # If self.make_variable() is called, self.variable was None anyway beforehand, so the super().make_variable() can easily be used.

    def _make_prompt(self):
        self.dataPrompt = RadiomenuButton(self, choices=self.choices, choiceVariable=self.variable, arrowSymbol=self.arrowSymbol, **self.get_prompt_kwargs())
        self.variable = self.dataPrompt.get_choiceVar()  # if self.variable was None before, because it is meant to be taken after the RadiomenuButton construction, the self.variable must be updated now.


if __name__ == "__main__":
    from myFuncs import print_default_kwargs
    print_default_kwargs(RadiomenuButtonFrame)
