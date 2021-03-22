import tkinter as tk
import numpy as np

import GUI
import GridworldPlayground

'''
class Gridworld:
    def __init__(self, frame):
        self.frame = frame


class State:
    def __init__(self, env, x, y):
        pass
'''


class RLproject:
    def __init__(self, root):
        self.gp = GridworldPlayground.GridworldPlayground()
        self.gui = GUI.GUI(root)
        self.gp.set_gui(self.gui)
        self.gui.set_gp(self.gp)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    RLproject(root)
    root.mainloop()
