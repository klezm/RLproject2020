import tkinter as tk
import numpy as np

from functools import cache

from Agent import Agent
import myFuncs


class Tile(tk.Frame):
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

    TYPE_BLANK = {"text": "", "fg": LETTER_COLOR, "bg": BLANK_COLOR}
    TYPE_WALL = {"text": "", "fg": LETTER_COLOR, "bg": WALL_COLOR}
    TYPE_START = {"text": START_CHAR, "fg": LETTER_COLOR, "bg": BLANK_COLOR}
    TYPE_GOAL = {"text": GOAL_CHAR, "fg": LETTER_COLOR, "bg": BLANK_COLOR}
    TYPES = [TYPE_BLANK, TYPE_WALL, TYPE_START, TYPE_GOAL]

    BORDER_COLORS = ["black", "cyan", "brown"]

    TELEPORTERS = [str(i) for i in range(1,10)]  # 1-9
    TELEPORTER_SOURCE_ONLY_SUFFIX = "+"
    TELEPORTER_SINK_ONLY_SUFFIX = "-"
    TELEPORTER_DEFAULT_SUFFIX = " "

    GREEDYCHARS_1_2 = np.array([['┛','↑','┗'],
                                ['←',' ','→'],
                                ['┓','↓','┏']])
    GREEDYCHAR_UP_DOWN = '┃'
    GREEDYCHAR_LEFT_RIGHT = '━'
    GREEDYCHARS_3_4 = np.array([[' ','┴',' '],
                                ['┤','┼','├'],
                                [' ','┬',' ']])
    GREEDYCHARS_SINGLE_NONDEFAULT_ACTION = np.array([['↖','↑','↗'],
                                                     ['←','◯','→'],
                                                     ['↙','↓','↘']])
    GREEDYCHAR_NONDEFAULT_ACTION_MIX = ' '
    DEFAULT_HSV_VALUE = 0.75

    @classmethod
    @cache
    def direction_to_hsvHexString(cls, direction):
        if direction == (0,0):
            return "#000000"  # black
        angle = myFuncs.angle_between(Agent.UP, direction)
        if direction[0] < 0:
            angle += 180
        return myFuncs.hsv_to_rgbHexString(angle / 360, 1, cls.DEFAULT_HSV_VALUE)

    @classmethod
    @cache
    def get_greedy_actions_representation(cls, greedyActions):
        actionSum = np.sum(greedyActions, axis=0)  # i.e. UP + RIGHT = (0,-1) + (1,0) = (1,-1)
        index = (actionSum[1]+1, actionSum[0]+1)
        color = "black"
        if bool(set(greedyActions) & set(Agent.create_actionspace(default=False))):  # greedyActions contains nondefault action
            if len(greedyActions) == 1:
                color = cls.direction_to_hsvHexString(tuple(actionSum))  # tuple cast because a cached function needs mutable args
                symbol = cls.GREEDYCHARS_SINGLE_NONDEFAULT_ACTION[index]
            else:
                symbol = cls.GREEDYCHAR_NONDEFAULT_ACTION_MIX
        else:  # greedyActions contains only default actions
            if len(greedyActions) <= 2:
                color = cls.direction_to_hsvHexString(tuple(actionSum))  # tuple cast because a cached function needs mutable args
                if actionSum.any():  # Other than opposing directions
                    symbol = cls.GREEDYCHARS_1_2[index]
                else:
                    if greedyActions[0][0]:  # x _value of arbitrary greedy action is nonzero
                        symbol = cls.GREEDYCHAR_LEFT_RIGHT
                    else:
                        symbol = cls.GREEDYCHAR_UP_DOWN
            else:
                symbol = cls.GREEDYCHARS_3_4[index]
        return {"text": symbol, "fg": color}

    def __init__(self, master, indicateNumericalValueChange, labelWidth, labelHeight, font="calibri 14 bold", **kwargs):
        super().__init__(master, relief=self.DEFAULT_RELIEF, **kwargs)
        self.label = tk.Label(self, bd=0, height=labelHeight, width=labelWidth, font=font)
        self.label.pack(fill=tk.BOTH, expand=True)
        self.typeCycleIndex = 0
        self.borderColorCycleIndex = 0
        self.protectedAttributes = set()
        for widget in [self, self.label]:
            widget.bind("<Button-1>", lambda _: self.cycle_type(direction=1))  # left click
            widget.bind("<Control-Button-1>", lambda _: self.cycle_type(direction=-1))  # ctrl + left click
            widget.bind("<Button-3>", lambda _: self.cycle_borderColor(direction=1))  # right click
            widget.bind("<Control-Button-3>", lambda _: self.cycle_borderColor(direction=-1))  # ctrl + right click
            widget.bind("<Button-2>", lambda _: widget.focus_set())  # focus is needed to toggle teleport
            for char in self.TELEPORTERS:
                widget.bind(char, lambda _, char_=char: self.toggle_teleport(number=char_))
            for button in ["<Up>", "w", "+"]:
                widget.bind(button, lambda _: self.specify_teleport(suffix=self.TELEPORTER_SOURCE_ONLY_SUFFIX))
            for button in ["<Down>", "s", "-"]:
                widget.bind(button, lambda _: self.specify_teleport(suffix=self.TELEPORTER_SINK_ONLY_SUFFIX))
        self.indicateNumericalValueChange = indicateNumericalValueChange
        self.update_appearance(borderColor=self.BORDER_COLORS[0], **self.TYPES[0])

    def protect_attributes(self, *args):
        self.protectedAttributes |= set(args)  # fancy new operator in python 3.9

    def unprotect_attributes(self, *args):
        self.protectedAttributes -= set(args)

    def toggle_teleport(self, number: str):
        if self.master.interactionAllowed:
            if number in self.label.cget("text"):
                number = ""
            else:
                number += self.TELEPORTER_DEFAULT_SUFFIX
            self.update_appearance(text=number, bg=self.BLANK_COLOR)  # without bg, if toggled on a wall tile, teleport number would hide behind the black color and cause unwanted behavior during run

    def specify_teleport(self, suffix):
        text = self.label.cget("text")
        if self.master.interactionAllowed and text and (text[0] in self.TELEPORTERS):
            if text.endswith(suffix):
                text = text[0] + self.TELEPORTER_DEFAULT_SUFFIX
            else:
                text = text[0] + suffix
            self.update_appearance(text=text)

    def cycle_type(self, direction):
        if self.master.interactionAllowed:
            self.typeCycleIndex = (self.typeCycleIndex + direction) % len(self.TYPES)
            self.update_appearance(**self.TYPES[self.typeCycleIndex])

    def cycle_borderColor(self, direction):
        if self.master.interactionAllowed:
            self.borderColorCycleIndex = (self.borderColorCycleIndex + direction) % len(self.BORDER_COLORS)
            self.update_appearance(borderColor=self.BORDER_COLORS[self.borderColorCycleIndex])

    def update_appearance(self, borderColor=None, **kwargs):
        kwargs = {key: value for key, value in kwargs.items() if key not in self.protectedAttributes}
        if self.indicateNumericalValueChange and "fg" not in self.protectedAttributes:
            try:
                oldValue = float(self.label.cget("text"))
                newValue = float(kwargs["text"])
                if newValue > oldValue:
                    kwargs["fg"] = self.VALUE_INCREASE_COLOR
                elif newValue < oldValue:
                    kwargs["fg"] = self.VALUE_DECREASE_COLOR
                else:
                    kwargs["fg"] = self.LETTER_COLOR
            except:
                kwargs["fg"] = self.LETTER_COLOR
        kwargs = {key: value for key, value in kwargs.items() if self.label.cget(key) != value}
        if kwargs:
            self.label.config(**kwargs)
        if borderColor:
            self.config(bg=borderColor)

    def get_yaml_dict(self):
        return {"text": self.label.cget("text"),
                "bg": self.label.cget("bg"),
                "borderColor": self.cget("bg")}
