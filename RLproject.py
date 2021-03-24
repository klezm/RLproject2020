import tkinter as tk

from GUI import GUI
from GridworldPlayground import GridworldPlayground
from Agent import Agent


class RLproject:
    def __init__(self, guiProcess):
        self.gridworldPlayground = GridworldPlayground()
        self.gui = GUI(process=guiProcess, actionspace=Agent.ACTIONS)
        self.gridworldPlayground.set_gui(self.gui)
        self.gui.set_gridworldPlayground(self.gridworldPlayground)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    RLproject(guiProcess=root)
    root.mainloop()
