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
        self.agent = Agent(self.environment)
        self.agent.ready()
        self.run(timestepsLeft=data["maxTimeSteps"])

    def run(self, timestepsLeft):
        self.visualize_gui()
        if not timestepsLeft:
            # make static plots
            return
        self.agent.step()
        self.gui.process.after(self.msDelay, lambda: self.run(timestepsLeft-1))
