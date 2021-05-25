import tkinter as tk
import numpy as np

from Tile import Tile


class Tilemap(tk.Frame):
    def __init__(self, master, X, Y, interactionAllowed, font="calibri 14 bold", indicateNumericalValueChange=False, tileWidth=2, tileHeight=2, tileBd=2, **kwargs):
        super().__init__(master, **kwargs)
        self.interactionAllowed = interactionAllowed
        self.tiles = np.empty((X,Y), dtype=Tile)
        for x in range(X):
            for y in range(Y):
                self.tiles[x,y] = Tile(self, indicateNumericalValueChange=indicateNumericalValueChange,
                                       bd=tileBd, labelWidth=tileWidth, labelHeight=tileHeight, font=font)
                self.tiles[x,y].grid(row=y, column=x)

    def protect_text_and_color(self, x, y):
        self.tiles[x,y].protect_attributes("text", "fg")

    def unprotect_text_and_textColor(self, x, y):
        self.tiles[x,y].unprotect_attributes("text", "fg")

    def set_interactionAllowed(self, value):
        self.interactionAllowed = value

    def get_tile_background_color(self, x, y):
        return self.tiles[x,y].label.cget("bg") # todo: distinguish between frame bg and label bg!

    def get_tile_text(self, x, y):
        return self.tiles[x,y].label.cget("text")

    def get_tile_border_color(self, x, y):
        return self.tiles[x,y].cget("bg")

    def update_tile_appearance(self, x, y, **kwargs):
        self.tiles[x,y].update_appearance(**kwargs)
