import tkinter as tk
import numpy as np

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

        #       visualizationSettingsFrame
        self.startPauseFrame = tk.Frame(self.visualizationSettingsFrame)
        self.timestepsLeftFrame = EntryFrame(self.visualizationSettingsFrame, "Time Steps Left:", 10000, int)
        self.refreshDelayFrame = EntryFrame(self.visualizationSettingsFrame, "Refresh Delay [ms] >", 1, int)
        self.showEveryNchangesFrame = EntryFrame(self.visualizationSettingsFrame, "Show Every N Changes:", 1, int)

        row = 0
        self.timestepsLeftFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.refreshDelayFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
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
        self.xTorusFrame = CheckbuttonFrame(self.algorithmSettingsFrame, "x-Torus:", False)
        self.yTorusFrame = CheckbuttonFrame(self.algorithmSettingsFrame, "y-Torus:", False)
        self.globalActionRewardFrame = EntryFrame(self.algorithmSettingsFrame, "Global Action Reward:", -1, float)
        self.discountFrame = EntryFrame(self.algorithmSettingsFrame, "Discount \u03B3:", 1, float)  # gamma
        self.learningRateFrame = EntryFrame(self.algorithmSettingsFrame, "Learning Rate \u03B1:", 0.1, float)  # alpha
        self.nStepFrame = EntryFrame(self.algorithmSettingsFrame, "n-Step n:", 1, int, textColor="red")
        self.onPolicyFrame = CheckbuttonFrame(self.algorithmSettingsFrame, "On-Policy:", True)
        self.epsilonFrame = EntryFrame(self.algorithmSettingsFrame, "Exploration Rate \u03B5:", 0.05, float)  # epsilon
        self.epsilonDecayFrame = EntryFrame(self.algorithmSettingsFrame, "\u03B5-Decay Rate:", 0.9999, float)  # epsilon

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
                tileData[x,y] = {"position": (x,y),
                                 "isWall": self.gridworldFrame.get_tile_type(x, y) == Tile.tileWall,
                                 "isStart": self.gridworldFrame.get_tile_type(x, y) == Tile.tileStart,
                                 "isGoal": self.gridworldFrame.get_tile_type(x, y) == Tile.tileGoal,
                                 "arrivalReward": self.gridworldFrame.get_tile_arrival_reward(x, y)}
        data = {"tileData": tileData,
                "timestepsLeft": self.timestepsLeftFrame.get_var(),
                "msDelay": self.refreshDelayFrame.get_var(),
                "showEveryNchanges": self.showEveryNchangesFrame.get_var(),
                "isXtorus": self.xTorusFrame.get_var(),
                "isYtorus": self.yTorusFrame.get_var(),
                "globalActionReward": self.globalActionRewardFrame.get_var(),
                "discount": self.discountFrame.get_var(),
                "learningRate": self.learningRateFrame.get_var(),
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
            agentColor = Tile.AGENTCOLOR_EXPLORATORY if data["madeExploratoryMove"] else Tile.AGENTCOLOR_DEFAULT
            self.gridworldFrame.update_tile_appearance(*agentPosition, bg=agentColor)
            self.lastAgentPosition = agentPosition
        for x in range(self.X):
            for y in range(self.Y):
                if self.gridworldFrame.get_tile_type(x, y) in [Tile.tileWall, Tile.tileGoal]:
                    continue
                maxValue = -1.e20
                maxAction = None
                for action, Qvalue in data["Qvalues"][x,y].items():
                    if self.qValueFrames[action].get_tile_text(x, y) != str(Qvalue):
                        self.qValueFrames[action].update_tile_appearance(x, y, text=f"{Qvalue:.2f}")
                    if Qvalue == maxValue:
                        maxAction = None
                    elif Qvalue >= maxValue:
                        maxValue = Qvalue
                        maxAction = action
                newTileType = Tile.tilePolicyTypes[maxAction]
                if self.greedyPolicyFrame.get_tile_type(x, y) != newTileType:
                    self.greedyPolicyFrame.update_tile_appearance(x, y, tileType=newTileType, )
