from functools import cache
import colorsys
import webcolors
import numpy as np
import tkinter as tk
from tkinter import filedialog
import yaml
import traceback
import sys


def custom_warning(condition, importance, message, hideNadditionalStackLines=0):
    if not condition and importance:
        stack = traceback.format_stack()
        if hideNadditionalStackLines >= 0:
            stack = stack[:-(1+hideNadditionalStackLines)]
        stack = "".join(stack)
        header = ["", "\033[93mWARNING", "\033[91mERROR"]
        print(f"\n{header[importance]}: {message}\n\nStack:\n{stack}\033[0m")
        if importance == 2:
            sys.exit(1)
        return True
    return False


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


def arrange_children(frame, order, useSticky=True, fillFrame=True, **kwargs):
    stickyValues = {"row": (tk.W + tk.E) * useSticky, "column": (tk.N + tk.S) * useSticky}
    kwargs = {"row": 0, "column": 0, "sticky": stickyValues[order]} | kwargs
    for i, child in enumerate(frame.winfo_children()):
        kwargs[order] = i
        child.grid(**kwargs)
        if fillFrame:
            getattr(frame, f"grid_{order}configure")(i, weight=1)


def get_dict_from_yaml_file(filename=None, initialdir="."):
    if not filename:
        filename = filedialog.askopenfilename(initialdir=initialdir, title="Load", filetypes=[("", "*.yaml")])
        if not filename:
            return {}
    if not filename.endswith(".yaml"):
        filename += ".yaml"
    with open(filename, "r") as file:
        return yaml.safe_load(file)


def create_yaml_file_from_dict(inputDict, filename=None, nameEmbedding="{}", initialdir="."):
    if not filename:
        filename = filedialog.asksaveasfilename(initialdir=initialdir, title="Save", filetypes=[("", "*.yaml")])
        if not filename:
            return
    if not nameEmbedding.replace("{}", "") in filename:  # user has NOT chosen already existing file
        filename = nameEmbedding.format(filename)
    if not filename.endswith(".yaml"):
        filename += ".yaml"
    with open(filename, "w") as file:
        yaml.dump(inputDict, file)


def create_font(size, family="calibri", weight="bold"):
    return f"{family} {size} {weight}"


def set_and_call_trace(tkVar, inputFunc, passTraceargs=False, callFunc=True):
    def traceFunc(*traceArgs):
        try:  # one never wants to leave an entry empty
            if passTraceargs:
                inputFunc(*traceArgs)
            else:
                inputFunc()
        except:
            return
    tkVar.trace_add("write", traceFunc)
    if callFunc:
        traceFunc()


# class ToolTip:
#     """
#     Create a tooltip for a given widget
#     (inspired by https://stackoverflow.com/a/36221216)
#     This is an INTERNALLY USED only class.  Users should not refer to this class at all.
#     """
#
#     def __init__(self, widget, text, timeout=DEFAULT_TOOLTIP_TIME):
#         """
#         :param widget: The tkinter widget
#         :type widget: widget type varies
#         :param text: text for the tooltip. It can inslude \n
#         :type text: (str)
#         :param timeout: Time in milliseconds that mouse must remain still before tip is shown
#         :type timeout: (int)
#         """
#         self.widget = widget
#         self.text = text
#         self.timeout = timeout
#         # self.wraplength = wraplength if wraplength else widget.winfo_screenwidth() // 2
#         self.tipwindow = None
#         self.id = None
#         self.x = self.y = 0
#         self.widget.bind("<Enter>", self.enter)
#         self.widget.bind("<Leave>", self.leave)
#         self.widget.bind("<ButtonPress>", self.leave)
#
#     def enter(self, event=None):
#         """
#         Called by tkinter when mouse enters a widget
#         :param event:  from tkinter.  Has x,y coordinates of mouse
#
#         """
#         self.x = event.x
#         self.y = event.y
#         self.schedule()
#
#     def leave(self, event=None):
#         """
#         Called by tktiner when mouse exits a widget
#         :param event:  from tkinter.  Event info that's not used by function.
#
#         """
#         self.unschedule()
#         self.hidetip()
#
#     def schedule(self):
#         """
#         Schedule a timer to time how long mouse is hovering
#         """
#         self.unschedule()
#         self.id = self.widget.after(self.timeout, self.showtip)
#
#     def unschedule(self):
#         """
#         Cancel timer used to time mouse hover
#         """
#         if self.id:
#             self.widget.after_cancel(self.id)
#         self.id = None
#
#     def showtip(self):
#         """
#         Creates a topoltip window with the tooltip text inside of it
#         """
#         if self.tipwindow:
#             return
#         x = self.widget.winfo_rootx() + self.x + DEFAULT_TOOLTIP_OFFSET[0]
#         y = self.widget.winfo_rooty() + self.y + DEFAULT_TOOLTIP_OFFSET[1]
#         self.tipwindow = tk.Toplevel(self.widget)
#         # if not sys.platform.startswith('darwin'):
#         try:
#             self.tipwindow.wm_overrideredirect(True)
#         except:
#             print('* Error performing wm_overrideredirect *')
#         self.tipwindow.wm_geometry("+%d+%d" % (x, y))
#         self.tipwindow.wm_attributes("-topmost", 1)
#
#         label = ttk.Label(self.tipwindow, text=self.text, justify=tk.LEFT,
#                           background=TOOLTIP_BACKGROUND_COLOR, relief=tk.SOLID, borderwidth=1)
#         if TOOLTIP_FONT is not None:
#             label.config(font=TOOLTIP_FONT)
#         label.pack()
#
#     def hidetip(self):
#         """
#         Destroy the tooltip window
#         """
#         if self.tipwindow:
#             self.tipwindow.destroy()
#         self.tipwindow = None