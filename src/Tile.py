import tkinter as tk
import numpy as np
from functools import cache

from Agent import Agent
import myFuncs
from myFuncs import evaluate


class Tile(tk.Frame):
    """This class manages the graphical representation of a single gridworld cell
    as well as optional user interaction to specify the properties of that cell.
    """
    BLANK_COLOR = "white"
    WALL_COLOR = "black"
    LETTER_COLOR = "black"
    VALUE_INCREASE_COLOR = "green"
    VALUE_DECREASE_COLOR = "red"
    DEFAULT_RELIEF = tk.GROOVE
    START_CHAR = "S"
    GOAL_CHAR = "G"
    AGENTCOLOR_DEFAULT = "#0000FF"  # blue
    AGENTCOLOR_EXPLORATORY = "#FF0000"  # red
    AGENTCOLOR_PLANNING = "#00FF00"  # green
    AGENTCOLOR_DEAD = "grey"
    TELEPORT_JUST_USED_COLOR = "#FFFF00"  # yellow
    WIND_JUST_USED_COLOR = "#FFFF00"  # yellow

    TYPE_BLANK = {"text": "", "fg": LETTER_COLOR, "bg": BLANK_COLOR}
    TYPE_WALL = {"text": "", "fg": LETTER_COLOR, "bg": WALL_COLOR}
    TYPE_START = {"text": START_CHAR, "fg": LETTER_COLOR, "bg": BLANK_COLOR}
    TYPE_GOAL = {"text": GOAL_CHAR, "fg": LETTER_COLOR, "bg": BLANK_COLOR}
    TYPES = [TYPE_BLANK, TYPE_WALL, TYPE_START, TYPE_GOAL]

    BORDER_COLORS = ["Grey", "Cyan", "Red"]

    TELEPORTERS = [str(i) for i in range(1,10)]  # 1-9
    TELEPORTER_SOURCE_ONLY_SUFFIX = "+"
    TELEPORTER_SINK_ONLY_SUFFIX = "-"
    TELEPORTER_DEFAULT_SUFFIX = " "  # "±"  # alternative

    GREEDYCHARS_1_2 = [['┛','↑','┗'],
                       ['←',' ','→'],
                       ['┓','↓','┏']]
    GREEDYCHAR_UP_DOWN = '┃'
    GREEDYCHAR_LEFT_RIGHT = '━'
    GREEDYCHARS_3_4 = [[' ','┴',' '],
                       ['┤','┼','├'],
                       [' ','┬',' ']]
    GREEDYCHARS_SINGLE_NONDEFAULT_ACTION = [['↖','↑','↗'],
                                            ['←','◯','→'],
                                            ['↙','↓','↘']]
    GREEDYCHAR_NONDEFAULT_ACTION_MIX = ' '
    DEFAULT_HSV_VALUE = 0.75

    @classmethod
    @cache
    def get_greedy_actions_representation(cls, greedyActions):
        """Returns the representation (char and its color) of a single action or a
        combination of those. Use them as parameters of the ``update_appearance``
        method of a single ``Tile`` to visualize the current choice of greedy actions
        in the corresponding state. Inherits from ``tk.Frame``.

        :param tuple greedyActions: tuple of unique actions
        :return dict[str, str]: {"text": <value>, "fg": <value>}
        """
        actionSum = np.sum(greedyActions, axis=0)  # i.e. UP + RIGHT = (-1,-0) + (0,1) = (-1,1)
        index = actionSum + 1  # index where to find the representation of greedyactions with that sum in the GREEDYCHARS_ matrices
        color = "black"
        if bool(set(greedyActions) & set(Agent.create_actionspace(straight=False))):  # greedyActions contains nondefault action
            if len(greedyActions) == 1:
                color = myFuncs.direction_to_hsvHexString(tuple(actionSum), hsvValue=cls.DEFAULT_HSV_VALUE)  # tuple cast because a cached function needs mutable args
                symbol = evaluate(cls.GREEDYCHARS_SINGLE_NONDEFAULT_ACTION, index)
            else:
                symbol = cls.GREEDYCHAR_NONDEFAULT_ACTION_MIX
        else:  # greedyActions contains only straight actions
            if len(greedyActions) <= 2:
                color = myFuncs.direction_to_hsvHexString(tuple(actionSum), hsvValue=cls.DEFAULT_HSV_VALUE)  # tuple cast because a cached function needs mutable args
                if actionSum.any():  # Other than opposing directions
                    symbol = evaluate(cls.GREEDYCHARS_1_2, index)
                else:
                    if greedyActions[0][0]:  # x _value of arbitrary greedy action is nonzero
                        symbol = cls.GREEDYCHAR_LEFT_RIGHT
                    else:
                        symbol = cls.GREEDYCHAR_UP_DOWN
            else:
                symbol = evaluate(cls.GREEDYCHARS_3_4, index)
        return {"text": symbol, "fg": color}

    def __init__(self, master, indicateNumericalValueChange, labelWidth, labelHeight, *args, font="calibri 14 bold", **kwargs):
        """Creates a ``Tile`` object. Manages a single ``packed tk.Label`` inside
        to allow providing information and explicitly coloring the the edges independent
        from the center by having two distinct background color parameters for config.

        :param master: Parent container.
        :param bool indicateNumericalValueChange: If True, a number will be colored red if the previous Tile content was a bigger number and green if it was a smaller number.
        :param int labelWidth: Width of the label inside.
        :param int labelHeight: Height of the label inside.
        :param args: Additional arguments passed to the super().__init__ (tk.Frame)
        :param str font: Font of the displayed text.
        :param kwargs: Additional keyword arguments passed to the super().__init__ (tk.Frame)
        """
        super().__init__(master, *args, relief=self.DEFAULT_RELIEF, **kwargs)
        self.label = tk.Label(self, bd=0, height=labelHeight, width=labelWidth, font=font)
        self.label.pack(fill=tk.BOTH, expand=True)
        self.typeCycleIndex = 0
        self.borderColorCycleIndex = 0
        self.protectedAttributes = set()
        for widget in [self, self.label]:
            widget.bind("<Button-1>", lambda _: self._cycle_type(direction=1))  # left click
            widget.bind("<Control-Button-1>", lambda _: self._cycle_type(direction=-1))  # ctrl + left click
            widget.bind("<Button-3>", lambda _: self._cycle_borderColor(direction=1))  # right click
            widget.bind("<Control-Button-3>", lambda _: self._cycle_borderColor(direction=-1))  # ctrl + right click
            widget.bind("<Button-2>", lambda _: widget.focus_set())  # focus is needed to toggle teleport
            for char in self.TELEPORTERS:
                widget.bind(char, lambda _, char_=char: self._toggle_teleport(number=char_))
            for button in ["<Up>", "w", "+"]:
                widget.bind(button, lambda _: self._specify_teleport(suffix=self.TELEPORTER_SOURCE_ONLY_SUFFIX))
            for button in ["<Down>", "s", "-"]:
                widget.bind(button, lambda _: self._specify_teleport(suffix=self.TELEPORTER_SINK_ONLY_SUFFIX))
        self.indicateNumericalValueChange = indicateNumericalValueChange
        self.reset()

    def reset(self):
        """Restore the initial representation of the ``Tile``.
        """
        self.update_appearance(borderColor=self.BORDER_COLORS[0], **self.TYPES[0])

    def protect_attributes(self, *args):
        """Protect visual attributes from being changed by the ``update_appearance``
        method. Used as a solution to fix bugs where goal- or teleport indicators
        were overwritten by actionvalues and vice versa when they shouldnt.
        Feels like there is a more clear and intuitive approach...

        :param args: Strings that match tk.Label attributes
        :return:
        """
        self.protectedAttributes |= set(args)  # fancy new operator in python 3.9

    def unprotect_attributes(self, *args):
        """Allows visual attributes to be changed by the ``update_appearance``
        method. Used as a solution to fix bugs where goal- or teleport indicators
        were overwritten by actionvalues and vice versa when they shouldnt.
        Feels like there is a more clear and intuitive approach...

        :param args: Strings that match tk.Label attributes
        :return:
        """
        self.protectedAttributes -= set(args)

    def update_appearance(self, borderColor=None, **labelKwargs):
        """Updates the visual appearance of this ``Tile``.
        Keyword arguments that would change protected attributes are ignored.
        If ``self.indicateNumericalChange`` is ``True``, also applies the appropriate
        textcolor change (keyword "fg"), unless "fg" is protected. For performance,
        the very expensive ``config`` method of the underlying ``tkinter`` objects
        will only be called if at least one attribute that doesnt keep the same value
        is left after the processing steps described above. The large amount of calls
        of this method along with the use of ``config`` inside makes it the bottleneck
        of the gridworld sandbox.

        :param str borderColor: background ("bg") of the ``Tile`` itself, of which only the borders are not covered by the packed tk.Label
        :param labelKwargs: Any keyword arguments that would also work with tk.Label.config()
        """
        labelKwargs = {key: value for key, value in labelKwargs.items() if key not in self.protectedAttributes}
        if self.indicateNumericalValueChange and "fg" not in self.protectedAttributes:
            try:
                oldValue = float(self.label.cget("text"))
                newValue = float(labelKwargs["text"])
                if newValue > oldValue:
                    labelKwargs["fg"] = self.VALUE_INCREASE_COLOR
                elif newValue < oldValue:
                    labelKwargs["fg"] = self.VALUE_DECREASE_COLOR
                else:
                    labelKwargs["fg"] = self.LETTER_COLOR
            except:  # old or new value not defined or not numerical for any reason
                labelKwargs["fg"] = self.LETTER_COLOR
        labelKwargs = {key: value for key, value in labelKwargs.items() if self.label.cget(key) != value}
        if labelKwargs:
            self.label.config(**labelKwargs)
        if borderColor and borderColor != self.cget("bg"):  # borderColor cannot be protected since "bg" isnt unique, but this isnt needed anyway.
            self.config(bg=borderColor)

    def get_yaml_dict(self):
        """Returns the representation of this ``Tile`` as a yaml-conform dictionary.

        :return dict: Tile data representation
        """
        yamlDict = {param: self.label.cget(param) for param in self.TYPE_BLANK.keys()}
        yamlDict["borderColor"] = self.cget("bg")
        return yamlDict

    def _toggle_teleport(self, number: str):
        if self.master.interactionAllowed:
            if number in self.label.cget("text"):
                number = ""
            else:
                number += self.TELEPORTER_DEFAULT_SUFFIX
            self.update_appearance(text=number, bg=self.BLANK_COLOR)  # without bg, if toggled on a wall tile, teleport number would hide behind the black color and cause unwanted behavior during run

    def _specify_teleport(self, suffix):
        text = self.label.cget("text")
        if self.master.interactionAllowed and text and (text[0] in self.TELEPORTERS):
            if text[1] == suffix:
                replacement = self.TELEPORTER_DEFAULT_SUFFIX
            else:
                replacement = suffix
            text = text[0] + replacement
            self.update_appearance(text=text)

    def _cycle_type(self, direction):
        if self.master.interactionAllowed:
            self.typeCycleIndex = (self.typeCycleIndex + direction) % len(self.TYPES)
            self.update_appearance(**self.TYPES[self.typeCycleIndex])

    def _cycle_borderColor(self, direction):
        if self.master.interactionAllowed:
            self.borderColorCycleIndex = (self.borderColorCycleIndex + direction) % len(self.BORDER_COLORS)
            self.update_appearance(borderColor=self.BORDER_COLORS[self.borderColorCycleIndex])
