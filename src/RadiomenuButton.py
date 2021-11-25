import tkinter as tk
from SafeVar import SafeVar
from myFuncs import custom_warning


class RadiomenuButton(tk.Menubutton):
    # Works with tk.StringVar and SafeVar as choiceVariable argument.
    # This way, one doesnt have to know the exact default value if passing args through. So passing None guarantees the default value without prior knowledge.
    # Alternative arror symbols: ⮟ ▼
    def __init__(self, master, choices, choiceVariable: tk.Variable = None, width=None, bd=3, arrowSymbol="⮛", **kwargs):
        custom_warning(isinstance(choices, (list, tuple)), 2, "Argument: 'choices' must be a list or a tuple.", hideNadditionalStackLines=1)
        custom_warning(choices, 2, "Argument: 'choices' must have nonzero length.", hideNadditionalStackLines=1)
        for key in ["textvariable", "text", "menu", "anchor", "relief", "indicatoron"]:
            custom_warning(key not in kwargs, 2, f"Argument '{key}' is invalid.", hideNadditionalStackLines=1)
        if choiceVariable is None:
            self.choiceVariable = SafeVar(choices[0], check_func=lambda choice_: choice_ in choices, invalidValueImportance=2)
        else:
            self.choiceVariable = choiceVariable
        nBlanks = 2
        if width is None:
            width = max(map(len, choices)) + len(arrowSymbol) + nBlanks + 1
        labelVar = tk.StringVar()
        super().__init__(master, textvariable=labelVar, width=width, bd=bd, anchor=tk.W, relief=tk.RAISED, indicatoron=0, **kwargs)
        self.config(activeforeground=self.cget("fg"))
        menu = tk.Menu(self, tearoff=0)
        self["menu"] = menu
        for choice in choices:
            menu.add_radiobutton(label=choice, variable=self.choiceVariable, font=self.cget("font"))
        self.choiceVariable.trace_add(callback=lambda *traceArgs: labelVar.set(f"{arrowSymbol}{' ' * nBlanks}{self.choiceVariable.get()}"), mode="write")
        self.set_choice(choices[0])  # if choiceVariable arg was not None

    def get_choiceVar(self):
        return self.choiceVariable

    def get_choice(self):
        return self.get_choiceVar().get()

    def set_choice(self, choice):
        self.get_choiceVar().set(choice)


def main():
    try:
        from myFuncs import print_default_kwargs
        print_default_kwargs(RadiomenuButton)
    except Exception:
        pass
    root = tk.Tk()
    var = SafeVar(0)
    rmb = RadiomenuButton(root, ["foo", "bar"], font="calibri 11")
    #rmb = RadiomenuButton(root, ["foo", "bar"], text="", font="calibri 11")
    #rmb = RadiomenuButton(root, [], font="calibri 11")
    #rmb = RadiomenuButton(root, ["foo", "bar"], choiceVariable=var, font="calibri 15 bold")
    rmb.pack()
    rmb.get_choiceVar().trace_add(mode="write", callback=lambda: print(f"extra trace! value is now {rmb.get_choice()}"))
    tk.Button(root, text="set correct", command=lambda: rmb.set_choice("foo")).pack()
    tk.Button(root, text="set correct2", command=lambda: rmb.set_choice("bar")).pack()
    tk.Button(root, text="set wrong", command=lambda: rmb.set_choice("fail")).pack()
    tk.Button(root, text="get", command=lambda: print(rmb.get_choice())).pack()
    root.mainloop()


if __name__ == "__main__":
    main()
