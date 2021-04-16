import tkinter as tk
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt

import myFuncs
from Environment import Environment
from Agent import Agent
from Tile import Tile
from Tilemap import Tilemap
from EntryFrame import EntryFrame
from CheckbuttonFrame import CheckbuttonFrame
from TypedStringVar import TypedStringVar


class GridworldSandbox:
    LABELFRAME_TEXTCOLOR = "blue"
    INITIAL_DIMSIZE = 9
    FONT = "calibri 15 bold"

    def __init__(self, guiProcess):
        self.environment = None
        self.agent = None
        self.latestAgentOperation = None
        self.agentOperationCounts = None
        self.flowPaused = True
        self.stopAtNextVisualization = False

        # Setting up the GUI

        self.guiProcess = guiProcess
        self.X, self.Y = self.ask_shape()
        
        valueTilemapsFontsize = 11
        valueTilemapsTileHeight = 1
        valueTilemapsTilewidth = 4
        worldTilemapFontsize = 43
        worldTilemapsTileHeight = 1

        self.window = tk.Toplevel(self.guiProcess)
        self.window.title("Gridworld Playground")
        self.window.iconbitmap("./blank.ico")
        self.window.protocol("WM_DELETE_WINDOW", self.guiProcess.quit)

        # window:
        self.gridworldFrame = Tilemap(self.window, X=self.X, Y=self.Y, interactionAllowed=True, fontSize=worldTilemapFontsize, bd=5, height=worldTilemapsTileHeight, relief=tk.GROOVE)
        self.valueVisualizationFrame = tk.Frame(self.window, bd=5, relief=tk.GROOVE)
        self.settingsFrame = tk.Frame(self.window, bd=5, relief=tk.GROOVE)

        self.gridworldFrame.grid(row=0, column=0)
        self.valueVisualizationFrame.grid(row=0, column=1)
        self.settingsFrame.grid(row=0, column=2)

        #   valueVisualizationFrame:
        self.qValueFrames = {}
        for action in Agent.ACTIONSPACE:
            self.qValueFrames[action] = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interactionAllowed=False,
                                                indicateNumericalValueChange=True, fontSize=valueTilemapsFontsize,
                                                tileWidth=valueTilemapsTilewidth, bd=5, relief=tk.GROOVE,
                                                bg=Tile.POLICY_COLORS[action], height=valueTilemapsTileHeight)
            self.qValueFrames[action].grid(row=action[1]+1, column=action[0]+1)  # maps the Tilemaps corresponding to the actions (which are actually 2D "vectors")  to coordinates inside the valueVisualizationFrame
        self.greedyPolicyFrame = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interactionAllowed=False, fontSize=valueTilemapsFontsize,
                                         tileWidth=valueTilemapsTilewidth, bd=3, height=valueTilemapsTileHeight, relief=tk.GROOVE)
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
        self.goButton = tk.Button(self.flowButtonsFrame, text="Go!", font=self.FONT, bd=5, command=lambda: self.start_flow(stopAtNextVisualization=False))
        self.pauseButton = tk.Button(self.flowButtonsFrame, text="Pause", font=self.FONT, bd=5, command=self.pause_flow, state=tk.DISABLED)
        self.nextButton = tk.Button(self.flowButtonsFrame, text="Next", font=self.FONT, bd=5, command=lambda: self.start_flow(stopAtNextVisualization=True))

        self.goButton.grid(row=0, column=0)
        self.pauseButton.grid(row=0, column=1)
        self.nextButton.grid(row=0, column=2)

        #           operationsPickFrame
        self.operationFrames = OrderedDict([(operation, CheckbuttonFrame(self.operationsPickFrame, text=f"...{operation}", defaultValue=True)) for operation in Agent.OPERATIONS])
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
        self.nPlanFrame = EntryFrame(self.algorithmSettingsFrame, text="Dyna-Q n:", defaultValue=0, targetType=int)
        self.onPolicyFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="On-Policy:", defaultValue=True)
        self.updateByExpectationFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="Update by Expectation", defaultValue=False)
        self.behaviorPolicyFrame = tk.LabelFrame(self.algorithmSettingsFrame, text="Behavior Policy", font=self.FONT, fg=self.LABELFRAME_TEXTCOLOR)
        self.targetPolicyFrame = tk.LabelFrame(self.algorithmSettingsFrame, text="Target Policy", font=self.FONT)

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
        self.nPlanFrame.grid(row=row, column=0, sticky=tk.W+tk.E)
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

        self.dynamicAlphaFrame.set_and_call_trace(self.toggle_alpha_freeze)
        self.onPolicyFrame.set_and_call_trace(self.toggle_targetPolicyFrame)
        self.onPolicyFrame.set_and_call_trace(self.toggle_offPolicy_nStep_warning)
        self.nStepFrame.set_and_call_trace(self.toggle_offPolicy_nStep_warning)
        myFuncs.center(self.window)

    def ask_shape(self):
        configWindow = tk.Toplevel(self.guiProcess)
        configWindow.title("Config")
        configWindow.iconbitmap("./blank.ico")
        #configWindow.protocol("WM_DELETE_WINDOW", self.guiProcess.quit)
        dim1StringVar = TypedStringVar(int, value=self.INITIAL_DIMSIZE)
        dim2StringVar = TypedStringVar(int, value=self.INITIAL_DIMSIZE)

        tk.Label(configWindow, text="Gridworld Size:", font=self.FONT).grid(row=0, column=0, columnspan=2)
        tk.Label(configWindow, text="Dim 1:", font=self.FONT).grid(row=1, column=0)
        tk.Label(configWindow, text="Dim 2:", font=self.FONT).grid(row=2, column=0)
        tk.Entry(configWindow, textvariable=dim1StringVar, width=3, font=self.FONT).grid(row=1, column=1)
        tk.Entry(configWindow, textvariable=dim2StringVar, width=3, font=self.FONT).grid(row=2, column=1)
        tk.Button(configWindow, text="Ok", font=self.FONT, command=configWindow.destroy).grid(row=3, column=0, columnspan=2)
        myFuncs.center(configWindow)
        self.guiProcess.wait_window(configWindow)
        X = min(dim1StringVar.get(), dim2StringVar.get())
        Y = max(dim1StringVar.get(), dim2StringVar.get())
        return X, Y
        
    def initialize_environment_and_agent(self):
        self.environment = Environment(X=self.X, Y=self.Y, isXtorusVar=self.xTorusFrame.get_var(),
                                       isYtorusVar=self.yTorusFrame.get_var(),
                                       globalActionRewardVar=self.globalActionRewardFrame.get_var(), )
        self.agent = Agent(environment=self.environment, learningRateVar=self.learningRateFrame.get_var(),
                           dynamicAlphaVar=self.dynamicAlphaFrame.get_var(),
                           discountVar=self.discountFrame.get_var(), nStepVar=self.nStepFrame.get_var(),
                           nPlanVar=self.nPlanFrame.get_var(), onPolicyVar=self.onPolicyFrame.get_var(),
                           updateByExpectationVar=self.updateByExpectationFrame.get_var(),
                           behaviorEpsilonVar=self.behaviorEpsilonFrame.get_var(),
                           behaviorEpsilonDecayRateVar=self.behaviorEpsilonDecayRateFrame.get_var(),
                           targetEpsilonVar=self.targetEpsilonFrame.get_var(),
                           targetEpsilonDecayRateVar=self.targetEpsilonDecayRateFrame.get_var())

    def update_gridworldPlayground_environment(self):
        tileData = np.empty((self.X,self.Y), dtype=object)
        valueVisualizationTilemaps = self.valueVisualizationFrame.winfo_children()
        for x in range(self.X):
            for y in range(self.Y):
                newText = self.gridworldFrame.get_tile_text(x,y)
                newBackground = self.gridworldFrame.get_tile_background_color(x, y)
                for tilemap in valueVisualizationTilemaps:
                    tilemap.unprotect_text_and_color(x,y)  # needed to set / remove Goalchar properly
                    if newText == Tile.GOAL_CHAR:
                        tilemap.update_tile_appearance(x, y, text=newText, fg=Tile.LETTER_COLOR)
                        tilemap.protect_text_and_color(x, y)
                    if newBackground == Tile.WALL_COLOR:
                        tilemap.update_tile_appearance(x, y, bg=Tile.WALL_COLOR, fg=Tile.LETTER_COLOR)
                tileData[x,y] = {"position": (x,y),
                                 "isWall": newBackground == Tile.WALL_COLOR,
                                 "isStart": newText == Tile.START_CHAR,
                                 "isGoal": newText == Tile.GOAL_CHAR,
                                 "arrivalReward": self.gridworldFrame.get_tile_arrival_reward(x, y)}
        self.environment.update(tileData)
        # TODO: Everytime a Tile is changed to an episode terminator, change its Qvalues to 0 explicitly. NO! Agent cant know this beforehand, thats the point!

    def iterate_flow(self):
        # Following condition is needed if the PAUSE State was set by pressing the Pause button, which will be resolved
        # as part of the after function, immediately before the recursive call.
        # The PAUSE should happen as soon as possible then, since the user wants to freeze what he sees at that time.
        # Without the following condition, another iteration would resolve before a return statement would be reached,
        # resulting in freezing after processing the subsequent state of the one that the user wanted to freeze instead.
        # (This would even happen if the flow_iteration call would be skipped completely.)
        if self.flowPaused:
            return
        next_msDelay = 0
        self.latestAgentOperation = self.agent.operate()
        self.agentOperationCounts[self.latestAgentOperation] += 1
        self.operationsLeftFrame.set_value(self.operationsLeftFrame.get_value() - 1)
        if self.operationsLeftFrame.get_value() <= 0:
            self.plot()
            del self.agent
            self.agent = None
            self.pause_flow()
            self.unfreeze_lifetime_parameters()
        elif self.latestAgentOperation in self.relevantOperations:
            totalRelevantCount = 0
            for operation in self.relevantOperations:
                totalRelevantCount += self.agentOperationCounts[operation]
            if totalRelevantCount % self.showEveryNoperationsFrame.get_value() == 0:
                self.visualize()
                next_msDelay = self.msDelayFrame.get_value()
                if self.stopAtNextVisualization:
                    self.pause_flow()
        # Following condition is needed if the PAUSE state was set in the flow_iteration method.
        # The Pause and the visualization, and especially disabling the Go and the Next button should happen
        # immediately after the processing.
        # Without the following condition, the user would have another next_msDelay amount of time to trigger
        # Next or Go again and therefore call this function again, which would cause undefined behavior.
        if self.flowPaused:
            return
        self.guiProcess.after(next_msDelay, self.iterate_flow)  # Queued GUI interactions will be resolved only during (?) the wait process of this call.

    def start_flow(self, stopAtNextVisualization):
        self.flowPaused = False
        self.stopAtNextVisualization = stopAtNextVisualization
        self.goButton.config(state=tk.DISABLED)
        self.pauseButton.config(state=tk.NORMAL)
        self.nextButton.config(state=tk.DISABLED)
        if self.agent is None:
            self.initialize_environment_and_agent()
            self.freeze_lifetime_parameters()
        if self.gridworldFrame.interactionAllowed:  # new episode is going to start
            self.gridworldFrame.set_interactionAllowed(False)
            self.freeze_episodetime_parameters()
            self.update_gridworldPlayground_environment()
        self.iterate_flow()

    def pause_flow(self):
        self.flowPaused = True
        self.stopAtNextVisualization = False
        self.goButton.config(state=tk.NORMAL)
        self.pauseButton.config(state=tk.DISABLED)
        self.nextButton.config(state=tk.NORMAL)
        if self.agent is None or self.latestAgentOperation == Agent.FINISHED_EPISODE:
            self.unfreeze_episodetime_parameters()
            self.gridworldFrame.set_interactionAllowed(True)

    def visualize(self):
        # TODO: Qlearning doesnt update some tiles after a while. THATS THE POINT! Because its off-policy. This shows that it works! Great for presentation! Example with no walls and Start/Goal in the edges.
        greedyActions = self.agent.get_greedyActions()
        for x in range(self.X):
            for y in range(self.Y):
                if self.gridworldFrame.get_tile_background_color(x, y) == Tile.WALL_COLOR:
                    continue
                gridworldFrameColor = Tile.BLANK_COLOR
                valueVisualizationFrameColor = Tile.BLANK_COLOR
                if (x,y) == self.agent.get_state():
                    if self.latestAgentOperation == Agent.UPDATED_BY_PLANNING:
                        gridworldFrameColor = Tile.AGENTCOLOR_PLANNING_DEFAULT
                        valueVisualizationFrameColor = Tile.AGENTCOLOR_PLANNING_LIGHT
                    elif self.agent.hasMadeExploratoryMove:
                        gridworldFrameColor = Tile.AGENTCOLOR_EXPLORATORY_DEFAULT
                        valueVisualizationFrameColor = Tile.AGENTCOLOR_EXPLORATORY_LIGHT
                    else:
                        gridworldFrameColor = Tile.AGENTCOLOR_DEFAULT_DEFAULT
                        valueVisualizationFrameColor = Tile.AGENTCOLOR_DEFAULT_LIGHT
                self.gridworldFrame.update_tile_appearance(x,y, bg=gridworldFrameColor)
                for action, Qvalue in self.agent.get_Qvalues()[x,y].items():
                    self.qValueFrames[action].update_tile_appearance(x, y, text=f"{Qvalue:< 3.2f}"[:5], bg=valueVisualizationFrameColor)
                if len(greedyActions[x,y]) == 1:
                    maxAction = greedyActions[x,y][0]
                else:
                    maxAction = None
                self.greedyPolicyFrame.update_tile_appearance(x, y, bg=valueVisualizationFrameColor, **Tile.tilePolicyTypes[maxAction])
        self.guiProcess.update_idletasks()

    def toggle_operation_relevance(self, operation):
        #  This could also happen in check_flow_status in a similar way, but this way the stuff which must be computed at every check_flow_status call is minimized, since this function is only called after a checkbutton flip
        if self.operationFrames[operation].get_value():
            self.relevantOperations.append(operation)
        else:
            self.relevantOperations.remove(operation)
        self.reset_agentOperationCounts()

    def reset_agentOperationCounts(self):
        self.agentOperationCounts = {operation: 0 for operation in Agent.OPERATIONS}

    def freeze_lifetime_parameters(self):
        self.dynamicAlphaFrame.freeze()

    def unfreeze_lifetime_parameters(self):
        self.dynamicAlphaFrame.unfreeze()

    def freeze_episodetime_parameters(self):
        self.discountFrame.freeze()

    def unfreeze_episodetime_parameters(self):
        self.discountFrame.unfreeze()

    def toggle_alpha_freeze(self):
        if self.dynamicAlphaFrame.get_value():
            self.learningRateFrame.freeze()
        else:
            self.learningRateFrame.unfreeze()

    def toggle_targetPolicyFrame(self):
        if self.onPolicyFrame.get_value():
            self.targetPolicyFrame.config(fg="grey")
            self.targetEpsilonFrame.freeze()
            self.targetEpsilonDecayRateFrame.freeze()
        else:
            self.targetPolicyFrame.config(fg=self.LABELFRAME_TEXTCOLOR)
            self.targetEpsilonFrame.unfreeze()
            self.targetEpsilonDecayRateFrame.unfreeze()
            
    def toggle_offPolicy_nStep_warning(self):
        if self.nStepFrame.get_value() > 1 and not self.onPolicyFrame.get_value():
            self.onPolicyFrame.set_color("red")
        else:
            self.onPolicyFrame.set_color("black")

    def plot(self):
        print(self.agent.get_episodeReturns())
        fig, ax = plt.subplots()
        ax.plot(self.agent.get_episodeReturns())
        ax.set(xlabel='Episode', ylabel='Reward', title='Development of the Reward per Episode')
        ax.grid()
        fig.savefig("RewardDevelopement.png")
        plt.show()
