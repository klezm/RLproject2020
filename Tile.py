import tkinter as tk


class Tile(tk.Label):
    BLANKCOLOR = "white"
    WALLCOLOR = "black"
    STARTLETTER = "S"
    GOALLETTER = "G"
    AGENTCOLOR = "blue"
    tileBlank = {"text": "", "bg": BLANKCOLOR}
    tileWall = {"text": "", "bg": WALLCOLOR}
    tileStart = {"text": STARTLETTER, "bg": BLANKCOLOR}
    tileGoal = {"text": GOALLETTER, "bg": BLANKCOLOR}
    tileTypes = [tileBlank, tileWall, tileStart, tileGoal]

    def __init__(self, mother, interact, **kwargs):
        super().__init__(mother, bd=1, relief=tk.GROOVE, **kwargs)
        self.arrivalReward = 0  # TODO: set this in GUI!
        self.typeID = 0
        self.cycle_type()
        if interact:
            self.bind("<Button-1>", lambda _: self.cycle_type(direction=1))
            self.bind("<Button-3>", lambda _: self.cycle_type(direction=-1))

    def get_arrival_reward(self):
        return self.arrivalReward

    def cycle_type(self, direction=0):
        self.typeID = (self.typeID + direction) % len(self.tileTypes)
        self.update_appearance()

    def update_appearance(self, **kwargs):
        if not kwargs:
            kwargs = self.tileTypes[self.typeID]
        self.config(**kwargs)
