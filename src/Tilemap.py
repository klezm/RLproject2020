import tkinter as tk

from myFuncs import matrix
from Tile import Tile


class Tilemap(tk.Frame):
    fontDefault = "calibri 14 bold"
    displayWindDefault = False
    indicateNumericalValueChangeDefault = False
    tileWidthDefault = 2
    tileHeightDefault = 2
    tileBdDefault = 2

    def __init__(self, master, H, W, interactionAllowed, font=None, displayWind=None, indicateNumericalValueChange=None, tileWidth=None, tileHeight=None, tileBd=None, **kwargs):
        super().__init__(master, **kwargs)
        self.interactionAllowed = interactionAllowed
        self.windLabel: tk.Label = None  # Wind frames must be added later manually, because they need a master (namely this tilemap instance) for the ctor call
        self.tiles = matrix(H, W)

        bd = self.tileBdDefault if tileBd is None else tileBd
        labelWidth = self.tileWidthDefault if tileWidth is None else tileWidth
        labelHeight = self.tileHeightDefault if tileHeight is None else tileHeight
        font = self.fontDefault if font is None else font
        indicateNumericalValueChange = self.indicateNumericalValueChangeDefault if indicateNumericalValueChange is None else indicateNumericalValueChange
        displayWind = self.displayWindDefault if displayWind is None else displayWind
        for h in range(H):
            for w in range(W):
                self.tiles[h][w] = Tile(self, bd=bd, labelWidth=labelWidth, labelHeight=labelHeight, font=font, indicateNumericalValueChange=indicateNumericalValueChange)
                self.tiles[h][w].grid(row=h+displayWind, column=w+displayWind)

    def protect_text_and_color(self, h, w):
        self.tiles[h][w].protect_attributes("text", "fg")

    def unprotect_text_and_textColor(self, h, w):
        self.tiles[h][w].unprotect_attributes("text", "fg")

    def get_tile_background_color(self, h, w):
        return self.tiles[h][w].label.cget("bg")

    def get_tile_text(self, h, w):
        return self.tiles[h][w].label.cget("text")

    def get_tile_border_color(self, h, w):
        return self.tiles[h][w].cget("bg")

    def add_wind(self, hWindFrames, wWindFrames):
        for w, frame in enumerate(hWindFrames):
            frame.grid(row=0, column=w+1)
        for h, frame in enumerate(wWindFrames):
            frame.grid(row=h+1, column=0)
        self.windLabel = tk.Label(self, text="W.", font=hWindFrames[0].get_font())
        self.windLabel.grid(row=0, column=0)

    def set_windLabel_color(self, color):
        self.windLabel.config(fg=color)

    def update_tile_appearance(self, h, w, **kwargs):
        self.tiles[h][w].update_appearance(**kwargs)

    def reset(self):
        for tile in self.tiles.flatten():
            tile.reset()

    def set_interactionAllowed(self, value):
        self.interactionAllowed = value

    def get_yaml_list(self):
        return [[tile.get_yaml_dict() for tile in row] for row in self.tiles]
