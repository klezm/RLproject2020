import tkinter as tk
import argparse

from GridworldSandbox import GridworldSandbox


def main():
    args = arg_parser()
    root = tk.Tk()
    root.withdraw()
    GridworldSandbox(guiProcess = root, pargs = args)
    root.mainloop()


def arg_parser():
    """
    Use e.g. --grid-shape 9 --steps 10000000 --refresh-rate 1 --show-rate 100 --off-policy --grid-world-template 13
    """
    parse = argparse.ArgumentParser()
    parse.add_argument("-s", "--grid-shape", action = "extend", nargs = "+", metavar = ("x", "y"), type = int,
                       help = "Choose the dimensions for the gridworld.")
    parse.add_argument("--steps", default = 100000, type = int, help = "Number of steps to run the training.")
    parse.add_argument("--refresh-rate", default = 10, type = int, help = "refresh rate for visualizatio in [ms]")
    parse.add_argument("--show-rate", default = 1, type = int, help = "render every nth frame")
    parse.add_argument("--lr", "--learning-rate", default = .1, type = float, help = "learning rate")
    parse.add_argument("--discount", default = 1, type = float, help = "discounted rewards")
    parse.add_argument("--n-step-n", default = 1, type = int, help = "n-step n")
    parse.add_argument("--dyna-q-n", default = 0, type = int, help = "dyna-q n")
    parse.add_argument("--off-policy", action = "store_false", help = "Use off policy")
    parse.add_argument("--use-expectation", action = "store_true", help = "Update by expectation")
    parse.add_argument("--exploration-rate", default = .5, type = float, help = "Exploration rate")
    parse.add_argument("--exploration-rate-decay", default = .9999, type = float, help = "Exploration decay rate")
    parse.add_argument("--grid-world-template", type = int, help = "Use the nth grid world preset.")

    args = parse.parse_args()
    if args.grid_shape is not None and len(args.grid_shape) > 2:
        parse.error("--grid-shape accepts either separated or one shared value for x and y")

    return vars(args)


if __name__ == "__main__":
    main()
