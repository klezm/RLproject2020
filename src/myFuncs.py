from functools import cache
from collections import OrderedDict
import colorsys
import webcolors
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from pprint import pprint
from pathlib import Path
import yaml
import traceback
import sys
import inspect
import re


def custom_warning(condition, importance, message, hideNadditionalStackLines=0, stream=sys.stdout):
    """
    An more customizable alternative to built-in exceptions, which in particular does not necessarily cause the program to halt.
    :param bool condition: Throw if condition does NOT hold (= evaluates to False).
    :param int importance: 2: Throw error (red color and system exit). / 1: Throw warning (orange color). 0: Throw nothing.
    :param str message: Message shown if anything was thrown.
    :param int hideNadditionalStackLines: By default, the trace will not bring the user back to this function. Use a number > 0 to hide even more of the trace.
    :param _io.TextIOWrapper stream:
    :return bool: True if error or warning was thrown, else False.
    """
    if not condition and importance:
        stack = traceback.format_stack()
        if hideNadditionalStackLines >= 0:
            stack = stack[:-(1+hideNadditionalStackLines)]
        stack = "".join(stack)
        header = ["", "\033[93mWARNING", "\033[91mERROR"]
        print(f"\n{header[importance]}: {message}\n\nStack:\n{stack}\033[0m", file=stream)
        if importance == 2:
            sys.exit(1)
        return True
    return False


def hRange(mat):
    return range(len(mat))


def wRange(mat):
    return range(len(mat[0]))


def matrix(H, W, value=0):
    return [[value for _ in range(W)] for _ in range(H)]


def matrix_like(mat, value=0):
    return [[value for _ in wRange(mat)] for _ in hRange(mat)]


def evaluate(mat, indexTuple):
    return mat[indexTuple[0]][indexTuple[1]]

def assign(mat, indexTuple, value):
    mat[indexTuple[0]][indexTuple[1]] = value


def shape(mat):
    return len(mat), len(mat[0])


@cache
def cached_power(base, exponent):
    return np.power(base, exponent)


def unit_vector(vector):
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.rad2deg(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))


@cache
def hsv_to_rgbHexString(hue, saturation, value):
    rgbTripleNormalized = colorsys.hsv_to_rgb(hue, saturation, value)
    rgbTripleInteger = tuple(int(value * 255) for value in rgbTripleNormalized)
    return webcolors.rgb_to_hex(rgbTripleInteger)


@cache
def rgbHexString_to_hsv(string):
    hsvTripleInteger = webcolors.hex_to_rgb(string)
    hsvTripleNormalized = tuple(value / 255 for value in hsvTripleInteger)
    return colorsys.rgb_to_hsv(*hsvTripleNormalized)


@cache
def direction_to_hsvHexString(direction, colorwheelAngleOffset=0, hsvValue=0.75):
    if direction == (0,0):
        return "#000000"  # black
    angle = angle_between((1,0), direction)  # arbitrary constant reference direction. Reference/Offset finetuning is more convenient by adding an angle.
    if direction[1] < 0:  # here the outer angle has to be measured
        angle = 360 - angle
    angle = (angle + colorwheelAngleOffset) % 360
    return hsv_to_rgbHexString(angle / 360, 1, hsvValue)


def get_light_color(color: str, lightness: str):
    return color.replace("0", lightness)


def center(window):
    # Centers a tkinter window. Function taken from stackoverflow.
    window.update_idletasks()  # For stability: Apply latest changes.
    # Now some magic to find the center of the visible screen, no matter what, and let the window center match that coordinates.
    width = window.winfo_width()
    frm_width = window.winfo_rootx() - window.winfo_x()
    window_width = width + 2 * frm_width
    height = window.winfo_height()
    titlebar_height = window.winfo_rooty() - window.winfo_y()
    window_height = height + titlebar_height + frm_width
    x = window.winfo_screenwidth() // 2 - window_width // 2
    y = window.winfo_screenheight() // 2 - window_height // 2
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def arrange_children(frame, order, useSticky=True, fillFrame=True, **gridKwargs):
    """
    Arranges child widgets of a tk container all in a single line using the grid geometry manager.

    :param frame: Parent container.
    :param str order: "row" assigns a new row to each child so that they will be aligned in vertical direction. "column" assigns a new column to each child so that they will be aligned in horizontal direction.
    :param bool useSticky: If True, each child will expand to use all its available space perpendicular to the direction given by the order argument.
    :param bool fillFrame: if True, the children will be aligned so that together they will use all available space in the direction given by the order argument.
    :param gridKwargs: Additional keyword arguments other than row, column or sticky that will be passed to the grid call of each child.
    """
    stickyValues = {"row": (tk.W + tk.E) * useSticky, "column": (tk.N + tk.S) * useSticky}
    gridKwargs = {"row": 0, "column": 0, "sticky": stickyValues[order]} | gridKwargs
    for i, child in enumerate(frame.winfo_children()):
        gridKwargs[order] = i
        child.grid(**gridKwargs)
        if fillFrame:
            getattr(frame, f"grid_{order}configure")(i, weight=1)


