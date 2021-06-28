from src.ParameterFrame import ParameterFrame
from SafeVar import SafeVar


class SafeVarFrame(ParameterFrame):
    promptWidthDefault = 8
    var_check_funcDefault = "lambda _: True"  # just for inspection purposes
    trustSetDefault = False

    def __init__(self, *args, VarTargetType, defaultValue=None, validityInstructions="", var_check_func=lambda _: True, trustSet=None, promptWidth=None, **kwargs):
        self.promptWidth = self.promptWidthDefault if promptWidth is None else promptWidth
        self.var_check_func = var_check_func  # using self.var_check_funcDefault doesnt work here!
        self.trustSet = self.trustSetDefault if trustSet is None else trustSet
        self.validityInstructions = validityInstructions
        self.VarTargetType = VarTargetType
        if defaultValue is None:
            self.defaultValue = self.VarTargetType()  # creating a dummy value by calling the default ctor of the targetType if no explicit default value is passed should satisfy the security check during the SafeVar Init
        else:
            self.defaultValue = defaultValue
        super().__init__(*args, **kwargs)  # default value will not be passed to super init, so the setter at the end of super init will not be called. This avoids redundance.

    def make_var(self):
        try:
            name = self.get_text()
        except:
            name = self.nameLabel
        self.variable = SafeVar(self.defaultValue, name=name, check_func=self.var_check_func, main_transform_func=self.VarTargetType,
                                gui_input_transform_func=float if self.VarTargetType in (int, float) else lambda arg: arg,
                                unstableValueImportance=1, invalidValueImportance=1, validityInstructions=self.validityInstructions,
                                tooltipFont=self.tooltipFont, trustSet=self.trustSet)

    def connect(self):
        self.variable.connect_widgets(self.dataPrompt)

    def set_and_call_trace(self, input_func):
        self.variable.trace_add(input_func, callFunc=True)
