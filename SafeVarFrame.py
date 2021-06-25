import tkinter as tk

from ParameterFrame import ParameterFrame
from SafeVar import SafeVar


class SafeVarFrame(ParameterFrame):
    widgetJustifyDefault = tk.LEFT
    var_check_funcDefault = lambda _: True

    def __init__(self, *args, VarTargetType, defaultValue=None, validityInstructions="", var_check_func=None, widgetJustify=None, **kwargs):
        self.widgetJustify = self.widgetJustifyDefault if widgetJustify is None else widgetJustify
        self.var_check_func = lambda _: True if var_check_func is None else var_check_func  # using self.var_check_funcDefault doesnt work here!
        self.validityInstructions = validityInstructions
        self.VarTargetType = VarTargetType
        if defaultValue is None:
            self.defaultValue = self.VarTargetType()  # creating a dummy value by calling the default ctor of the targetType if no explicit default value is passed should satisfy the security check during the SafeVar Init
        else:
            self.defaultValue = defaultValue
        super().__init__(*args, **kwargs)  # default value will not be passed to super init, so the setter at the end of super init will not be called. This avoids redundance.

    def make_var(self):
        try:
            name = self.get_text()
        except:
            name = self.nameLabel
        self.tkVar = SafeVar(self.defaultValue, name=name, check_func=self.var_check_func, main_transform_func=self.VarTargetType,
                             gui_input_transform_func=float if self.VarTargetType in (int, float) else lambda arg: arg,
                             unstableValueImportance=1, invalidValueImportance=1, validityInstructions=self.validityInstructions,
                             tooltipFont=self.tooltipFont)

    def connect(self):
        self.tkVar.connect_widgets(self.varWidget)

    def set_and_call_trace(self, input_func):
        self.tkVar.trace_add(input_func, callFunc=True)
