import tkinter as tk
import numpy as np
from collections import OrderedDict

from Tile import Tile
from Tilemap import Tilemap
from EntryFrame import EntryFrame
from CheckbuttonFrame import CheckbuttonFrame
from TypedStringVar import TypedStringVar

def center(window):
    # Centers a tkinter window. Function taken from stackoverflow.
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
        #configWindow.protocol("WM_DELETE_WINDOW", self.process.quit)
        dim1StringVar = TypedStringVar(int, value=9)
        dim2StringVar = TypedStringVar(int, value=9)
        font = "calibri 15 bold"
        tk.Label(configWindow, text="Gridworld Size:", font=font).grid(row=0, column=0, columnspan=2)
        tk.Label(configWindow, text="Dim 1:", font=font).grid(row=1, column=0)
        tk.Label(configWindow, text="Dim 2:", font=font).grid(row=2, column=0)
        tk.Entry(configWindow, textvariable=dim1StringVar, width=3, font=font).grid(row=1, column=1)
        tk.Entry(configWindow, textvariable=dim2StringVar, width=3, font=font).grid(row=2, column=1)
        tk.Button(configWindow, text="Ok", font=font, command=configWindow.destroy).grid(row=3, column=0, columnspan=2)
        center(configWindow)
        self.process.wait_window(configWindow)
        self.X = min(dim1StringVar.get(), dim2StringVar.get())
        self.Y = max(dim1StringVar.get(), dim2StringVar.get())

        valueTilemapsFontsize = 12
        valueTilemapsTilewidth = 4
        worldTilemapFontsize = 43

        self.window = tk.Toplevel(self.process)
        self.window.title("Gridworld Playground")
        self.window.iconbitmap("./blank.ico")
        self.window.protocol("WM_DELETE_WINDOW", self.process.quit)

        # window:
        self.gridworldFrame = Tilemap(self.window, X=self.X, Y=self.Y, interact=True, fontsize=worldTilemapFontsize, bd=5, relief=tk.GROOVE)
        self.valueVisualizationFrame = tk.Frame(self.window, bd=5, relief=tk.GROOVE)
        self.settingsFrame = tk.Frame(self.window, bd=5, relief=tk.GROOVE)

        self.gridworldFrame.grid(row=0, column=0)
        self.valueVisualizationFrame.grid(row=0, column=1)
        self.settingsFrame.grid(row=0, column=2)

        #   valueVisualizationFrame:
        self.qValueFrames = {}
        for action in actionspace:
            self.qValueFrames[action] = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interact=False,
                                                fontsize=valueTilemapsFontsize, tileWidth=valueTilemapsTilewidth,
                                                bd=5, relief=tk.GROOVE, bg=Tile.POLICY_COLORS[action])
            self.qValueFrames[action].grid(row=action[1]+1, column=action[0]+1)  # maps the Tilemaps corresponing to the actions (which are actually 2D "vectors")  to coordinates inside the valueVisualizationFrame
        self.greedyPolicyFrame = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interact=False,
                                         fontsize=valueTilemapsFontsize, tileWidth=valueTilemapsTilewidth,
                                         bd=3, relief=tk.GROOVE)
        self.greedyPolicyFrame.grid(row=1, column=1)

        #   settingsFrame:
        self.visualizationSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=tk.GROOVE)
        self.algorithmSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=tk.GROOVE)

        self.visualizationSettingsFrame.grid(row=0, column=0)
        self.algorithmSettingsFrame.grid(row=1, column=0)

        #self.parameterFrames = OrderedDict()
        #       visualizationSettingsFrame
        self.startPauseFrame = tk.Frame(self.visualizationSettingsFrame)
        self.timestepsLeftFrame = EntryFrame(self.visualizationSettingsFrame, text="Time Steps Left:", defaultValue=10000, targetType=int)
        self.msDelayFrame = EntryFrame(self.visualizationSettingsFrame, text="Refresh Delay [ms] >", defaultValue=1, targetType=int)
        self.showEveryNchangesFrame = EntryFrame(self.visualizationSettingsFrame, text="Show Every N Changes:", defaultValue=1, targetType=int)

        row = 0
        self.timestepsLeftFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.msDelayFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.showEveryNchangesFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.startPauseFrame.grid(row=row, column=0)
        row += 1

        #           startStopFrame:
        self.startButton = tk.Button(self.startPauseFrame, text="Go!", font=font, bd=5, command=self.initialize_gridworldPlayground)
        self.pauseButton = tk.Button(self.startPauseFrame, text="Pause", font=font, bd=5, command=lambda: None, fg="red")

        self.startButton.grid(row=0, column=0)
        self.pauseButton.grid(row=0, column=1)

        #       algorithmSettingsFrame

        self.xTorusFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="x-Torus:", defaultValue=False)
        self.yTorusFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="y-Torus:", defaultValue=False)
        self.globalActionRewardFrame = EntryFrame(self.algorithmSettingsFrame, text="Global Action Reward:", defaultValue=-1, targetType=float)
        self.discountFrame = EntryFrame(self.algorithmSettingsFrame, text="Discount \u03B3:", defaultValue=1, targetType=float)  # gamma
        self.learningRateFrame = EntryFrame(self.algorithmSettingsFrame, text="Learning Rate \u03B1:", defaultValue=0.1, targetType=float)  # alpha
        self.dynamicAlphaFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="\u03B1 = 1/count((S,A))", defaultValue=False)  # alpha
        self.nStepFrame = EntryFrame(self.algorithmSettingsFrame, text="n-Step n:", defaultValue=1, targetType=int)
        self.onPolicyFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="On-Policy:", defaultValue=True)
        self.epsilonFrame = EntryFrame(self.algorithmSettingsFrame, text="Exploration Rate \u03B5:", defaultValue=0.05, targetType=float)  # epsilon
        self.epsilonDecayFrame = EntryFrame(self.algorithmSettingsFrame, text="\u03B5-Decay Rate:", defaultValue=0.9999, targetType=float)  # epsilon

        row = 0
        self.xTorusFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.yTorusFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.globalActionRewardFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.discountFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.learningRateFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.dynamicAlphaFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.nStepFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.onPolicyFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.epsilonFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.epsilonDecayFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1

        self.lastAgentPosition = None

        center(self.window)

    def set_gridworldPlayground(self, gridworldPlayground):
        self.gridworldPlayground = gridworldPlayground

    def initialize_gridworldPlayground(self):
        self.initialize_value_visualization_frames()
        tileData = np.empty((self.X,self.Y), dtype=object)
        for x in range(self.X):
            for y in range(self.Y):
                tileType = self.gridworldFrame.get_tile_type(x,y)
                tileData[x,y] = {"position": (x,y),
                                 "isWall": tileType == Tile.tileWall,
                                 "isStart": tileType == Tile.tileStart,
                                 "isGoal": tileType == Tile.tileGoal,
                                 "arrivalReward": self.gridworldFrame.get_tile_arrival_reward(x, y)}
        data = {"tileData": tileData,
                "timestepsLeft": self.timestepsLeftFrame.get_var(),
                "msDelay": self.msDelayFrame.get_var(),
                "showEveryNchanges": self.showEveryNchangesFrame.get_var(),
                "Xtorus": self.xTorusFrame.get_var(),
                "Ytorus": self.yTorusFrame.get_var(),
                "globalActionReward": self.globalActionRewardFrame.get_var(),
                "discount": self.discountFrame.get_var(),
                "learningRate": self.learningRateFrame.get_var(),
                "dynamicAlpha": self.dynamicAlphaFrame.get_var(),
                "nStep": self.nStepFrame.get_var(),
                "onPolicy": self.onPolicyFrame.get_var(),
                "epsilon": self.epsilonFrame.get_var(),
                "epsilonDecayRate": self.epsilonDecayFrame.get_var()}
        self.gridworldPlayground.initialize(data)  # GUI gathers data, then calls initialize method of gridworldPlayground. This should all GUIs do.

    def initialize_value_visualization_frames(self):
        for x in range(self.X):
            for y in range(self.Y):
                tileType = self.gridworldFrame.get_tile_type(x, y)
                if tileType in [Tile.tileWall, Tile.tileGoal]:
                    for frame in [*self.qValueFrames.values(), self.greedyPolicyFrame]:
                        frame.update_tile_appearance(x, y, tileType=tileType)

    def visualize(self, data):
        # TODO: Qlearning doesnt update some tiles after a while. THATS THE POINT! Because its off-policy. This shows that it works! Great for presentation! Example with no walls and Start/Goal in the edges.
        agentPosition = data["agentPosition"]
        if agentPosition != self.lastAgentPosition:
            if self.lastAgentPosition is not None:  # reset tile of last position, if any
                self.gridworldFrame.update_tile_appearance(*self.lastAgentPosition)
        agentColor = Tile.AGENTCOLOR_EXPLORATORY if data["hasMadeExploratoryMove"] else Tile.AGENTCOLOR_DEFAULT
        self.gridworldFrame.update_tile_appearance(*agentPosition, bg=agentColor)
        self.lastAgentPosition = agentPosition
        greedyActions = data["greedyActions"]
        for x in range(self.X):
            for y in range(self.Y):
                if self.gridworldFrame.get_tile_type(x, y) in [Tile.tileWall, Tile.tileGoal]:
                    continue
                for action, Qvalue in data["Qvalues"][x,y].items():
                    self.qValueFrames[action].update_tile_appearance(x, y, text=f"{Qvalue:.2f}")
                if len(greedyActions[x,y]) == 1:
                    maxAction = greedyActions[x,y][0]
                else:
                    maxAction = None
                newTileType = Tile.tilePolicyTypes[maxAction]
                self.greedyPolicyFrame.update_tile_appearance(x, y, tileType=newTileType)

    def freeze_lifetime_parameters(self):
        self.dynamicAlphaFrame.freeze()
        if self.dynamicAlphaFrame.get_var().get():
            self.learningRateFrame.freeze()

    def unfreeze_lifetime_parameters(self):
        self.dynamicAlphaFrame.unfreeze()
        self.learningRateFrame.unfreeze()
