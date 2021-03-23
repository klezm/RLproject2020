from Agent import Agent
from Environment import Environment

class GridworldPlayground:
    def __init__(self):
        self.gui = None
        self.environment = None
        self.agent = None

    def set_gui(self, gui):
        self.gui = gui

    def visualize(self):
        data = {"agentPosition": self.agent.state}
        self.gui.visualize(data)  # gwpg gathers data, then calls visualize method of gwpg. This method should all GUIs have.

    def initialize(self, data):
        self.environment = Environment(data)
        self.agent = Agent(self.environment)
        self.agent.ready()
        self.visualize()  # initial visualization
        for t in range(data["maxTimeSteps"]):
            self.agent.step()
            self.visualize()
