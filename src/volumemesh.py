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
import meshutil

class VolumeMeshDlg(basedialog.BaseDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('ボリュームメッシュ作成')
        self.CreateWidgets()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.frmParam = tk.Frame(self.frmTop)
        self.frmParam.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X)

        self.entSize = widget.LabelEntry(self.frmParam, text='要素長:', width=5, value=20)
        self.entSize.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnMerge = tk.Button(self.frmCtrl, text=' 作成 ', command=self.Create, width=btnWidth)
        self.btnMerge.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def Create(self):
        try:
            size = float(self.entSize.Get())
        except:
            messagebox.showinfo('情報', '実数を指定してください')
            return

        importlib.reload(meshutil)
        stretchMinVal = 0.01
        meshutil.volumeMesh(size, stretchMinVal)
