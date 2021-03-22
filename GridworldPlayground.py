class GridworldPlayground:
    def __init__(self):
        self.gui = None

    def set_gui(self, gui):
        self.gui = gui

    def visualize(self):
        data = None  # gather data
        self.gui.visualize(data)

    def initialize(self, data):
        # start env and agent
        pass