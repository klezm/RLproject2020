from ParameterFrame import ParameterFrame
from SafeVar import SafeVar


class SafeVarFrame(ParameterFrame):
    promptWidthDefault = 8
    check_funcDefault = SafeVar.check_funcDefault  # not used, but needed for default value inspection. None will get passed to the SafeVar ctor, which then will assign check_funcDefault
    trustSetDefault = SafeVar.trustSetDefault  # # not used, but needed for default value inspection. None will get passed to the SafeVar ctor, which then will assign trustSetDefault

    def __init__(self, *args, varTargetType, value=None, validityInstructions=None, check_func=None, trustSet=None, promptWidth=None, **kwargs):
        self.promptWidth = self.promptWidthDefault if promptWidth is None else promptWidth
        self.check_func = check_func  # the check if is None must not be applied here since None will just get passed to the SafeVar ctor later, which handles the check
        self.trustSet = trustSet  # the check if is None must not be applied here since None will just get passed to the SafeVar ctor later, which handles the check
        self.validityInstructions = validityInstructions
        self.varTargetType = varTargetType
        if value is None:
            self.value = self.varTargetType()  # creating a dummy value by calling the default ctor of the targetType if no explicit default value is passed should satisfy the security check during the SafeVar Init
        else:
            self.value = value
        super().__init__(*args, **kwargs)  # default value will not be passed to super init, so the setter at the end of super init will not be called. This avoids redundance.

    def make_var(self):
        try:
            name = self.get_text()
        except:
            name = self.nameLabel
        self.variable = SafeVar.basic_type(self.value, self.varTargetType, name=name, check_func=self.check_func, tooltipFont=self.tooltipFont, trustSet=self.trustSet,
                                           unstableValueImportance=1, invalidValueImportance=1, validityInstructions=self.validityInstructions)

    def connect(self):
        self.variable.connect_widgets(self.dataPrompt)

    def set_and_call_trace(self, input_func):
        self.variable.trace_add(input_func, callFunc=True)
