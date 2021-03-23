import tkinter as tk
import numpy as np

from GUI import GUI
from GridworldPlayground import GridworldPlayground


class RLproject:
    def __init__(self, guiProcess):
        self.gwp = GridworldPlayground()
        self.gui = GUI(process=guiProcess)
        self.gwp.set_gui(self.gui)
        self.gui.set_gwp(self.gwp)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    RLproject(guiProcess=root)
    root.mainloop()
