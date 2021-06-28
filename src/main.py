import tkinter as tk

from src.GridworldSandbox import GridworldSandbox


def main():
    root = tk.Tk()
    root.withdraw()
    GridworldSandbox(guiProcess=root)
    root.mainloop()


if __name__ == "__main__":
    main()
