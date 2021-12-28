import tkinter as tk

from GridworldSandbox import GridworldSandbox


def main():
    """Sets up a ``tkinter`` root process, a ``GridworldSandbox``, and connects them.
    """
    root = tk.Tk()
    root.withdraw()  # dont wanna use the root process like a toplevel
    GridworldSandbox(guiProcess=root)
    root.mainloop()


if __name__ == "__main__":
    main()
