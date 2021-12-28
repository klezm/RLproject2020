from ParameterFrame import ParameterFrame
from RadiomenuButton import RadiomenuButton
from myFuncs import get_default_kwargs


class RadiomenuButtonFrame(ParameterFrame):
    """Inheriting from ``ParameterFrame``, this class uses a ``RadiomenuButton`` as prompt.\n
    """
    def __init__(self, *args, choices, promptBd=3, promptWidth=None, arrowSymbol=get_default_kwargs(RadiomenuButton)["arrowSymbol"], **kwargs):
        """Creates a RadiomenuButtonFrame object

        :param args: Additional arguments passed to the super().__init__ (ParameterFrame)
        :param list | tuple choices: Allowed options.
        :param int promptBd: Borderwidth of the RadiomenuButton.
        :param int promptWidth: Width of the RadiomenuButton, as number of signs. If None, it will be derived from the longest item among all valid choices.
        :param str arrowSymbol: Arrow to be used to indicate the RadiomenuButton as a dropdown menu.
        :param kwargs: Additional keyword arguments passed to the super().__init__ (ParameterFrame)
        """
        self.choices = choices
        self.arrowSymbol = arrowSymbol
        self.promptBd = promptBd
        self.promptWidth = promptWidth  # setting promptWidth to None makes the RadiomenuButton width the largest of its choices
        super().__init__(*args, **kwargs)

    # If self._make_var() is called, self.variable was None anyway beforehand, so the super()._make_var() can easily be used.

    def _make_prompt(self):
        self.dataPrompt = RadiomenuButton(self, choices=self.choices, choiceVariable=self.variable, arrowSymbol=self.arrowSymbol, **self._get_prompt_kwargs())
        if self.variable is None:
            self.variable = self.dataPrompt.get_choiceVar()  # if self.variable was None before, because it is meant to be taken after the RadiomenuButton construction, the self.variable must be updated now.


if __name__ == "__main__":
    from myFuncs import print_default_kwargs
    print_default_kwargs(RadiomenuButtonFrame)
