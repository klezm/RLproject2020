import tkinter as tk

from GridworldSandbox import GridworldSandbox

"""A reinforcement learner that interacts with a gridworld environment
by passing actions to it and receiving rewards and successor states from it.
It is able to apply a variety of tabular temporal difference control algorithms
introduced in the book "Reinforcement Learning - An Introduction by Sutton & Barto,
aswell as combinations between those algorithms. It also passes detailed information
about its actions, decision making and value tables to a GUI."""

def main():
    """Sets up a tkinter GUI, a GridworldSandbox, and connects them."""
    root = tk.Tk()
    root.withdraw()
    GridworldSandbox(guiProcess=root)
    root.mainloop()


if __name__ == "__main__":
    main()
