import tkinter as tk

from SafeVarFrame import SafeVarFrame


class InfoFrame(SafeVarFrame):
    promptAnchorDefault = tk.W
    promptWidthDefault = SafeVarFrame.promptWidthDefault - 1  # Measurement of Label width seems to be a bit different from Entry width
    isInteractive = False

    def __init__(self, *args, promptAnchor=None, **kwargs):
        self.promptAnchor = self.promptAnchorDefault if promptAnchor is None else promptAnchor
        super().__init__(*args, **kwargs)

    def make_prompt(self):
        self.dataPrompt = tk.Label(self, **self.get_prompt_kwargs())
        self.connect()
