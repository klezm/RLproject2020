import tkinter as tk
from random import random
from inspect import signature

# use @wraps

#class SafeEntry
# todo: mark private vars _...

class SafeVar:
    #returns None if wrong use (and skips tracefunc call in this case)
    DefaultSafeCheckCalls = {tk.IntVar: int,
                             tk.DoubleVar: float,
                             tk.BooleanVar: bool,
                             tk.StringVar: str}

    def __init__(self, VarType, defaultValue=None, safeCheck_func=lambda arg: arg is not None):
        self.VarType = VarType
        self.tkVar = self.VarType()
        self.trace_add(lambda: None)
        self.lastSafeValue = self.DefaultSafeCheckCalls[VarType]()
        if not (len(signature(safeCheck_func).parameters) == 1 and safeCheck_func(None) is False):  # None arg should always return False, also this is what get returns if failing in tracecall
            raise
        self.safeCheck_func = safeCheck_func
        self.processingTraceCall = False
        self.set(defaultValue)

    def get(self):
        try:
            return self.tkVar.get()  # if vartype is int but a float is entered into an entry, get will take this float and return an int, but doesnt change the entry
            #self.tkVar.set(value)  # the value that was set here will be overwritten in the end if the hierachy was set() -> trace_add() -> get(). In general this line is important to "correct" values. Assume the vartype is int but a float was setted. then the value itself stays float, but every get() approach will convert the return value to int although the real value wasnt changed. in addition, the real value would still be displayed in entries etc although it cant be used at all because of that getter behaviour
            #return value
            #if self.safeCheck_func(value):
            #    return value
            #else:
            #    raise
        except:
            if self.processingTraceCall:
                return None
            else:
                self.tkVar.set(self.lastSafeValue)  # hier self.set oder tkVar.set()?
                return self.tkVar.get()

    def set(self, value):
        try:
            value = self.DefaultSafeCheckCalls[self.VarType](value)
            # vllt vorher try cast, dann set, except: return?
            self.tkVar.set(value)
        except:
            self.tkVar.set(self.lastSafeValue)  # this is a correction because the "corrected" value set in the getter called in the tracefunc will be overwritten as thr line above finally resolves, but it is saved in the lastSafeValue param

    def trace_add(self, input_func, callFunc=False, passTraceArgs=False):
        def traceFunc(*traceArgs):
            self.processingTraceCall = True
            newValue = self.get()
            # alternative zu drunter, wenn der safecheck_func() im getter-try wäre und bei False reisen würde: if newvalue is None:
            if not self.safeCheck_func(newValue):  # if get fails here, it will not throw an error but return None, which by definition wont pass the check
                self.processingTraceCall = False
                return  # Ein leeres Entry zb darf eben nicht sofort wieder durch den letzten safe value ersetzt werden, erschwert die bedienung sehr. erst, wenn das value gebrauchtt wird (get call) soll es sichtbar ersetzt werden!"
            self.lastSafeValue = newValue
            if not passTraceArgs:
                traceArgs = ()
            input_func(*traceArgs)
            self.processingTraceCall = False
        self.tkVar.trace_add("write", traceFunc)
        if callFunc:
            traceFunc()

    def default_safeCheck_func(self, value):
        return self.safeCheck_func(value) and isinstance(value, self.DefaultSafeCheckCalls[self.VarType])


def get_test():
    print("hi")
    print(var.get())
    print(entry.get())


def set_test():
    var.set(10*random())


def both_test():
    # dont only print, also call abs()
    print(var.get())
    var.set(random())
    print(var.get())


def varTraceFunc():
    print(var.get())


root = tk.Tk()
root.call('tk', 'scaling', 2)
# 2 entries die beide in der gleichen trace benutzt werden!
#var = SafeVar(tk.IntVar, defaultValue=1)  # check initialize with default and different vatTypes
var = SafeVar(tk.DoubleVar, defaultValue=4.6)  # check initialize with default and different vatTypes
entry = tk.Entry(root, textvariable=var.tkVar)
entry.pack()
tk.Button(root, text="get test", command=get_test).pack()
tk.Button(root, text="set test", command=set_test).pack()
tk.Button(root, text="both test", command=both_test).pack()
root.mainloop()
