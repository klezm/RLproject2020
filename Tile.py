import collections
import tkinter as tk

from Agent import Agent

import numpy as np


class Tile(tk.Label):
    BLANK_COLOR = "white"
    WALL_COLOR = "black"
    LETTER_COLOR = "black"
    VALUE_INCREASE_COLOR = "green"
    VALUE_DECREASE_COLOR = "red"
    DEFAULT_RELIEF = tk.GROOVE
    START_CHAR = "🐇"  # 🐇🏎️🏎🏍️🏍  # 🐭🐀🐁  # 🐒🐵  # 👽  # 👶👧🧒👦  # ⚽️
    GOAL_CHAR = "🏁"  # 🏁  # 🧀  # 🍌  # 🪐🌌🌠  # 🍭🍧🍨🍦🥧🧁🍰🎂  # 🥅
    CHAR_CHOICES = ["🐇🏁", "🏎🏁", "🐭🧀", "🐵🍌", "👽🪐", "👶🍭"]
    START_CHAR, GOAL_CHAR = np.random.choice(CHAR_CHOICES)
    # START_CHAR, GOAL_CHAR = [x.encode("raw-unicode-escape").decode("utf8", "replace") for x in [START_CHAR, GOAL_CHAR]]
    # START_CHAR, GOAL_CHAR = [x.encode("raw-unicode-escape") for x in [START_CHAR, GOAL_CHAR]]
    # START_CHAR, GOAL_CHAR = [chr(ord(x)) for x in [START_CHAR, GOAL_CHAR]]
    AGENTCOLOR_DEFAULT_DEFAULT = "blue"
    AGENTCOLOR_DEFAULT_LIGHT = "#AAAAFF"  # light blue
    AGENTCOLOR_EXPLORATORY_DEFAULT = "red"
    AGENTCOLOR_EXPLORATORY_LIGHT = "#FFAAAA"  # light red
    AGENTCOLOR_PLANNING_DEFAULT = "green"
    AGENTCOLOR_PLANNING_LIGHT = "#AAFFAA"  # light green

    tileBlank = {"text": "", "fg": LETTER_COLOR, "bg": BLANK_COLOR}
    tileWall = {"text": "", "fg": LETTER_COLOR, "bg": WALL_COLOR}
    tileStart = {"text": START_CHAR, "fg": LETTER_COLOR, "bg": BLANK_COLOR}
    tileGoal = {"text": GOAL_CHAR, "fg": LETTER_COLOR, "bg": BLANK_COLOR}

    # 2 actions
    NW = (-1, -1)
    NE = ( 1, -1)
    SE = ( 1,  1)
    SW = (-1,  1)

    greedy12actions = np.array([["↖", "↑", "↗", None],
                                ["←",  "", "→", "⭤"],
                                ["↙", "↓", "↘", None],
                                [None, "⭥", None, None]])
    # greedy12actions = np.array([x.encode("raw-unicode-escape") if x is not None else x for x in greedy12actions.flatten()]).reshape(greedy12actions.shape)
    greedy12actions[:3, :3] = np.rot90(np.flipud(greedy12actions[:3, :3]), -1)

    # 3 actions
    NL = ( 1,  0)
    NR = (-1,  0)
    NU = ( 0,  1)
    ND = ( 0, -1)

    greedy34actions = np.array([[None, "┴", None],
                                ["┤",  "┼", "├"],
                                [None, "┬", None]])
    greedy34actions = np.rot90(np.flipud(greedy34actions), -1)

    # no zip for better readability
    POLICY_CHARS = {Agent.UP: "↑",     # ↑  \u2191
                    Agent.DOWN: "↓",   # ↓  \u2193
                    Agent.LEFT: "←",   # ←  \u2190
                    Agent.RIGHT: "→",  # →  \u2192

                    NW: "↖",  # "#00ffff"),  # ↖  # #00ffff
                    NE: "↗",  # "#FF00FF"),  # ↗  # #808080
                    SE: "↘",  # "#FFA38A"),  # ↘  # #ff8000 #ff5500
                    SW: "↙",  # "#D5FF00"),  # ↙  # #808000

                    "lr": "⭤",  # ),  # ⭤ \u2B64  # ↔  # ⇄ \u21C4
                    "ud": "⭥",  # ),  # ⭥ \u2B65  # ↕  # ⇅ \u21C5

                    # https://en.wikipedia.org/wiki/Box-drawing_character
                    "nl": "├",  # Tile.POLICY_COLORS[Agent.LEFT]),   # ├  # ┣ \u2523  # ⤨ \u2928  # not-left
                    "nr": "┤",  # Tile.POLICY_COLORS[Agent.RIGHT]),  # ┤  # ┫ \u252B  # ⤩ \u2929
                    "nu": "┬",  # Tile.POLICY_COLORS[Agent.UP]),     # ┬  # ┳ \u2533  # ⤪ \u292A
                    "nd": "┴",  # Tile.POLICY_COLORS[Agent.DOWN]),   # ┴  # ┻ \u253B  # ⤧ \u2927
                    "all": "┼",  # ),  # ┼  # ╋ \u254B
                    }

    # POLICY_COLORS = {}
    POLICY_COLORS = collections.defaultdict(lambda: "grey")
    # POLICY_COLORS.setdefault()
    POLICY_COLORS[None] = LETTER_COLOR
    POLICY_COLORS[""] = LETTER_COLOR
    POLICY_COLORS[" "] = LETTER_COLOR
    POLICY_COLORS[(0, 0)] = "grey"
    POLICY_COLORS[Agent.UP] = "#FFC800"  # (47,  100, 100)  # HSB triple and HEX
    POLICY_COLORS[Agent.RIGHT] = "#FF0000"  # (0,   100, 100)
    POLICY_COLORS[Agent.DOWN] = "#0016FF"  # (235, 100, 100)
    POLICY_COLORS[Agent.LEFT] = "#00FF48"  # (137, 100, 100)

    # 2 actions
    POLICY_COLORS[NE] = "#FFA100"  # (38,  100, 100)
    POLICY_COLORS[SE] = "#C000FF"  # (285, 100, 100)
    POLICY_COLORS[SW] = "#00DCFF"  # (188, 100, 100)
    # POLICY_COLORS[NW] = "#ADFF01"  # (79,  100, 100)
    POLICY_COLORS[NW] = "#D5FF00"  # (70,  100, 100)
    # POLICY_COLORS[NW] = "#FFF000"  # (57,  100, 100)

    POLICY_COLORS["lr"] = "grey"
    POLICY_COLORS[(1, 3)] = "grey"
    POLICY_COLORS["ud"] = "grey"
    POLICY_COLORS[(3, 1)] = "grey"

    # 3 actions (not left, etc)
    POLICY_COLORS["nl"] = POLICY_COLORS[Agent.RIGHT]
    POLICY_COLORS["nr"] = POLICY_COLORS[Agent.LEFT]
    POLICY_COLORS["nu"] = POLICY_COLORS[Agent.DOWN]
    POLICY_COLORS["nd"] = POLICY_COLORS[Agent.UP]

    # 4 actions
    POLICY_COLORS["all"] = "grey"

    # tilePolicyTypes = None  # No dict comp available here, so this will be assigned at end of file

    tileCycleTypes = [tileBlank, tileWall, tileStart, tileGoal]

    def __init__(self, master, indicateNumericalValueChange: bool, **kwargs):
        super().__init__(master, bd=1, relief=self.DEFAULT_RELIEF, **kwargs)
        self.arrivalReward = 0  # TODO: set this in GUI
        self.cycleIndex = 0
        self.protectedAttributes = set()
        self.bind("<Button-1>", lambda _: self.cycle_type(direction=1))
        self.bind("<Button-3>", lambda _: self.cycle_type(direction=-1))
        self.indicateNumericalValueChange = indicateNumericalValueChange
        self.update_appearance(**self.tileBlank)

    def protect_attributes(self, *args):
        self.protectedAttributes |= set(args)  # fancy new operator in python 3.9

    def unprotect_attributes(self, *args):
        self.protectedAttributes -= set(args)

    def get_arrivalReward(self):
        return self.arrivalReward

    def cycle_type(self, direction):
        if self.master.interactionAllowed:
            self.cycleIndex = (self.cycleIndex + direction) % len(self.tileCycleTypes)
            self.update_appearance(**self.tileCycleTypes[self.cycleIndex])

    def update_appearance(self, **kwargs):
        kwargs = {key: value for key, value in kwargs.items() if key not in self.protectedAttributes}
        if self.indicateNumericalValueChange and "fg" not in self.protectedAttributes:
            # TODO: Make the color proportional to relative value change
            try:
                oldValue = float(self.cget("text"))
                newValue = float(kwargs["text"])
                if newValue > oldValue:
                    kwargs["fg"] = self.VALUE_INCREASE_COLOR
                elif newValue < oldValue:
                    kwargs["fg"] = self.VALUE_DECREASE_COLOR
                else:
                    kwargs["fg"] = self.LETTER_COLOR
            except:
                kwargs["fg"] = self.LETTER_COLOR
        kwargs = {key: value for key, value in kwargs.items() if self.cget(key) != value}
        if kwargs:
            self.config(**kwargs)


Tile.tilePolicyTypes = {action: {"text": Tile.POLICY_CHARS[action],
                                 "fg": Tile.POLICY_COLORS[action]}
                        for action in Agent.ACTIONSPACE}
Tile.tilePolicyTypes[None] = {"text": "",
                              "fg": Tile.LETTER_COLOR}
