import tkinter as tk

from SafeVarFrame import SafeVarFrame


class EntryFrame(SafeVarFrame):
    promptJustifyDefault = tk.LEFT
    promptHighlightthicknessDefault = 2
    highlightAttributes = ["highlightcolor", "highlightbackground"]

    def __init__(self, *args, promptHighlightthickness=None, promptJustify=None, **kwargs):
        self.promptHighlightthickness = self.promptHighlightthicknessDefault if promptHighlightthickness is None else promptHighlightthickness
        self.promptJustify = self.promptJustifyDefault if promptJustify is None else promptJustify
        super().__init__(*args, **kwargs)

    def make_prompt(self):
        self.dataPrompt = tk.Entry(self, **self.get_prompt_kwargs())
        self.connect()
