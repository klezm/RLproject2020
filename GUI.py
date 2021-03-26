import tkinter as tk
import numpy as np

from Tile import Tile
from Tilemap import Tilemap
from EntryFrame import EntryFrame
from CheckbuttonFrame import CheckbuttonFrame

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
        self.window.protocol("WM_DELETE_WINDOW", self.process.quit)

        # window:
        self.gridworldFrame = Tilemap(self.window, X=self.X, Y=self.Y, interact=True, fontsize=worldTilemapFontsize, bd=5, relief=tk.GROOVE)
        self.valueVisualizationFrame = tk.Frame(self.window, bd=5, relief=tk.GROOVE)
        self.settingsFrame = tk.Frame(self.window, bd=5, relief=tk.GROOVE)

        self.gridworldFrame.grid(row=0, column=0)
        self.valueVisualizationFrame.grid(row=0, column=1)
        self.settingsFrame.grid(row=0, column=2)

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

        #   settingsFrame:
        self.visualizationSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=tk.GROOVE)
        self.algorithmSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=tk.GROOVE)

        self.visualizationSettingsFrame.grid(row=0, column=0)
        self.algorithmSettingsFrame.grid(row=1, column=0)

        #       visualizationSettingsFrame
        self.startStopFrame = tk.Frame(self.visualizationSettingsFrame)
        self.maxTimeStepsFrame = EntryFrame(self.visualizationSettingsFrame, "Max Time Steps:", 10000)
        self.refreshDelayFrame = EntryFrame(self.visualizationSettingsFrame, "Refresh Delay [ms] >", 1)
        self.showEveryNchangesFrame = EntryFrame(self.visualizationSettingsFrame, "Show Every N Changes:", 1)

        row = 0
        self.maxTimeStepsFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.refreshDelayFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.showEveryNchangesFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.startStopFrame.grid(row=row, column=0)
        row += 1

        #           startStopFrame:
        self.startButton = tk.Button(self.startStopFrame, text="Go!", font=font, bd=5, command=self.initialize_gridworldPlayground)
        self.stopButton = tk.Button(self.startStopFrame, text="Pause", font=font, bd=5, command=lambda: None)

        self.startButton.grid(row=0, column=0)
        self.stopButton.grid(row=0, column=1)

        #       algorithmSettingsFrame
        self.globalActionRewardFrame = EntryFrame(self.algorithmSettingsFrame, "Global Action Reward:", -1)
        self.discountFrame = EntryFrame(self.algorithmSettingsFrame, "Discount \u03B3:", 1)  # gamma
        self.stepsizeFrame = EntryFrame(self.algorithmSettingsFrame, "Stepsize \u03B1:", 0.1)  # alpha
        self.lambdaFrame = EntryFrame(self.algorithmSettingsFrame, "n-Step \u03BB:", 1)  # lambda
        self.onPolicyFrame = CheckbuttonFrame(self.algorithmSettingsFrame, "On-Policy:", True)
        self.epsilonFrame = EntryFrame(self.algorithmSettingsFrame, "Exploration Rate \u03B5:", 0.05)  # epsilon
        self.epsilonDecayFrame = EntryFrame(self.algorithmSettingsFrame, "\u03B5-Decay Rate:", 0.99)

        row = 0
        self.globalActionRewardFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.discountFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.stepsizeFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.lambdaFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
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
        globalActionReward = -1  # TODO: read this in from GUI
        environmentData = np.empty((self.X,self.Y), dtype=object)
        for x in range(self.X):
            for y in range(self.Y):
                environmentData[x,y] = {"position": (x,y),
                                        "isWall": self.gridworldFrame.get_tile_background_color(x, y) == Tile.WALLCOLOR,
                                        "isStart": self.gridworldFrame.get_tile_text(x, y) == Tile.STARTLETTER,
                                        "isGoal": self.gridworldFrame.get_tile_text(x, y) == Tile.GOALLETTER,
                                        "arrivalReward": self.gridworldFrame.get_tile_arrival_reward(x, y)}
        data = {"environmentData": environmentData,
                "maxTimeSteps": self.maxTimeStepsFrame.get_var(),
                "msDelay": self.refreshDelayFrame.get_var(),
                "showEveryNchanges": self.showEveryNchangesFrame.get_var(),
                "globalActionReward": self.globalActionRewardFrame.get_var(),
                "discount": self.discountFrame.get_var(),
                "stepsize": self.stepsizeFrame.get_var(),
                "lambda_": self.lambdaFrame.get_var(),
                "onPolicy": self.onPolicyFrame.get_var(),
                "epsilon": self.epsilonFrame.get_var(),
                "epsilonDecayRate": self.epsilonDecayFrame.get_var()}
        self.gridworldPlayground.initialize(data)  # GUI gathers data, then calls initialize method of gridworldPlayground. This should all GUIs do.

    def visualize(self, data):
        # TODO: Qlearning doesnt update some tiles after a while. THATS THE POINT! Because its off-policy. This shows that it works! Great for presentation! Example with no walls and Start/Goal in the edges.
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
