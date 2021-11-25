import tkinter as tk

from myFuncs import matrix, get_default_kwargs
from Tile import Tile


class Tilemap(tk.Frame):
    def __init__(self, master, H, W, interactionAllowed, font=get_default_kwargs(Tile)["font"], displayWind=False, indicateNumericalValueChange=False, tileWidth=2, tileHeight=2, tileBd=2, **kwargs):
        super().__init__(master, **kwargs)
        self.interactionAllowed = interactionAllowed
        self.windLabel: tk.Label = None  # Wind frames must be added later manually, because they need a master (namely this tilemap instance) for the init call
        self.tiles = matrix(H, W)
        for h in range(H):
            for w in range(W):
                self.tiles[h][w] = Tile(self, bd=tileBd, labelWidth=tileWidth, labelHeight=tileHeight, font=font, indicateNumericalValueChange=indicateNumericalValueChange)
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
