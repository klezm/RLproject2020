import tkinter as tk

from SafeVarFrame import SafeVarFrame
from myFuncs import get_default_kwargs


class InfoFrame(SafeVarFrame):
    """Inheriting om SafeVarFrame, this class uses a ``tk.Label`` as prompt
    and can therefore not accept any user input.
    """
    isInteractive = False

    def __init__(self, *args, promptWidth=get_default_kwargs(SafeVarFrame)["promptWidth"] - 1, promptAnchor=tk.W, **kwargs):  # Measurement of Label width seems to be a bit different from Entry width, therefore the default kwarg correction
        """Specifies attributes of the tk.Label prompt and calls super init.

        :param args: Additional arguments passed to the SafeVarFrame constructor.
        :param int promptWidth: Width of the tk.Label used as prompt. This will be passed to the width argument of its init.
        :param str promptAnchor: Alignment of the value displayed in the tk.Label used as prompt.
        :param kwargs: Additional keyword arguments passed to the SafeVarFrame constructor.
        """
        self.promptAnchor = promptAnchor
        super().__init__(*args, promptWidth=promptWidth, **kwargs)

    def _make_prompt(self):
        self.dataPrompt = tk.Label(self, **self._get_prompt_kwargs())
        self._connect()


if __name__ == "__main__":
    from myFuncs import print_default_kwargs
    print_default_kwargs(InfoFrame)