def get_dict_from_yaml_file(filepath=None, initialdir=None):
    '''
    :param pathlib.Path filepath: Path to file (.yaml suffix not necessary here). If None, opens filedialog.
    :param pathlib.Path initialdir: Initial filedialog path. If None, filedialog opens in cwd.
    :return dict: Contains content of yaml file if successful, empty if not.
    '''
    if initialdir is None:
        initialdir = "."
    else:
        initialdir = initialdir.name
    if filepath is None:
        filepath = Path(filedialog.askopenfilename(initialdir=initialdir, title="Load", filetypes=[("", "*.yaml")]))
        if not filepath.name:  # True when X was pressed
            return {}
    filepath = filepath.with_suffix(".yaml")
    with filepath.open(mode="r") as file:
        return yaml.safe_load(file)


def create_yaml_file_from_dict(inputDict, filepath=None, nameEmbedding="", initialdir=None):
    '''
    :param dict inputDict: Data dictionary that can be dumped into a yaml file
    :param pathlib.Path filepath: Path to file (.yaml suffix not necessary here). If None, opens filedialog.
    :param str nameEmbedding: String to be wrapped around a user-given filepath to structure important information in filenames without the user having to deal with it. Calls format(), so the insert position is defined by curly braces.
    :param pathlib.Path initialdir: Initial filedialog path. If None, filedialog opens in cwd.
    :return bool: False if file creation was aborted (by pressing X/cancel in filedialog or denying overwriting an already existing file), else True.
    '''
    if initialdir is None:  # Do it this way, dont put Path(".") as default arg, since it will be evaluated at function definition and will then not be influenced by calls of cd() and alike anymore
        initialdir = "."
    else:
        initialdir = initialdir.name
    if filepath is None:
        filepath = Path(filedialog.asksaveasfilename(initialdir=initialdir, title="Save", filetypes=[("", "*.yaml")]))
        if not filepath.name:  # True when X was pressed in the filedialog
            return False
    # Edge case: If a user provides a path that doesnt match an existing filepath, but does after appending ".yaml" and/or embedding it into a given nameEmbedding, the filedialog above will miss that and the old file would be overwritten without asking or giving any hint.
    chosenPath = filepath  # To handle this later, the user-given path must be stored at ths point.
    if "{}" in nameEmbedding:
        if not nameEmbedding.replace("{}", "") in filepath.name:  # user has NOT chosen a filepath that already contains the embedding
            filepath = filepath.with_stem(nameEmbedding.format(filepath.stem))
    elif nameEmbedding:  # doesnt contain "{}", but is also not empty
        custom_warning(False, 1, 'Argument "nameEmbedding" doesnt contain "{}". Embedding was therefore not applied.', 1)
    filepath = filepath.with_suffix(".yaml")
    if filepath != chosenPath and filepath.exists():  # If the edge case described above occurs: Check if the new filepath matches an already existing one and manually ask the user if he wants to overwrite.
        # To avoid asking twice if the edge case didnt occur, also check if embedding and handling the yaml ending has changed the user-given filepath at all and dont ask if it didnt.
        if messagebox.askquestion("Confirm Overwrite", f"{filepath.name} already exists.\nDo you want to overwrite it?") == "no":
            return False
    with filepath.open(mode="w") as file:
        yaml.dump(inputDict, file)
    return True


def create_font(size, family="calibri", weight="bold"):
    return f"{family} {size} {weight}"


def get_kwarg_defaults(func):
    return {name: param.default for
            name, param
            in inspect.signature(func).parameters.items()
            if param.default is not inspect._empty}


def print_default_kwargs(classObject, indent=2, width=1):
    od = OrderedDict()  # no nice orderedDict comprehension available
    for mroClass in inspect.getmro(classObject):
        if "__init__" in mroClass.__dict__.keys():
            od[mroClass.__name__] = get_kwarg_defaults(mroClass.__init__)
        else:
            od[mroClass.__name__] = f"__init___inherited_from_{mroClass.__init__.__qualname__.replace('.__init__', '')}"
            # blanks in the string instead of underscores would look bad because of width=1, which is needed for the indentation to look good
    pprint(od, indent=indent, width=width)
