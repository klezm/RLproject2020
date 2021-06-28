﻿import tkinter as tk
from tkinter import messagebox
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt
import os
from pprint import pprint

import myFuncs
from Environment import Environment
from src.Agent import Agent
from Tile import Tile
from Tilemap import Tilemap
from ParameterFrame import ParameterFrame
from EntryFrame import EntryFrame
from CheckbuttonFrame import CheckbuttonFrame
from InfoFrame import InfoFrame
from RadiomenuButtonFrame import RadiomenuButtonFrame


class GridworldSandbox:
    LABELFRAME_ENABLED_COLOR = "blue"
    LABELFRAME_DISABLED_COLOR = "grey"
    WARNING_COLOR = "red"
    VALUE_TILEMAPS_RELIEF_DEFAULT = tk.FLAT
    VALUE_TILEMAPS_RELIEF_TARGET_ACTION = tk.GROOVE
    GUI_FRAMES_RELIEF_DEFAULT = tk.GROOVE
    SAFEFILE_FOLDER = "worlds"
    ALGORITHMS_FOLDER = "algorithms"
    PLOTS_FOLDER = "plots"

    def __init__(self, guiProcess):
        myFuncs.print_default_values(RadiomenuButtonFrame)
        # RL objects:
        self.environment = None
        self.agent = None
        self.predefinedAlgorithms = {name.replace(".yaml", ""): myFuncs.get_dict_from_yaml_file(f"../{self.ALGORITHMS_FOLDER}/{name}")
                                     for name in os.listdir(f"../{self.ALGORITHMS_FOLDER}")}
        self.predefinedAlgorithms["Custom"] = dict()

        # Flow control variables
        self.latestAgentOperation = None
        self.agentOperationCounts = None
        self.demandPauseAtNextVisualization = False
        self.pauseDemanded = False

        # Setting up the GUI
        self.guiProcess = guiProcess
        initialWindowDict = myFuncs.get_dict_from_yaml_file("settings/initial")
        sizesDict = myFuncs.get_dict_from_yaml_file("settings/visual")

        fontQvalues = myFuncs.create_font(sizesDict["qvalues fontsize"])
        fontWorldtiles = myFuncs.create_font(sizesDict["worldtiles fontsize"])
        fontSmall = myFuncs.create_font(sizesDict["fontsize small"])
        fontMiddle = myFuncs.create_font(sizesDict["fontsize middle"])
        fontBig = myFuncs.create_font(sizesDict["fontsize big"])
        self.agentLightnessQvalueFrames = str(sizesDict["agent qValueTilemaps lightness"])
        self.minLightnessAgentTrace = sizesDict["agent trace min saturation rate"]
        self.maxLightnessAgentTrace = sizesDict["agent trace max saturation rate"]

        guiScale = initialWindowDict["GUI Scale"]
        dim1 = initialWindowDict["Dim 1 Size"]
        dim2 = initialWindowDict["Dim 2 Size"]
        self.allow_defaultActions = initialWindowDict["Default-Actions"]
        self.allow_kingActions = initialWindowDict["King-Actions"]
        self.allow_idleActions = initialWindowDict["Idle-Actions"]

        if not initialWindowDict["skip config window"]:
            configWindow = tk.Toplevel(self.guiProcess, pady=5, padx=5)
            configWindow.title("")
            configWindow.iconbitmap("../settings/icon.ico")

            scaleVar = tk.DoubleVar(value=guiScale)
            tk.Scale(configWindow, label="GUI Scale:", variable=scaleVar, from_=1.0, to=1.5, resolution=0.05, font=fontMiddle, orient=tk.HORIZONTAL, width=15, sliderlength=20)
            labelWidth = 15
            dim1Frame = EntryFrame(configWindow, nameLabel="Dim 1 Size", VarTargetType=int, var_check_func=lambda n: n >= 1, defaultValue=dim1, font=fontMiddle, labelWidth=labelWidth, promptWidth=3)
            dim2Frame = EntryFrame(configWindow, nameLabel="Dim 2 Size", VarTargetType=int, var_check_func=lambda n: n >= 1, defaultValue=dim2, font=fontMiddle, labelWidth=labelWidth, promptWidth=3)
            defaultActionsFrame = CheckbuttonFrame(configWindow, nameLabel="Default-Actions", font=fontMiddle, defaultValue=self.allow_defaultActions, labelWidth=labelWidth)
            kingActionsFrame = CheckbuttonFrame(configWindow, nameLabel="King-Actions", font=fontMiddle, defaultValue=self.allow_kingActions, labelWidth=labelWidth)
            idleActionsFrame = CheckbuttonFrame(configWindow, nameLabel="Idle-Actions", font=fontMiddle, defaultValue=self.allow_idleActions, labelWidth=labelWidth)
            tk.Button(configWindow, text="Proceed", height=1, font=fontBig, bd=5, command=configWindow.destroy)

            myFuncs.arrange_children(configWindow, order="row")

            # configWindow.protocol("WM_DELETE_WINDOW", self.guiProcess.quit)
            myFuncs.center(configWindow)
            self.guiProcess.wait_window(configWindow)
            guiScale = scaleVar.get()
            dim1 = dim1Frame.get_value()
            dim2 = dim2Frame.get_value()
            self.allow_defaultActions = defaultActionsFrame.get_value()
            self.allow_kingActions = kingActionsFrame.get_value()
            self.allow_idleActions = idleActionsFrame.get_value()
        self.guiProcess.call('tk', 'scaling', guiScale)
        self.X = max(dim1, dim2)
        self.Y = min(dim1, dim2)

        self.mainWindow = tk.Toplevel(self.guiProcess)
        self.mainWindow.title("Gridworld Sandbox")
        self.mainWindow.iconbitmap("../settings/icon.ico")
        self.mainWindow.protocol("WM_DELETE_WINDOW", self.guiProcess.quit)

        # mainWindow:
        self.settingsFrame = tk.Frame(self.mainWindow, bd=5, relief=self.GUI_FRAMES_RELIEF_DEFAULT)
        self.tilemapsFrame = tk.Frame(self.mainWindow, bd=5, relief=self.GUI_FRAMES_RELIEF_DEFAULT)

        myFuncs.arrange_children(self.mainWindow, order="row")

        if True:  # tilemapsFrame:
            self.gridworldTilemap = Tilemap(self.tilemapsFrame, X=self.X, Y=self.Y, interactionAllowed=True, font=fontWorldtiles, relief=self.GUI_FRAMES_RELIEF_DEFAULT, displayWind=True,
                                            bd=5, tileHeight=sizesDict["worldtiles height"], tileWidth=sizesDict["worldtiles width"], tileBd=sizesDict["worldtiles borderwidth"])
            self.valueVisualizationFrame = tk.Frame(self.tilemapsFrame, bd=5, relief=self.GUI_FRAMES_RELIEF_DEFAULT)

            myFuncs.arrange_children(self.tilemapsFrame, order="column", useSticky=False)

            if True:  # gridworldTilemap:
                self.xWindFrames = [EntryFrame(self.gridworldTilemap, font=fontMiddle, VarTargetType=int, promptWidth=2, promptHighlightthickness=4) for _ in range(self.Y)]
                self.yWindFrames = [EntryFrame(self.gridworldTilemap, font=fontMiddle, VarTargetType=int, promptWidth=2, promptHighlightthickness=4) for _ in range(self.X)]
                self.gridworldTilemap.add_wind(self.xWindFrames, self.yWindFrames)

            if True:  # valueVisualizationFrame:
                self.QVALUES_WIDTH = sizesDict["qvalues width"]
                self.qValueTilemaps = {}
                for action in Agent.create_actionspace(default=self.allow_defaultActions, king=self.allow_kingActions, idle=self.allow_idleActions):
                    self.qValueTilemaps[action] = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interactionAllowed=False,
                                                          indicateNumericalValueChange=True, font=fontQvalues, tileWidth=self.QVALUES_WIDTH,
                                                          bd=sizesDict["targetmarker width"], relief=self.VALUE_TILEMAPS_RELIEF_DEFAULT,
                                                          bg=Tile.direction_to_hsvHexString(action), tileHeight=sizesDict["qvalues height"], tileBd=sizesDict["qvalues borderwidth"])
                    self.qValueTilemaps[action].grid(row=action[1] + 1, column=action[0] + 1)  # maps the Tilemaps corresponding to the actions (which are actually 2D "vectors")  to coordinates inside the valueVisualizationFrame
                self.greedyPolicyTilemap = Tilemap(self.valueVisualizationFrame, X=self.X, Y=self.Y, interactionAllowed=False, font=fontQvalues,
                                                   tileWidth=self.QVALUES_WIDTH, bd=sizesDict["targetmarker width"], tileHeight=sizesDict["qvalues height"], tileBd=sizesDict["qvalues borderwidth"], relief=self.VALUE_TILEMAPS_RELIEF_TARGET_ACTION)
                self.greedyPolicyTilemap.grid(row=1, column=1)
                self.guiProcess.bind_all("<space>", lambda _: self.toggle_idleActionValues())
                self.idleActionValues_visible = False

        if True:  # settingsFrame:
            self.worldSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=self.GUI_FRAMES_RELIEF_DEFAULT)
            self.algorithmSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=self.GUI_FRAMES_RELIEF_DEFAULT)
            self.policySettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=self.GUI_FRAMES_RELIEF_DEFAULT)
            self.flowControlFrame = tk.Frame(self.settingsFrame, bd=3, relief=self.GUI_FRAMES_RELIEF_DEFAULT)
            self.miscSettingsFrame = tk.Frame(self.settingsFrame, bd=3, relief=self.GUI_FRAMES_RELIEF_DEFAULT)

            myFuncs.arrange_children(self.settingsFrame, order="column", ipadx=3, ipady=3)

            # Default values below are meaningless, since they will be read from the yaml default file later. One just needs to pass an arbitrary value here that passes the SafeVar check_func to avoid an error.

            if True:  # worldSettingsFrame
                self.iceFloorFrame = CheckbuttonFrame(self.worldSettingsFrame, nameLabel="Ice Floor", font=fontMiddle)
                self.xTorusFrame = CheckbuttonFrame(self.worldSettingsFrame, nameLabel="X-Torus", font=fontMiddle)
                self.yTorusFrame = CheckbuttonFrame(self.worldSettingsFrame, nameLabel="Y-Torus", font=fontMiddle)
                self.rewardFrames = OrderedDict([(color, EntryFrame(self.worldSettingsFrame, nameLabel=f"Reward {color.capitalize()}", promptFg=color, font=fontMiddle, VarTargetType=int)) for color in Tile.BORDER_COLORS])
                self.resetButton = tk.Button(self.worldSettingsFrame, text="Reset World", font=fontBig, bd=5, command=self.reset_gridworld)
                myFuncs.arrange_children(self.worldSettingsFrame, order="row")

            if True:  # algorithmSettingsFrame
                self.dynamicAlphaFrame = CheckbuttonFrame(self.algorithmSettingsFrame, nameLabel="α = 1/count((S,A))", font=fontMiddle)
                self.learningRateFrame = EntryFrame(self.algorithmSettingsFrame, nameLabel="Learning Rate α", font=fontMiddle, VarTargetType=float)
                self.discountFrame = EntryFrame(self.algorithmSettingsFrame, nameLabel="Discount γ", font=fontMiddle, VarTargetType=float)
                self.nStepFrame = EntryFrame(self.algorithmSettingsFrame, nameLabel="n-Step n", font=fontMiddle, VarTargetType=int, var_check_func=lambda x: x >= 0)
                self.nPlanFrame = EntryFrame(self.algorithmSettingsFrame, nameLabel="Dyna-Q n", font=fontMiddle, VarTargetType=int, labelWidth=8)
                self.expectationUpdateFrame = CheckbuttonFrame(self.algorithmSettingsFrame, nameLabel="Expectation Update", font=fontMiddle)
                self.predefinedAlgorithmFrame = RadiomenuButtonFrame(self.algorithmSettingsFrame, nameLabel="Algorithm", font=fontMiddle, choices=list(self.predefinedAlgorithms.keys()), promptFg="blue")

                myFuncs.arrange_children(self.algorithmSettingsFrame, order="row")

            if True:  # policySettingsFrame
                self.onPolicyFrame = CheckbuttonFrame(self.policySettingsFrame, nameLabel="On-Policy", font=fontMiddle)
                self.decayEpsilonEpisodeWiseFrame = CheckbuttonFrame(self.policySettingsFrame, nameLabel="Decay ε Episode-wise", font=fontMiddle)
                self.behaviorPolicyFrame = tk.LabelFrame(self.policySettingsFrame, text="Behavior Policy", bd=3, font=fontBig, fg=self.LABELFRAME_ENABLED_COLOR)
                self.targetPolicyFrame = tk.LabelFrame(self.policySettingsFrame, text="Target Policy", bd=3, font=fontBig)

                myFuncs.arrange_children(self.policySettingsFrame, order="row")

                if True:  # behaviorPolicyFrame
                    self.behaviorEpsilonFrame = EntryFrame(self.behaviorPolicyFrame, nameLabel="Exploration Rate ε", font=fontMiddle, VarTargetType=float, var_check_func=lambda x: x >= 0, trustSet=False)  # epsilon
                    self.behaviorEpsilonDecayRateFrame = EntryFrame(self.behaviorPolicyFrame, nameLabel="ε-Decay Rate", font=fontMiddle, VarTargetType=float, var_check_func=lambda x: x >= 0)  # epsilon

                    myFuncs.arrange_children(self.behaviorPolicyFrame, order="row")

                if True:  # targetPolicyFrame
                    self.targetEpsilonFrame = EntryFrame(self.targetPolicyFrame, nameLabel="Exploration Rate ε\u200C", font=fontMiddle, VarTargetType=float, var_check_func=lambda x: x >= 0, trustSet=False)  # epsilon
                    self.targetEpsilonDecayRateFrame = EntryFrame(self.targetPolicyFrame, nameLabel="ε-Decay Rate\u200C", font=fontMiddle, VarTargetType=float, var_check_func=lambda x: x >= 0)  # epsilon

                    myFuncs.arrange_children(self.targetPolicyFrame, order="row")

            if True:  # flowControlFrame
                self.showEveryNoperationsFrame = EntryFrame(self.flowControlFrame, nameLabel="Show Every...", font=fontMiddle, VarTargetType=int, var_check_func=lambda x: x >= 1, defaultValue=1)
                self.operationFrames = OrderedDict([(operation, CheckbuttonFrame(self.flowControlFrame, nameLabel=f"...{operation}", font=fontMiddle)) for operation in Agent.OPERATIONS])
                self.flowButtonsFrame = tk.Frame(self.flowControlFrame)

                myFuncs.arrange_children(self.flowControlFrame, order="row")
                self.flowButtonsFrame.grid_configure(sticky="")

                if True:  # flowButtonsFrame:
                    # pause is only hidden behind go because of the order of lines below. If this somehow fails, uncomment all lines that say "use this again if Pause appears over Go! when it shouldnt" as a comment
                    self.pauseButton = tk.Button(self.flowButtonsFrame, text="Pause", font=fontBig, bd=5, width=5, command=self.demand_pause)
                    self.goButton = tk.Button(self.flowButtonsFrame, text="Go!", font=fontBig, bd=5, width=5, command=lambda: self.start_flow(demandPauseAtNextVisualization=False))
                    self.nextButton = tk.Button(self.flowButtonsFrame, text="Next", font=fontBig, bd=5, width=5, command=lambda: self.start_flow(demandPauseAtNextVisualization=True))
                    self.goButton.grid(row=0, column=0)
                    self.pauseButton.grid(row=0, column=0)
                    # self.pauseButton.grid_remove()  # use this again if Pause appears over Go! when it shouldnt
                    self.nextButton.grid(row=0, column=1)

            if True:  # miscSettingsFrame:
                self.initialActionvalueMeanFrame = EntryFrame(self.miscSettingsFrame, nameLabel="Initial Q-Value Mean", font=fontMiddle, VarTargetType=float)
                self.initialActionvalueSigmaFrame = EntryFrame(self.miscSettingsFrame, nameLabel="Initial Q-Value Sigma", font=fontMiddle, VarTargetType=float, var_check_func=lambda x: x >= 0)
                self.currentReturnFrame = InfoFrame(self.miscSettingsFrame, nameLabel="Current Return", font=fontMiddle, VarTargetType=int, trustSet=False)
                self.operationsLeftFrame = EntryFrame(self.miscSettingsFrame, nameLabel="Operations Left", font=fontMiddle, VarTargetType=int, trustSet=False)
                self.minDelayFrame = EntryFrame(self.miscSettingsFrame, nameLabel="Min Delay [ms]", font=fontMiddle, VarTargetType=int, var_check_func=lambda x: 0 <= x <= 9999)
                self.visualizeMemoryFrame = CheckbuttonFrame(self.miscSettingsFrame, nameLabel="Visualize Memory", font=fontMiddle)
                self.dataButtonsFrame = tk.Frame(self.miscSettingsFrame)

                myFuncs.arrange_children(self.miscSettingsFrame, order="row")
                self.dataButtonsFrame.grid_configure(sticky="")  # this is a correction after the arrange_children() call, since the children of dataButtonsFrame should not be sticky

                if True:  # dataButtonsFrame:
                    self.loadButton = tk.Button(self.dataButtonsFrame, text="Load", font=fontBig, bd=5, width=5, command=self.load)
                    self.saveButton = tk.Button(self.dataButtonsFrame, text="Save", font=fontBig, bd=5, width=5, command=self.save)

                    myFuncs.arrange_children(self.dataButtonsFrame, order="column")  # this is a correction after the arrange_children() call, since the children of dataButtonsFrame should not be sticky

        self.parameterFramesDict = self.recursiveGather_namedInteractiveParameterFrames(self.mainWindow)
        pprint(self.parameterFramesDict)
        self.load(f"{self.SAFEFILE_FOLDER}/{initialWindowDict['default configfile']}")

        self.relevantOperations = set()
        self.showEveryNoperationsFrame.set_and_call_trace(self.reset_agentOperationCounts)
        for operation, frame in(self.operationFrames.items()):
            frame.set_and_call_trace(lambda operation=operation: self.toggle_operation_relevance(operation))
        self.dynamicAlphaFrame.set_and_call_trace(self.toggle_alpha_freeze)
        self.onPolicyFrame.set_and_call_trace(self.toggle_targetPolicyFrame)
        self.onPolicyFrame.set_and_call_trace(self.toggle_offPolicy_nStep_warning)
        self.nStepFrame.set_and_call_trace(self.toggle_offPolicy_nStep_warning)
        for frame in self.xWindFrames + self.yWindFrames:
            frame.set_and_call_trace(self.toggle_ice_and_crosswind_warning)
        self.iceFloorFrame.set_and_call_trace(self.toggle_ice_and_crosswind_warning)
        self.predefinedAlgorithmFrame.set_and_call_trace(self.toggle_algorithm)

        myFuncs.center(self.mainWindow)
        if self.allow_idleActions and initialWindowDict["show idle action warning"]:
            messagebox.showinfo("Idle Action Available", "You have chosen to include (0,0) in the agents actionspace.\nPress space to toggle the view between the Q-values of that action and the agents greedy choices.")

    def reset_gridworld(self):
        self.gridworldTilemap.reset()
        self.iceFloorFrame.set_value(False)
        self.xTorusFrame.set_value(False)
        self.yTorusFrame.set_value(False)
        for frame in self.xWindFrames + self.yWindFrames:
            frame.set_value(0)

    def toggle_idleActionValues(self):
        if self.allow_idleActions:
            if self.idleActionValues_visible:
                self.greedyPolicyTilemap.grid()
                self.qValueTilemaps[Agent.IDLE].grid_remove()
                self.idleActionValues_visible = False
            else:
                self.greedyPolicyTilemap.grid_remove()
                self.qValueTilemaps[Agent.IDLE].grid()
                self.idleActionValues_visible = True

    def recursiveGather_namedInteractiveParameterFrames(self, frame):
        collection = dict()
        for child in frame.winfo_children():
            if isinstance(child, ParameterFrame) and child.isInteractive and child.get_text():
                collection[child.get_text()] = child
            else:
                collection |= self.recursiveGather_namedInteractiveParameterFrames(child)
        return collection

    def load(self, filename=None):
        yamlDict = myFuncs.get_dict_from_yaml_file(filename, initialdir=self.SAFEFILE_FOLDER)
        if yamlDict:  # get_dict_from_yaml_file could have returned an empty Dict if dialog was canceled
            throwWorldShapeError = False
            tileDictMatrix = yamlDict.pop("world")
            if tileDictMatrix is not None:
                if len(tileDictMatrix) == self.X and len(tileDictMatrix[0]) == self.Y:
                    for x in range(self.X):
                        for y in range(self.Y):
                            self.gridworldTilemap.update_tile_appearance(x, y, **tileDictMatrix[x][y])
                else:
                    throwWorldShapeError = True
            xWindValues = yamlDict.pop("xWind")
            if xWindValues is not None:
                if len(xWindValues) == self.Y:
                    for frame, value in zip(self.xWindFrames, xWindValues):
                        frame.set_value(value)
                else:
                    throwWorldShapeError = True
            yWindValues = yamlDict.pop("yWind")
            if yWindValues is not None:
                if len(yWindValues) == self.X:
                    for frame, value in zip(self.yWindFrames, yWindValues):
                        frame.set_value(value)
                else:
                    throwWorldShapeError = True
            if throwWorldShapeError:
                messagebox.showerror("Error", "World shape does not match.")

            for name, frame in self.parameterFramesDict.items():  # must be executed only after world and wind was popped
                frame.set_value(yamlDict[name])

    def save(self, filename=None):
        valueDict = {name: frame.get_value() for name, frame in self.parameterFramesDict.items()}
        valueDict["world"] = self.gridworldTilemap.get_yaml_list()
        valueDict["xWind"] = [frame.get_value() for frame in self.xWindFrames]
        valueDict["yWind"] = [frame.get_value() for frame in self.yWindFrames]
        myFuncs.create_yaml_file_from_dict(valueDict, filename, nameEmbedding=f"{{}}_{self.X}x{self.Y}", initialdir=self.SAFEFILE_FOLDER)

    def initialize_environment_and_agent(self):
        self.environment = Environment(X=self.X,
                                       Y=self.Y,
                                       hasIceFloorVar=self.iceFloorFrame.get_variable(),
                                       isXtorusVar=self.xTorusFrame.get_variable(),
                                       isYtorusVar=self.yTorusFrame.get_variable(),
                                       xWindVars=[frame.get_variable() for frame in self.xWindFrames],
                                       yWindVars=[frame.get_variable() for frame in self.yWindFrames])
        # Agent needs an environment to exist, but environment doesnt need an agent to exist
        self.agent = Agent(environment=self.environment,
                           use_defaultActions=self.allow_defaultActions,
                           use_kingActions=self.allow_kingActions,
                           use_idleActions=self.allow_idleActions,
                           currentReturnVar=self.currentReturnFrame.get_variable(),
                           learningRateVar=self.learningRateFrame.get_variable(),
                           dynamicAlphaVar=self.dynamicAlphaFrame.get_variable(),
                           discountVar=self.discountFrame.get_variable(),
                           nStepVar=self.nStepFrame.get_variable(),
                           nPlanVar=self.nPlanFrame.get_variable(),
                           onPolicyVar=self.onPolicyFrame.get_variable(),
                           updateByExpectationVar=self.expectationUpdateFrame.get_variable(),
                           behaviorEpsilonVar=self.behaviorEpsilonFrame.get_variable(),
                           behaviorEpsilonDecayRateVar=self.behaviorEpsilonDecayRateFrame.get_variable(),
                           targetEpsilonVar=self.targetEpsilonFrame.get_variable(),
                           targetEpsilonDecayRateVar=self.targetEpsilonDecayRateFrame.get_variable(),
                           decayEpsilonEpisodeWiseVar=self.decayEpsilonEpisodeWiseFrame.get_variable(),
                           initialActionvalueMean=self.initialActionvalueMeanFrame.get_value(),
                           initialActionvalueSigma=self.initialActionvalueSigmaFrame.get_value())

    def update_environment(self):
        tileData = np.empty((self.X,self.Y), dtype=dict)
        valueVisualizationTilemaps = self.valueVisualizationFrame.winfo_children()
        for x in range(self.X):
            for y in range(self.Y):
                newText = self.gridworldTilemap.get_tile_text(x, y)
                newBackground = self.gridworldTilemap.get_tile_background_color(x, y)
                newBordercolor = self.gridworldTilemap.get_tile_border_color(x, y)
                updateKwargs = {"fg": Tile.LETTER_COLOR, "borderColor": newBordercolor, "bg": newBackground}
                for tilemap in valueVisualizationTilemaps:
                    tilemap.unprotect_text_and_textColor(x, y)  # needed to set / remove Goalchar properly
                    if newText and (newText[-1] in [Tile.GOAL_CHAR, Tile.TELEPORTER_SINK_ONLY_SUFFIX]):
                        tilemap.update_tile_appearance(x, y, text=newText, **updateKwargs)
                        tilemap.protect_text_and_color(x, y)
                    else:
                        tilemap.update_tile_appearance(x, y, **updateKwargs)
                teleportSource = None
                teleportSink = None
                if newText and newText[0] in Tile.TELEPORTERS:
                    if newText[1] != Tile.TELEPORTER_SINK_ONLY_SUFFIX:
                        teleportSource = newText[0]
                    if newText[1] != Tile.TELEPORTER_SOURCE_ONLY_SUFFIX:
                        teleportSink = newText[0]
                arrivalRewardVarName = "Reward " + newBordercolor.capitalize()
                tileData[x,y] = {"position": (x,y),
                                 "isWall": newBackground == Tile.WALL_COLOR,
                                 "isStart": newText == Tile.START_CHAR,
                                 "isGoal": newText == Tile.GOAL_CHAR,
                                 "arrivalRewardVar": self.parameterFramesDict[arrivalRewardVarName].get_variable(),
                                 "teleportSource": teleportSource,
                                 "teleportSink": teleportSink}
        self.environment.update(tileData)
        # TODO: Everytime a Tile is changed to an episode terminator, change its Qvalues to 0 explicitly. NO! Agent cant know this beforehand, thats the point!

    def start_flow(self, demandPauseAtNextVisualization):
        self.pauseDemanded = False
        self.demandPauseAtNextVisualization = demandPauseAtNextVisualization
        #self.pauseButton.grid()  # use this again if Pause appears over Go when it shouldnt
        self.goButton.grid_remove()
        self.nextButton.config(state=tk.DISABLED)
        if self.agent is None:
            self.initialize_environment_and_agent()
            self.freeze_lifetime_parameters()
        if self.gridworldTilemap.interactionAllowed:  # new episode is going to start
            self.gridworldTilemap.set_interactionAllowed(False)
            self.freeze_episodetime_parameters()
            self.update_environment()
        self.iterate_flow()

    def iterate_flow(self):
        if self.operationsLeftFrame.get_value() <= 0:
            self.apply_pause(end=True)
            return
        if self.pauseDemanded:
            if self.latestAgentOperation in self.relevantOperations:
                self.apply_pause()
                return
            else:  # User clicked too late! Refresh time was over and iterate flow was already running again in the background. Now wait for the next relevant operation and visualization to enter the block above.
                self.pauseDemanded = False
                self.demandPauseAtNextVisualization = True
        next_msDelay = 0
        self.latestAgentOperation = self.agent.operate()  # This is where all the RL-Stuff happens
        self.agentOperationCounts[self.latestAgentOperation] += 1
        self.operationsLeftFrame.set_value(self.operationsLeftFrame.get_value() - 1)
        if self.latestAgentOperation in self.relevantOperations:
            totalRelevantCount = 0
            for operation in self.relevantOperations:
                totalRelevantCount += self.agentOperationCounts[operation]
            if totalRelevantCount % self.showEveryNoperationsFrame.get_value() == 0:
                self.pauseDemanded = self.demandPauseAtNextVisualization
                self.visualize()
                next_msDelay = self.minDelayFrame.get_value()
        self.guiProcess.after(next_msDelay, self.iterate_flow)

    def demand_pause(self):
        self.pauseDemanded = True

    def apply_pause(self, end=False):
        self.pauseDemanded = False
        self.demandPauseAtNextVisualization = False
        self.goButton.grid()
        #self.pauseButton.grid_remove()  # use this again if Pause appears over Go! when it shouldnt
        self.nextButton.config(state=tk.NORMAL)
        if end:
            self.unfreeze_lifetime_parameters()
            self.visualize()
            self.plot()
            del self.agent
            self.agent = None
        if self.agent is None or self.latestAgentOperation == Agent.FINISHED_EPISODE:
            self.unfreeze_episodetime_parameters()
            self.gridworldTilemap.set_interactionAllowed(True)

    def visualize(self):
        # TODO: Qlearning doesnt update some tiles after a while. THATS THE POINT! Because its off-policy. This shows that it works! Great for presentation! Example with no walls and Start/Goal in the edges.
        if self.visualizeMemoryFrame.get_value():
            agentcolorDefaultHue, agentcolorDefaultSaturation, agentcolorDefaultValue = myFuncs.rgbHexString_to_hsv(myFuncs.get_light_color(Tile.AGENTCOLOR_DEFAULT, self.agentLightnessQvalueFrames))
            traceCandidates = {state for state, _, _ in self.agent.get_memory()}
            traceTail = self.agent.get_memory().yield_lastForgottenState()
            memorySize = self.agent.get_memory_size() + int(bool(traceTail))
            if traceTail:
                traceCandidates.add(traceTail)

        for x in range(self.X):
            for y in range(self.Y):
                if self.gridworldTilemap.get_tile_background_color(x, y) == Tile.WALL_COLOR:
                    continue
                gridworldFrame_Color = Tile.BLANK_COLOR
                valueVisualizationFrame_Color = Tile.BLANK_COLOR
                if self.visualizeMemoryFrame.get_value() and (x,y) in traceCandidates:
                    newSaturation = (self.maxLightnessAgentTrace - self.minLightnessAgentTrace * self.agent.get_absence((x,y)) / (memorySize+1)) * agentcolorDefaultSaturation
                    valueVisualizationFrame_Color = myFuncs.hsv_to_rgbHexString(agentcolorDefaultHue, newSaturation, agentcolorDefaultValue)
                if (x,y) == self.agent.get_state():
                    if self.operationsLeftFrame.get_value() <= 0:
                        gridworldFrame_Color = Tile.AGENTCOLOR_DEAD
                        valueVisualizationFrame_Color = Tile.AGENTCOLOR_DEAD
                    elif self.latestAgentOperation == Agent.UPDATED_BY_PLANNING:
                        gridworldFrame_Color = Tile.AGENTCOLOR_PLANNING
                        valueVisualizationFrame_Color = myFuncs.get_light_color(Tile.AGENTCOLOR_PLANNING, self.agentLightnessQvalueFrames)
                    elif self.agent.hasMadeExploratoryAction:
                        gridworldFrame_Color = Tile.AGENTCOLOR_EXPLORATORY
                        valueVisualizationFrame_Color = myFuncs.get_light_color(Tile.AGENTCOLOR_EXPLORATORY, self.agentLightnessQvalueFrames)
                    else:
                        gridworldFrame_Color = Tile.AGENTCOLOR_DEFAULT
                        valueVisualizationFrame_Color = myFuncs.get_light_color(Tile.AGENTCOLOR_DEFAULT, self.agentLightnessQvalueFrames)
                elif (x,y) == self.environment.get_teleportJustUsed():
                    gridworldFrame_Color = Tile.TELEPORT_JUST_USED_COLOR
                    valueVisualizationFrame_Color = myFuncs.get_light_color(Tile.TELEPORT_JUST_USED_COLOR, self.agentLightnessQvalueFrames)
                self.gridworldTilemap.update_tile_appearance(x, y, bg=gridworldFrame_Color)
                for action, Qvalue in self.agent.get_Qvalues()[x,y].items():
                    self.qValueTilemaps[action].update_tile_appearance(x, y, text=f"{Qvalue:< 3.2f}"[:self.QVALUES_WIDTH + 1], bg=valueVisualizationFrame_Color)

                greedyReprKwargs = Tile.get_greedy_actions_representation(tuple(self.agent.get_greedyActions()[x,y]))  # tuple cast because a cached function needs mutable args
                self.greedyPolicyTilemap.update_tile_appearance(x, y, bg=valueVisualizationFrame_Color, **greedyReprKwargs)

        for action, tilemap in self.qValueTilemaps.items():
            if action == self.agent.get_targetAction():
                relief = self.VALUE_TILEMAPS_RELIEF_TARGET_ACTION
            else:
                relief = self.VALUE_TILEMAPS_RELIEF_DEFAULT
            if tilemap.cget("relief") != relief:  # pre-check gives huge speedup (also used in Tile class)
                tilemap.config(relief=relief)

        self.guiProcess.update_idletasks()

    def toggle_operation_relevance(self, operation):
        #  This could also be implemented in check_flow_status in a similar way, but this way the stuff which must be computed at every check_flow_status call is minimized, since this function is only called after a checkbutton flip
        if self.operationFrames[operation].get_value():
            self.relevantOperations.add(operation)
        else:
            self.relevantOperations.remove(operation)
        self.reset_agentOperationCounts()

    def reset_agentOperationCounts(self):
        self.agentOperationCounts = {operation: 0 for operation in Agent.OPERATIONS}

    def freeze_lifetime_parameters(self):
        self.predefinedAlgorithmFrame.freeze()
        self.dynamicAlphaFrame.freeze()
        self.initialActionvalueMeanFrame.freeze()
        self.initialActionvalueSigmaFrame.freeze()

    def unfreeze_lifetime_parameters(self):
        self.predefinedAlgorithmFrame.unfreeze()
        self.dynamicAlphaFrame.unfreeze()
        self.initialActionvalueMeanFrame.unfreeze()
        self.initialActionvalueSigmaFrame.unfreeze()

    def freeze_episodetime_parameters(self):
        self.discountFrame.freeze()
        self.loadButton.config(state=tk.DISABLED)
        self.saveButton.config(state=tk.DISABLED)
        self.resetButton.config(state=tk.DISABLED)

    def unfreeze_episodetime_parameters(self):
        self.discountFrame.unfreeze()
        self.loadButton.config(state=tk.NORMAL)
        self.saveButton.config(state=tk.NORMAL)
        self.resetButton.config(state=tk.NORMAL)

    def toggle_algorithm(self):
        for frame in self.parameterFramesDict.values():
            frame.unfreeze()
        # All parameter frames locked by previous algorithm settings are now unlocked. The freeze-status of all frames as a whole might not be well defined anymore!
        settingsDict = self.predefinedAlgorithms[self.predefinedAlgorithmFrame.get_value()]
        toFreeze = []
        for name, frame in self.parameterFramesDict.items():
            if name in settingsDict.keys():
                newValue = settingsDict[name]
                toFreeze.append(frame)
            else:  # so EVERY parameter will activate its trace at least once, this restores a well defined freeze-status for all frames.
                newValue = frame.get_value()
            frame.set_value(newValue)
        for frame in toFreeze:
            frame.freeze()  # Now safely applying restrictions for the new algorithm after every value was handled

    def toggle_alpha_freeze(self):
        if self.dynamicAlphaFrame.get_value():
            self.learningRateFrame.freeze()
        else:
            self.learningRateFrame.unfreeze()

    def toggle_targetPolicyFrame(self):
        if self.onPolicyFrame.get_value():
            self.targetPolicyFrame.config(fg=self.LABELFRAME_DISABLED_COLOR)
            self.targetEpsilonFrame.freeze()
            self.targetEpsilonDecayRateFrame.freeze()
        else:
            self.targetPolicyFrame.config(fg=self.LABELFRAME_ENABLED_COLOR)
            self.targetEpsilonFrame.unfreeze()
            self.targetEpsilonDecayRateFrame.unfreeze()

    def toggle_offPolicy_nStep_warning(self):
        if self.nStepFrame.get_value() != 1 and not self.onPolicyFrame.get_value():  # covers true nStep algorithm and MC (nStep == 0)
            self.onPolicyFrame.highlight(self.WARNING_COLOR)
            self.nStepFrame.highlight(self.WARNING_COLOR)
        else:
            self.onPolicyFrame.normalize()
            self.nStepFrame.normalize()

    def toggle_ice_and_crosswind_warning(self):
        windLabelColor = "black"
        iceFloorValid = True
        if self.iceFloorFrame.get_value():
            for frame in self.xWindFrames + self.yWindFrames:
                if frame.get_value():
                    frame.highlight(self.WARNING_COLOR)
                    windLabelColor = self.WARNING_COLOR
                    iceFloorValid = False
                else:
                    frame.normalize()
        else:
            yWindAbsNonzeroValues = {abs(frame.get_value()) for frame in self.yWindFrames if frame.get_value()}
            for xWindFrame in self.xWindFrames:  # use indices
                xValue = xWindFrame.get_value()
                if not xValue or yWindAbsNonzeroValues in [set(), {abs(xValue)}]:
                    xWindFrame.normalize()
                else:
                    xWindFrame.highlight("orange")
                    windLabelColor = "orange"
            xWindAbsNonzeroValues = {abs(frame.get_value()) for frame in self.xWindFrames if frame.get_value()}
            for yWindFrame in self.yWindFrames:  # use indices
                yValue = yWindFrame.get_value()
                if not yValue or xWindAbsNonzeroValues in [set(), {abs(yValue)}]:
                    yWindFrame.normalize()
                else:
                    yWindFrame.highlight("orange")
                    windLabelColor = "orange"
        self.gridworldTilemap.set_windLabel_color(windLabelColor)
        if iceFloorValid:
            self.iceFloorFrame.normalize()
        else:
            self.iceFloorFrame.highlight(self.WARNING_COLOR)

    def plot(self):
        _, axes = plt.subplots(2, figsize=(7, 9))
        axes[0].plot(self.agent.get_episodeReturns())
        axes[0].set(xlabel="Episode", ylabel="Return")
        axes[1].plot(self.agent.get_stepReturns())
        axes[1].set(xlabel="Action", ylabel="Return")
        plt.savefig(f"{self.PLOTS_FOLDER}/{len(self.agent.get_stepReturns())}_Actions.png")
        plt.show()

        # diff between plt.save and fig.save?

        #print("Episode returns of the agent:", self.agent.get_episodeReturns())
        #fig, ax = plt.subplots()
        #ax.plot(self.agent.get_stepReturns())
        #ax.set(xlabel='Episode', ylabel='Reward', title='Development of the Reward per Episode')
        #ax.grid()
        #fig.savefig("RewardDevelopement.png")
        #plt.show()