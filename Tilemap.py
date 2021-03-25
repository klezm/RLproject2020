import tkinter as tk
import numpy as np

from Tile import Tile


class Tilemap(tk.Frame):
    def __init__(self, mother, X, Y, interact, fontsize, tileWidth=2, **kwargs):
        super().__init__(mother, **kwargs)
        self.tiles = np.empty((X,Y), dtype=np.object)
        for x in range(X):
            for y in range(Y):
                self.tiles[x,y] = Tile(self, interact=interact, width=tileWidth, height=1, font=f"calibri {fontsize} bold")
                self.tiles[x,y].grid(row=y, column=x)

    def get_tile_background_color(self, x, y):
        return self.tiles[x,y].cget("bg")

    def get_tile_text(self, x, y):
        return self.tiles[x,y].cget("text")

    def get_tile_arrival_reward(self, x, y):
        return self.tiles[x,y].get_arrival_reward()

    def update_tile_appearance(self, x, y, **kwargs):
        self.tiles[x,y].update_appearance(**kwargs)
