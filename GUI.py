import tkinter as tk
import numpy as np

from Tile import Tile
from Tilemap import Tilemap


class GUI:
    def __init__(self, process, actionspace):
        self.process = process
        self.gwp = None
        self.lastAgentPosition = None
        self.X = 10  # TODO: read this in from GUI before Init
        self.Y = 10  # TODO: read this in from GUI before Init

        self.window = tk.Toplevel(self.process)
        self.window.title("Gridworld Playground")
        self.window.iconbitmap("./blank.ico")

        # window:
        self.gridworldFrame = Tilemap(self.window, X=self.X, Y=self.Y, interact=True, fontsize=14, bd=5, relief=tk.GROOVE)
        self.valueVisualizationFrame = tk.Frame(self.window, bd=5, relief=tk.GROOVE)
        self.buttonFrame = tk.Frame(self.window)

        self.gridworldFrame.grid(row=0, column=0)
        self.buttonFrame.grid(row=1, column=0)
        self.valueVisualizationFrame.grid(row=0, column=1)

        #   valueVisualizationFrame:
        colors = ["blue", "red", "green", "orange"]
        actionIndicatorColors = {action: color for action, color in zip(actionspace, colors)}
        valueTilemapsFontsize = 8
        self.qValueFrames = {}
        for action in actionspace:
            self.qValueFrames[action] = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interact=False,
                                                fontsize=valueTilemapsFontsize, bd=5, relief=tk.GROOVE, bg=actionIndicatorColors[action])
            self.qValueFrames[action].grid(row=action[1]+1, column=action[0]+1)
        self.greedyPolicyFrame = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interact=False,
                                         fontsize=valueTilemapsFontsize, bd=3, relief=tk.GROOVE)
        self.greedyPolicyFrame.grid(row=1, column=1)

        #   buttonFrame:
        self.startButton = tk.Button(self.buttonFrame, text="Go!", command=self.initialize_gwp)

        self.startButton.grid(row=0, column=0)

    def set_gwp(self, gwp):
        self.gwp = gwp

    def initialize_gwp(self):
        globalActionReward = -1  # TODO: read this in from GUI
        maxTimeSteps = 1000  # TODO: read this in from GUI
        msDelay = 100  # TODO: read this in from GUI
        showEveryNsteps = 1  # TODO: read this in from GUI
        environmentData = np.empty((self.X,self.Y), dtype=object)
        for x in range(self.X):
            for y in range(self.Y):
                environmentData[x,y] = {"position": (x,y),
                                        "isWall": self.gridworldFrame.tiles[x,y].cget("bg") == Tile.WALLCOLOR,
                                        "isStart": self.gridworldFrame.tiles[x,y].cget("text") == Tile.STARTLETTER,
                                        "isGoal": self.gridworldFrame.tiles[x,y].cget("text") == Tile.GOALLETTER,
                                        "arrivalReward": self.gridworldFrame.tiles[x,y].arrivalReward}
        data = {"environmentData": environmentData,
                "globalActionReward": globalActionReward,
                "maxTimeSteps":  maxTimeSteps,
                "msDelay": msDelay,
                "showEveryNsteps": showEveryNsteps}
        self.gwp.initialize(data)  # GUI gathers data, then calls initialize method of gwp. This should all GUIs do.

    def visualize(self, data):
        agentPosition = data["agentPosition"]
        if agentPosition != self.lastAgentPosition:
            if self.lastAgentPosition is not None:
                self.gridworldFrame.tiles[self.lastAgentPosition].update_appearance()
            self.gridworldFrame.tiles[agentPosition].update_appearance(bg=Tile.AGENTCOLOR)
            self.lastAgentPosition = agentPosition
