import tkinter as tk
import numpy as np
from collections import OrderedDict
from enum import IntEnum

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


class FlowStates(IntEnum):  # TODO: still needed?
    # Order matters, consequences of a state with ID = i are a subset of consequences of a state with ID = j>i, holds for all state pairs
    PASS = 0
    VISUALIZE = 1
    PAUSE = 2
    END = 3


class GUI:
    LABELFRAME_TEXTCOLOR = "blue"
    INITIAL_DIMSIZE = 9

    def __init__(self, process, agentActionspace, agentOperations):
        self.process = process
        self.gridworldPlayground = None

        self.agentOperations = agentOperations
        self.agentOperationCounts = None

        configWindow = tk.Toplevel(self.process)
        configWindow.title("Config")
        configWindow.iconbitmap("./blank.ico")
        #configWindow.protocol("WM_DELETE_WINDOW", self.process.quit)
        dim1StringVar = TypedStringVar(int, value=self.INITIAL_DIMSIZE)
        dim2StringVar = TypedStringVar(int, value=self.INITIAL_DIMSIZE)
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

        valueTilemapsFontsize = 10
        valueTilemapsTilewidth = 4
        worldTilemapFontsize = 43

        self.window = tk.Toplevel(self.process)
        self.window.title("Gridworld Playground")
        self.window.iconbitmap("./blank.ico")
        self.window.protocol("WM_DELETE_WINDOW", self.process.quit)

        # window:
        self.gridworldFrame = Tilemap(self.window, X=self.X, Y=self.Y, interactionAllowed=True, fontSize=worldTilemapFontsize, bd=5, height=1, relief=tk.GROOVE)
        self.valueVisualizationFrame = tk.Frame(self.window, bd=5, relief=tk.GROOVE)
        self.settingsFrame = tk.Frame(self.window, bd=5, relief=tk.GROOVE)

        self.gridworldFrame.grid(row=0, column=0)
        self.valueVisualizationFrame.grid(row=0, column=1)
        self.settingsFrame.grid(row=0, column=2)

        #   valueVisualizationFrame:
        self.qValueFrames = {}
        for action in agentActionspace:
            self.qValueFrames[action] = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interactionAllowed=False,
                                                indicateNumericalValueChange=True, fontSize=valueTilemapsFontsize,
                                                tileWidth=valueTilemapsTilewidth, bd=5, relief=tk.GROOVE,
                                                bg=Tile.POLICY_COLORS[action], anchor=tk.W)
            self.qValueFrames[action].grid(row=action[1]+1, column=action[0]+1)  # maps the Tilemaps corresponing to the actions (which are actually 2D "vectors")  to coordinates inside the valueVisualizationFrame
        self.greedyPolicyFrame = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interactionAllowed=False,
                                         indicateArbitraryValueChange=False, fontSize=valueTilemapsFontsize,
                                         tileWidth=valueTilemapsTilewidth, bd=3, relief=tk.GROOVE)
        self.greedyPolicyFrame.grid(row=1, column=1)

        #   settingsFrame:
        self.visualizationSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=tk.GROOVE)
        self.algorithmSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=tk.GROOVE)

        self.visualizationSettingsFrame.grid(row=0, column=0, ipadx=3, ipady=3, sticky=tk.W+tk.E)
        self.algorithmSettingsFrame.grid(row=1, column=0, ipadx=3, ipady=3, sticky=tk.W+tk.E)

        #       visualizationSettingsFrame
        self.operationsLeftFrame = EntryFrame(self.visualizationSettingsFrame, text="Operations Left:", defaultValue=100000, targetType=int)
        self.msDelayFrame = EntryFrame(self.visualizationSettingsFrame, text="Refresh Delay [ms] >", defaultValue=1000, targetType=int)
        self.flowButtonsFrame = tk.Frame(self.visualizationSettingsFrame)
        self.showEveryNoperationsFrame = EntryFrame(self.visualizationSettingsFrame, text="Show Every...", defaultValue=1, targetType=int)
        self.operationsPickFrame = tk.Frame(self.visualizationSettingsFrame)

        row = 0
        self.operationsLeftFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.msDelayFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.flowButtonsFrame.grid(row=row, column=0)
        row += 1
        self.showEveryNoperationsFrame.grid(row=row, column=0, sticky=tk.W + tk.E)
        row += 1
        self.operationsPickFrame.grid(row=row, column=0, sticky=tk.W + tk.E)

        self.showEveryNoperationsFrame.set_and_call_trace(self.reset_agentOperationCounts)

        #           flowButtonsFrame:
        # TODO: Freeze Pause und Next Buttons. Neee, Next soll auch in der Lage sein, die Gridworld zu initializen!
        self.goButton = tk.Button(self.flowButtonsFrame, text="Go!", font=font, bd=5, command=lambda: self.continue_flow(stopAtNextVisualization=False))
        self.pauseButton = tk.Button(self.flowButtonsFrame, text="Pause", font=font, bd=5, command=self.pause_flow, state=tk.DISABLED)
        self.nextButton = tk.Button(self.flowButtonsFrame, text="Next", font=font, bd=5, command=lambda: self.continue_flow(stopAtNextVisualization=True))

        self.goButton.grid(row=0, column=0)
        self.pauseButton.grid(row=0, column=1)
        self.nextButton.grid(row=0, column=2)

        #           operationsPickFrame
        self.operationFrames = OrderedDict([(operation, CheckbuttonFrame(self.operationsPickFrame, text=f"...{operation.value}", defaultValue=True)) for operation in self.agentOperations])
        self.relevantOperations = []
        for i, item in enumerate(self.operationFrames.items()):
            operation, frame = item
            frame.grid(row=i, column=0, sticky=tk.W + tk.E)
            frame.set_and_call_trace(lambda operation=operation: self.toggle_operation_relevance(operation))

        #       algorithmSettingsFrame
        self.xTorusFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="X-Torus:", defaultValue=False)
        self.yTorusFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="Y-Torus:", defaultValue=False)
        self.globalActionRewardFrame = EntryFrame(self.algorithmSettingsFrame, text="Global Action Reward:", defaultValue=-1, targetType=float)
        self.discountFrame = EntryFrame(self.algorithmSettingsFrame, text="Discount \u03B3:", defaultValue=1, targetType=float)  # gamma
        self.learningRateFrame = EntryFrame(self.algorithmSettingsFrame, text="Learning Rate \u03B1:", defaultValue=0.1, targetType=float)  # alpha
        self.dynamicAlphaFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="\u03B1 = 1/count((S,A))", defaultValue=False)  # alpha
        self.nStepFrame = EntryFrame(self.algorithmSettingsFrame, text="n-Step n:", defaultValue=1, targetType=int)
        self.onPolicyFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="On-Policy:", defaultValue=True)
        self.updateByExpectationFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="Update by Expectation", defaultValue=False)
        self.behaviorPolicyFrame = tk.LabelFrame(self.algorithmSettingsFrame, text="Behavior Policy", font=font, fg=self.LABELFRAME_TEXTCOLOR)
        self.targetPolicyFrame = tk.LabelFrame(self.algorithmSettingsFrame, text="Target Policy", font=font)

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
        self.updateByExpectationFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
        row += 1
        self.behaviorPolicyFrame.grid(row=row, column=0, sticky=tk.W+tk.E, ipadx=3)
        row += 1
        self.targetPolicyFrame.grid(row=row, column=0, sticky=tk.W+tk.E, ipadx=3)

        #           behaviorPolicyFrame
        self.behaviorEpsilonFrame = EntryFrame(self.behaviorPolicyFrame, text="Exploration Rate \u03B5:", defaultValue=0.5, targetType=float)  # epsilon
        self.behaviorEpsilonDecayRateFrame = EntryFrame(self.behaviorPolicyFrame, text="\u03B5-Decay Rate:", defaultValue=0.9999, targetType=float)  # epsilon

        self.behaviorEpsilonFrame.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.behaviorEpsilonDecayRateFrame.grid(row=1, column=0, sticky=tk.W + tk.E)

        #           targetPolicyFrame
        self.targetEpsilonFrame = EntryFrame(self.targetPolicyFrame, text="Exploration Rate \u03B5:", defaultValue=0, targetType=float)  # epsilon
        self.targetEpsilonDecayRateFrame = EntryFrame(self.targetPolicyFrame, text="\u03B5-Decay Rate:", defaultValue=1, targetType=float)  # epsilon

        self.targetEpsilonFrame.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.targetEpsilonDecayRateFrame.grid(row=1, column=0, sticky=tk.W + tk.E)

        self.onPolicyFrame.set_and_call_trace(self.toggle_targetPolicyFrame)
        self.lastAgentPosition = None
        self.runStarted = False
        self.stopAtNextVisualization = False
        self.runPaused = False
        self.flowStatus = FlowStates.PASS
        center(self.window)

        self.flag=True

    def toggle_operation_relevance(self, operation):
        #  This could also happen in check_flow_status in a similar way, but this way the stuff which must be computed at every check_flow_status call is minimized, since this function is only called after a checkbutton flip
        if self.operationFrames[operation].get_value():
            self.relevantOperations.append(operation)
        else:
            self.relevantOperations.remove(operation)
        self.reset_agentOperationCounts()

    def flow_iteration(self, latestAgentOperation):
        # TODO: 2 Cases überprüfen für fix: N = 1, großes N
        self.gridworldFrame.set_interactionAllowed(False)
        self.agentOperationCounts[latestAgentOperation] += 1  # TODO: are this and next line okay when PAUSE?
        self.operationsLeftFrame.set_value(self.operationsLeftFrame.get_value() - 1)
        if self.operationsLeftFrame.get_value() <= 0:
            self.unfreeze_lifetime_parameters()
            self.runStarted = False
            # TODO: Freeze Pause und Next Buttons. Neee, Next soll auch in der Lage sein, die Gridworld zu initializen!
            self.flowStatus = FlowStates.END
            self.gridworldFrame.set_interactionAllowed(True)
            return
        elif latestAgentOperation in self.relevantOperations:
            totalRelevantCount = 0
            for operation in self.relevantOperations:
                totalRelevantCount += self.agentOperationCounts[operation]
            if totalRelevantCount % self.showEveryNoperationsFrame.get_value() == 0:
                if self.stopAtNextVisualization:
                    self.pause_flow()  # also sets self.flowStatus = FlowStates.PAUSE
                    if latestAgentOperation == self.agentOperations.FINISHED_EPISODE:
                        # TODO: Hier noch andere dis-/enable maßnahmen
                        self.gridworldFrame.set_interactionAllowed(True)
                    return
                else:
                    self.flowStatus = FlowStates.VISUALIZE
                    return
            else:  # TODO: Elses können eigentlich weg für oneliner, der PASS setzt. zeile drüber return weg
                self.flowStatus = FlowStates.PASS
                return
        else:
            self.flowStatus = FlowStates.PASS
            return

    def pause_flow(self):
        self.flowStatus = FlowStates.PAUSE
        self.stopAtNextVisualization = False
        self.goButton.config(state=tk.NORMAL)
        self.pauseButton.config(state=tk.DISABLED)
        self.nextButton.config(state=tk.NORMAL)

    def continue_flow(self, stopAtNextVisualization):
        self.flowStatus = FlowStates.PASS
        self.stopAtNextVisualization = stopAtNextVisualization
        self.goButton.config(state=tk.DISABLED)
        self.pauseButton.config(state=tk.NORMAL)
        self.nextButton.config(state=tk.DISABLED)
        if not self.runStarted:
            self.runStarted = True
            self.initialize_gridworldPlayground()
        if self.gridworldFrame.interactionAllowed:
            self.update_gridworldPlayground_environment()
        self.gridworldPlayground.run()

    def set_gridworldPlayground(self, gridworldPlayground):
        self.gridworldPlayground = gridworldPlayground

    def update_gridworldPlayground_environment(self):
        tileData = np.empty((self.X,self.Y), dtype=object)
        valueVisualizationTilemaps = self.valueVisualizationFrame.winfo_children()
        for x in range(self.X):
            for y in range(self.Y):
                newText = self.gridworldFrame.get_tile_text(x,y)
                newBackground = self.gridworldFrame.get_tile_background_color(x, y)
                for tilemap in valueVisualizationTilemaps:
                    tilemap.unprotect_text_and_color(x,y)
                    if newText == Tile.GOAL_CHAR:
                        tilemap.update_tile_appearance(x, y, text=newText, fg=Tile.LETTER_COLOR)
                        tilemap.protect_text_and_color(x, y)
                    if newBackground == Tile.WALL_COLOR:
                        tilemap.update_tile_appearance(x, y, bg=Tile.WALL_COLOR)
                tileData[x,y] = {"position": (x,y),
                                 "isWall": newBackground == Tile.WALL_COLOR,
                                 "isStart": newText == Tile.START_CHAR,
                                 "isGoal": newText == Tile.GOAL_CHAR,
                                 "arrivalReward": self.gridworldFrame.get_tile_arrival_reward(x, y)}
        self.gridworldPlayground.update_environment(tileData)
        # TODO: Everytime a Tile is changed to an episode ender, change its Qvalues to 0 explicitly. NO! Agent cant know this beforehand, thats the point!

    def initialize_gridworldPlayground(self):
        #TODO: separate into "pure" initialization and recallable agent birth only. then we can seperate the tiledata dict from the data dict.
        data = {"shape": (self.X, self.Y),
                "operationsLeft": self.operationsLeftFrame.get_var(),
                "msDelay": self.msDelayFrame.get_var(),
                "showEveryNchanges": self.showEveryNoperationsFrame.get_var(),
                "Xtorus": self.xTorusFrame.get_var(),
                "Ytorus": self.yTorusFrame.get_var(),
                "globalActionReward": self.globalActionRewardFrame.get_var(),
                "discount": self.discountFrame.get_var(),
                "learningRate": self.learningRateFrame.get_var(),
                "dynamicAlpha": self.dynamicAlphaFrame.get_var(),
                "nStep": self.nStepFrame.get_var(),
                "onPolicy": self.onPolicyFrame.get_var(),
                "updateByExpectation": self.updateByExpectationFrame.get_var(),
                "behaviorEpsilon": self.behaviorEpsilonFrame.get_var(),
                "behaviorEpsilonDecayRate": self.behaviorEpsilonDecayRateFrame.get_var(),
                "targetEpsilon": self.targetEpsilonFrame.get_var(),
                "targetEpsilonDecayRate": self.targetEpsilonDecayRateFrame.get_var()}
        self.freeze_lifetime_parameters()
        self.gridworldPlayground.initialize(data)  # GUI gathers data, then calls initialize method of gridworldPlayground. This should all GUIs do.

    def reset_agentOperationCounts(self):
        self.agentOperationCounts = {operation: 0 for operation in self.agentOperations}

    def visualize(self, data):
        #print("vvvvvvvvvvvvvv begin vvvvvvvvvvvvvvvv")
        # TODO: Qlearning doesnt update some tiles after a while. THATS THE POINT! Because its off-policy. This shows that it works! Great for presentation! Example with no walls and Start/Goal in the edges.
        greedyActions = data["greedyActions"]
        for x in range(self.X):
            for y in range(self.Y):
                if self.gridworldFrame.get_tile_background_color(x, y) == Tile.WALL_COLOR:
                    continue
                gridworldFrameColor = Tile.BLANK_COLOR
                valueVisualizationFrameColor = Tile.BLANK_COLOR
                if (x,y) == data["agentPosition"]:
                    if data["hasMadeExploratoryMove"]:
                        gridworldFrameColor = Tile.AGENTCOLOR_EXPLORATORY_DEFAULT
                        valueVisualizationFrameColor = Tile.AGENTCOLOR_EXPLORATORY_LIGHT
                    else:
                        gridworldFrameColor = Tile.AGENTCOLOR_GREEDY_DEFAULT
                        valueVisualizationFrameColor = Tile.AGENTCOLOR_GREEDY_LIGHT
                self.gridworldFrame.update_tile_appearance(x,y, bg=gridworldFrameColor)
                for action, Qvalue in data["Qvalues"][x,y].items():
                    self.qValueFrames[action].update_tile_appearance(x, y, text=f"{Qvalue:+.3f}", bg=valueVisualizationFrameColor)
                if len(greedyActions[x,y]) == 1:
                    maxAction = greedyActions[x,y][0]
                else:
                    maxAction = None
                self.greedyPolicyFrame.update_tile_appearance(x, y, bg=valueVisualizationFrameColor, **Tile.tilePolicyTypes[maxAction])
        self.process.update_idletasks()
        #print("vvvvvvvvvvvvvv END vvvvvvvvvvvvvvvv")

    def freeze_lifetime_parameters(self):
        self.dynamicAlphaFrame.freeze()
        if self.dynamicAlphaFrame.get_var().get():
            self.learningRateFrame.freeze()

    def unfreeze_lifetime_parameters(self):
        self.dynamicAlphaFrame.unfreeze()
        self.learningRateFrame.unfreeze()

    def toggle_targetPolicyFrame(self):
        if self.onPolicyFrame.get_var().get():
            self.targetPolicyFrame.config(fg="grey")
            self.targetEpsilonFrame.freeze()
            self.targetEpsilonDecayRateFrame.freeze()
        else:
            self.targetPolicyFrame.config(fg=self.LABELFRAME_TEXTCOLOR)
            self.targetEpsilonFrame.unfreeze()
            self.targetEpsilonDecayRateFrame.unfreeze()
