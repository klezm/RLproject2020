import tkinter as tk
import re

from ToolTip import ToolTip


class ParameterFrame(tk.Frame):
    fontDefault = "calibri 14 bold"
    widgetWidthDefault = 8
    widgetFgDefault = "black"
    nNameLabelBlanksDefault = 3
    highlightAttributes = ["bg"]

    def __init__(self, master, *args, tkVar=None, nameLabel=None, defaultValue=None, labelWidth=None, explanation="", widgetWidth=None, widgetFg=None, font=None, nNameLabelBlanks=None, **kwargs):
        super().__init__(master, *args, **kwargs)
        # setting labelwidth to None gives flexible labels
        self.widgetWidth = self.widgetWidthDefault if widgetWidth is None else widgetWidth
        self.widgetFg = self.widgetFgDefault if widgetFg is None else widgetFg
        self.nNameLabelBlanks = self.nNameLabelBlanksDefault if nNameLabelBlanks is None else nNameLabelBlanks
        self.font = self.fontDefault if font is None else font
        self.widgetFont = self.font
        for i in [0,1]:
            self.grid_columnconfigure(i, weight=1)
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
        self.tkVar: tk.Variable = tkVar
        if tkVar is None:
            self.make_var()
        self.varWidget: tk.Widget = None
        self.make_varWidget()
        self.varWidget.grid(row=0, column=1, sticky=tk.E)
        self.normalize()
        if defaultValue is not None:
            self.set_value(defaultValue)

    def set_and_call_trace(self, input_Func):
        self.tkVar.trace_add(mode="write", callback=lambda *traceArgs: input_Func())
        input_Func()

    def freeze(self, includeText=True):
        if includeText and self.nameLabel:
            self.nameLabel.config(state=tk.DISABLED)
        self.varWidget.config(state=tk.DISABLED)

    def unfreeze(self):
        if self.nameLabel:
            self.nameLabel.config(state=tk.NORMAL)
        self.varWidget.config(state=tk.NORMAL)

    def highlight(self, color):
        if self.nameLabel:
            self.nameLabel.config(fg=color)
        for attribute in self.highlightAttributes:
            self.varWidget[attribute] = color

    def normalize(self):
        if self.nameLabel:
            self.nameLabel.config(fg="black")
        for attribute in self.highlightAttributes:
            self.varWidget[attribute] = self.defaultFrameBg

    def get_text(self, raw=False):
        if self.nameLabel:
            if raw:
                return self.nameLabel.cget("text")
            else:
                return self.nameLabel.cget("text")[:-(self.nNameLabelBlanks+1)]
        else:
            return ""

    def get_var(self):
        return self.tkVar

    def get_value(self):
        return self.get_var().get()

    def get_font(self):
        return self.font

    def set_value(self, value):
        return self.get_var().set(value)

    def make_var(self):
        pass

    def make_varWidget(self):
        pass

    def get_widget_kwargs(self):
        #print(self.__dict__)
        prefix = "widget"
        l = len(prefix)
        return {key[l].lower() + key[l+1:]: value for key, value in self.__dict__.items() if key.startswith(prefix)}
