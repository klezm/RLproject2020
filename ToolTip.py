import tkinter as tk


class ToolTip:
    delayDefault = 400  # [ms]

    def __init__(self, widget, delay=None, **labelKwargs):
        self.widget = widget
        self.delay = self.delayDefault if delay is None else delay
        self.tipWindow = tk.Toplevel(self.widget)
        self.tipWindow.withdraw()
        self.tipWindow.wm_attributes("-topmost", 1)
        self.tipWindow.wm_overrideredirect(True)
        tk.Label(self.tipWindow, justify=tk.LEFT, bg="white", borderwidth=1,
                 relief=tk.SOLID, **labelKwargs).pack(ipadx=3)
        self.afterId = None
        self.widget.bind("<Enter>", lambda _: self.enter())
        for event in ("<Leave>", "<Button>", "<Key>"):
            self.widget.bind(event, lambda _: self.leave())

    def enter(self):
        self.afterId = self.widget.after(self.delay, self.show_tip)

    def show_tip(self):
        x = self.widget.winfo_pointerx() + 10
        y = self.widget.winfo_pointery()
        # That extra pixels are crucial: otherwise the tooltip would
        # appear DIRECTLY under the cursor, immediately causing the
        # cursor to leave() the varWidget again because it "entered" the
        # tooltip, which therefore would never become visible.
        self.tipWindow.wm_geometry(f"+{x}+{y}")
        self.tipWindow.deiconify()

    def leave(self):
        self.tipWindow.withdraw()
        if self.afterId is not None:
            self.widget.after_cancel(self.afterId)
            self.afterId = None


if __name__ == "__main__":
    root = tk.Tk()
    for i in range(5):
        label = tk.Label(root, text=f"Label {i}",
                         bg="#" + 6 * str(i+5), width=i+7)
        label.pack()
        ToolTip(label, text=f"Tooltip {i}")
    root.mainloop()
