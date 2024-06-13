import tkinter as tk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib
from datetime import datetime
from PIL import Image, ImageTk
import re
from xml.sax.saxutils import escape

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

# local import
import basedialog
import simlabutil
import widget as wt
import tooltip as tp
import backup
import messageboxWithCheckbox as mc
import simlablib
import grouputil

class FaceMergeDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup, config):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.backup = backup
        self.config = config

        self.master.title('面結合')
        self.CreateWidgets()
        simlab.setSelectionFilter('Face')

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.lblNote1 = tk.Label(self.frmTop, text='Tips: 結合したい面を選択して、[ 結合 ]ボタンを押してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmFig = tk.Frame(self.frmTop)
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER)
        self.imgFace = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'facemerge.png')), master=self.frmFig)
        tk.Label(self.frmFig, image=self.imgFace).pack(side=tk.TOP, anchor=tk.CENTER)

        # self.preserveEdge = tk.BooleanVar()
        # self.preserveEdge.set(False)
        # self.remeshCheck = tk.Checkbutton(self.frmTop, text="Preserve Boundary Edge", variable=self.preserveEdge)
        # self.remeshCheck.pack(side=tk.TOP, anchor=tk.SE, pady=2)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)        

        btnWidth = 10
        self.btnMerge = tk.Button(self.frmCtrl, text=' 結合 ', compound=tk.LEFT, command=self.Merge, width=btnWidth)
        self.btnMerge.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.tpMerge = tp.ToolTip(self.btnMerge, '選択したボディを結合します。', self.master)
        self.tpUndo = tp.ToolTip(self.btnUndo, '操作を戻します。', self.master)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def Merge(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) < 2:
            messagebox.showinfo('情報','結合したい面を2つ以上選択してください。')
            return

        self.backup.Save('FaceMerge')

        importlib.reload(grouputil)
        # preserveEdge = self.preserveEdge.get()
        grouputil.mergeFaces(faces)

    def Undo(self):
        self.backup.Load()
    
        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')
    


