import tkinter as tk
import numpy as np

from Tile import Tile
from Tilemap import Tilemap

def center(window):
    #Centers a tkinter window. Function taken from stackoverflow.
    window.update_idletasks()  # For stability: Apply latest changes.
    # Now some magic to find the center of the visible screen, no matter what, and let the window center match that coordinates.
    width = window.winfo_width()
    frm_width = window.winfo_rootx() - window.winfo_x()
    window_width = width + 2 * frm_width
    height = window.winfo_height()
    titlebar_height = window.winfo_rooty() - window.winfo_y()
    window_height = height + titlebar_height + frm_width
    x = window.winfo_screenwidth() // 2 - window_width // 2
    y = window.winfo_screenheight() // 2 - window_height // 2
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))


class GUI:
    def __init__(self, process, actionspace):
        self.process = process
        self.gridworldPlayground = None

        configWindow = tk.Toplevel(self.process)
        configWindow.title("Config")
        configWindow.iconbitmap("./blank.ico")
        xStringVar = tk.StringVar(value=9)
        yStringVar = tk.StringVar(value=9)
        font = "calibri 15 bold"
        tk.Label(configWindow, text="Gridworld Size:", font=font).grid(row=0, column=0, columnspan=2)
        tk.Label(configWindow, text="Width:", font=font).grid(row=1, column=0)
        tk.Label(configWindow, text="Height:", font=font).grid(row=2, column=0)
        tk.Entry(configWindow, textvariable=xStringVar, width=3, font=font).grid(row=1, column=1)
        tk.Entry(configWindow, textvariable=yStringVar, width=3, font=font).grid(row=2, column=1)
        tk.Button(configWindow, text="Ok", font=font, command=configWindow.destroy).grid(row=3, column=0, columnspan=2)
        center(configWindow)
        self.process.wait_window(configWindow)
        self.X = int(xStringVar.get())
        self.Y = int(yStringVar.get())

        valueTilemapsFontsize = 12
        valueTilemapsTilewidth = 4
        worldTilemapFontsize = 43

        self.window = tk.Toplevel(self.process)
        self.window.title("Gridworld Playground")
        self.window.iconbitmap("./blank.ico")

        # window:
        self.gridworldFrame = Tilemap(self.window, X=self.X, Y=self.Y, interact=True, fontsize=worldTilemapFontsize, bd=5, relief=tk.GROOVE)
        self.valueVisualizationFrame = tk.Frame(self.window, bd=5, relief=tk.GROOVE)
        self.buttonFrame = tk.Frame(self.window)

        self.gridworldFrame.grid(row=0, column=0)
        self.buttonFrame.grid(row=1, column=0)
        self.valueVisualizationFrame.grid(row=0, column=1)

        #   valueVisualizationFrame:
        colors = ["blue", "red", "green", "orange"]
        self.actionIndicatorColors = {action: color for action, color in zip(actionspace, colors)}
        self.actionIndicatorColors[(0,0)] = "white"

        self.qValueFrames = {}
        for action in actionspace:
            self.qValueFrames[action] = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interact=False,
                                                fontsize=valueTilemapsFontsize, tileWidth=valueTilemapsTilewidth,
                                                bd=5, relief=tk.GROOVE, bg=self.actionIndicatorColors[action])
            self.qValueFrames[action].grid(row=action[1]+1, column=action[0]+1)  # maps the Tilemaps corresponing to the actions (which are actually 2D "vectors")  to coordinates inside the valueVisualizationFrame
        self.greedyPolicyFrame = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interact=False,
                                         fontsize=valueTilemapsFontsize, tileWidth=valueTilemapsTilewidth,
                                         bd=3, relief=tk.GROOVE)
        self.greedyPolicyFrame.grid(row=1, column=1)

        #   buttonFrame:
        self.startButton = tk.Button(self.buttonFrame, text="Go!", command=self.initialize_gridworldPlayground)

        self.startButton.grid(row=0, column=0)

        #center(self.window)

        self.lastAgentPosition = None

    def set_gridworldPlayground(self, gridworldPlayground):
        self.gridworldPlayground = gridworldPlayground

    def initialize_gridworldPlayground(self):
        globalActionReward = -1  # TODO: read this in from GUI
        maxTimeSteps = 1000000  # TODO: read this in from GUI
        msDelay = 1  # TODO: read this in from GUI
        showEveryNchanges = 1000  # TODO: read this in from GUI
        environmentData = np.empty((self.X,self.Y), dtype=object)
        for x in range(self.X):
            for y in range(self.Y):
                environmentData[x,y] = {"position": (x,y),
                                        "isWall": self.gridworldFrame.get_tile_background_color(x, y) == Tile.WALLCOLOR,
                                        "isStart": self.gridworldFrame.get_tile_text(x, y) == Tile.STARTLETTER,
                                        "isGoal": self.gridworldFrame.get_tile_text(x, y) == Tile.GOALLETTER,
                                        "arrivalReward": self.gridworldFrame.get_tile_arrival_reward(x, y)}
        data = {"environmentData": environmentData,
                "globalActionReward": globalActionReward,
                "maxTimeSteps": maxTimeSteps,
                "msDelay": msDelay,
                "showEveryNchanges": showEveryNchanges}
        self.gridworldPlayground.initialize(data)  # GUI gathers data, then calls initialize method of gridworldPlayground. This should all GUIs do.

    def visualize(self, data):
        agentPosition = data["agentPosition"]
        if agentPosition != self.lastAgentPosition:
            if self.lastAgentPosition is not None:
                self.gridworldFrame.update_tile_appearance(*self.lastAgentPosition)
            self.gridworldFrame.update_tile_appearance(*agentPosition, bg=Tile.AGENTCOLOR)
            self.lastAgentPosition = agentPosition
        Qvalues = data["Qvalues"]
        for x in range(self.X):
            for y in range(self.Y):
                maxValue = -1.e20
                maxAction = (0,0)
                for action, Qvalue in Qvalues[x,y].items():
                    if self.qValueFrames[action].get_tile_text(x, y) != str(Qvalue):
                        self.qValueFrames[action].update_tile_appearance(x, y, text=f"{Qvalue:.2f}")
                    if Qvalue == maxValue:
                        maxAction = (0,0)
                    elif Qvalue >= maxValue:
                        maxValue = Qvalue
                        maxAction = action
                newColor = self.actionIndicatorColors[maxAction]
                if self.greedyPolicyFrame.get_tile_text(x, y) != newColor:
                    self.greedyPolicyFrame.update_tile_appearance(x, y, bg=newColor)
