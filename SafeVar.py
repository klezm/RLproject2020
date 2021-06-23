import tkinter as tk
from functools import partial

import myFuncs


class MyEntry(tk.Entry):
    def __init__(self, master=None, cnf={}, **kw):
        self._log_from_dict(cnf | kw)
        super().__init__(master, cnf, **kw)

    def configure(self, cnf=None, **kw):
        self._log_from_dict(kw if cnf is None else cnf | kw)
        super().configure(cnf, **kw)

    config = configure

    def _log_from_dict(self, dictionary):
        try:
            dictionary["textvariable"].log_widget(self)
        except:
            pass


class MyVar(tk.Variable):
    def __init__(self, value, *args, check_func=lambda arg: True, main_transform_func=lambda arg: arg, gui_input_transform_func=lambda arg: arg, backwards_cast_func=None, unstableValueImportance=1, invalidValueImportance=2, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = None  # Will never be accessed for code use, but updated when reset_to_stable is called.
        # Useful for debugger, since its not able to show the native _value in the tk.Variable container
        self._processingInit = True
        self._processingTrace = False
        self._processingSuperSet = False
        self._processingSet = False
        super().trace_add("write", self._traceFunc_wrapper)
        self._custom_traces = []
        self._usedBy = []
        self._check_func = check_func
        self._main_transform_func = main_transform_func
        self._gui_input_transform_func = gui_input_transform_func
        self._default_backwards_cast_func = backwards_cast_func
        self._unstableValueImportance = unstableValueImportance
        self._invalidValueImportance = invalidValueImportance
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
        if not self._processingTrace and (not self._isValid or not self._isStable):  # last check is for speedup only
            self._reset_to_stable()
        # wenn getter in eigener tracefunc aufgerufen wird, kann nichts schief gehen:
        # Sollte das value im Fall von entry-insert -> trace()  nicht einwandfrei gewesen sein,
        # würde im traceFunc_wrapper eh returned werden, bevor ein get-aufruf in einer custom trace erfolgt,
        # und im fall von set() -> trace() wird die trace eh erst gecalled, nachdem im setter schon alles korrigiert wurde.
        return self._lastStableValue

    def set(self, value):
        self._processingSet = True
        self._process_new_value(value)
        self._reset_to_stable()
        self._processingSet = False

    def _reset_to_stable(self):
        self._processingSuperSet = True
        super().set(self._lastStableValue)  # calls trace!
        self._processingSuperSet = False
        myFuncs.custom_warning(not self._isValid, self._invalidValueImportance, f"\n{self}: Value {self._lastProposedValue} is INVALID. The LAST VALID value {super().get()} has been set instead.", hideNdeepestStackLines=3)
        myFuncs.custom_warning(not self._isStable, self._unstableValueImportance, f"\n{self}: Value {self._lastProposedValue} was UNSTABLE. The TRANSFORMED value {super().get()} has been set instead.", hideNdeepestStackLines=3)
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
            self._lastStableValue = tempValue
        except:
            self._isValid = False
        if self._isValid:
            try:
                if self._default_backwards_cast_func is None:
                    backwards_cast_func = type(self._lastProposedValue)
                else:
                    backwards_cast_func = self._default_backwards_cast_func
                backwardsCastedValue = backwards_cast_func(self._lastStableValue)
                self._isStable = (backwardsCastedValue == self._lastProposedValue)
            except:  # backwards cast failed
                self._isStable = (self._lastStableValue == self._lastProposedValue)
        elif self._processingInit:
            raise ValueError(f"{value} is no valid initialization value for {self}.")

    def trace_add(self, input_func, callFunc=False, passSelf=False):
        if passSelf:
            input_func = partial(input_func, self)
        self._custom_traces.append(input_func)
        if callFunc:
            input_func()

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
        self._color_logged_widgets("white")
        for func in self._custom_traces:
            func()
        self._processingTrace = False

    def _color_logged_widgets(self, color):
        for widget in self._usedBy:
            try:  # so no garbage collector is needed if a widget doesnt refer to this object anymore
                if widget.cget("bg") != color:  # so config is skipped for performance if nothing has to change
                    widget.config(bg=color)
            except:
                pass

    def log_widget(self, widget):  # only called by MyEntry objects
        self._usedBy.append(widget)


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
    # var = SafeVar(tk.IntVar, defaultValue=1)  # check initialize with default and different vatTypes
    # var = SafeVar(tk.Variable, defaultValue=4.6)  # check initialize with default and different vatTypes
    var = MyVar(12, check_func=lambda i: 0 < i < 20, main_transform_func=int, gui_input_transform_func=float)#, _invalidValueImportance=1)
    #var = MyVar(12, check_func=lambda i: 0 < i < 21, main_transform_func=float)#, _invalidValueImportance=1)
    #var = MyVar(12, check_func=lambda i: 0 < i < 20, main_transform_func=lambda _: 5, gui_input_transform_func=float)#, _invalidValueImportance=1)
    #var = MyVar(1.2, check_func=lambda i: 0 < i < 20, main_transform_func=my_trafo, gui_input_transform_func=float)
    #var = MyVar("1.2", _check_func=lambda i: isinstance(i, str))#, _main_transform_func=int, _gui_input_transform_func=float)
    #var = MyVar(0)
    #var.trace_add(varTraceFunc, callFunc=True)
    #var.trace_add(varTraceFunc2, callFunc=True)
    e1 = MyEntry(root, textvariable=var, justify=tk.RIGHT)
    e1.pack()
    e2 = MyEntry(root)
    e2.pack()
    e2["textvariable"] = var
    e3 = MyEntry(root)
    e3.pack()
    e3.config(textvariable=var)
    tk.Button(root, text="get test", command=get_test).pack()
    #MyVar(tk.IntVar)
    testValues = [C(1, 2), "0", 5, "0.5", 1, 1., "1.5", "12", "12.5", 20, "20.5", "a", "12a", "-", None, "-", True, [1, 2], MyVar]
    for value in testValues:
        tk.Button(root, text=f"test {value}", command=lambda value_=value: set_test(value_)).pack()
   # set_test(21)
    root.mainloop()
