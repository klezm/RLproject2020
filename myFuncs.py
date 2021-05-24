from functools import cache
import colorsys
import webcolors
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import yaml


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


def arrange_children(frame, rowDiff=0, columnDiff=0, useSticky=True, **kwargs):
    sticky = ""
    if rowDiff:
        if useSticky:
            sticky = tk.W + tk.E
        rowspan = rowDiff
        columnspan = 1
    if columnDiff:
        if useSticky:
            sticky = tk.N + tk.S
        rowspan = 1
        columnspan = columnDiff
    row = 0
    column = 0
    for child in frame.winfo_children():
        child.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, **kwargs)
        row += rowDiff
        column += columnDiff


def get_dict_from_yaml_file(filename=None, initialdir="."):
    if not filename:
        filename = filedialog.askopenfilename(initialdir=initialdir, filetypes=[("", "*.yaml")])
    else:
        filename += ".yaml"
    with open(filename, "r") as file:
        return yaml.safe_load(file)


def create_yaml_file_from_dict(inputDict, filename=None):
    if filename is None:
        filename = simpledialog.askstring("Name", "Please enter name.")
    with open(filename + ".yaml", "w") as file:
        yaml.dump(inputDict, file)


def create_font(size, family= "calibri", weight="bold"):
    return f"{family} {size} {weight}"
