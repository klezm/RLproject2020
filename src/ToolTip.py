import tkinter as tk


class ToolTip(tk.Toplevel):
    """Dynamic, intuitive tooltip for arbitrary ``tkinter Widgets``
    """
    def __init__(self, master, delay=400, **labelKwargs):  # delay in ms
        """ Creates a ``Tooltip`` object. Manages a single ``packed tk.Label`` inside to display text.

        :param master: Parent Widget
        :param delay: Time delay in milliseconds until the Tooltip appears after entering the parent widget with the cursor.
        :param labelKwargs: Keyword arguments passed to the initialization call of the tk.Label inside.
        """
        self.delay = delay
        super().__init__(master)
        self.withdraw()
        self.wm_attributes("-topmost", 1)
        self.wm_overrideredirect(True)
        tk.Label(self, justify=tk.LEFT, bg="white", borderwidth=1,
                 relief=tk.SOLID, **labelKwargs).pack(ipadx=3)
        self.afterId = None
        self.master.bind("<Enter>", lambda _: self._enter())
        for event in ("<Leave>", "<Button>", "<Key>"):
            self.master.bind(event, lambda _: self._leave())

    def _enter(self):
        self.afterId = self.after(self.delay, self._show_tip)

    def _show_tip(self):
        x = self.master.winfo_pointerx() + 10
        y = self.master.winfo_pointery()
        # That extra pixels are crucial: otherwise the tooltip would
        # appear DIRECTLY under the cursor, immediately causing the
        # cursor to leave() the widget again because it "entered" the
        # tooltip, which therefore would never become visible.
        self.wm_geometry(f"+{x}+{y}")
        self.deiconify()

    def _leave(self):
        self.master.winfo_toplevel().deiconify()  # Prevents the master-toplevel from iconifying if the curser left the widget directly via the toplevel border
        self.withdraw()
        if self.afterId is not None:
            self.afterId = self.after_cancel(self.afterId)  # returns None


def main():
    try:
        from myFuncs import print_default_kwargs
        print_default_kwargs(ToolTip)
    except Exception:
        pass

    root = tk.Tk()
    for i in range(5):
        label = tk.Label(root, text=f"Label {i}", bg="#" + 6 * str(i+5), width=i+7)
        label.pack()
        ToolTip(label, text=f"Tooltip {i}")
    root.mainloop()


if __name__ == "__main__":
    main()
