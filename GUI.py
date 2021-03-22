import tkinter as tk
import numpy as np

import Tile


class GUI:
    def __init__(self, root):
        self.gp = None
        X = 8
        Y = 5
        self.window = tk.Toplevel(root)
        self.gridworldFrame = tk.Frame(self.window)
        self.gridworldFrame.grid(row=0, column=0)
        self.tiles = np.empty((X, Y), dtype=np.object)
        for x in range(X):
            for y in range(Y):
                self.tiles[x, y] = Tile.Tile(self.gridworldFrame, width=5, height=2)
                self.tiles[x, y].grid(row=y, column=x)

    def set_gp(self, gp):
        self.gp = gp

    def initialize(self):
        data = None # gather data
        self.gp.initialize(data)

    def visualize(self, data):
        # update gui
        pass
