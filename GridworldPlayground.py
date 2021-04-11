import matplotlib.pyplot as plt

from Agent import Agent
from Environment import Environment


class GridworldPlayground:
    def __init__(self):
        self.gui = None
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
        self.run()

    def run(self):
        if self.operationsLeft.get() <= 0:
            self.plot()
            del self.agent
            self.gui.unfreeze_lifetime_parameters()
            return
        if self.gui.runPaused:
            return
        self.agent.operate()
        self.operationsLeft.set(self.operationsLeft.get() - 1)
        if True:
            self.visualize_gui()
        self.gui.process.after(self.msDelay.get(), self.run)

    def plot(self):
        fig, ax = plt.subplots()
        ax.plot(self.agent.get_episodeReturns())
        ax.set(xlabel='Episode', ylabel='Reward', title='Development of the Reward per Episode')
        ax.grid()
        fig.savefig("RewardDevelopement.png")
        plt.show()
