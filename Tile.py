import tkinter as tk

from Agent import Agent


class Tile(tk.Label):
    BLANK_COLOR = "white"
    WALL_COLOR = "black"
    LETTER_COLOR = "black"
    VALUE_INCREASE_COLOR = "green"
    VALUE_DECREASE_COLOR = "red"
    VALUE_CHANGE_RELIEF = tk.RAISED
    DEFAULT_RELIEF = tk.GROOVE
    START_CHAR = "S"
    GOAL_CHAR = "G"
    AGENTCOLOR_DEFAULT_DEFAULT = "blue"
    AGENTCOLOR_DEFAULT_LIGHT = "#AAAAFF"  # light blue
    AGENTCOLOR_EXPLORATORY_DEFAULT = "red"
    AGENTCOLOR_EXPLORATORY_LIGHT = "#FFAAAA"  # light red
    AGENTCOLOR_PLANNING_DEFAULT = "green"
    AGENTCOLOR_PLANNING_LIGHT = "#AAFFAA"  # light green

    tileBlank = {"text": "", "fg": LETTER_COLOR, "bg": BLANK_COLOR}
    tileWall = {"text": "", "fg": LETTER_COLOR, "bg": WALL_COLOR}
    tileStart = {"text": START_CHAR, "fg": LETTER_COLOR, "bg": BLANK_COLOR}
    tileGoal = {"text": GOAL_CHAR, "fg": LETTER_COLOR, "bg": BLANK_COLOR}

    # no zip for better readability
    POLICY_CHARS = {Agent.UP: "\u2191",
                    Agent.DOWN: "\u2193",
                    Agent.LEFT: "\u2190",
                    Agent.RIGHT: "\u2192"}
    POLICY_COLORS = {Agent.UP: "blue",
                     Agent.DOWN: "red",
                     Agent.LEFT: "green",
                     Agent.RIGHT: "orange"}

    tilePolicyTypes = None  # No dict comp available here, so this will be assigned at end of file

    tileCycleTypes = [tileBlank, tileWall, tileStart, tileGoal]

    def __init__(self, master, indicateNumericalValueChange, **kwargs):
        super().__init__(master, bd=1, relief=self.DEFAULT_RELIEF, **kwargs)
        self.arrivalReward = 0  # TODO: set this in GUI
        self.cycleIndex = 0
        self.protectedAttributes = set()
        self.bind("<Button-1>", lambda _: self.cycle_type(direction=1))
        self.bind("<Button-3>", lambda _: self.cycle_type(direction=-1))
        self.indicateNumericalValueChange = indicateNumericalValueChange
        self.update_appearance(**self.tileBlank)

    def protect_attributes(self, *args):
        self.protectedAttributes |= set(args)  # fancy new operator in python 3.9

    def unprotect_attributes(self, *args):
        self.protectedAttributes -= set(args)

    def get_arrivalReward(self):
        return self.arrivalReward

    def cycle_type(self, direction):
        if self.master.interactionAllowed:
            self.cycleIndex = (self.cycleIndex + direction) % len(self.tileCycleTypes)
            self.update_appearance(**self.tileCycleTypes[self.cycleIndex])

    def update_appearance(self, **kwargs):
        kwargs = {key: value for key, value in kwargs.items() if key not in self.protectedAttributes}
        if self.indicateNumericalValueChange and "fg" not in self.protectedAttributes:
            # TODO: Make the color proportional to relative value change
            try:
                oldValue = float(self.cget("text"))
                newValue = float(kwargs["text"])
                if newValue > oldValue:
                    kwargs["fg"] = self.VALUE_INCREASE_COLOR
                elif newValue < oldValue:
                    kwargs["fg"] = self.VALUE_DECREASE_COLOR
                else:
                    kwargs["fg"] = self.LETTER_COLOR
            except:
                kwargs["fg"] = self.LETTER_COLOR
        kwargs = {key: value for key, value in kwargs.items() if self.cget(key) != value}
        if kwargs:
            self.config(**kwargs)


Tile.tilePolicyTypes = {action: {"text": Tile.POLICY_CHARS[action],
                                 "fg": Tile.POLICY_COLORS[action]}
                        for action in Agent.ACTIONSPACE}
Tile.tilePolicyTypes[None] = {"text": "",
                              "fg": Tile.LETTER_COLOR}
