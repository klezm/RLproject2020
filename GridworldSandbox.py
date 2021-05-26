import tkinter as tk
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt
from pprint import pprint

import myFuncs
from Environment import Environment
from Agent import Agent
from Tile import Tile
from Tilemap import Tilemap
from EntryFrame import EntryFrame
from CheckbuttonFrame import CheckbuttonFrame


class GridworldSandbox:
    LABELFRAME_TEXTCOLOR = "blue"
    VALUE_TILEMAPS_RELIEF_DEFAULT = tk.FLAT
    VALUE_TILEMAPS_RELIEF_TARGET_ACTION = tk.GROOVE
    SAFEFILE_FOLDER = "worldfiles"

    def __init__(self, guiProcess):
        # RL objects:
        self.environment = None
        self.agent = None

        # Flow control variables
        self.latestAgentOperation = None
        self.agentOperationCounts = None
        self.flowPaused = True
        self.stopAtNextVisualization = False

        # Setting up the GUI
        self.guiProcess = guiProcess
        initialWindowDict = myFuncs.get_dict_from_yaml_file("initialWindow")
        sizesDict = myFuncs.get_dict_from_yaml_file("sizes")
        fontQvalues = myFuncs.create_font(sizesDict["qvalues fontsize"])
        fontWorldtiles = myFuncs.create_font(sizesDict["worldtiles fontsize"])
        fontMiddle = myFuncs.create_font(sizesDict["fontsize middle"])
        fontBig = myFuncs.create_font(sizesDict["fontsize big"])

        if initialWindowDict["skip config window"]:
            guiScale = initialWindowDict["GUI Scale"]
            dim1 = initialWindowDict["Dim 1 Size"]
            dim2 = initialWindowDict["Dim 2 Size"]
            self.allow_kingMoves = initialWindowDict["King-Moves"]
        else:
            configWindow = tk.Toplevel(self.guiProcess, pady=5, padx=5)
            configWindow.title("Config")
            configWindow.iconbitmap("./blank.ico")

            scaleVar = tk.DoubleVar(value=initialWindowDict["GUI Scale"])
            tk.Scale(configWindow, label="GUI Scale:", variable=scaleVar, from_=1.0, to=1.5, resolution=0.05, font=fontMiddle, orient=tk.HORIZONTAL, width=15, sliderlength=20)
            dim1Frame = EntryFrame(configWindow, text="Dim 1 Size", font=fontMiddle, defaultValue=initialWindowDict["Dim 1 Size"], targetType=int, labelWidth=10, entryWidth=2)
            dim2Frame = EntryFrame(configWindow, text="Dim 2 Size", font=fontMiddle, defaultValue=initialWindowDict["Dim 2 Size"], targetType=int, labelWidth=10, entryWidth=2)
            kingMovesFrame = CheckbuttonFrame(configWindow, text="King-Moves", font=fontMiddle, defaultValue=initialWindowDict["King-Moves"], labelWidth=10)
            tk.Button(configWindow, text="Ok", height=1, font=fontBig, command=configWindow.destroy)

            myFuncs.arrange_children(configWindow, rowDiff=1)

            # configWindow.protocol("WM_DELETE_WINDOW", self.guiProcess.quit)
            myFuncs.center(configWindow)
            self.guiProcess.wait_window(configWindow)
            guiScale = scaleVar.get()
            dim1 = dim1Frame.get_value()
            dim2 = dim2Frame.get_value()
            self.allow_kingMoves = kingMovesFrame.get_value()
        self.guiProcess.call('tk', 'scaling', guiScale)
        self.X = min(dim1, dim2)
        self.Y = max(dim1, dim2)

        self.mainWindow = tk.Toplevel(self.guiProcess)
        self.mainWindow.title("Gridworld Playground")
        self.mainWindow.iconbitmap("./blank.ico")
        self.mainWindow.protocol("WM_DELETE_WINDOW", self.guiProcess.quit)

        # window:
        self.gridworldFrame = Tilemap(self.mainWindow, X=self.X, Y=self.Y, interactionAllowed=True, font=fontWorldtiles, relief=tk.GROOVE,
                                      bd=5, tileHeight=sizesDict["worldtiles height"], tileWidth=sizesDict["worldtiles width"], tileBd=sizesDict["worldtiles borderwidth"])
        self.valueVisualizationFrame = tk.Frame(self.mainWindow, bd=5, relief=tk.GROOVE)
        self.settingsFrame = tk.Frame(self.mainWindow, bd=5, relief=tk.GROOVE)

        myFuncs.arrange_children(self.mainWindow, columnDiff=1, useSticky=False)

        if True:  # valueVisualizationFrame:
            self.QVALUES_WIDTH = sizesDict["qvalues width"]
            self.qValueFrames = {}
            for action in (Agent.EXTENDED_ACTIONSPACE if self.allow_kingMoves else Agent.DEFAULT_ACTIONSPACE):
                self.qValueFrames[action] = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interactionAllowed=False,
                                                    indicateNumericalValueChange=True, font=fontQvalues, tileWidth=self.QVALUES_WIDTH,
                                                    bd=sizesDict["targetmarker width"], relief=self.VALUE_TILEMAPS_RELIEF_DEFAULT,
                                                    bg=Tile.direction_to_hsvHexString(action), tileHeight=sizesDict["qvalues height"], tileBd=sizesDict["qvalues borderwidth"])
                self.qValueFrames[action].grid(row=action[1]+1, column=action[0]+1)  # maps the Tilemaps corresponding to the actions (which are actually 2D "vectors")  to coordinates inside the valueVisualizationFrame
            self.greedyPolicyFrame = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interactionAllowed=False, font=fontQvalues,
                                             tileWidth=self.QVALUES_WIDTH, bd=sizesDict["targetmarker width"], tileHeight=sizesDict["qvalues height"], tileBd=sizesDict["qvalues borderwidth"], relief=tk.GROOVE)
            self.greedyPolicyFrame.grid(row=1, column=1)

        if True:  # settingsFrame:
            self.visualizationSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=tk.GROOVE)
            self.algorithmSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=tk.GROOVE)
            self.dataButtonsFrame = tk.Frame(self.settingsFrame)

            myFuncs.arrange_children(self.settingsFrame, rowDiff=1, ipadx=3, ipady=3)
            self.dataButtonsFrame.grid_configure(sticky="")

            if True:  # visualizationSettingsFrame
                self.initialActionvalueMeanFrame = EntryFrame(self.visualizationSettingsFrame, text="Initial Q-Values Mean", font=fontMiddle, targetType=float)
                self.initialActionvalueSigmaFrame = EntryFrame(self.visualizationSettingsFrame, text="Initial Q-Values Sigma", font=fontMiddle, targetType=float)
                self.operationsLeftFrame = EntryFrame(self.visualizationSettingsFrame, text="Operations Left", font=fontMiddle, targetType=int)
                self.msDelayFrame = EntryFrame(self.visualizationSettingsFrame, text="Min Refresh Rate [ms]", font=fontMiddle, targetType=int)
                self.visualizeMemoryFrame = CheckbuttonFrame(self.visualizationSettingsFrame, text="Visualize Memory", font=fontMiddle)
                self.flowButtonsFrame = tk.Frame(self.visualizationSettingsFrame)
                self.showEveryNoperationsFrame = EntryFrame(self.visualizationSettingsFrame, text="Show Every...", font=fontMiddle, targetType=int)
                self.operationFrames = OrderedDict([(operation, CheckbuttonFrame(self.visualizationSettingsFrame, text=f"...{operation}", font=fontMiddle)) for operation in Agent.OPERATIONS])

                myFuncs.arrange_children(self.visualizationSettingsFrame, rowDiff=1)
                self.flowButtonsFrame.grid_configure(sticky="")

                if True:  # flowButtonsFrame:
                    # pause is only hidden behind go because of the order of lines below. If this somehow fails, uncomment all lines that say "use this again if Pause appears over Go! when it shouldnt" as a comment
                    self.pauseButton = tk.Button(self.flowButtonsFrame, text="Pause", font=fontBig, bd=5, width=5, command=self.pause_flow)
                    self.goButton = tk.Button(self.flowButtonsFrame, text="Go!", font=fontBig, bd=5, width=5, command=lambda: self.start_flow(stopAtNextVisualization=False))
                    self.nextButton = tk.Button(self.flowButtonsFrame, text="Next", font=fontBig, bd=5, width=5, command=lambda: self.start_flow(stopAtNextVisualization=True))

                    self.goButton.grid(row=0, column=0)
                    self.pauseButton.grid(row=0, column=0)
                    #self.pauseButton.grid_remove()  # use this again if Pause appears over Go! when it shouldnt
                    self.nextButton.grid(row=0, column=1)

            if True:  # algorithmSettingsFrame
                self.iceFloorFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="Ice Floor", font=fontMiddle)
                self.xTorusFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="X-Torus", font=fontMiddle)
                self.yTorusFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="Y-Torus", font=fontMiddle)
                self.rewardFrames = OrderedDict([(color, EntryFrame(self.algorithmSettingsFrame, text=f"Reward {color.capitalize()}", entryColor=color, font=fontMiddle, targetType=int)) for color in Tile.BORDER_COLORS])
                self.discountFrame = EntryFrame(self.algorithmSettingsFrame, text="Discount \u03B3", font=fontMiddle, targetType=float)  # gamma
                self.learningRateFrame = EntryFrame(self.algorithmSettingsFrame, text="Learning Rate \u03B1", font=fontMiddle, targetType=float)  # alpha
                self.dynamicAlphaFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="\u03B1 = 1/count((S,A))", font=fontMiddle)  # alpha
                self.nStepFrame = EntryFrame(self.algorithmSettingsFrame, text="n-Step n", font=fontMiddle, targetType=int)
                self.nPlanFrame = EntryFrame(self.algorithmSettingsFrame, text="Dyna-Q n", font=fontMiddle, targetType=int)
                self.onPolicyFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="On-Policy", font=fontMiddle)
                self.updateByExpectationFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="Update by Expectation", font=fontMiddle)
                self.decayEpsilonEpisodeWiseFrame = CheckbuttonFrame(self.algorithmSettingsFrame, text="Decay \u03B5 Episode-wise", font=fontMiddle)
                self.behaviorPolicyFrame = tk.LabelFrame(self.algorithmSettingsFrame, text="Behavior Policy", bd=3, font=fontBig, fg=self.LABELFRAME_TEXTCOLOR)
                self.targetPolicyFrame = tk.LabelFrame(self.algorithmSettingsFrame, text="Target Policy", bd=3, font=fontBig)

                myFuncs.arrange_children(self.algorithmSettingsFrame, rowDiff=1)

                if True:  # behaviorPolicyFrame
                    self.behaviorEpsilonFrame = EntryFrame(self.behaviorPolicyFrame, text="Exploration Rate \u03B5 (b)", font=fontMiddle, targetType=float)  # epsilon
                    self.behaviorEpsilonDecayRateFrame = EntryFrame(self.behaviorPolicyFrame, text="\u03B5-Decay Rate (b)", font=fontMiddle, targetType=float)  # epsilon

                    myFuncs.arrange_children(self.behaviorPolicyFrame, rowDiff=1)

                if True:  # targetPolicyFrame
                    self.targetEpsilonFrame = EntryFrame(self.targetPolicyFrame, text="Exploration Rate \u03B5 (t)", font=fontMiddle, targetType=float)  # epsilon
                    self.targetEpsilonDecayRateFrame = EntryFrame(self.targetPolicyFrame, text="\u03B5-Decay Rate (t)", font=fontMiddle, targetType=float)  # epsilon

                    myFuncs.arrange_children(self.targetPolicyFrame, rowDiff=1)

            if True:  # dataButtonsFrame:
                self.loadButton = tk.Button(self.dataButtonsFrame, text="Load", font=fontBig, bd=5, width=5, command=self.load)
                self.saveButton = tk.Button(self.dataButtonsFrame, text="Save", font=fontBig, bd=5, width=5, command=self.save)

                myFuncs.arrange_children(self.dataButtonsFrame, columnDiff=1)

        self.parameterFramesVarsDict = self.recursiveGather_parameterFrameVars(self.mainWindow)
        self.load(f"{self.SAFEFILE_FOLDER}/{initialWindowDict['default configfile']}")

        self.relevantOperations = set()
        self.showEveryNoperationsFrame.set_and_call_trace(self.reset_agentOperationCounts)
        for operation, frame in(self.operationFrames.items()):
            frame.set_and_call_trace(lambda operation=operation: self.toggle_operation_relevance(operation))
        self.dynamicAlphaFrame.set_and_call_trace(self.toggle_alpha_freeze)
        self.onPolicyFrame.set_and_call_trace(self.toggle_targetPolicyFrame)
        self.onPolicyFrame.set_and_call_trace(self.toggle_offPolicy_nStep_warning)
        self.nStepFrame.set_and_call_trace(self.toggle_offPolicy_nStep_warning)

        myFuncs.center(self.mainWindow)

    def recursiveGather_parameterFrameVars(self, frame):
        collection = dict()
        for child in frame.winfo_children():
            try:
                collection[child.get_text()] = child.get_var()
            except:
                collection |= self.recursiveGather_parameterFrameVars(child)
        return collection

    def load(self, filename=None):
        yamlDict = myFuncs.get_dict_from_yaml_file(filename, initialdir=self.SAFEFILE_FOLDER)
        if yamlDict:
            for name, tkVar in self.parameterFramesVarsDict.items():
                tkVar.set(yamlDict[name])

    def save(self):
        valueDict = {name: tkVar.get() for name, tkVar in self.parameterFramesVarsDict.items()}
        myFuncs.create_yaml_file_from_dict(valueDict, initialdir=self.SAFEFILE_FOLDER)

    def initialize_environment_and_agent(self):
        self.environment = Environment(X=self.X, Y=self.Y, hasIceFloorVar=self.iceFloorFrame.get_var(),
                                       isXtorusVar=self.xTorusFrame.get_var(), isYtorusVar=self.yTorusFrame.get_var())
        # Agent needs an environment to exist, but environment doesnt need an agent
        self.agent = Agent(environment=self.environment, use_kingMoves=self.allow_kingMoves, learningRateVar=self.learningRateFrame.get_var(),
                           dynamicAlphaVar=self.dynamicAlphaFrame.get_var(),
                           discountVar=self.discountFrame.get_var(), nStepVar=self.nStepFrame.get_var(),
                           nPlanVar=self.nPlanFrame.get_var(), onPolicyVar=self.onPolicyFrame.get_var(),
                           updateByExpectationVar=self.updateByExpectationFrame.get_var(),
                           behaviorEpsilonVar=self.behaviorEpsilonFrame.get_var(),
                           behaviorEpsilonDecayRateVar=self.behaviorEpsilonDecayRateFrame.get_var(),
                           targetEpsilonVar=self.targetEpsilonFrame.get_var(),
                           targetEpsilonDecayRateVar=self.targetEpsilonDecayRateFrame.get_var(),
                           decayEpsilonEpisodeWiseVar=self.decayEpsilonEpisodeWiseFrame.get_var(),
                           initialActionvalueMean=self.initialActionvalueMeanFrame.get_value(),
                           initialActionvalueSigma=self.initialActionvalueSigmaFrame.get_value())

    def update_gridworldPlayground_environment(self):
        tileData = np.empty((self.X,self.Y), dtype=dict)
        valueVisualizationTilemaps = self.valueVisualizationFrame.winfo_children()
        for x in range(self.X):
            for y in range(self.Y):
                newText = self.gridworldFrame.get_tile_text(x,y)
                newBackground = self.gridworldFrame.get_tile_background_color(x, y)
                newBordercolor = self.gridworldFrame.get_tile_border_color(x, y)
                updateKwargs = {"fg": Tile.LETTER_COLOR, "borderColor": newBordercolor, "bg": newBackground}
                for tilemap in valueVisualizationTilemaps:
                    tilemap.unprotect_text_and_textColor(x, y)  # needed to set / remove Goalchar properly
                    if newText and newText[-1] in [Tile.GOAL_CHAR, Tile.TELEPORTER_SINK_ONLY_CHAR]:
                        tilemap.update_tile_appearance(x, y, text=newText, **updateKwargs)
                        tilemap.protect_text_and_color(x, y)
                    else:
                        tilemap.update_tile_appearance(x, y, **updateKwargs)
                arrivalRewardVarName = "Reward " + newBordercolor.capitalize()
                tileData[x,y] = {"position": (x,y),
                                 "isWall": newBackground == Tile.WALL_COLOR,
                                 "isStart": newText == Tile.START_CHAR,
                                 "isGoal": newText == Tile.GOAL_CHAR,
                                 "arrivalRewardVar": self.parameterFramesVarsDict[arrivalRewardVarName]}
        self.environment.update(tileData)
        # TODO: Everytime a Tile is changed to an episode terminator, change its Qvalues to 0 explicitly. NO! Agent cant know this beforehand, thats the point!

    def start_flow(self, stopAtNextVisualization):
        self.flowPaused = False
        self.stopAtNextVisualization = stopAtNextVisualization
        #self.pauseButton.grid()  # use this again if Pause appears over Go! when it shouldnt
        self.goButton.grid_remove()
        self.nextButton.config(state=tk.DISABLED)
        if self.agent is None:
            self.initialize_environment_and_agent()
            self.freeze_lifetime_parameters()
        if self.gridworldFrame.interactionAllowed:  # new episode is going to start
            self.gridworldFrame.set_interactionAllowed(False)
            self.freeze_episodetime_parameters()
            self.update_gridworldPlayground_environment()
        self.iterate_flow()

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
        self.latestAgentOperation = self.agent.operate()  # This is where all the RL-Stuff happens
        self.agentOperationCounts[self.latestAgentOperation] += 1
        self.operationsLeftFrame.set_value(self.operationsLeftFrame.get_value() - 1)
        if self.operationsLeftFrame.get_value() <= 0:
            if self.agent.get_episodeReturns():
                self.visualize()
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

    def pause_flow(self):
        self.flowPaused = True
        #self.stopAtNextVisualization = False
        self.goButton.grid()
        #self.pauseButton.grid_remove()  # use this again if Pause appears over Go! when it shouldnt
        self.nextButton.config(state=tk.NORMAL)
        if self.agent is None or self.latestAgentOperation == Agent.FINISHED_EPISODE or self.relevantOperations == {Agent.FINISHED_EPISODE}:
            # Last case catches if the pause button was clicked when only "Episode Finish" is a relevant operation BUT at the very moment the button was clicked, latestAgentOperation had a different value than "Episode Finish".
            # Not perfect, but should catch most situations where the map cannot be edited after the pause button was clicked although "Episode Finish" was the last operation before visualization.
            # First case is for safety (dunno if really needed)
            self.unfreeze_episodetime_parameters()
            self.gridworldFrame.set_interactionAllowed(True)

    def visualize(self):
        # TODO: Qlearning doesnt update some tiles after a while. THATS THE POINT! Because its off-policy. This shows that it works! Great for presentation! Example with no walls and Start/Goal in the edges.
        greedyActions: np.ndarray = self.agent.get_greedyActions()
        if self.visualizeMemoryFrame.get_value():
            agentcolorDefaultHue, agentcolorDefaultSaturation, agentcolorDefaultValue = myFuncs.rgbHexString_to_hsv(Tile.AGENTCOLOR_DEFAULT_LIGHT)
            traceCandidates = {state for state, _, _ in self.agent.get_memory()}
            traceTail = self.agent.get_memory().yield_lastForgottenState()
            memorySize = self.agent.get_memory_size() + int(bool(traceTail))
            if traceTail:
                traceCandidates.add(traceTail)

        for x in range(self.X):
            for y in range(self.Y):
                if self.gridworldFrame.get_tile_background_color(x, y) == Tile.WALL_COLOR:
                    continue
                gridworldFrame_Color = Tile.BLANK_COLOR
                valueVisualizationFrame_Color = Tile.BLANK_COLOR
                if self.visualizeMemoryFrame.get_value() and (x,y) in traceCandidates:
                    newSaturation = (0.75 - 0.4 * self.agent.get_absence((x,y)) / (memorySize+1)) * agentcolorDefaultSaturation
                    valueVisualizationFrame_Color = myFuncs.hsv_to_rgbHexString(agentcolorDefaultHue, newSaturation, agentcolorDefaultValue)
                if (x,y) == self.agent.get_state():
                    if self.latestAgentOperation == Agent.UPDATED_BY_PLANNING:
                        gridworldFrame_Color = Tile.AGENTCOLOR_PLANNING_DEFAULT
                        valueVisualizationFrame_Color = Tile.AGENTCOLOR_PLANNING_LIGHT
                    elif self.agent.hasMadeExploratoryMove:
                        gridworldFrame_Color = Tile.AGENTCOLOR_EXPLORATORY_DEFAULT
                        valueVisualizationFrame_Color = Tile.AGENTCOLOR_EXPLORATORY_LIGHT
                    else:
                        gridworldFrame_Color = Tile.AGENTCOLOR_DEFAULT_DEFAULT
                        valueVisualizationFrame_Color = Tile.AGENTCOLOR_DEFAULT_LIGHT
                self.gridworldFrame.update_tile_appearance(x, y, bg=gridworldFrame_Color)
                for action, Qvalue in self.agent.get_Qvalues()[x,y].items():
                    self.qValueFrames[action].update_tile_appearance(x, y, text=f"{Qvalue:< 3.2f}"[:self.QVALUES_WIDTH + 1], bg=valueVisualizationFrame_Color)

                greedyReprKwargs = Tile.get_greedy_actions_representation(tuple(greedyActions[x,y]))  # tuple cast because a cached function needs mutable args
                self.greedyPolicyFrame.update_tile_appearance(x, y, bg=valueVisualizationFrame_Color, **greedyReprKwargs)

        for action, tilemap in self.qValueFrames.items():
            if action == self.agent.get_targetAction():
                relief = self.VALUE_TILEMAPS_RELIEF_TARGET_ACTION
            else:
                relief = self.VALUE_TILEMAPS_RELIEF_DEFAULT
            if tilemap.cget("relief") != relief:  # pre-check gives huge speedup (also used in Tile class)
                tilemap.config(relief=relief)

        self.guiProcess.update_idletasks()

    def toggle_operation_relevance(self, operation):
        #  This could also happen in check_flow_status in a similar way, but this way the stuff which must be computed at every check_flow_status call is minimized, since this function is only called after a checkbutton flip
        if self.operationFrames[operation].get_value():
            self.relevantOperations.add(operation)
        else:
            try:
                self.relevantOperations.remove(operation)
            except:
                pass
        self.reset_agentOperationCounts()

    def reset_agentOperationCounts(self):
        self.agentOperationCounts = {operation: 0 for operation in Agent.OPERATIONS}

    def freeze_lifetime_parameters(self):
        self.dynamicAlphaFrame.freeze()
        self.initialActionvalueMeanFrame.freeze()
        self.initialActionvalueSigmaFrame.freeze()

    def unfreeze_lifetime_parameters(self):
        self.dynamicAlphaFrame.unfreeze()
        self.initialActionvalueMeanFrame.unfreeze()
        self.initialActionvalueSigmaFrame.unfreeze()

    def freeze_episodetime_parameters(self):
        self.discountFrame.freeze()
        self.loadButton.config(state=tk.DISABLED)
        self.saveButton.config(state=tk.DISABLED)

    def unfreeze_episodetime_parameters(self):
        self.discountFrame.unfreeze()
        self.loadButton.config(state=tk.NORMAL)
        self.saveButton.config(state=tk.NORMAL)

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
        # print("Episode returns of the agent:", self.agent.get_episodeReturns())
        fig, ax = plt.subplots()
        ax.plot(self.agent.get_episodeReturns())
        ax.set(xlabel='Episode', ylabel='Reward', title='Development of the Reward per Episode')
        ax.grid()
        fig.savefig("RewardDevelopement.png")
        plt.show()
