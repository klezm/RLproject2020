import tkinter as tk
from SafeVar import MyVar
from myFuncs import custom_warning


class RadiomenuButton(tk.Menubutton):
    # Works with tk.StringVar and SafeVar as choiceVariable argument.
    _bdDefault = 3
    _arrowSymbolDefault = "\u2B9F"  # Good alternative symbol: "\u25BC"
    # This way, one doesnt have to know the exact default value if passing args through. So passing None guarantees the default value without prior knowledge.

    def __init__(self, master, choices, choiceVariable: tk.Variable = None, width=None, bd=None, arrowSymbol=None, **kwargs):
        custom_warning(isinstance(choices, (list, tuple)), 2, "Argument: 'choices' must be a list or a tuple.", hideNadditionalStackLines=1)
        custom_warning(choices, 2, "Argument: 'choices' must have nonzero length.", hideNadditionalStackLines=1)
        for key in ["textvariable", "text", "menu", "anchor", "relief", "indicatoron"]:
            custom_warning(key not in kwargs, 2, f"Argument '{key}' is invalid.", hideNadditionalStackLines=1)
        bd = self._bdDefault if bd is None else bd
        arrowSymbol = self._arrowSymbolDefault if arrowSymbol is None else arrowSymbol
        if choiceVariable is None:
            self._choiceVariable = MyVar(choices[0], check_func=lambda choice_: choice_ in choices, invalidValueImportance=2)
        else:
            self._choiceVariable = choiceVariable

        if width is None:
            width = max(map(len, choices)) + len(arrowSymbol) + 2
        labelVar = tk.StringVar()
        super().__init__(master, textvariable=labelVar, width=width, bd=bd, anchor=tk.W, relief=tk.RAISED, indicatoron=0, **kwargs)
        menu = tk.Menu(self, tearoff=0)
        self["menu"] = menu
        for choice in choices:
            menu.add_radiobutton(label=choice, variable=self._choiceVariable, font=self.cget("font"))
        self._choiceVariable.trace_add(callback=lambda *traceArgs: labelVar.set(f"{arrowSymbol}  {self._choiceVariable.get()}"), mode="write")
        self._choiceVariable.set(choices[0])

    def get_choiceVar(self):
        return self._choiceVariable

    def get_choice(self):
        return self.get_choiceVar().get()

    def set_choice(self, choice):
        self.get_choiceVar().set(choice)


if __name__ == "__main__":
    root = tk.Tk()
    var = MyVar(0)
    rmb = RadiomenuButton(root, ["ana", "irjngf"], font="calibri 11")
    #rmb = RadiomenuButton(root, ["ana", "irjngf"], text="",font="calibri 11")
    #rmb = RadiomenuButton(root, [], font="calibri 11")
    #rmb = RadiomenuButton(root, ["ana", "irjngf"], choiceVariable=var, font="calibri 15 bold")
    rmb.pack()
    rmb.get_choiceVar().trace_add(mode="write", callback=lambda: print(f"extra trace! value is now {rmb.get_choice()}"))
    tk.Button(root, text="set correct", command=lambda: rmb.set_choice("ana")).pack()
    tk.Button(root, text="set correct2", command=lambda: rmb.set_choice("irjngf")).pack()
    tk.Button(root, text="set wrong", command=lambda: rmb.set_choice("edefe")).pack()
    tk.Button(root, text="get", command=lambda: print(rmb.get_choice())).pack()
    root.mainloop()
