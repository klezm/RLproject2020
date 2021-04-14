import matplotlib.pyplot as plt

from Agent import Agent
from Environment import Environment


class GridworldPlayground:
    def __init__(self, flowStates):
        self.gui = None
        self.flowStates = flowStates
        self.guiFlowStatus = self.flowStates.PASS  # For first call of self.run(), status should be < PAUSE
        self.environment = None
        self.agent = None
        self.msDelay = None
        self.showEveryNchanges = None
        self.operationsLeft = None

    def set_gui(self, gui):
        self.gui = gui

    def visualize_gui(self):
        data = {"agentPosition": self.agent.get_state(),
                "Qvalues": self.agent.get_Qvalues(),
                "greedyActions": self.agent.get_greedyActions(),
                "hasMadeExploratoryMove": self.agent.hasMadeExploratoryMove}
        self.gui.visualize(data)  # gridworldPlayground gathers data, then calls visualize method of gridworldPlayground. This method should all GUIs have.

    def initialize(self, data):
        self.msDelay = data["msDelay"]
        self.showEveryNchanges = data["showEveryNchanges"]
        self.operationsLeft = data["operationsLeft"]
        self.environment = Environment(data)
        self.agent = Agent(self.environment, **data)

    def update_environment(self, tileData):
        self.environment.update(tileData)

    def run(self):
        # TODO: operationsLeft var must not be send to gwpg anymore
        # TODO: gui state setter/getter!
        # Following condition is needed if the PAUSE State was set by pressing the Pause button, which will be resolved
        # as part of the after function, immediately before the recursive call.
        # The PAUSE should happen as soon as possible then, since the user wants to freeze what he sees at that time.
        # Without the following condition, another iteration would resolve before a return statement would be reached,
        # resulting in freezing after processing the subsequent state of the one that the user wanted to freeze instead.
        # (This would even happen if the flow_iteration call would be skipped completely.)
        if self.gui.flowStatus >= self.flowStates.PAUSE:
            self.gui.flowStatus = self.flowStates.PASS
            return
        operation = self.agent.operate()
        self.gui.flow_iteration(operation)
        next_msDelay = 0
        if self.gui.flowStatus >= self.flowStates.VISUALIZE:  # includes VISUALIZE, PAUSE, END
            self.visualize_gui()
            next_msDelay = self.msDelay.get()
        if self.gui.flowStatus == self.flowStates.END:
            self.plot()
            del self.agent
        # Following condition is needed if the PAUSE state was set in the flow_iteration method.
        # The Pause and the visualization, and especially disabling the Go and the Next button should happen
        # immediately after the processing.
        # Without the following condition, the user would have another next_msDelay amount of time to trigger
        # Next or Go again and therefore call this function again, which would cause undefined behavior.
        if self.gui.flowStatus >= self.flowStates.PAUSE:  # includes PAUSE, END
            return
        self.gui.process.after(next_msDelay, self.run)  # Queued GUI interactions will be resolved only during the wait process of this call.

    def plot(self):
        fig, ax = plt.subplots()
        ax.plot(self.agent.get_episodeReturns())
        ax.set(xlabel='Episode', ylabel='Reward', title='Development of the Reward per Episode')
        ax.grid()
        fig.savefig("RewardDevelopement.png")
        plt.show()
