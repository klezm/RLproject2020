import tkinter as tk

from ParameterFrame import ParameterFrame
from SafeVar import MyVar


class SafeVarFrame(ParameterFrame):
    tkVar: MyVar

    def __init__(self, *args, defaultValue=None, VarTargetType=None, var_check_func=lambda arg: True, varWidgetWidth=8, varWidgetFg="black", varWidgetJustify=tk.LEFT, **kwargs):
        if defaultValue is None:
            self.defaultValue = VarTargetType()  # creating a dummy value by calling the default ctor of the targetType if no explicit default value is passed should satisfy the security check during the SafeVar Init
        else:
            self.defaultValue = defaultValue
        self.VarTargetType = VarTargetType
        self.var_check_func = var_check_func
        self.varWidgetWidth = varWidgetWidth
        self.varWidgetFg = varWidgetFg
        self.varWidgetJustify = varWidgetJustify
        super().__init__(*args, **kwargs)  # default value will not be passed to super init, so the setter at the end of super init will not be called. This avoids redundance.

    def make_tkVar(self):
        return MyVar(self.defaultValue, check_func=self.var_check_func, transform_func=self.VarTargetType,
                     str_pre_transform_func=float if self.VarTargetType == int else lambda arg: arg,
                     unstableValueImportance=1, invalidValueImportance=1)

    def set_and_call_trace(self, input_func):
        self.tkVar.trace_add(input_func, callFunc=True)