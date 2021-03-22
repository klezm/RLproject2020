import tkinter as tk
from itertools import cycle


class Tile(tk.Label):
    # input für colormap
    tileBlank = {"text": "", "bg": "white"}
    tileWall = {"text": "", "bg": "black"}
    tileStart = {"text": "S", "bg": "white"}
    tileGoal = {"text": "G", "bg": "white"}
    tileTypes = [tileBlank, tileWall, tileStart, tileGoal]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, bd=1, relief=tk.GROOVE, **kwargs)
        self.cycler = cycle(self.tileTypes)
        self.toggle()
        self.bind("<Button-1>", self.toggle)
        self.bind("<Button-3>", self.toggle)

    def toggle(self, *args):
        self.config(**next(self.cycler))

    def set(self):
        pass

        #self.env = Gridworld(self.gridworldFrame, X, Y)