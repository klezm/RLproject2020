import tkinter as tk

from GUI import GUI, FlowStates
from GridworldPlayground import GridworldPlayground
from Agent import Agent, Operations


class RLproject:
    def __init__(self, guiProcess):
        self.gridworldPlayground = GridworldPlayground(flowStates=FlowStates)  # TODO: Set gui.status as arg
        self.gui = GUI(process=guiProcess, agentActionspace=Agent.ACTIONSPACE, agentOperations=Operations)
        self.gridworldPlayground.set_gui(self.gui)
        self.gui.set_gridworldPlayground(self.gridworldPlayground)


def main():
    root = tk.Tk()
    root.withdraw()
    RLproject(guiProcess=root)
    root.mainloop()


if __name__ == "__main__":
    main()
