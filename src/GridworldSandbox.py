﻿import tkinter as tk
from tkinter import messagebox
from collections import OrderedDict
from pathlib import Path
import matplotlib.pyplot as plt
import sys
import cProfile  # used for benchmarking, but doesnt give useful information because just one iteration of iterate_flow() can be measured at a time
import pstats    # used for benchmarking, but doesnt give useful information because just one iteration of iterate_flow() can be measured at a time

import myFuncs
from myFuncs import matrix, shape
from Environment import Environment
from Agent import Agent
from Tile import Tile
from Tilemap import Tilemap
from ParameterFrame import ParameterFrame
from EntryFrame import EntryFrame
from CheckbuttonFrame import CheckbuttonFrame
from InfoFrame import InfoFrame
from RadiomenuButtonFrame import RadiomenuButtonFrame


class GridworldSandbox:
    """A reinforcement learner interacts with a gridworld environment
    by passing actions to it and in return receives rewards and successor states
    from the environment.\n
    Detailed information about the environment, the agents actions,
    decision making and value tables is visualized by a GUI.\n
    Dynamically customizable visualization rules that allow users to pause
    the whole process, viewing it step by step or skip rendering unimportant
    steps completely enable an efficient view and analysis of the underlying processes.\n
    The user can build custom gridwordls in the GUI,
    which may be saved and loaded in/from files.\n
    This is the main class that holds the Agent, the Environment
    and the GUI and manages most interactions between them."""

    LABELFRAME_ENABLED_COLOR = "blue"
    LABELFRAME_DISABLED_COLOR = "grey"
    WARNING_COLOR = "red"
    WEAK_WARNING_COLOR = "orange"
    VALUE_TILEMAPS_RELIEF_DEFAULT = tk.FLAT
    VALUE_TILEMAPS_RELIEF_TARGET_ACTION = tk.GROOVE
    GUI_FRAMES_RELIEF_DEFAULT = tk.GROOVE

    ROOT_PATH = Path(__file__).parent.parent
    SAFEFILE_PATH = ROOT_PATH / "worlds"
    ALGORITHMS_PATH = ROOT_PATH / "algorithms"
    PLOTS_PATH = ROOT_PATH / "plots"
    SETTINGS_PATH = ROOT_PATH / "settings"

    def __init__(self, guiProcess):
        """Declares RL- and flow control variables ans builds the GUI.

        :param tk.Tk guiProcess: tk root object
        """
        # RL objects:
        self.environment = None
        self.agent = None
        self.predefinedAlgorithms = {filepath.stem: myFuncs.get_dict_from_yaml_file(self.ALGORITHMS_PATH / filepath)
                                     for filepath in self.ALGORITHMS_PATH.iterdir()}
        self.predefinedAlgorithms["Custom"] = dict()  # No restrictions

        # Flow control variables
        self.latestAgentOperation = None
        self.agentOperationCounts = None
        self.demandPauseAtNextVisualization = False
        self.pauseDemanded = False

        # Setting up the GUI
        self.guiProcess = guiProcess
        initialWindowDict = myFuncs.get_dict_from_yaml_file(self.SETTINGS_PATH / "initial")
        sizesDict = myFuncs.get_dict_from_yaml_file(self.SETTINGS_PATH / "visual")

        icon = "iconGS.ico"
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
        self.allow_straightActions = initialWindowDict["Straight-Actions"]
        self.allow_diagonalActions = initialWindowDict["Diagonal-Actions"]
        self.allow_idleActions = initialWindowDict["Idle-Actions"]

        if not initialWindowDict["skip config window"]:
            configWindow = tk.Toplevel(self.guiProcess, pady=5, padx=5)
            configWindow.title("")
            if sys.platform == "win32":
                configWindow.iconbitmap(self.SETTINGS_PATH.resolve() / icon)

            quitFlag = tk.BooleanVar(False)
            scaleVar = tk.DoubleVar(value=guiScale)
            tk.Scale(configWindow, label="GUI Scale:", variable=scaleVar, from_=1.0, to=1.5, resolution=0.05, font=fontMiddle, orient=tk.HORIZONTAL, width=15, sliderlength=20)
            labelWidth = 15
            dim1Frame = EntryFrame(configWindow, nameLabel="Dim 1 Size", varTargetType=int, check_func=lambda n: n >= 1, value=dim1, font=fontMiddle, labelWidth=labelWidth, promptWidth=3)
            dim2Frame = EntryFrame(configWindow, nameLabel="Dim 2 Size", varTargetType=int, check_func=lambda n: n >= 1, value=dim2, font=fontMiddle, labelWidth=labelWidth, promptWidth=3)
            straightActionsFrame = CheckbuttonFrame(configWindow, nameLabel="Straight-Actions", font=fontMiddle, value=self.allow_straightActions, labelWidth=labelWidth)
            diagonalActionsFrame = CheckbuttonFrame(configWindow, nameLabel="Diagonal-Actions", font=fontMiddle, value=self.allow_diagonalActions, labelWidth=labelWidth)
            idleActionsFrame = CheckbuttonFrame(configWindow, nameLabel="Idle-Actions", font=fontMiddle, value=self.allow_idleActions, labelWidth=labelWidth)
            tk.Button(configWindow, text="Proceed", height=1, font=fontBig, bd=5, command=lambda: quitFlag.set(False))

            myFuncs.arrange_children(configWindow, order="row")
            myFuncs.center(configWindow)

            configWindow.protocol("WM_DELETE_WINDOW", lambda: quitFlag.set(True))
            self.guiProcess.wait_variable(quitFlag)
            if quitFlag.get():
                sys.exit(0)
            else:
                configWindow.destroy()
            guiScale = scaleVar.get()
            dim1 = dim1Frame.get_value()
            dim2 = dim2Frame.get_value()
            self.allow_straightActions = straightActionsFrame.get_value()
            self.allow_diagonalActions = diagonalActionsFrame.get_value()
            self.allow_idleActions = idleActionsFrame.get_value()
        self.guiProcess.call('tk', 'scaling', guiScale)
        self.H = min(dim1, dim2)
        self.W = max(dim1, dim2)

        # The following scheme is an attempt to visually align the structure of the GUI source code with the GUI itself,
        # with the goal of making it as intuitively understandable and extensible as possible.
        # The key idea is to manage nested containers/frames in a tree structure where each frame is a node
        # and the children of almost every frame are graphically arranged EITHER exclusively side-by-side
        # OR exclusively on top of each other inside their parent frames.
        # The root of the tree is a tk.Toplevel object, the leaves may also be tk objects without container property.
        # The depth of each node in the tree respectively the nesting depth of the associated frame is represented by
        # the indentation depth of its constructor call, where the indentation is artificially realized by "If True:" lines,
        # each representing one node respectively one frame.
        # After all children of a frame are defined, they are arranged using the arrange_children function,
        # which takes the desired alignment as an argument and hides all geometry-related tk function calls.
        # The sorting of the children-frames inside their parent-frame automatically corresponds to the order
        # of their constructor calls.

        # Initial values can be arbitrary, since the default config is loaded anyway right after the GUI was built.

        self.mainWindow = tk.Toplevel(self.guiProcess)
        self.mainWindow.title("Gridworld Sandbox")
        if sys.platform == "win32":
            self.mainWindow.iconbitmap(self.SETTINGS_PATH / icon)
        self.mainWindow.protocol("WM_DELETE_WINDOW", self.guiProcess.quit)

        if True:  # mainWindow:
            self.settingsFrame = tk.Frame(self.mainWindow, bd=5, relief=self.GUI_FRAMES_RELIEF_DEFAULT)
            self.tilemapsFrame = tk.Frame(self.mainWindow, bd=5, relief=self.GUI_FRAMES_RELIEF_DEFAULT)

            myFuncs.arrange_children(self.mainWindow, order="row")

            if True:  # tilemapsFrame:
                self.gridworldTilemap = Tilemap(self.tilemapsFrame, H=self.H, W=self.W, interactionAllowed=True, font=fontWorldtiles, relief=self.GUI_FRAMES_RELIEF_DEFAULT, displayWind=True,
                                                bd=5, tileHeight=sizesDict["worldtiles height"], tileWidth=sizesDict["worldtiles width"], tileBd=sizesDict["worldtiles borderwidth"])
                self.valueVisualizationFrame = tk.Frame(self.tilemapsFrame, bd=5, relief=self.GUI_FRAMES_RELIEF_DEFAULT)

                myFuncs.arrange_children(self.tilemapsFrame, order="column", useSticky=False)

                if True:  # gridworldTilemap:
                    self.hWindFrames = [EntryFrame(self.gridworldTilemap, font=fontMiddle, varTargetType=int, promptWidth=2, promptHighlightthickness=4) for _ in range(self.W)]
                    self.wWindFrames = [EntryFrame(self.gridworldTilemap, font=fontMiddle, varTargetType=int, promptWidth=2, promptHighlightthickness=4) for _ in range(self.H)]
                    self.gridworldTilemap.add_wind(self.hWindFrames, self.wWindFrames)

                    # no arrange_children call here since a more complex alignment is needed

                if True:  # valueVisualizationFrame:
                    self.QVALUES_WIDTH = sizesDict["qvalues width"]
                    self.qValueTilemaps = {}
                    for action in Agent.create_actionspace(straight=self.allow_straightActions, diagonal=self.allow_diagonalActions, idle=self.allow_idleActions):
                        self.qValueTilemaps[action] = Tilemap(self.valueVisualizationFrame, H=self.H, W=self.W, interactionAllowed=False,
                                                              indicateNumericalValueChange=True, font=fontQvalues, tileWidth=self.QVALUES_WIDTH,
                                                              bd=sizesDict["targetmarker width"], relief=self.VALUE_TILEMAPS_RELIEF_DEFAULT,
                                                              bg=myFuncs.direction_to_hsvHexString(action, hsvValue=Tile.DEFAULT_HSV_VALUE), tileHeight=sizesDict["qvalues height"], tileBd=sizesDict["qvalues borderwidth"])
                        self.qValueTilemaps[action].grid(row=action[0] + 1, column=action[1] + 1)  # maps the Tilemaps corresponding to the actions (which are actually 2D "vectors")  to coordinates inside the valueVisualizationFrame
                    self.greedyPolicyTilemap = Tilemap(self.valueVisualizationFrame, H=self.H, W=self.W, interactionAllowed=False, font=fontQvalues,
                                                       tileWidth=self.QVALUES_WIDTH, bd=sizesDict["targetmarker width"], tileHeight=sizesDict["qvalues height"], tileBd=sizesDict["qvalues borderwidth"], relief=self.VALUE_TILEMAPS_RELIEF_TARGET_ACTION)
                    self.greedyPolicyTilemap.grid(row=1, column=1)
                    self.guiProcess.bind_all("<space>", lambda _: self._toggle_idleActionValues())
                    self.idleActionValues_visible = False

                    # no arrange_children call here since a more complex alignment is needed

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
                    self.hTorusFrame = CheckbuttonFrame(self.worldSettingsFrame, nameLabel="H-Torus", font=fontMiddle)
                    self.wTorusFrame = CheckbuttonFrame(self.worldSettingsFrame, nameLabel="W-Torus", font=fontMiddle)
                    self.rewardFrames = OrderedDict([(color, EntryFrame(self.worldSettingsFrame, nameLabel=f"Reward {color.capitalize()}", promptFg=color, font=fontMiddle, varTargetType=int)) for color in Tile.BORDER_COLORS])
                    self.resetButton = tk.Button(self.worldSettingsFrame, text="Reset World", font=fontBig, bd=5, command=self._reset_gridworld)

                    myFuncs.arrange_children(self.worldSettingsFrame, order="row")

                if True:  # algorithmSettingsFrame
                    self.dynamicAlphaFrame = CheckbuttonFrame(self.algorithmSettingsFrame, nameLabel="α = 1/count((S,A))", font=fontMiddle)
                    self.learningRateFrame = EntryFrame(self.algorithmSettingsFrame, nameLabel="Learning Rate α", font=fontMiddle, varTargetType=float)
                    self.discountFrame = EntryFrame(self.algorithmSettingsFrame, nameLabel="Discount γ", font=fontMiddle, varTargetType=float)
                    self.nStepFrame = EntryFrame(self.algorithmSettingsFrame, nameLabel="n-Step n", font=fontMiddle, varTargetType=int, check_func=lambda x: x >= 0)
                    self.nPlanFrame = EntryFrame(self.algorithmSettingsFrame, nameLabel="Dyna-Q n", font=fontMiddle, varTargetType=int, labelWidth=8)
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
                        self.behaviorEpsilonFrame = EntryFrame(self.behaviorPolicyFrame, nameLabel="Exploration Rate ε", font=fontMiddle, varTargetType=float, check_func=lambda x: x >= 0, trustSet=False)  # epsilon
                        self.behaviorEpsilonDecayRateFrame = EntryFrame(self.behaviorPolicyFrame, nameLabel="ε-Decay Rate", font=fontMiddle, varTargetType=float, check_func=lambda x: x >= 0)  # epsilon

                        myFuncs.arrange_children(self.behaviorPolicyFrame, order="row")

                    if True:  # targetPolicyFrame
                        self.targetEpsilonFrame = EntryFrame(self.targetPolicyFrame, nameLabel="Exploration Rate ε\u200C", font=fontMiddle, varTargetType=float, check_func=lambda x: x >= 0, trustSet=False)  # epsilon
                        self.targetEpsilonDecayRateFrame = EntryFrame(self.targetPolicyFrame, nameLabel="ε-Decay Rate\u200C", font=fontMiddle, varTargetType=float, check_func=lambda x: x >= 0)  # epsilon

                        myFuncs.arrange_children(self.targetPolicyFrame, order="row")

                if True:  # flowControlFrame
                    self.showEveryNoperationsFrame = EntryFrame(self.flowControlFrame, nameLabel="Show Every...", font=fontMiddle, varTargetType=int, check_func=lambda x: x >= 1, value=1)
                    self.operationFrames = OrderedDict([(operation, CheckbuttonFrame(self.flowControlFrame, nameLabel=f"...{operation}", font=fontMiddle)) for operation in Agent.OPERATIONS])
                    self.flowButtonsFrame = tk.Frame(self.flowControlFrame)

                    myFuncs.arrange_children(self.flowControlFrame, order="row")
                    self.flowButtonsFrame.grid_configure(sticky="")   # this is a correction after the arrange_children() call, since the children of flowButtonsFrame should not be sticky

                    if True:  # flowButtonsFrame:
                        # pause is only hidden behind go because of the order of lines below. If this somehow fails, uncomment all lines that say "use this again if Pause appears over Go! when it shouldnt" as a comment
                        self.pauseButton = tk.Button(self.flowButtonsFrame, text="Pause", font=fontBig, bd=5, width=6, command=self._demand_pause)
                        self.goButton = tk.Button(self.flowButtonsFrame, text="Go!", font=fontBig, bd=5, width=6, command=lambda: self._start_flow(demandPauseAtNextVisualization=False))
                        self.nextButton = tk.Button(self.flowButtonsFrame, text="Next", font=fontBig, bd=5, width=6, command=lambda: self._start_flow(demandPauseAtNextVisualization=True))
                        self.goButton.grid(row=0, column=0)
                        self.pauseButton.grid(row=0, column=0)
                        # self.pauseButton.grid_remove()  # use this again if Pause appears over Go when it shouldnt
                        self.nextButton.grid(row=0, column=1)

                        # no arrange_children call here since a more complex alignment is needed

                if True:  # miscSettingsFrame:
                    self.initialActionvalueMeanFrame = EntryFrame(self.miscSettingsFrame, nameLabel="Initial Q-Value Mean", font=fontMiddle, varTargetType=float)
                    self.initialActionvalueSigmaFrame = EntryFrame(self.miscSettingsFrame, nameLabel="Initial Q-Value Sigma", font=fontMiddle, varTargetType=float, check_func=lambda x: x >= 0)
                    self.currentReturnFrame = InfoFrame(self.miscSettingsFrame, nameLabel="Current Return", font=fontMiddle, varTargetType=int, trustSet=False)
                    self.currentEpisodeFrame = InfoFrame(self.miscSettingsFrame, nameLabel="Current Episode", font=fontMiddle, varTargetType=int, trustSet=False)
                    self.operationsLeftFrame = EntryFrame(self.miscSettingsFrame, nameLabel="Operations Left", font=fontMiddle, varTargetType=int, trustSet=False)
                    self.minDelayFrame = EntryFrame(self.miscSettingsFrame, nameLabel="Min Delay [ms]", font=fontMiddle, varTargetType=int, check_func=lambda x: 0 <= x <= 9999)
                    self.visualizeMemoryFrame = CheckbuttonFrame(self.miscSettingsFrame, nameLabel="Visualize Memory", font=fontMiddle)
                    self.dataButtonsFrame = tk.Frame(self.miscSettingsFrame)

                    myFuncs.arrange_children(self.miscSettingsFrame, order="row")
                    self.dataButtonsFrame.grid_configure(sticky="")  # this is a correction after the arrange_children() call, since the children of dataButtonsFrame should not be sticky

                    if True:  # dataButtonsFrame:
                        self.loadButton = tk.Button(self.dataButtonsFrame, text="Load", font=fontBig, bd=5, width=5, command=self._load)
                        self.saveButton = tk.Button(self.dataButtonsFrame, text="Save", font=fontBig, bd=5, width=5, command=self._save)

                        myFuncs.arrange_children(self.dataButtonsFrame, order="column")

        self.parameterFramesDict = self._recursiveGather_namedInteractiveParameterFrames(self.mainWindow)
        # Following params stay constant over an Agents whole lifespan so their frames will be disabled for that time
        self.lifetimeParameterFrames = [self.predefinedAlgorithmFrame,
                                        self.dynamicAlphaFrame,
                                        self.initialActionvalueMeanFrame,
                                        self.initialActionvalueSigmaFrame]
        self._load(self.SAFEFILE_PATH / initialWindowDict['default configfile'])

        # assign traces
        self.relevantOperations = set()
        self.showEveryNoperationsFrame.set_and_call_trace(self._reset_agentOperationCounts)
        for operation, frame in (self.operationFrames.items()):
            frame.set_and_call_trace(lambda operation=operation: self._toggle_operation_relevance(operation))
        self.dynamicAlphaFrame.set_and_call_trace(self._toggle_alpha_freeze)
        self.onPolicyFrame.set_and_call_trace(self._toggle_targetPolicyFrame)
        self.onPolicyFrame.set_and_call_trace(self._toggle_offPolicy_nStep_warning)
        self.nStepFrame.set_and_call_trace(self._toggle_offPolicy_nStep_warning)
        for frame in self.hWindFrames + self.wWindFrames:
            frame.set_and_call_trace(self._toggle_ice_and_crosswind_warning)
        self.iceFloorFrame.set_and_call_trace(self._toggle_ice_and_crosswind_warning)
        self.predefinedAlgorithmFrame.set_and_call_trace(self._toggle_algorithm)

        myFuncs.center(self.mainWindow)
        if self.allow_idleActions and initialWindowDict["show idle action warning"]:
            messagebox.showinfo("Idle Action Available", "You have chosen to include (0,0) in the agents actionspace.\nPress space to toggle the view between the Q-values of that action and the agents greedy choices.")

    def _reset_gridworld(self):
        """Resets the whole gridworld environment to its initial state.
        """
        self.gridworldTilemap.reset()
        self.iceFloorFrame.set_value(False)
        self.hTorusFrame.set_value(False)
        self.wTorusFrame.set_value(False)
        for frame in self.hWindFrames + self.wWindFrames:
            frame.set_value(0)

    def _toggle_idleActionValues(self):
        """Triggered by user input. If idle actions are part of the chosen actionspace,
        switches the center ``Tilemap`` of the value visualization frame between
        showing greedy actions and showing the value of the idle action.
        """
        if self.allow_idleActions:
            if self.idleActionValues_visible:
                self.greedyPolicyTilemap.grid()
                self.qValueTilemaps[Agent.IDLE].grid_remove()
                self.idleActionValues_visible = False
            else:
                self.greedyPolicyTilemap.grid_remove()
                self.qValueTilemaps[Agent.IDLE].grid()
                self.idleActionValues_visible = True

    def _recursiveGather_namedInteractiveParameterFrames(self, frame):
        """Recursive helper method to create a mapping of all (arbitrarily deep nested)
        ``ParameterFrames`` inside a given root container to their names. Makes some
        things much easier.
        :param frame:
        :return:
        """
        collection = dict()
        for child in frame.winfo_children():
            if isinstance(child, ParameterFrame) and child.isInteractive and child.get_text():
                collection[child.get_text()] = child
            else:
                collection |= self._recursiveGather_namedInteractiveParameterFrames(child)
        return collection

    def _load(self, filename=None):
        """Triggered by user input or at initialization.
        Loads a predefined environment along with agents algorithm settings from a yaml file.
        Triggers a popup if the word- or wind shape doesnt match.

        :param str filename: Name of the file. ".yaml" suffix optional. If None, opens a dialog for user input.
        """
        yamlDict = myFuncs.get_dict_from_yaml_file(filename, initialdir=self.SAFEFILE_PATH)
        if yamlDict:  # get_dict_from_yaml_file could have returned an empty Dict if dialog was canceled
            throwWorldShapeError = False
            tileDictMatrix = yamlDict.pop("world")
            if tileDictMatrix is not None:
                if shape(tileDictMatrix) == (self.H, self.W):
                    for h in range(self.H):
                        for w in range(self.W):
                            self.gridworldTilemap.update_tile_appearance(h, w, **tileDictMatrix[h][w])
                else:
                    throwWorldShapeError = True
            hWindValues = yamlDict.pop("hWind")
            if hWindValues is not None:
                if len(hWindValues) == self.W:
                    for frame, value in zip(self.hWindFrames, hWindValues):
                        frame.set_value(value)
                else:
                    throwWorldShapeError = True
            wWindValues = yamlDict.pop("wWind")
            if wWindValues is not None:
                if len(wWindValues) == self.H:
                    for frame, value in zip(self.wWindFrames, wWindValues):
                        frame.set_value(value)
                else:
                    throwWorldShapeError = True
            if throwWorldShapeError:
                messagebox.showerror("Error", "World shape does not match.")

            for name, frame in self.parameterFramesDict.items():  # must be executed only after world and wind was popped
                frame.set_value(yamlDict[name])

    def _save(self, filepath=None):
        """Triggered by user input. Saves the current state of the environment
        and the agents current algorithm settings to a yaml file.
        Agents actionvalues are **not** included.

        :param filepath:  Name of the file. ".yaml" suffix optional. If None, opens a dialog for user input.
        """
        valueDict = {name: frame.get_value() for name, frame in self.parameterFramesDict.items()}
        valueDict["world"] = self.gridworldTilemap.get_yaml_list()
        valueDict["hWind"] = [frame.get_value() for frame in self.hWindFrames]
        valueDict["wWind"] = [frame.get_value() for frame in self.wWindFrames]
        myFuncs.create_yaml_file_from_dict(valueDict, filepath, nameEmbedding=f"{{}}_{self.H}x{self.W}", initialdir=self.SAFEFILE_PATH)

    def _initialize_environment_and_agent(self):
        self.environment = Environment(H=self.H, W=self.W,
                                       hasIceFloorVar=self.iceFloorFrame.get_variable(),
                                       isHtorusVar=self.hTorusFrame.get_variable(),
                                       isWtorusVar=self.wTorusFrame.get_variable(),
                                       hWindVars=[frame.get_variable() for frame in self.hWindFrames],
                                       wWindVars=[frame.get_variable() for frame in self.wWindFrames])
        # Agent needs an environment to exist, but environment doesnt need an agent to exist
        self.agent = Agent(environment=self.environment,
                           use_straightActions=self.allow_straightActions,
                           use_diagonalActions=self.allow_diagonalActions,
                           use_idleActions=self.allow_idleActions,
                           currentReturnVar=self.currentReturnFrame.get_variable(),
                           currentEpisodeVar=self.currentEpisodeFrame.get_variable(),
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

    def _update_environment(self):
        tileData = matrix(self.H, self.W)
        valueVisualizationTilemaps = self.valueVisualizationFrame.winfo_children()
        for h in range(self.H):
            for w in range(self.W):
                newText = self.gridworldTilemap.get_tile_text(h, w)
                newBackground = self.gridworldTilemap.get_tile_background_color(h, w)
                newBordercolor = self.gridworldTilemap.get_tile_border_color(h, w)
                updateKwargs = {"fg": Tile.LETTER_COLOR, "borderColor": newBordercolor, "bg": newBackground}
                for tilemap in valueVisualizationTilemaps:
                    tilemap.unprotect_text_and_textColor(h, w)  # needed to set / remove Goalchar properly
                    if newText and (newText[-1] in [Tile.GOAL_CHAR, Tile.TELEPORTER_SINK_ONLY_SUFFIX]):
                        tilemap.update_tile_appearance(h, w, text=newText, **updateKwargs)
                        tilemap.protect_text_and_color(h, w)
                    else:
                        tilemap.update_tile_appearance(h, w, **updateKwargs)
                teleportSource = None
                teleportSink = None
                if newText and newText[0] in Tile.TELEPORTERS:
                    if newText[1] != Tile.TELEPORTER_SINK_ONLY_SUFFIX:
                        teleportSource = newText[0]
                    if newText[1] != Tile.TELEPORTER_SOURCE_ONLY_SUFFIX:
                        teleportSink = newText[0]
                arrivalRewardVarName = "Reward " + newBordercolor.capitalize()
                tileData[h][w] = {"position": (h,w),
                                  "isWall": newBackground == Tile.WALL_COLOR,
                                  "isStart": newText == Tile.START_CHAR,
                                  "isGoal": newText == Tile.GOAL_CHAR,
                                  "arrivalRewardVar": self.parameterFramesDict[arrivalRewardVarName].get_variable(),
                                  "teleportSource": teleportSource,
                                  "teleportSink": teleportSink}
        self.environment.update(tileData)
        # TODO: Everytime a Tile is changed to an episode terminator, change its Qvalues to 0 explicitly. NO! Agent cant know this beforehand, thats the point!

    #def _start_flow(self, demandPauseAtNextVisualization):
    #    profile = cProfile.Profile()
    #    profile.runcall(lambda arg=demandPauseAtNextVisualization: self._start_flow_real(arg))
    #    ps = pstats.Stats(profile)
    #    ps.print_stats()

    def _start_flow(self, demandPauseAtNextVisualization):
        self.pauseDemanded = False
        self.demandPauseAtNextVisualization = demandPauseAtNextVisualization
        #self.pauseButton.grid()  # use this again if Pause appears over Go when it shouldnt
        self.goButton.grid_remove()
        self.nextButton.config(state=tk.DISABLED)
        if self.agent is None:
            self._initialize_environment_and_agent()
            self._freeze_lifetime_parameters()
        if self.gridworldTilemap.interactionAllowed:  # new episode is going to start
            self.gridworldTilemap.set_interactionAllowed(False)
            self._freeze_episodetime_parameters()
            self._update_environment()
        self._iterate_flow()

    def _iterate_flow(self):
        if self.operationsLeftFrame.get_value() <= 0:
            self._apply_pause(end=True)
            return
        if self.pauseDemanded:
            if self.latestAgentOperation in self.relevantOperations:
                self._apply_pause()
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
                self._visualize()
                next_msDelay = self.minDelayFrame.get_value()
        self.guiProcess.after(next_msDelay, self._iterate_flow)

    def _demand_pause(self):
        self.pauseDemanded = True

    def _apply_pause(self, end=False):
        self.pauseDemanded = False
        self.demandPauseAtNextVisualization = False
        self.goButton.grid()
        #self.pauseButton.grid_remove()  # use this again if Pause appears over Go! when it shouldnt
        self.nextButton.config(state=tk.NORMAL)
        if end:
            self._unfreeze_lifetime_parameters()
            self._visualize()
            self._plot()
            del self.agent
            self.agent = None
        if self.agent is None or self.latestAgentOperation == Agent.FINISHED_EPISODE:
            self._unfreeze_episodetime_parameters()
            self.gridworldTilemap.set_interactionAllowed(True)

    def _visualize(self):
        # TODO: Qlearning doesnt update some tiles after a while. THATS THE POINT! Because its off-policy. This shows that it works! Great for presentation! Example with no walls and Start/Goal in the edges.
        if self.visualizeMemoryFrame.get_value():
            agentcolorDefaultHue, agentcolorDefaultSaturation, agentcolorValue = myFuncs.rgbHexString_to_hsv(myFuncs.get_light_color(Tile.AGENTCOLOR_DEFAULT, self.agentLightnessQvalueFrames))
            traceCandidates = {state for state, _, _ in self.agent.get_memory()}
            traceTail = self.agent.get_memory().yield_lastForgottenState()
            memorySize = self.agent.get_memory_size() + int(bool(traceTail))
            if traceTail:
                traceCandidates.add(traceTail)

        for h in range(self.H):
            for w in range(self.W):
                if self.gridworldTilemap.get_tile_background_color(h, w) == Tile.WALL_COLOR:
                    continue
                gridworldFrame_Color = Tile.BLANK_COLOR
                valueVisualizationFrame_Color = Tile.BLANK_COLOR
                if self.visualizeMemoryFrame.get_value() and (h,w) in traceCandidates:
                    newSaturation = (self.maxLightnessAgentTrace - self.minLightnessAgentTrace * self.agent.get_absence((h,w)) / (memorySize+1)) * agentcolorDefaultSaturation
                    valueVisualizationFrame_Color = myFuncs.hsv_to_rgbHexString(agentcolorDefaultHue, newSaturation, agentcolorValue)
                if (h,w) == self.agent.get_state():
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
                elif (h,w) == self.environment.get_teleportJustUsed():
                    gridworldFrame_Color = Tile.TELEPORT_JUST_USED_COLOR
                    valueVisualizationFrame_Color = myFuncs.get_light_color(Tile.TELEPORT_JUST_USED_COLOR, self.agentLightnessQvalueFrames)
                elif (h,w) == self.environment.get_windJustUsed():
                    gridworldFrame_Color = Tile.WIND_JUST_USED_COLOR
                    valueVisualizationFrame_Color = myFuncs.get_light_color(Tile.WIND_JUST_USED_COLOR, self.agentLightnessQvalueFrames)
                self.gridworldTilemap.update_tile_appearance(h, w, bg=gridworldFrame_Color)
                for action, Qvalue in self.agent.get_Qvalues()[h][w].items():
                    self.qValueTilemaps[action].update_tile_appearance(h, w, text=f"{Qvalue:< 3.2f}"[:self.QVALUES_WIDTH + 1], bg=valueVisualizationFrame_Color)

                greedyReprKwargs = Tile.get_greedy_actions_representation(tuple(self.agent.get_greedyActions()[h][w]))  # tuple cast because a cached function needs mutable args
                self.greedyPolicyTilemap.update_tile_appearance(h, w, bg=valueVisualizationFrame_Color, **greedyReprKwargs)

        for action, tilemap in self.qValueTilemaps.items():
            if action == self.agent.get_targetAction():
                relief = self.VALUE_TILEMAPS_RELIEF_TARGET_ACTION
            else:
                relief = self.VALUE_TILEMAPS_RELIEF_DEFAULT
            if tilemap.cget("relief") != relief:  # pre-check gives huge speedup (also used in Tile class)
                tilemap.config(relief=relief)

        self.guiProcess.update_idletasks()

    def _toggle_operation_relevance(self, operation):
        #  This could also be implemented in check_flow_status in a similar way, but this way the stuff which must be computed at every check_flow_status call is minimized, since this function is only called after a checkbutton flip
        if self.operationFrames[operation].get_value():
            self.relevantOperations.add(operation)
        elif operation in self.relevantOperations:  # in-check prevents from error if frames will be set simultaneously by load() when some where unchecked before
            self.relevantOperations.remove(operation)
        self._reset_agentOperationCounts()

    def _reset_agentOperationCounts(self):
        self.agentOperationCounts = {operation: 0 for operation in Agent.OPERATIONS}

    def _freeze_lifetime_parameters(self):
        for frame in self.lifetimeParameterFrames:
            frame.freeze()

    def _unfreeze_lifetime_parameters(self):
        for frame in self.lifetimeParameterFrames:
            frame.unfreeze()

    def _freeze_episodetime_parameters(self):
        self.discountFrame.freeze()
        self.loadButton.config(state=tk.DISABLED)
        self.saveButton.config(state=tk.DISABLED)
        self.resetButton.config(state=tk.DISABLED)

    def _unfreeze_episodetime_parameters(self):
        self.discountFrame.unfreeze()
        self.loadButton.config(state=tk.NORMAL)
        self.saveButton.config(state=tk.NORMAL)
        self.resetButton.config(state=tk.NORMAL)

    def _toggle_algorithm(self):
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

    def _toggle_alpha_freeze(self):
        if self.dynamicAlphaFrame.get_value():
            self.learningRateFrame.freeze()
        else:
            self.learningRateFrame.unfreeze()

    def _toggle_targetPolicyFrame(self):
        if self.onPolicyFrame.get_value():
            self.targetPolicyFrame.config(fg=self.LABELFRAME_DISABLED_COLOR)
            self.targetEpsilonFrame.freeze()
            self.targetEpsilonDecayRateFrame.freeze()
        else:
            self.targetPolicyFrame.config(fg=self.LABELFRAME_ENABLED_COLOR)
            self.targetEpsilonFrame.unfreeze()
            self.targetEpsilonDecayRateFrame.unfreeze()

    def _warn_and_pause(self, color, *frames):
        for frame in frames:
            frame.highlight(color)
        self._demand_pause()

    def _toggle_offPolicy_nStep_warning(self):
        if self.nStepFrame.get_value() != 1 and not self.onPolicyFrame.get_value():  # covers true nStep algorithm and MC (nStep == 0)
            self._warn_and_pause(self.WARNING_COLOR, self.onPolicyFrame, self.nStepFrame)
        else:
            self.onPolicyFrame.normalize()
            self.nStepFrame.normalize()

    def _toggle_ice_and_crosswind_warning(self):
        windLabelColor = "black"
        iceFloorValid = True
        if self.iceFloorFrame.get_value():
            for frame in self.hWindFrames + self.wWindFrames:
                if frame.get_value():
                    self._warn_and_pause(self.WARNING_COLOR, frame)
                    windLabelColor = self.WARNING_COLOR
                    iceFloorValid = False
                else:
                    frame.normalize()
        else:
            wWindAbsNonzeroValues = {abs(frame.get_value()) for frame in self.wWindFrames if frame.get_value()}
            for hWindFrame in self.hWindFrames:  # use indices
                hValue = hWindFrame.get_value()
                if not hValue or wWindAbsNonzeroValues in [set(), {abs(hValue)}]:
                    hWindFrame.normalize()
                else:
                    self._warn_and_pause(self.WEAK_WARNING_COLOR, hWindFrame)
                    windLabelColor = self.WEAK_WARNING_COLOR
            hWindAbsNonzeroValues = {abs(frame.get_value()) for frame in self.hWindFrames if frame.get_value()}
            for wWindFrame in self.wWindFrames:  # use indices
                wValue = wWindFrame.get_value()
                if not wValue or hWindAbsNonzeroValues in [set(), {abs(wValue)}]:
                    wWindFrame.normalize()
                else:
                    self._warn_and_pause(self.WEAK_WARNING_COLOR, wWindFrame)
                    windLabelColor = self.WEAK_WARNING_COLOR
        self.gridworldTilemap.set_windLabel_color(windLabelColor)
        if iceFloorValid:
            self.iceFloorFrame.normalize()
        else:
            self._warn_and_pause(self.WARNING_COLOR, self.iceFloorFrame)

    def _plot(self):
        _, axes = plt.subplots(2, figsize=(7, 9))
        axes[0].plot(self.agent.get_episodeReturns())
        axes[0].set(xlabel="Episode", ylabel="Return")
        axes[1].plot(self.agent.get_stepReturns())
        axes[1].set(xlabel="Action", ylabel="Return")
        plt.savefig(self.PLOTS_PATH / f"{len(self.agent.get_stepReturns())}_Actions.png")
        plt.show()


if __name__ == "__main__":
    #myFuncs.print_default_kwargs(Agent)
    #myFuncs.print_default_kwargs(Environment)
    #myFuncs.print_default_kwargs(Tilemap)
    #myFuncs.print_default_kwargs(Tile)
    #myFuncs.print_default_kwargs(CheckbuttonFrame)
    #myFuncs.print_default_kwargs(RadiomenuButtonFrame)
    #myFuncs.print_default_kwargs(InfoFrame)
    myFuncs.print_default_kwargs(EntryFrame)
