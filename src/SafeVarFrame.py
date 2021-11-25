from ParameterFrame import ParameterFrame
from SafeVar import SafeVar


class SafeVarFrame(ParameterFrame):
    def __init__(self, *args, varTargetType, value=None, validityInstructions="", check_func=lambda _: True, trustSet=False, promptWidth=8, **kwargs):
        self.promptWidth = promptWidth
        # For the following attributes, the check if <var> is None must not be applied here since None will just get passed to the SafeVar ctor later, which handles the check
        self.check_func = check_func
        self.trustSet = trustSet
        self.validityInstructions = validityInstructions
        self.varTargetType = varTargetType
        if value is None:
            self.value = self.varTargetType()  # creating a dummy value by calling the default ctor of the targetType if no explicit default value is passed should satisfy the first security check (during the SafeVar Init)
        else:
            self.value = value
        super().__init__(*args, **kwargs)  # default value will not be passed to super init, so the setter at the end of super init will not be called. This avoids redundance.

    def _make_var(self):
        try:
            name = self.get_text()  # namelabel is an actual tk.Label
        except:
            name = self.nameLabel  # namelabel is a string
        self.variable = SafeVar.basic_type(self.value, self.varTargetType, name=name, check_func=self.check_func, tooltipFont=self.tooltipFont, trustSet=self.trustSet,
                                           unstableValueImportance=1, invalidValueImportance=1, validityInstructions=self.validityInstructions)

    def connect(self):
        self.variable.connect_widgets(self.dataPrompt)

    def set_and_call_trace(self, input_func):
        self.variable.trace_add(input_func, callFunc=True)


if __name__ == "__main__":
    from myFuncs import print_default_kwargs
    print_default_kwargs(SafeVarFrame)
