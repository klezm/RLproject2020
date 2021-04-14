import tkinter as tk
import numpy as np

from Tile import Tile


class Tilemap(tk.Frame):
    def __init__(self, master, X, Y, interactionAllowed, fontSize, indicateNumericalValueChange=False, indicateArbitraryValueChange=False, tileWidth=2, height=2, anchor=tk.CENTER, **kwargs):
        super().__init__(master, **kwargs)
        self.interactionAllowed = interactionAllowed
        self.tiles = np.empty((X,Y), dtype=np.object)
        for x in range(X):
            for y in range(Y):
                self.tiles[x,y] = Tile(self, indicateNumericalValueChange=indicateNumericalValueChange,
                                       indicateArbitraryValueChange=indicateArbitraryValueChange,
                                       width=tileWidth, height=height, anchor=anchor, font=f"calibri {fontSize} bold")
                self.tiles[x,y].grid(row=y, column=x)

    def protect_text_and_color(self, x, y):
        self.tiles[x,y].protect_attributes("text", "fg")

    def unprotect_text_and_color(self, x, y):
        self.tiles[x,y].unprotect_attributes("text", "fg")

    def set_interactionAllowed(self, value):
        self.interactionAllowed = value

    def get_tile_background_color(self, x, y):
        return self.tiles[x,y].cget("bg")

    def get_tile_text(self, x, y):
        return self.tiles[x,y].cget("text")

    def get_tile_arrival_reward(self, x, y):
        return self.tiles[x,y].get_arrivalReward()

    def update_tile_appearance(self, x, y, **kwargs):
        self.tiles[x,y].update_appearance(**kwargs)
