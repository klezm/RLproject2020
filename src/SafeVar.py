import tkinter as tk
from tkinter import messagebox
from functools import partial

import myFuncs
from ToolTip import ToolTip


class SafeVar(tk.Variable):
    @classmethod
    def basic_type(cls, value, type_, **kwargs):
        myFuncs.custom_warning(type_ in [int, float, str, bool], 2, f"type_ must be int, float, str or bool, not {type_}", 1)
        return cls(value, gui_input_transform_func=float if type_ in (int, float) else None,
                   main_transform_func=type_, **kwargs)

    @staticmethod
    def check_funcDefault(_): return True
    @staticmethod
    def main_transform_funcDefault(arg): return arg
    gui_input_transform_funcDefault = main_transform_funcDefault
    unstableValueImportanceDefault = 1
    invalidValueImportanceDefault = 2
    tooltipFontDefault = "calibri 11"
    trustSetDefault = False

    def __init__(self, value, *args, widgets=None, validityInstructions=None, tooltipFont=None, trustSet=None,
                 check_func=None, main_transform_func=None, gui_input_transform_func=None, backwards_cast_func=None,
                 unstableValueImportance=None, invalidValueImportance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = None  # Will never be accessed for code use, but updated when reset_to_stable is called.
        # Useful for debugger, since its not able to show the native _value in the tk.Variable container
        self._processingInit = True
        self._processingTrace = False
        self._processingSuperSet = False
        self._processingSet = False
        self.tooltipFont = self.tooltipFontDefault if tooltipFont is None else tooltipFont
        self._connectedWidgets = []
        if widgets is not None:
            self.connect_widgets(widgets)
        super().trace_add("write", self._traceFunc_wrapper)
        self._custom_traces = []
        self._validityInstructions = validityInstructions
        self._check_func = self.check_funcDefault if check_func is None else check_func
        self._main_transform_func = self.main_transform_funcDefault if main_transform_func is None else main_transform_func
        self._gui_input_transform_func = self.gui_input_transform_funcDefault if gui_input_transform_func is None else gui_input_transform_func
        self._backwards_cast_func = backwards_cast_func
        self._unstableValueImportance = self.unstableValueImportanceDefault if unstableValueImportance is None else unstableValueImportance
        self._invalidValueImportance = self.invalidValueImportanceDefault if invalidValueImportance is None else invalidValueImportance
        self._trustSet = self.trustSetDefault if trustSet is None else trustSet
        self._lastProposedValue = value
        self._lastStableValue: object = None
        self._isValid: bool = None
        self._isStable: bool = None
        # the 3 declarations above will get a _value assigned in the set() call below
        self.set(value)
        self._processingInit = False

    def get(self):
        # getter soll nur dann resetten oder transformen, wenn er im code aufgerufen wird.
        # wenn er durch trace aufgerufen wird, nicht!
        # Auch nicht dann, wenn er durch eine custom tracefunc gerufen wird, deshalb ist der flag self._processingTrace so wichtig!
        if not self._processingTrace and not self.is_correct():  # last check is for speedup only
            self._reset_to_stable()
        # wenn getter in eigener tracefunc aufgerufen wird, kann nichts schief gehen:
        # Sollte das value im Fall von entry-insert -> trace()  nicht einwandfrei gewesen sein,
        # würde im traceFunc_wrapper eh returned werden, bevor ein get-aufruf in einer custom trace erfolgt,
        # und im fall von set() -> trace() wird die trace eh erst gecalled, nachdem im setter schon alles korrigiert wurde.
        return self._lastStableValue

    def set(self, value):
        self._processingSet = True
        if self._trustSet:
            self._lastProposedValue = value
            self._lastStableValue = value
            self._isStable = True
            self._isValid = True
        else:
            self._process_new_value(value)
        self._reset_to_stable()
        self._processingSet = False

    def _reset_to_stable(self):
        self._processingSuperSet = True
        super().set(self._lastStableValue)  # calls trace!
        self._processingSuperSet = False
        myFuncs.custom_warning(self._isValid, self._invalidValueImportance, f"\n{self}: Value {self._lastProposedValue} is INVALID. The LAST VALID value {super().get()} has been set instead.", hideNadditionalStackLines=2)
        myFuncs.custom_warning(self._isStable, self._unstableValueImportance, f"\n{self}: Value {self._lastProposedValue} was UNSTABLE. The TRANSFORMED value {super().get()} has been set instead.", hideNadditionalStackLines=2)
        self._isStable = True
        self._isValid = True
        self._value = self._lastStableValue

    def _process_new_value(self, value):
        #self._isStable = True  # pretty sure this isn't needed anymore.
        # staySame might seem not well defined if _isValid is False, but there seems to be no case where this is an issue.
        self._lastProposedValue = value
        # original arg should not be overwritten since it may be needed to perform the equality check to determine _isStable.
        try:
            if not self._processingSet:  # called by trace after gui interaction
                self._lastProposedValue = self._gui_input_transform_func(self._lastProposedValue)
            tempValue = self._main_transform_func(self._lastProposedValue)
            self._isValid = self._check_func(tempValue)
        except:
            self._isValid = False
        if self._isValid:
            self._lastStableValue = tempValue
            try:
                temp_backwards_cast_func = type(self._lastProposedValue) if self._backwards_cast_func is None else self._backwards_cast_func
                backwardsCastedValue = temp_backwards_cast_func(self._lastStableValue)
                self._isStable = (backwardsCastedValue == self._lastProposedValue)
            except:  # backwards cast failed
                self._isStable = (self._lastStableValue == self._lastProposedValue)
        elif self._processingInit:
            raise ValueError(f"{value} is no valid initialization value for {self}.")

    def trace_add(self, callback, callFunc=False, passSelf=False, mode=None):  # last arg is just to match the signature of super().trace_add
        if passSelf:
            callback = partial(callback, self)
        self._custom_traces.append(callback)
        if callFunc:
            callback()

    def _traceFunc_wrapper(self, *traceArgs):
        self._processingTrace = True  # activate this here since it should stay activated also during the custom_traces call
        if not self._processingSuperSet:  # if self._processingSuperSet would be true, the value has already been processed and reset to stable at this point
            newValue = super().get()  # just calls super().get() here
            self._process_new_value(newValue)
            if not self._isValid:
                self._color_logged_widgets("red")
                self._processingTrace = False
                return  # return immediately! # Ein leeres Entry zb darf eben nicht sofort wieder durch den letzten safe value ersetzt werden, erschwert die bedienung sehr.
                # erst, wenn das value gebrauchtt wird (get() call) soll es sichtbar ersetzt werden!
            if not self._isStable:
                self._color_logged_widgets("orange")
                self._processingTrace = False
                return  # return immediately! (see above)
        self._color_logged_widgets()
        for func in self._custom_traces:
            func()
        self._processingTrace = False

    def _color_logged_widgets(self, color=None):
        for widget, defaultColor in self._connectedWidgets:
            color = defaultColor if color is None else color
            if widget.cget("bg") != color:  # so config is skipped for performance if nothing has to change
                widget.config(bg=color)

    def connect_widgets(self, widgets):  # only called by MyEntry objects
        if not isinstance(widgets, list):
            widgets = [widgets]
        for widget in widgets:
            widget.config(textvariable=self)
            self._connectedWidgets.append((widget, widget.cget("bg")))
            if self._validityInstructions:
                ToolTip(widget, text=self._validityInstructions, font=self.tooltipFont)

    def is_correct(self):
        return self._isStable and self._isValid

    def instruction_popup(self, force=False):
        if force or not self.is_correct():
            messagebox.showerror("Invalid value", f"{self} is invalid.\n{self._validityInstructions}")
            return True
        return False


if __name__ == "__main__":

    class C:
        def __init__(self, a, b):
            pass

    def get_test():
        varVal = var.get()
        entryVal = e1.get()
        print(type(varVal), varVal)
        print(type(entryVal), entryVal)


    def set_test(value):
        print(value)
        var.set(value)
        #print(var.get())
        print(e1.get())

    def varTraceFunc(varArg):
        print(f"Thats the tracefunc!!!!!!!!!!!!!!!!!!!!!!!!!!!! {varArg.get()}")

    def varTraceFunc2(varArg):
        print(f"Thats the second of two tracefuncs!!!!!!!!!!!!!!!!!!!!!!!!!!!! {varArg.get()}")

    def my_trafo(value):
        return int(value) + 1

    root = tk.Tk()
    root.call('tk', 'scaling', 2)
    # 2 entries die beide in der gleichen trace benutzt werden!
    # var = SafeVar(tk.IntVar, value=1)  # check initialize with default and different vatTypes
    # var = SafeVar(tk.Variable, value=4.6)  # check initialize with default and different vatTypes
    var = SafeVar(12, check_func=lambda i: 0 < i < 20, main_transform_func=int, gui_input_transform_func=float)#, _invalidValueImportance=1)
    #var = SafeVar(12, check_func=lambda i: 0 < i < 21, main_transform_func=float)#, _invalidValueImportance=1)
    #var = SafeVar(12, check_func=lambda i: 0 < i < 20, main_transform_func=lambda _: 5, gui_input_transform_func=float)#, _invalidValueImportance=1)
    #var = SafeVar(1.2, check_func=lambda i: 0 < i < 20, main_transform_func=my_trafo, gui_input_transform_func=float)
    #var = SafeVar("1.2", _check_func=lambda i: isinstance(i, str))#, _main_transform_func=int, _gui_input_transform_func=float)
    #var = SafeVar(0)
    #var.trace_add(varTraceFunc, callFunc=True)
    #var.trace_add(varTraceFunc2, callFunc=True)
    e1 = tk.Entry(root, justify=tk.RIGHT)
    e1.pack()
    var.connect_widgets(e1)
    tk.Button(root, text="get test", command=get_test).pack()
    #SafeVar(tk.IntVar)
    testValues = [C(1, 2), "0", 5, "0.5", 1, 1., "1.5", "12", "12.5", 20, "20.5", "a", "12a", "-", None, "-", True, [1, 2], SafeVar]
    for value in testValues:
        tk.Button(root, text=f"test {value}", command=lambda value_=value: set_test(value_)).pack()
   # set_test(21)
    root.mainloop()
