import tkinter as tk
import numpy as np
from Tile import Tile


class GUI:
    def __init__(self, root):
        self.gwpg = None
        self.X = 8
        self.Y = 5
        self.window = tk.Toplevel(root)
        self.gridworldFrame = tk.Frame(self.window)
        self.gridworldFrame.grid(row=0, column=0)
        self.tiles = np.empty((self.X, self.Y), dtype=np.object)
        for x in range(self.X):
            for y in range(self.Y):
                self.tiles[x,y] = Tile(True, self.gridworldFrame, width=5, height=2)
                self.tiles[x,y].grid(row=y, column=x)
        self.buttonFrame = tk.Frame(self.window)
        self.buttonFrame.grid(row=1, column=0)
        self.startButton = tk.Button(self.buttonFrame, text="Go!", command=self.initialize)
        self.startButton.grid(row=0, column=0)
        self.lastAgentPosition = None

    def set_gwpg(self, gwpg):
        self.gwpg = gwpg

    def initialize(self):
        globalActionReward = -1  # TODO: read this in from GUI
        maxTimeSteps = 100  # TODO: read this in from GUI
        environmentData = np.empty_like(self.tiles)
        for x in range(self.X):
            for y in range(self.Y):
                environmentData[x,y] = {"position": (x,y),
                                        "isWall": self.tiles[x,y].cget("bg") == Tile.WALLCOLOR,
                                        "isStart": self.tiles[x,y].cget("text") == Tile.STARTLETTER,
                                        "isGoal": self.tiles[x,y].cget("text") == Tile.GOALLETTER,
                                        "arrivalReward": self.tiles[x,y].arrivalReward}
        data = {"environmentData": environmentData,
                "globalActionReward": globalActionReward,
                "maxTimeSteps":  maxTimeSteps}
        self.gwpg.initialize(data)  # GUI gathers data, then calls initialize method of gwpg. This should all GUIs do.

    def visualize(self, data):
        agentPosition = data["agentPosition"]
        if agentPosition != self.lastAgentPosition:
            if self.lastAgentPosition is not None:
                self.tiles[self.lastAgentPosition].update_appearance()
            self.tiles[agentPosition].update_appearance(bg=Tile.AGENTCOLOR)
            self.lastAgentPosition = agentPosition
