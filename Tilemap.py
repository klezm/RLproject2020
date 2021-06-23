import tkinter as tk
import numpy as np
from functools import cache

from Tile import Tile


class Tilemap(tk.Frame):
    def __init__(self, master, X, Y, interactionAllowed, font="calibri 14 bold", displayWind=False, indicateNumericalValueChange=False, tileWidth=2, tileHeight=2, tileBd=2, **kwargs):
        super().__init__(master, **kwargs)
        self.interactionAllowed = interactionAllowed
        self.windLabel: tk.Label = None  # Wind frames must be added later manually, because they need a master (namely this tilemap instance) for the ctor call
        self.tiles = np.empty((X,Y), dtype=tk.Frame)
        for x in range(X):
            for y in range(Y):
                self.tiles[x,y] = Tile(self, bd=tileBd, labelWidth=tileWidth, labelHeight=tileHeight, font=font, indicateNumericalValueChange=indicateNumericalValueChange)
                self.tiles[x,y].grid(row=y+displayWind, column=x+displayWind)

    #@cache
    #def correct_coordinates(self, x, y):
    #    offset = int(bool(self.windLabel))
    #    return x + offset, y + offset

    def protect_text_and_color(self, x, y):
        self.tiles[x,y].protect_attributes("text", "fg")

    def unprotect_text_and_textColor(self, x, y):
        self.tiles[x,y].unprotect_attributes("text", "fg")

    def get_tile_background_color(self, x, y):
        return self.tiles[x,y].label.cget("bg")

    def get_tile_text(self, x, y):
        return self.tiles[x,y].label.cget("text")

    def get_tile_border_color(self, x, y):
        return self.tiles[x,y].cget("bg")

    def add_wind(self, xWindFrames, yWindFrames):
        for y, frame in enumerate(xWindFrames):
            frame.grid(row=y+1, column=0)
        for x, frame in enumerate(yWindFrames):
            frame.grid(row=0, column=x+1)
        self.windLabel = tk.Label(self, text="W.", font=xWindFrames[0].get_font())
        self.windLabel.grid(row=0, column=0)

    def set_windLabel_color(self, color):
        self.windLabel.config(fg=color)

    def update_tile_appearance(self, x, y, **kwargs):
        self.tiles[x,y].update_appearance(**kwargs)

    def reset(self):
        for tile in self.tiles.flatten():
            tile.reset()

    def set_interactionAllowed(self, value):
        self.interactionAllowed = value

    def get_yaml_list(self):
        return [[tile.get_yaml_dict() for tile in row] for row in self.tiles]
