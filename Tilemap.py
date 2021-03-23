import tkinter as tk
import numpy as np

from Tile import Tile


class Tilemap(tk.Frame):
    def __init__(self, mother, X, Y, interact, fontsize, **kwargs):
        super().__init__(mother, **kwargs)
        self.tiles = np.empty((X,Y), dtype=np.object)
        for x in range(X):
            for y in range(Y):
                self.tiles[x,y] = Tile(self, interact=interact, width=2, height=1, font=f"calibri {fontsize} bold")
                self.tiles[x,y].grid(row=y, column=x)
