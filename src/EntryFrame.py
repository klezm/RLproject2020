import tkinter as tk

from SafeVarFrame import SafeVarFrame


class EntryFrame(SafeVarFrame):
    """Inheriting om SafeVarFrame, this class uses a ``tk.Entry`` as prompt.
    """
    highlightAttributes = ["highlightcolor", "highlightbackground"]

    def __init__(self, *args, promptHighlightthickness=2, promptJustify=tk.LEFT, **kwargs):
        """Specifies attributes of the tk.Entry prompt and calls super init.

        :param args: Additional arguments passed to the SafeVarFrame constructor.
        :param int promptHighlightthickness: When highlighting a tk.Entry, only the border of it changes color. This value defines the width of that border.
        :param promptJustify:
        :param kwargs:
        """
        self.promptHighlightthickness = promptHighlightthickness
        self.promptJustify = promptJustify
        super().__init__(*args, **kwargs)

    def _make_prompt(self):
        self.dataPrompt = tk.Entry(self, **self.get_prompt_kwargs())
        self.connect()


if __name__ == "__main__":
    from myFuncs import print_default_kwargs
    print_default_kwargs(EntryFrame)
