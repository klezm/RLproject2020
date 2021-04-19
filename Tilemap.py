import tkinter as tk
import numpy as np

import worlds
from Tile import Tile


class Tilemap(tk.Frame):
    def __init__(self, master, X, Y, interactionAllowed, fontSize, indicateNumericalValueChange=False, tileWidth=2, height=2, anchor=tk.CENTER, **kwargs):
        super().__init__(master, **kwargs)
        self.interactionAllowed = interactionAllowed
        self.tiles = np.empty((X,Y), dtype = Tile)
        for x in range(X):
            for y in range(Y):
                self.tiles[x,y] = Tile(self, indicateNumericalValueChange=indicateNumericalValueChange,
                                       width=tileWidth, height=height, anchor=anchor, font=f"calibri {fontSize} bold")
                self.tiles[x,y].grid(row=y, column=x)
        # TODO: you have to click pixel perfect on the edge of the tilemap...
        self.bind("<Button-1>", lambda _: self.print_world())
        self.bind("<Button-2>", lambda _: self.cycle_maps())

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

    def reset_world(self):
        # np.vectorize(lambda x: x.update_appearance(**Tile.tileBlank))(self.tiles)
        for tl in self.tiles:
            for t in tl:
                t.update_appearance(**Tile.tileBlank)

    def print_world(self):
        def to_str(v):
            if txt := v.cget("text"):
                if txt == Tile.GOAL_CHAR:
                    txt = "G"
                elif txt == Tile.START_CHAR:
                    txt = "S"
                return txt
            if bg := v.cget("bg") == Tile.WALL_COLOR:
                return "#"
            else:
                return " "

        # world = np.vectorize(lambda x: x.cget("text"))(self.tiles)
        world = np.vectorize(to_str)(self.tiles)
        world = np.rot90(np.fliplr(world))
        print(*["-"*20]*2, sep = "\n")
        print(*["".join(x) for x in world.tolist()], sep = "\n")
        print(*["-"*20]*2, sep = "\n")

        # import json
        # with open("save_grid_world.json", "w") as f:
        #     json.dump(world, f)

    def cycle_maps(self, n: int = None):
        """
        prints the current map
        """
        self.print_world()
        if hasattr(self, "world_templates_c"):
            self.world_templates_c = (self.world_templates_c + 1) % len(worlds.grid_worlds)
            print(self.world_templates_c)
        else:
            self.world_templates_c = 0
        if n is not None:  # use the nth map
            self.world_templates_c = n - 1

        gworld = worlds.grid_worlds[self.world_templates_c]

        # # adjust lengths
        # gworld = gworld.split("\n")
        # max_len = max(map(len, gworld))
        # gworld = [[gworld[l][c] if c < len(gworld[l]) else " " for c in range(max_len)] for l in range(len(gworld))]
        tiles_len, tiles_width = self.tiles.shape
        # gworld = [[gworld[l][c] if c < len(gworld[l]) else " " for c in range(tiles_len)] for l in range(tiles_width)]
        # flip & rotate
        # gworld = np.rot90(np.fliplr(gworld))
        gworld = gworld[:tiles_width, :tiles_len]

        def map_value(v):
            if v in "#X-O0xo*":
                return Tile.tileWall
            elif v in "Ss🐭🐇🏎🐵👽👶":
                return Tile.tileStart
            elif v in "Gg🏁🧀🍌🪐🍭":
                return Tile.tileGoal
            else:  # if v == " ":
                return Tile.tileBlank

        self.reset_world()

        for i, ml in enumerate(gworld):
            for j, m in enumerate(ml):
                self.tiles[i, j].update_appearance(**map_value(m))

        # for ml, tl in zip(gworld, self.tiles):
        #     for m, t in zip(ml, tl):
        #         t.update_appearance(**map_value(m))
