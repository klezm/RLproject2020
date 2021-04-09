from Agent import Agent
from Environment import Environment
import matplotlib.pyplot as plt


class GridworldPlayground:
    def __init__(self):
        self.gui = None
        self.environment = None
        self.agent = None
        self.msDelay = None
        self.showEveryNchanges = None
        self.timestepsLeft = None

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
        self.environment = Environment(data)
        self.timestepsLeft = data["timestepsLeft"]
        self.agent = Agent(self.environment, **data)
        self.gui.freeze_lifetime_parameters()
        self.run()

    def run(self):
        #print(timestepsLeft)
        if self.timestepsLeft.get() <= 0:
            self.plot()
            del self.agent
            self.gui.unfreeze_lifetime_parameters()
            return
        for _ in range(self.showEveryNchanges.get()):
            if self.agent.episodeFinished:
                if self.agent.has_memory():
                    self.agent.process_earliest_memory()
                else:
                    self.agent.start_episode()
            else:
                self.agent.step()
                self.timestepsLeft.set(self.timestepsLeft.get() - 1)
        self.visualize_gui()
        self.gui.process.after(self.msDelay.get(), self.run)

    def plot(self):
        #print(self.agent.get_episodeReturns())
        fig, ax = plt.subplots()
        ax.plot(self.agent.get_episodeReturns())
        ax.set(xlabel='Episode', ylabel='Reward', title='Development of the Reward per Episode')
        ax.grid()
        fig.savefig("RewardDevelopement.png")
        plt.show()
