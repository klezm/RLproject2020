import tkinter as tk
import re

from ToolTip import ToolTip


class ParameterFrame(tk.Frame):
    fontDefault = "calibri 14 bold"
    promptFgDefault = "black"
    nNameLabelBlanksDefault = 2
    highlightAttributes = ["bg"]  # Default for subclasses
    isInteractive = True  # Default for subclasses

    def __init__(self, master, *args, variable=None, nameLabel=None, value=None, labelWidth=None, explanation=None, promptFg=None, font=None, promptFont=None, nNameLabelBlanks=None, **kwargs):
        super().__init__(master, *args, **kwargs)
        # setting labelwidth to None gives flexible labels
        self.promptFg = self.promptFgDefault if promptFg is None else promptFg
        self.nNameLabelBlanks = self.nNameLabelBlanksDefault if nNameLabelBlanks is None else nNameLabelBlanks
        self.font = self.fontDefault if font is None else font
        self.promptFont = self.font if promptFont is None else promptFont
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        fontSize = re.findall(r"\d+", self.font)[0]  # get fontSize
        self.tooltipFont = self.font.replace(fontSize, str(int(0.8 * int(fontSize))))  # inner int() because findall() returned a string, outer int() because fontSize must be an integer
        self.defaultFrameBg = master.cget("bg")
        self.nameLabel = nameLabel  # allows connecting labels of external Frames as nameLabels, if given as nameLabel arg
        if isinstance(self.nameLabel, str):
            self.nameLabel = tk.Label(self, text=f"{nameLabel}:{' ' * self.nNameLabelBlanks}", width=labelWidth, anchor=tk.W, font=self.font)
        if self.nameLabel:  # argument None allows ParameterFrame without description
            self.nameLabel.grid(row=0, column=0, sticky=tk.W)
            if explanation:
                ToolTip(self.nameLabel, text=explanation, font=self.tooltipFont)
        self.variable: tk.Variable = variable
        if variable is None:
            self._make_var()
        self.dataPrompt: tk.Widget = None
        self._make_prompt()
        self.dataPrompt.grid(row=0, column=1, sticky=tk.E)
        self.normalize()
        if value is not None:
            self.set_value(value)

    def set_and_call_trace(self, input_Func):
        self.variable.trace_add(mode="write", callback=lambda *traceArgs: input_Func())
        input_Func()

    def freeze(self, includeText=True):
        if includeText and self.nameLabel:
            self.nameLabel.config(state=tk.DISABLED)
        self.dataPrompt.config(state=tk.DISABLED)

    def unfreeze(self):
        if self.nameLabel:
            self.nameLabel.config(state=tk.NORMAL)
        self.dataPrompt.config(state=tk.NORMAL)

    def highlight(self, color):
        if self.nameLabel:
            self.nameLabel.config(fg=color)
        for attribute in self.highlightAttributes:
            self.dataPrompt[attribute] = color

    def normalize(self):
        if self.nameLabel:
            self.nameLabel.config(fg="black")
        for attribute in self.highlightAttributes:
            self.dataPrompt[attribute] = self.defaultFrameBg

    def get_text(self, raw=False):
        if self.nameLabel:
            if raw:
                return self.nameLabel.cget("text")
            else:
                return self.nameLabel.cget("text")[:-(self.nNameLabelBlanks+1)]
        else:
            return ""

    def get_variable(self):
        return self.variable

    def get_value(self):
        return self.get_variable().get()

    def get_font(self):
        return self.font

    def set_value(self, value):
        return self.get_variable().set(value)

    def _make_var(self):
        pass

    def _make_prompt(self):
        pass

    def get_prompt_kwargs(self):
        prefix = "prompt"
        l = len(prefix)
        return {key[l].lower() + key[l+1:]: value for key, value in self.__dict__.items() if key.startswith(prefix)}
