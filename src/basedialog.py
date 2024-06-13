# coding: utf_8
# SimLab Version 2019.2 (64-bit)
#***************************************************************
import tkinter as tk
import os, sys, importlib

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

class BaseDialog(tk.Frame):
    def __init__(self, master, parent):
        super().__init__(master)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.parent = parent
        rootx, rooty = self.GetParentPosition()
        self.parent.iconify()

        self.master.resizable(width=False, height=False)
        self.master.attributes("-topmost", True)
        self.master.protocol("WM_DELETE_WINDOW", self.CloseDialog)
        self.master.wm_geometry("+%d+%d" % (rootx, rooty))
        
    def GetParentPosition(self):
        x = y = 0
        x, y, _, _ = self.parent.bbox("insert")
        x += self.parent.winfo_rootx()
        y += self.parent.winfo_rooty()
        return x, y

    def CloseDialog(self):
        self.master.destroy()
        self.parent.deiconify()