from ParameterFrame import ParameterFrame
from SafeVar import SafeVar


class SafeVarFrame(ParameterFrame):
    """Inheriting from ``ParameterFrame``, this class uses a ``SafeVar`` as variable container.
    """
    def __init__(self, *args, varTargetType, value=None, validityInstructions="", check_func=lambda _: True, trustSet=False, promptWidth=8, **kwargs):
        """Creates a SafeVarFrame object.

        :param args: Additional arguments passed to the super().__init__ (ParameterFrame)
        :param type varTargetType: Choose between int, float, str, bool
        :param value: Initial Value for the SafeVar.
        :param str validityInstructions: Description of the properties of a stable SafeVar value. They will be shown in each warning/error and as a prompt ToolTip
        :param function check_func: Signature: Any -> bool. Defines the condition a value has to fulfil to be valid.
        :param bool trustSet: If True, every value assigned by SafeVar.set will automatically be treated as valid and stable. Use with caution.
        :param promptWidth: Width of the prompt used in this SafeVarFrame.
        :param kwargs: Additional keyword arguments passed to the super().__init__ (ParameterFrame)
        """
        self.promptWidth = promptWidth
        self.check_func = check_func
        self.trustSet = trustSet
        self.validityInstructions = validityInstructions
        self.varTargetType = varTargetType
        if value is None:
            self.value = self.varTargetType()  # creating a dummy value by calling the default ctor of the targetType if no explicit default value is passed should satisfy the first security check (during the SafeVar Init)
        else:
            self.value = value
        super().__init__(*args, **kwargs)  # default value will not be passed to super init, so the setter at the end of super init will not be called. This avoids redundance.

    def set_and_call_trace(self, input_func):
        """Sets a function to be called if the variable connected to this ``SafeVarFrame`` changes its value.
        Also calls that function once.

        :param function input_func: Function to be called
        """
        self.variable.trace_add(input_func, callFunc=True)

    def _make_var(self):
        try:
            name = self.get_text()  # namelabel is an actual tk.Label
        except:
            name = self.nameLabel  # namelabel is a string
        self.variable = SafeVar.basic_type(self.value, self.varTargetType, name=name, check_func=self.check_func, tooltipFont=self.tooltipFont, trustSet=self.trustSet,
                                           unstableValueImportance=1, invalidValueImportance=1, validityInstructions=self.validityInstructions)

    def _connect(self):
        self.variable.connect_widgets(self.dataPrompt)
