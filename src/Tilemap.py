import tkinter as tk

from myFuncs import matrix, get_default_kwargs
from Tile import Tile


class Tilemap(tk.Frame):
    """This class inherits from ``tk.Frame`` and acts as a container for ``Tiles``.
    It provides a geometric representation of the underlying gridworld environment.
    """
    def __init__(self, master, H, W, interactionAllowed, *args, font=get_default_kwargs(Tile)["font"], displayWind=False, indicateNumericalValueChange=False, tileWidth=2, tileHeight=2, tileBd=2, **kwargs):
        """Creates a ``Tilemap`` object.

        :param master: Parent container.
        :param int H: Height of the environment in Cells. Cannot be changed afterwards.
        :param int W: Width  of the environment in Cells. Cannot be changed afterwards.
        :param bool interactionAllowed: if True, the user may change the appearance of the Tiles of this Tilemap by interacting with them. Can be changed afterwards.
        :param args: Additional arguments passed to the super().__init__ (tk.Frame)
        :param str font: tkinter font used for the text of the Tiles of this Tilemap
        :param bool displayWind: If True, changes the coordinates of all ``Tiles`` by +1/+1 to make the 0-th row/column a placeholder for wind strength EntryFrames for each column/row. Cannot be changed afterwards. The EntryFrames must be added afterwards using the add_wind method.
        :param bool indicateNumericalValueChange: If True, for each Tile, a number will be colored red if the previous Tile content was a bigger number and green if it was a smaller number.
        :param int tileWidth:   Width of the label inside each Tile.
        :param int tileHeight: Height of the label inside each Tile.
        :param int tileBd: Borderwidth of each Tile.
        :param kwargs: Additional keyword arguments passed to the super().__init__ (tk.Frame)
        """
        super().__init__(master, *args, **kwargs)
        self.interactionAllowed = interactionAllowed
        self.windLabel: tk.Label = None  # Wind frames must be added later manually, because they need a master (namely this tilemap instance) for the init call
        self.tiles = matrix(H, W)
        for h in range(H):
            for w in range(W):
                self.tiles[h][w] = Tile(self, bd=tileBd, labelWidth=tileWidth, labelHeight=tileHeight, font=font, indicateNumericalValueChange=indicateNumericalValueChange)
                self.tiles[h][w].grid(row=h+displayWind, column=w+displayWind)

    def protect_text_and_color(self, h, w):
        """Protect text and color of a ``Tile`` from being changed by its ``update_appearance`` method.

        :param int h: Height coordinate of the Tile
        :param int w: Width  coordinate of the Tile
        """
        self.tiles[h][w].protect_attributes("text", "fg")

    def unprotect_text_and_textColor(self, h, w):
        """Allows text and color of a ``Tile`` to be changed by its ``update_appearance`` method.

        :param int h: Height coordinate of the Tile
        :param int w: Width  coordinate of the Tile
        """
        self.tiles[h][w].unprotect_attributes("text", "fg")

    def get_tile_background_color(self, h, w):
        """Returns the ""bg"" of the ``tk.Label`` of a ``Tile``

        :param int h: Height coordinate of the Tile
        :param int w: Width  coordinate of the Tile
        :return str: tkinter color
        """
        return self.tiles[h][w].label.cget("bg")

    def get_tile_text(self, h, w):
        """Returns the "text" of the ``tk.Label`` of a ``Tile``

        :param int h: Height coordinate of the Tile
        :param int w: Width  coordinate of the Tile
        :return str: text
        """
        return self.tiles[h][w].label.cget("text")

    def get_tile_border_color(self, h, w):
        """Returns the "bg" of a ``Tile``

        :param int h: Height coordinate of the Tile
        :param int w: Width  coordinate of the Tile
        :return str: tkinter color
        """
        return self.tiles[h][w].cget("bg")

    def add_wind(self, hWindFrames, wWindFrames):
        """Fills the wind placeholders with given EntryFrames.
        Use only if this object was initialized with True displayWind argument.

        :param list[EntryFrame] hWindFrames: EntryFrames for the wind strengths in each column. Number must equal the environment WIDTH!
        :param list[EntryFrame] wWindFrames: EntryFrames for the wind strengths in each row. Number must equal the environment HEIGHT!
        """
        for w, frame in enumerate(hWindFrames):
            frame.grid(row=0, column=w+1)
        for h, frame in enumerate(wWindFrames):
            frame.grid(row=h+1, column=0)
        self.windLabel = tk.Label(self, text="W.", font=hWindFrames[0].get_font())
        self.windLabel.grid(row=0, column=0)

    def set_windLabel_color(self, color):
        """Sets the text "W." in (0,0) to a given color.
        Use only if this object was initialized with True displayWind argument.

        :param str color: tkinter color
        """
        self.windLabel.config(fg=color)

    def update_tile_appearance(self, h, w, **kwargs):
        """Updates the visual appearance of a ``Tile``.
        Keyword arguments that would change its protected attributes are ignored.
        If ``Tile.indicateNumericalChange`` is ``True``, also applies the appropriate
        textcolor change (keyword "fg"), unless its "fg" is protected.

        :param h: Height coordinate of the Tile
        :param w: Width  coordinate of the Tile
        :param kwargs: Keyword arguments that are passed to Tile.update_appearance.
        """
        self.tiles[h][w].update_appearance(**kwargs)

    def reset(self):
        """Restore the initial representation of all ``Tiles``.
        """
        for tile in self.tiles.flatten():
            tile.reset()

    def set_interactionAllowed(self, value):
        """Toggles if the user may change the appearance of the ``Tiles``
        of this ``Tilemap`` by interacting with them.

        :param bool value: True allows, False prohibits
        """
        self.interactionAllowed = value

    def get_yaml_list(self):
        """Returns a geometry-conserving matrix containing the representations
        of the ``Tiles`` of this ``Tilemap`` as yaml conform dictionaries.

        :return list[dict]: Tilemap data representation
        """
        return [[tile.get_yaml_dict() for tile in row] for row in self.tiles]
