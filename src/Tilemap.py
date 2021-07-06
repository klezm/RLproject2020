import tkinter as tk
import numpy as np

from Tile import Tile


class Tilemap(tk.Frame):
    fontDefault = "calibri 14 bold"
    displayWindDefault = False
    indicateNumericalValueChangeDefault = False
    tileWidthDefault = 2
    tileHeightDefault = 2
    tileBdDefault = 2

    def __init__(self, master, X, Y, interactionAllowed, font=None, displayWind=None, indicateNumericalValueChange=None, tileWidth=None, tileHeight=None, tileBd=None, **kwargs):
        super().__init__(master, **kwargs)
        self.interactionAllowed = interactionAllowed
        self.windLabel: tk.Label = None  # Wind frames must be added later manually, because they need a master (namely this tilemap instance) for the ctor call
        self.tiles = np.empty((X,Y), dtype=tk.Frame)

        bd = self.tileBdDefault if tileBd is None else tileBd
        labelWidth = self.tileWidthDefault if tileWidth is None else tileWidth
        labelHeight = self.tileHeightDefault if tileHeight is None else tileHeight
        font = self.fontDefault if font is None else font
        indicateNumericalValueChange = self.indicateNumericalValueChangeDefault if indicateNumericalValueChange is None else indicateNumericalValueChange
        displayWind = self.displayWindDefault if displayWind is None else displayWind
        for x in range(X):
            for y in range(Y):
                self.tiles[x,y] = Tile(self, bd=bd, labelWidth=labelWidth, labelHeight=labelHeight, font=font, indicateNumericalValueChange=indicateNumericalValueChange)
                self.tiles[x,y].grid(row=y+displayWind, column=x+displayWind)

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
