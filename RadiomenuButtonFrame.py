from ParameterFrame import ParameterFrame
from RadiomenuButton import RadiomenuButton


class RadiomenuButtonFrame(ParameterFrame):
    widgetWidthDefault = None

    def __init__(self, *args, choices, widgetBd=None, buttonArrowSymbol=None, **kwargs):
        self.choices = choices
        self.widgetBd = widgetBd
        self.buttonArrowSymbol = buttonArrowSymbol
        super().__init__(*args, **kwargs)

        # If self.make_tkVar() is called, self.tkVar was None anyway beforehand, so the super().make_tkVar() can easily be used.

    def make_varWidget(self):
        self.varWidget = RadiomenuButton(self, choices=self.choices, choiceVariable=self.tkVar, arrowSymbol=self.buttonArrowSymbol, **self.get_widget_kwargs())
        self.tkVar = self.varWidget.get_choiceVar()  # if self.tkVar was None before, because it is meant to be taken after the RadiomenuButton construction, the self.tkVar must be updated now.
