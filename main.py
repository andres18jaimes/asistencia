import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

import tkinter as tk
from presentation.main_window import MainWindow


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()