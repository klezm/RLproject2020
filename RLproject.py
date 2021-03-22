import tkinter as tk
import numpy as np
from itertools import cycle


class Gridworld:
    def __init__(self, frame):
        self.frame = frame


class State:
    def __init__(self, env, x, y):
        pass


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


class GridworldPlayground:
    # gui und env kapseln
    def __init__(self, root):
        X = 8
        Y = 5
        self.window = tk.Toplevel(root)
        self.gridworldFrame = tk.Frame(self.window)
        self.gridworldFrame.grid(row=0, column=0)
        self.tiles = np.empty((X, Y), dtype=np.object)
        for x in range(X):
            for y in range(Y):
                self.tiles[x, y] = Tile(self.gridworldFrame, width=5, height=2)
                self.tiles[x, y].grid(row=y, column=x)

        #self.env = Gridworld(self.gridworldFrame, X, Y)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    GridworldPlayground(root)
    root.mainloop()
