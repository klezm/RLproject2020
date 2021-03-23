import numpy as np

from Agent import Agent
from Environment import Environment

class GridworldPlayground:
    def __init__(self):
        self.gui = None
        self.environment = None
        self.agent = None

    def set_gui(self, gui):
        self.gui = gui

    def visualize_gui(self):
        data = {"agentPosition": self.agent.state}
        self.gui.visualize(data)  # gwp gathers data, then calls visualize method of gwp. This method should all GUIs have.

    def initialize(self, data):
        self.environment = Environment(data)
        self.msDelay = data["msDelay"]
        self.showEveryNsteps = data["showEveryNsteps"]
        self.agent = Agent(self.environment)
        self.episodeReturns = np.array([])
        self.agent.ready()
        self.run(timestepsLeft=data["maxTimeSteps"])

    def run(self, timestepsLeft):
        print(timestepsLeft)
        self.visualize_gui()
        if not timestepsLeft:
            # make static plots
            return
        for t in range(self.showEveryNsteps):
            episodeFinished, return_ = self.agent.step()
            if episodeFinished:
                np.append(self.episodeReturns, return_)
                self.agent.ready(episodeJustEnded=True)
        self.gui.process.after(self.msDelay, lambda: self.run(timestepsLeft-self.showEveryNsteps))
