import tkinter as tk
from random import random
import inspect
# todo: alles tkVar.get() dann zu super().get()


class MyVar:
    def __init__(self, value, *args, check_func=lambda arg: True, transform_func=lambda arg: arg, str_pre_transform_func=lambda arg: arg, **kwargs):
        self.value = None  # Will never be accessed for code use, but updated when trace is called. Useful fpr debugger, since its not able to show the native value in the tk.container
        self.processingInit = True
        self.processingTrace = False
        self.processingSet = False
        #self.processingGet = False
        self.tkVar = tk.Variable()
        self.tkVar.trace_add("write", self.traceFunc_wrapper)
        self.custom_traces = []
        self.check_func = check_func
        self.transform_func = transform_func
        self.str_pre_transform_func = str_pre_transform_func
        self.isValid: bool = None
        self.staysSame: bool = None
        self.lastValidValue: object = None
        #self.transformedValue: object = None
        # the 4 declarations above will get a value assigned in the set() call below
        self.set(value)
        self.processingInit = False

    def traceFunc_wrapper(self, *traceArgs):
        self.processingTrace = True  # activate this here since it should stay activated also during the callFunc call
        if not self.processingSet:  # if self.processingSet would be true, the value is isValid and staySame warning have already resolved at this point and the value is good (white entry)
            newValue = self.get()
            # newValue = self.tkVar.get()
            self.process_new_value(newValue)  # if get fails here, it will not throw an error but return None, which by definition wont pass the check
            if not self.isValid:
                print("Coloring all entries red")
                self.processingTrace = False
                return  # return immediately! # Ein leeres Entry zb darf eben nicht sofort wieder durch den letzten safe value ersetzt werden, erschwert die bedienung sehr. erst, wenn das value gebrauchtt wird (get call) soll es sichtbar ersetzt werden!"
            if not self.staysSame:
                print("Coloring all entries orange")
                self.processingTrace = False
                return  # return immediately!
        print("Coloring all entries white")  # warum hier 2mal vorbei?
        for func in self.custom_traces:
            func(self)
        self.processingTrace = False

    def process_new_value(self, value):
        #self.isValid = True
        #self.staysSame = True  # pretty sure this isnt needed anymore. staySame might seem not well defined if isValid is False, but staysSame will anyway only be read if isValid is True. Even if this line would be used, its unclear if assigning False is the best practice for upcoming changes of this class.
        tempValue = value  # original arg should not be overwritten since it may be needed to perform the equality check to determine staysSame.
        try:
            if isinstance(value, str):
                tempValue = self.str_pre_transform_func(tempValue)
            tempValue = self.transform_func(tempValue)
            self.isValid = self.check_func(tempValue)
        except:
            self.isValid = False
        print(f"{value} valid? {self.isValid}")
        if self.isValid:
            self.lastValidValue = tempValue
            try:
                defaultBackwardsCastFunc = type(value)
                backwardsCastedValue = defaultBackwardsCastFunc(self.lastValidValue)
                self.staysSame = backwardsCastedValue == value
                print(f"self.staysSame is now {self.staysSame}")  # warum hier 2mal vorbei?
            except:
                print(f"Backwards cast failed. self.staysSame is still {self.staysSame}")
        elif self.processingInit:
            raise ValueError(f"{value} is no valid initialization value for {self.tkVar}.")

    def trace_add(self, input_func, callFunc=False):
        self.custom_traces.append(input_func)
        if callFunc:
            input_func(self)

    def set(self, value):
        self.process_new_value(value)
        if not self.isValid:
            print(f"Set called, new value not valid, value is still {self.tkVar.get()}")  # dont insert self.lastSafeValue instead of the getter, because it might be that the current value is invalid after it was entered into entry. In this case, the entry should stay the same nevertheless!
            return
        if not self.staysSame:
            print(f"Set called, transformation changed input value from {value} to {self.lastValidValue}, which is the new value now.")
        self.reset()

    def reset(self):
        self.processingSet = True  # keep this here rather than in the first line to avoid the line "self.processingSet = False" an additional time before the return in the "if not self.isValid" case above
        self.tkVar.set(self.lastValidValue)  # calls trace!
        self.processingSet = False
        self.staysSame = True
        self.isValid = True
        self.value = self.lastValidValue

    def get(self):
        # getter soll nur dann resetten oder transformen, wenn er im code aufgerufen wird.
        # wenn er durch trace aufgerufen wird, nicht! Auch nicht dann, wenn er durch eine custom tracefunc gerufen wird, deshalb ist der flag self.processingTrace so wichtig!
        if not self.processingTrace and (not self.isValid or not self.staysSame):
        #if not self.isValid or not self.staysSame:
            self.reset()
        # wenn getter in eigener tracefunc aufgerufen wird, wurde im falle von entry-insert eh returned bevor der aufruf erfolgt, und im fall von set wurde vor dem aufruf schon alles korrigiert. es kann also nichts schief gehen!
        return self.tkVar.get()

    # switch to something like this to avoid nested defs:
    #def trace_add(self, input_func, callFunc=False, passTraceArgs=False):
    #    if passTraceArgs:
    #        completeTraceFunc = lambda *traceargs, input_func: self.traceFunc_wrapper()
    #    else:
    #        completeTraceFunc = lambda *tuple(), input_func: self.traceFunc_wrapper()
    #    self.tkVar.trace_add("write", completeTraceFunc)
    #    if callFunc:
    #        completeTraceFunc()


if __name__ == "__main__":
    def get_test():
        varVal = var.get()
        entryVal = entry.get()
        print(type(varVal), varVal)
        print(type(entryVal), entryVal)


    def set_test(value):
        print(value)
        var.set(value)
        print(var.get())
        print(entry.get())


    def both_test():
        # dont only print, also call abs()
        print(var.get())
        var.set(random())
        print(var.get())


    def varTraceFunc(varArg):
        print(f"Thats the tracefunc!!!!!!!!!!!!!!!!!!!!!!!!!!!! {varArg.get()}")

    def varTraceFunc2(varArg):
        print(f"Thats the second of two tracefuncs!!!!!!!!!!!!!!!!!!!!!!!!!!!! {varArg.get()}")


    root = tk.Tk()
    root.call('tk', 'scaling', 2)
    # 2 entries die beide in der gleichen trace benutzt werden!
    # var = SafeVar(tk.IntVar, defaultValue=1)  # check initialize with default and different vatTypes
    # var = SafeVar(tk.Variable, defaultValue=4.6)  # check initialize with default and different vatTypes
    var = MyVar(1.2, check_func=lambda i: 0 < i < 10, transform_func=int, str_pre_transform_func=float)
    var.trace_add(varTraceFunc, callFunc=True)
    var.trace_add(varTraceFunc2, callFunc=True)
    entry = tk.Entry(root, textvariable=var.tkVar)
    entry.pack()
    tk.Button(root, text="get test", command=get_test).pack()
    testValues = ["0", "0.", "0.5", 1, 1., "1.5", "12", "12.5", "20", "20.5", "a", "12a", "-", None, "-", True, [1, 2]]#, MyVar, MyVar(tk.IntVar),
    for value in testValues:
        tk.Button(root, text=f"test {value}", command=lambda value_=value: set_test(value_)).pack()
    tk.Button(root, text="both test", command=both_test).pack()
    root.mainloop()

#  is not valid
# Coloring all entries red
# 3 is valid
# self.staysSame is now False
# Coloring all entries orange
# 34 is valid
# Coloring all entries red