from Agent import Agent
from Environment import Environment
import matplotlib
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
                "Qvalues": self.agent.get_Qvalues()}
        self.gui.visualize(data)  # gridworldPlayground gathers data, then calls visualize method of gridworldPlayground. This method should all GUIs have.

    def initialize(self, data):
        self.msDelay = data["msDelay"]
        self.showEveryNchanges = data["showEveryNchanges"]
        self.environment = Environment(data)
        self.timestepsLeft = data["maxTimeSteps"]
        self.agent = Agent(self.environment, **data)
        self.run()

    def run(self):
        #print(timestepsLeft)
        if int(self.timestepsLeft.get()) <= 0:
            self.plot()
            del self.agent
            return
        for _ in range(int(self.showEveryNchanges.get())):
            if self.agent.episodeFinished:
                self.agent.process_remaining_memory()
                self.agent.start_episode()
            else:
                self.agent.step()
                self.timestepsLeft.set(int(self.timestepsLeft.get()) - 1)
        self.visualize_gui()
        self.gui.process.after(int(self.msDelay.get()), self.run)

    def plot(self):
        print(self.agent.get_episode_returns())
        fig, ax = plt.subplots()
        ax.plot([episode_nr for episode_nr in range(len(self.agent.get_episode_returns()))], self.agent.get_episode_returns())

        ax.set(xlabel='episode', ylabel='reward', title='Development of the Reward per Episode')
        ax.grid()

        fig.savefig("RewardDevelopement.png")
        plt.show()