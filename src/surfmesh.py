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

class SurfMeshDlg(basedialog.BaseDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('サーフェイスメッシュ作成')
        self.CreateWidgets()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.frmParam = tk.Frame(self.frmTop)
        self.frmParam.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X)

        if simlab.isParameterPresent('DefaultMeshSize'):
            defaultMeshSize = simlab.getDoubleParameter('$DefaultMeshSize')
        else:
            defaultMeshSize = 20
        self.entSize = widget.LabelEntry(self.frmParam, text='要素長:', width=5, value=defaultMeshSize)
        self.entSize.pack(side=tk.LEFT, anchor=tk.W)
        self.entAngle = widget.LabelEntry(self.frmParam, text='最大要素角:', width=5, value=45)
        self.entAngle.pack(side=tk.LEFT, anchor=tk.W)
        self.entAspect = widget.LabelEntry(self.frmParam, text='アスペクト比:', width=5, value=10)
        self.entAspect.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmParam2 = tk.Frame(self.frmTop)
        self.frmParam2.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X)

        self.entDefHole = widget.LabelEntry(self.frmParam2, text='削除する穴の最大直径:', width=5, value=20)
        self.entDefHole.pack(side=tk.LEFT, anchor=tk.W)

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
            angle = float(self.entAngle.Get())
            aspect = float(self.entAspect.Get())
            hole = float(self.entDefHole.Get()) * 0.5
        except:
            messagebox.showinfo('情報', '実数で指定してください')
            return

        importlib.reload(meshutil)
        meshProp = size, angle, aspect
        meshutil.surfaceMesh(meshProp, hole)