import tkinter as tk
import numpy as np

from GUI import GUI
from GridworldPlayground import GridworldPlayground


class RLproject:
    def __init__(self, root):
        self.gwpg = GridworldPlayground()
        self.gui = GUI(root)
        self.gwpg.set_gui(self.gui)
        self.gui.set_gwpg(self.gwpg)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    RLproject(root)
    root.mainloop()
