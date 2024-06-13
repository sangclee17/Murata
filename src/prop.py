import tkinter as tk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

# local import
import basedialog
import tooltip as tp
import widget

class PropertyDlg(basedialog.BaseDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('物性値割り当て')
        self.CreateWidgets()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.frmParam = tk.Frame(self.frmTop)
        self.frmParam.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X)

        tk.Label(self.frmParam, text='Not impliment.').pack()

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
