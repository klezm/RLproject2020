import numpy as np

from Agent import Agent
from SarsaAgent import SarsaAgent
from Environment import Environment


class GridworldPlayground:
    def __init__(self):
        self.gui = None
        self.environment = None
        self.agent = None
        self.msDelay = None
        self.showEveryNchanges = None

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
        self.agent = SarsaAgent(self.environment, stepSize=0.3, discount=1, epsilon=0.05)#, actionPlan=[(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)])  # TODO: remove plan arg
        self.run(timestepsLeft=data["maxTimeSteps"])

    def run(self, timestepsLeft):
        #print(timestepsLeft)
        if timestepsLeft <= 0:
            self.plot()
            del self.agent
            return
        timestepsPassed = 0
        for i in range(self.showEveryNchanges):
            if self.agent.episodeFinished:
                self.agent.process_remaining_memory()
                self.agent.start_episode()
            else:
                self.agent.step()
                timestepsPassed += 1
        self.visualize_gui()
        self.gui.process.after(self.msDelay, lambda: self.run(timestepsLeft - timestepsPassed))

    def plot(self):
        print(self.agent.episodeReturns)
