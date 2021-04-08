import tkinter as tk

from Agent import Agent


class Tile(tk.Label):
    BLANKCOLOR = "white"
    WALLCOLOR = "black"
    LETTERCOLOR = "black"
    STARTCHAR = "S"
    GOALCHAR = "G"
    AGENTCOLOR_DEFAULT = "blue"
    AGENTCOLOR_EXPLORATORY = "red"

    tileBlank = {"text": "", "bg": BLANKCOLOR}
    tileWall = {"text": "", "bg": WALLCOLOR}
    tileStart = {"text": STARTCHAR, "fg": LETTERCOLOR, "bg": BLANKCOLOR}
    tileGoal = {"text": GOALCHAR, "fg": LETTERCOLOR, "bg": BLANKCOLOR}

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

    def __init__(self, mother, interact, **kwargs):
        super().__init__(mother, bd=1, relief=tk.GROOVE, **kwargs)
        self.arrivalReward = 0  # TODO: set this in GUI!
        self.tileType = self.tileBlank
        self.cycleIndex = 0
        if interact:
            self.bind("<Button-1>", lambda _: self.cycle_type(direction=1))
            self.bind("<Button-3>", lambda _: self.cycle_type(direction=-1))
        self.update_appearance()

    def get_tileType(self):
        return self.tileType

    def get_arrivalReward(self):
        return self.arrivalReward

    def cycle_type(self, direction=0):
        self.cycleIndex = (self.cycleIndex + direction) % len(self.tileCycleTypes)
        self.tileType = self.tileCycleTypes[self.cycleIndex]
        self.update_appearance()

    def update_appearance(self, tileType=None, **kwargs):
        if tileType:
            self.tileType = tileType
        kwargs = self.tileType | kwargs  # new in python 3.9.0: '|' merges dictionaries
        self.config(**kwargs)


Tile.tilePolicyTypes = {action: {"text": Tile.POLICY_CHARS[action],
                                 "fg": Tile.POLICY_COLORS[action],
                                 "bg": Tile.BLANKCOLOR}
                        for action in Agent.ACTIONS}
Tile.tilePolicyTypes[None] = Tile.tileBlank
