import tkinter as tk

from SafeVarFrame import SafeVarFrame
from myFuncs import get_default_kwargs


class InfoFrame(SafeVarFrame):
    isInteractive = False

    def __init__(self, *args, promptWidth=get_default_kwargs(SafeVarFrame)["promptWidth"] - 1, promptAnchor=tk.W, **kwargs):
        # Measurement of Label width seems to be a bit different from Entry width
        self.promptAnchor = promptAnchor
        super().__init__(*args, promptWidth=promptWidth, **kwargs)

    def _make_prompt(self):
        self.dataPrompt = tk.Label(self, **self.get_prompt_kwargs())
        self.connect()


if __name__ == "__main__":
    from myFuncs import print_default_kwargs
    print_default_kwargs(InfoFrame)
