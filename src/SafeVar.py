import tkinter as tk
from functools import partial
from collections.abc import Iterable

import myFuncs
from ToolTip import ToolTip


class SafeVar(tk.Variable):
    """A variable container that keeps track if an input fulfills arbitrarily user-given conditions and
    always returns the *last stable value*, while throwing a warning or an error if this doesnt equal the
    most recent input.\n
     ..
    **THIS CLASS INHERITS FROM** ``tk.Variable``, **SO TO CREATE INSTANCES YOU NEED TO CALL**
    ``tk.Tk()`` **AT LEAST ONCE.**\n
     ..
    Additionally to passing a function that defines the condition-check and applies it to an input,
    the user may also pass a function that first transforms the input before the condition check.
    Note that the default transform function just returns the input itself.\n
    An input that stays the same after being transformed and also passes the check is considered
    *stable* and will be registered as the *last stable value*.\n
    An input is considered *unstable* if it **has** been changed by the transformation and then passes
    the condition check. Then the **transformed** value will be registered as the *last stable value*.\n
    An input is considered *invalid* if it doesnt pass the condition check or causes an exception
    during either the transformation or the check. In this case nothing will be registered.\n
    To quickly construct ``SafeVar`` objects that just act like typesafe containers for the most basic
    types, use the ``SafeVar.basic_type`` class method.\n
    To see a concrete example, just run this file.\n
     ..
    This class inherits from ``tk.Variable``, so it may also be connected to ``tk`` widgets.\n
    This is especially useful for GUIs that visualize fast paced processes while allowing the user to
    change parameters dynamically via the GUI without having to pause the whole process:\n
    In contrast to just passing a value to the ``SafeVar.set`` function, when typing an *invalid* or
    *unstable* value into a widget such as a ``tk.Entry``, the widget will be colored. Additionally,
    the value will be reset to the *last stable value* **only right before the next time it is needed**.
    Due to this delayed reset, the user is not disrupted or prevented from typing values that would form
    an *invalid* or *unstable* expression when only a substring of the final value is typed in yet.
    """
    @classmethod
    def basic_type(cls, value, type_, **kwargs):
        """Quickly construct a SafeVar object that just acts like typesafe containers for the most basic types.

        :param value: Initial Value. An error is thrown if it does not pass the check.
        :param type type_: Choose between int, float, str, bool.
        :param kwargs: Additional keyword arguments passed to the SafeVar constructor.
        :return SafeVar: SafeVar object.
        """
        myFuncs.custom_warning(type_ in [int, float, str, bool], 2, f"type_ must be int, float, str or bool, not {type_}", 1)
        return cls(value, str_input_transform_func=float if type_ in (int, float) else lambda arg: arg,
                   main_transform_func=type_, **kwargs)

    def __init__(self, value, *args, widgets=None, validityInstructions="", tooltipFont="calibri 11", trustSet=False,
                 check_func=lambda _: True, main_transform_func=lambda arg: arg, str_input_transform_func=lambda arg: arg, backwards_cast_func=None,
                 unstableValueImportance=1, invalidValueImportance=2, **kwargs):
        """Sets up a SafeVar object.

        :param value: Initial Value. An error is thrown if it does not pass the check.
        :param args: Additional arguments passed to the super().__init__ (tk.Variable).
        :param widgets: Object inheriting from tk.Widget or iterable of those. They will be connected to the SafeVar object, which in turn will be set as textvariable.
        :param str validityInstructions: Description of the properties of a stable value. They will be shown in each warning/error.
        :param str tooltipFont: tk font that may be used to display information about this variable in a different widget
        :param bool trustSet: If True, every value assigned by SafeVar.set will automatically be treated as valid and stable. Use with caution.
        :param function check_func: Signature: Any -> bool. Defines the condition a value has to fulfil to be valid.
        :param function | type main_transform_func: Signature: Any -> Any. Defines the transformation that is applied to a value before calling the check_func.
        :param function | type str_input_transform_func: Signature: str -> Any. Defines an extra transformation that is applied to a str-type value before calling the main_transform_func. This is crucial if the SafeVar object is connected to an Entry-like widget that can only take str inputs.
        :param function | type backwards_cast_func: Signature: Any -> Any. This function should act as the inverse of the main_transform_func to be able to check if the transformation changed the value. By default, an explicit cast into the input type is called.
        :param int unstableValueImportance: Defines behavior after resetting an unstable values: 2- Throw Error and halt. 1- Throw Warning and continue. 0- Throw nothing and continue.
        :param int invalidValueImportance: Defines behavior after resetting an invalid values: 2- Throw Error and halt. 1- Throw Warning and continue. 0- Throw nothing and continue.
        :param kwargs: Additional keyword arguments passed to the super().__init__ (tk.Variable).
        """
        super().__init__(*args, **kwargs)
        self._value = None  # Will never be accessed for code use, but updated when reset_to_stable is called.
        # Useful for debugger, since its not able to show the native value in the tk.Variable container
        self.processingInit = True
        self.processingTrace = False
        self.processingSuperSet = False
        self.tooltipFont = tooltipFont
        self.connectedWidgets = []
        if widgets is not None:
            self.connect_widgets(widgets)
        super().trace_add("write", lambda *traceArgs: self._traceFunc_wrapper())
        self.custom_traces = []
        self.validityInstructions = validityInstructions
        self.check_func = check_func
        self.main_transform_func = main_transform_func
        self.str_input_transform_func = str_input_transform_func
        self.backwards_cast_func = backwards_cast_func
        self.unstableValueImportance = unstableValueImportance
        self.invalidValueImportance = invalidValueImportance
        self.trustSet = trustSet
        self.lastProposedValue = value
        self.lastStableValue: object = None
        self.isValid: bool = None
        self.isStable: bool = None
        # the 3 declarations above will get a value assigned in the set() call below
        self.set(value)
        self.processingInit = False

    def get(self):
        """Overrides tk.Variable.get. If the current value was not stable and valid,
        the value will be reset to the last stable value before returning it.

        :return Any: Latest stable value.
        """
        # getter soll nur dann resetten oder transformen, wenn er im code aufgerufen wird.
        # wenn er durch trace aufgerufen wird, nicht!
        # Auch nicht dann, wenn er durch eine custom tracefunc gerufen wird, deshalb ist der flag self.processingTrace so wichtig!
        if not self.processingTrace and not (self.isStable and self.isValid):  # last check is for speedup only
            self._reset_to_stable()
        # wenn getter in eigener tracefunc aufgerufen wird, kann nichts schief gehen:
        # Sollte das value im Fall von entry-insert -> trace()  nicht einwandfrei gewesen sein,
        # würde im traceFunc_wrapper eh returned werden, bevor ein get-aufruf in einer custom trace erfolgt,
        # und im fall von set() -> trace() wird die trace eh erst gecalled, nachdem im setter schon alles korrigiert wurde.
        return self.lastStableValue

    def set(self, value):
        """Overrides tk.Variable.set. Determines if the input is valid and stable,
        then sets the value to the last stable value.

        :param Any value: Proposed value.
        """
        if self.trustSet:
            self.lastProposedValue = value
            self.lastStableValue = value
            self.isStable = True
            self.isValid = True
        else:
            self._process_new_value(value)
        self._reset_to_stable()

    def trace_add(self, callback, callFunc=False, passSelf=False, mode="write"):  # last arg is just to match the signature of super().trace_add
        """Overrides tk.trace_add. Registers a function that will automatically be called after a stable value was set.

        :param function callback: Function to be registered.
        :param callFunc: If True, calls the registered function once at the end of this method.
        :param passSelf: If True, always passes the instance that called this method as the first argument to the registered function
        :param mode: Argument not used and only added to match the super().trace_add signature for compatibility.
        """
        if passSelf:
            callback = partial(callback, self)
        self.custom_traces.append(callback)
        if callFunc:
            callback()

    def connect_widgets(self, widgets):
        """Assigns this instance to the textvariable of given widgets.
        They will be colored orange if the value is unstable and red if the value is invalid.
        Additionally, if validityInstructions were specified in the constructor call,
        a popup showing those instructions will appear when hovering over a connected widget.

        :param widgets: Object inheriting from tk.Widget or iterable of those.
        """
        if not isinstance(widgets, Iterable):
            widgets = [widgets]
        for widget in widgets:
            widget.config(textvariable=self)
            self.connectedWidgets.append((widget, widget.cget("bg")))  # assuming the bg at the time of connecting is the default bg
            if self.validityInstructions:
                ToolTip(widget, text=self.validityInstructions, font=self.tooltipFont)

    def _reset_to_stable(self):
        self.processingSuperSet = True
        super().set(self.lastStableValue)  # calls trace!
        self.processingSuperSet = False
        hideNlines = 2 + self.processingInit
        myFuncs.custom_warning(self.isValid, self.invalidValueImportance, f"\n{self._get_warning_prefix()}Value {self.lastProposedValue} is INVALID. The LAST VALID value {super().get()} has been set instead. {self.validityInstructions}", hideNadditionalStackLines=hideNlines)
        myFuncs.custom_warning(self.isStable, self.unstableValueImportance, f"\n{self._get_warning_prefix()}Value {self.lastProposedValue} was UNSTABLE. The TRANSFORMED value {super().get()} has been set instead. {self.validityInstructions}", hideNadditionalStackLines=hideNlines)
        self.isStable = True
        self.isValid = True
        self._value = self.lastStableValue

    def _process_new_value(self, value):
        #self.isStable = True  # pretty sure this isn't needed anymore.
        self.lastProposedValue = value
        # original arg should not be overwritten since it may be needed to perform the equality check to determine isStable.
        try:
            #if not self.processingSet:
            if isinstance(self.lastProposedValue, str):  # always True if this function is called by trace after gui interaction
                self.lastProposedValue = self.str_input_transform_func(self.lastProposedValue)
            tempValue = self.main_transform_func(self.lastProposedValue)
            self.isValid = self.check_func(tempValue)
        except:
            self.isValid = False
        if self.isValid:
            self.lastStableValue = tempValue
            try:
                temp_backwards_cast_func = type(self.lastProposedValue) if self.backwards_cast_func is None else self.backwards_cast_func
                backwardsCastedValue = temp_backwards_cast_func(self.lastStableValue)
                self.isStable = (backwardsCastedValue == self.lastProposedValue)
            except:  # backwards cast failed
                self.isStable = (self.lastStableValue == self.lastProposedValue)
        elif self.processingInit:
            myFuncs.custom_warning(condition=False, importance=2, message=f"{self._get_warning_prefix()}{value} is no valid initialization value.", hideNadditionalStackLines=3)

    def _traceFunc_wrapper(self):
        """This is actually the only function registered by super().trace_add.
        It processes the value and colors widgets, then if the value is stable and valid.
        consecutively calls a list of functions registered via self.trace_add.
        """
        self.processingTrace = True  # activate this here since it should stay activated also during the custom_traces call
        if not self.processingSuperSet:  # if self.processingSuperSet would be true, the value has already been processed and reset to stable at this point
            self._process_new_value(super().get())
            if not self.isValid:
                self._color_connected_widgets("red")
                self.processingTrace = False
                return  # return immediately! # Ein leeres Entry zb darf eben nicht sofort wieder durch den letzten safe value ersetzt werden, erschwert die bedienung sehr.
                # erst, wenn das value gebrauchtt wird (get() call) soll es sichtbar ersetzt werden!
            if not self.isStable:
                self._color_connected_widgets("orange")
                self.processingTrace = False
                return  # return immediately! (see above)
        self._color_connected_widgets()
        for func in self.custom_traces:
            func()
        self.processingTrace = False

    def _color_connected_widgets(self, color=None):
        for widget, defaultColor in self.connectedWidgets:
            color = defaultColor if color is None else color
            try:  # widget might be deleted already somehow
                if widget.cget("bg") != color:  # so config is skipped for performance if nothing has to change
                    widget.config(bg=color)
            except:
                pass

    def _get_warning_prefix(self):
        if str(self).startswith("PY_VAR"):  # User gave no name, so the default tk-given name shouldnt be displayed either.
            return ""
        else:
            return f"{self}: "


def main():
    try:
        from myFuncs import print_default_kwargs
        print_default_kwargs(SafeVar)
    except Exception:
        pass
    tk.Tk()  # Needs to be called at least once to create instances of SafeVar.
    restrictedInt = SafeVar.basic_type(3, int, check_func=lambda x: 0 <= x <= 10, validityInstructions="Value must be an int between 0 and 10.")
    print(f"{restrictedInt.get() = }")
    restrictedInt.set(1.7)
    print(f"{restrictedInt.get() = }")
    restrictedInt.set("5")
    print(f"{restrictedInt.get() = }")
    restrictedInt.set("7.3")
    print(f"{restrictedInt.get() = }")
    restrictedInt.set(12)
    # Program will halt at this point.
    print(f"{restrictedInt.get() = }")


if __name__ == "__main__":
    main()
