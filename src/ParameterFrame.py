import tkinter as tk
import re

from ToolTip import ToolTip


class ParameterFrame(tk.Frame):
    """Base class for a custom Frame that holds two widgets side by side.
    The left widget should provide information, the right widget is an
    interactive widget connected to a variable. Its behaviour will be
    defined by daughter classes inheriting from this class.
    """
    fontDefault = "calibri 14 bold"
    promptFgDefault = "black"
    nNameLabelBlanksDefault = 2
    highlightAttributes = ["bg"]  # Default for subclasses
    isInteractive = True  # Default for subclasses

    def __init__(self, master, *args, variable=None, nameLabel=None, value=None, labelWidth=None, explanation=None, promptFg=None, font=None, promptFont=None, nNameLabelBlanks=None, **kwargs):
        """Creates a ParameterFrame object.

        :param master: Parent container.
        :param args: Additional arguments passed to the super().__init__ (tk.Frame)
        :param variable: Pre-build tk.Variable (or daughter class) that will be connected to the interactive widget on the right. If None is passed, a new variable will be build and assigned by the _make_var method that is overwritten by daughter classes.
        :param nameLabel: Widget (or daughter class) that will be used as the widget on the left. If a nonempty str is passed instead, a tk.Label will be build from that. If None or an empty string is passed, there will be no widget on the left at all.
        :param value: Optional initial value for the used variable.
        :param int labelWidth: Width of the widget on the left.
        :param str explanation: If not empty or None, this explanation will be shown in a popup while hovering anywhere over the Frame.
        :param promptFg: Default foreground color of the widget on the right.
        :param font: Font of the widget on the left
        :param promptFont: Font of the widget on the right. If None is passed, propmtFont will be set to the value of font.
        :param nNameLabelBlanks: For optical finetuning, specify how many blanks should be appended to the string shown in the left widget.
        :param kwargs: Additional keyword arguments passed to the super().__init__ (tk.Frame)
        """
        super().__init__(master, *args, **kwargs)
        # setting labelwidth to None gives flexible labels
        self.promptFg = self.promptFgDefault if promptFg is None else promptFg
        self.nNameLabelBlanks = self.nNameLabelBlanksDefault if nNameLabelBlanks is None else nNameLabelBlanks
        self.font = self.fontDefault if font is None else font
        self.promptFont = self.font if promptFont is None else promptFont
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        fontSize = re.findall(r"\d+", self.font)[0]  # get fontSize
        self.tooltipFont = self.font.replace(fontSize, str(int(0.8 * int(fontSize))))  # inner int() because findall() returned a string, outer int() because fontSize must be an integer, not a float
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
        """Should be overwritten by daughter classes.
        """
        pass

    def _make_prompt(self):
        """Should be overwritten by daughter classes.
        """
        pass

    def get_prompt_kwargs(self):
        prefix = "prompt"
        l = len(prefix)
        return {key[l].lower() + key[l+1:]: value for key, value in self.__dict__.items() if key.startswith(prefix)}
