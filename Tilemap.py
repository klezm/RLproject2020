import tkinter as tk
import numpy as np

from Tile import Tile
from NonEmptyIntVar import NonEmptyIntVar


class Tilemap(tk.Frame):
    def __init__(self, master, X, Y, interactionAllowed, font="calibri 14 bold", windFont="", indicateNumericalValueChange=False, tileWidth=2, tileHeight=2, tileBd=2, **kwargs):
        super().__init__(master, **kwargs)
        self.interactionAllowed = interactionAllowed
        self.displayWind = bool(windFont)
        self.tiles = np.empty(self.correct_coordinates(X,Y), dtype=tk.Frame)
        for x in range(X):
            for y in range(Y):
                xCorr, yCorr = self.correct_coordinates(x,y)
                self.tiles[xCorr,yCorr] = Tile(self, indicateNumericalValueChange=indicateNumericalValueChange,
                                               bd=tileBd, labelWidth=tileWidth, labelHeight=tileHeight, font=font)
                self.tiles[xCorr,yCorr].grid(row=yCorr, column=xCorr)
        if self.displayWind:
            self.xWindVars = [NonEmptyIntVar() for _ in range(Y)]
            self.yWindVars = [NonEmptyIntVar() for _ in range(X)]
            self.xWindEntries = [tk.Entry(self, textvariable=intVar, width=2, font=windFont) for intVar in self.xWindVars]
            self.yWindEntries = [tk.Entry(self, textvariable=intVar, width=2, font=windFont) for intVar in self.yWindVars]
            self.windLabel = tk.Label(self, text="W.", font=windFont)
            self.windLabel.grid(row=0, column=0)
            for y in range(Y):
                self.xWindEntries[y].grid(row=y+1, column=0)
                #self.xWindVars[y].trace_add("write", lambda _: self.toggle_crosswind_warning)
            for x in range(X):
                self.yWindEntries[x].grid(row=0, column=x+1)
                #elf.xWindVars[x].trace_add("write", lambda _: self.toggle_crosswind_warning)
            #self.toggle_crosswind_warning()

    def toggle_crosswind_warning(self):
        windLabelColor = "black"
        yWindAbsNonzeroValues = {abs(intVar.get()) for intVar in self.get_yWindVars() if intVar.get()}
        for xEntry, xVar in zip(self.get_xWindEntries(), self.get_xWindVars()):  # use indices
            if (not xVar.get()) or yWindAbsNonzeroValues in [set(), {abs(xVar.get())}]:
                xEntry.config(bg="white")
            else:
                xEntry.config(bg="orange")
                windLabelColor = "orange"
        xWindAbsNonzeroValues = {abs(intVar.get()) for intVar in self.get_xWindVars() if intVar.get()}
        for yEntry, yVar in zip(self.get_yWindEntries(), self.get_yWindVars()):  # use indices
            if (not yVar.get()) or xWindAbsNonzeroValues in [set(), {abs(yVar.get())}]:
                yEntry.config(bg="white")
            else:
                yEntry.config(bg="orange")
                windLabelColor = "orange"
        self.set_windLabel_color(windLabelColor)

    def correct_coordinates(self, x, y):
        offset = int(self.displayWind)
        return x + offset, y + offset

    def protect_text_and_color(self, x, y):
        self.tiles[self.correct_coordinates(x,y)].protect_attributes("text", "fg")

    def unprotect_text_and_textColor(self, x, y):
        self.tiles[self.correct_coordinates(x,y)].unprotect_attributes("text", "fg")

    def get_tile_background_color(self, x, y):
        return self.tiles[self.correct_coordinates(x,y)].label.cget("bg")

    def get_tile_text(self, x, y):
        return self.tiles[self.correct_coordinates(x,y)].label.cget("text")

    def get_tile_border_color(self, x, y):
        return self.tiles[self.correct_coordinates(x,y)].cget("bg")

    def get_xWindVars(self):
        return self.xWindVars

    def get_yWindVars(self):
        return self.yWindVars

    def get_xWindEntries(self):
        return self.xWindEntries

    def get_yWindEntries(self):
        return self.yWindEntries

    def set_windLabel_color(self, color):
        self.windLabel.config(fg=color)

    def update_tile_appearance(self, x, y, **kwargs):
        self.tiles[self.correct_coordinates(x,y)].update_appearance(**kwargs)

    def set_interactionAllowed(self, value):
        self.interactionAllowed = value

    def get_yaml_list(self):
        return [[tile.get_yaml_dict() for tile in row] for row in self.tiles[1:,1:]]
