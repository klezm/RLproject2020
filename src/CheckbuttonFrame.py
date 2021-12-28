import tkinter as tk

from ParameterFrame import ParameterFrame


class CheckbuttonFrame(ParameterFrame):
    """Inheriting from ``ParameterFrame``, this class uses a ``tk.Checkbutton`` as prompt.
    """
    def _make_var(self):
        self.variable = tk.BooleanVar()

    def _make_prompt(self):
        kwargs = self._get_prompt_kwargs()
        self.dataPrompt = tk.Checkbutton(self, variable=self.variable, **kwargs)


if __name__ == "__main__":
    from myFuncs import print_default_kwargs
    print_default_kwargs(CheckbuttonFrame)
