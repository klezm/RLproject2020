import tkinter as tk
from SafeVar import SafeVar
from myFuncs import custom_warning


class RadiomenuButton(tk.Menubutton):
    """A button to use in a ``tkinter`` interface.\n
    It opens a dropdown menu containing user-given, pairwise-exclusive options.
    After clicking one of them, the menu closes and the text of the Button as well as
    the value of the connected variable container is set to the chosen option.\n
    By default, an error is thrown if the variable container is set to a value
    that isnt in the option list.\n
    Reasonable alternative arrow symbols: ⮟ ▼
    """
    def __init__(self, master, choices, *args, choiceVariable: tk.Variable = None, width=None, bd=3, arrowSymbol="⮛", **kwargs):
        """Creates a RadiomenuButton object.
        :param args: Additional arguments passed to the super().__init__ (tk.Menubutton)
        :param master: Parent container.
        :param list | tuple choices: Allowed options.
        :param tk.Variable choiceVariable: Variable container that holds the actual choice. If None, a SafeVar object will be created that also keeps track if values assigned to it are valid choices.
        :param int width: Button width as number of signs. If None, width will be derived from the longest item among all valid choices.
        :param int bd: Borderwidth passed to the super().__init__ (tk.Menubutton)
        :param str arrowSymbol: Arrow to be used to indicate this button as a dropdown menu.
        :param kwargs: Additional keyword arguments passed to the super().__init__ (tk.Menubutton)
        """
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
        super().__init__(master, *args, textvariable=labelVar, width=width, bd=bd, anchor=tk.W, relief=tk.RAISED, indicatoron=0, **kwargs)
        self.config(activeforeground=self.cget("fg"))
        menu = tk.Menu(self, tearoff=0)
        self["menu"] = menu  # mandatory, line above isnt enough for some reason
        for choice in choices:
            menu.add_radiobutton(label=choice, variable=self.choiceVariable, font=self.cget("font"))
        self.choiceVariable.trace_add(callback=lambda *traceArgs: labelVar.set(f"{arrowSymbol}{' ' * nBlanks}{self.choiceVariable.get()}"), mode="write")
        self.set_choice(self.get_choice())  # triggers the callback once to initially display the correct option. (Only needed if an external variable container is provided, but that isnt recommended anyway, since the security features added in the ctor when just giving a list of options would then be omitted

    def get_choiceVar(self):
        """Return the variable container that holds the actual choice.

        :return tk.Variable: Variable container
        """
        return self.choiceVariable

    def get_choice(self):
        """Return the actual chosen value

        :return: Chosen value
        """
        return self.get_choiceVar().get()

    def set_choice(self, choice):
        """Set the actual choice to a given value.

        :param choice: Value
        """
        self.get_choiceVar().set(choice)


def main():
    try:
        from myFuncs import print_default_kwargs
        print_default_kwargs(RadiomenuButton)
    except Exception:
        pass

    root = tk.Tk()
    var = SafeVar("bar")
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
