import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

# local import
import basedialog
import simlabutil
import simlablib
import tooltip as tp
import grouputil

class UnitEntry(tk.Frame):
    def __init__(self, master, unit='[mm]', width=10, default=''):
        super().__init__(master)
        self.CreateWidgets(unit, width, default)

    def CreateWidgets(self, unit, width, default):
        self.ent = tk.Entry(self, width=width)
        self.ent.insert(tk.END, str(default))
        self.ent.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.lbl = tk.Label(self, text=unit)
        self.lbl.pack(side=tk.LEFT, anchor=tk.W, padx=5)

    def get(self):
        return self.ent.get()

class UnitCombobox(tk.Frame):
    def __init__(self, master, unit='[mm]', width=10, values=[], default=''):
        super().__init__(master)
        self.CreateWidgets(unit, width, values, default)

    def CreateWidgets(self, unit, width, values, default):
        self.val = tk.StringVar()
        self.val.set(default)
        self.cmb = ttk.Combobox(self, textvariable=self.val, values=values, width=width)
        self.cmb.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.lbl = tk.Label(self, text=unit)
        self.lbl.pack(side=tk.LEFT, anchor=tk.W, padx=5)

    def get(self):
        return self.val.get()

class MeshCtrlDlg(basedialog.BaseDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('メッシュコントロール作成')
        self.CreateWidgets()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.lblNote1 = tk.Label(self.frmTop, text='Tips: [作成]ボタンを押してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        ## ISO Line
        self.frmISOTabTop = tk.LabelFrame(self.frmTop, text='ISO Line :')
        self.frmISOTabTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        # ISO-Line table
        tk.Frame(self.frmISOTabTop, width=10).pack(side=tk.LEFT, anchor=tk.W)
        self.frmISOTab = tk.Frame(self.frmISOTabTop)
        self.frmISOTab.pack(side=tk.LEFT, anchor=tk.W, expand=1, fill=tk.X)
        self.frmISOTab.grid_columnconfigure((0,1,2,3), weight=1)
        self.frmISOTab.grid_rowconfigure((0,1,2,3), weight=1)

        # header
        row = 0
        tk.Label(self.frmISOTab, text='軸方向長さ').grid(row=row, column=1)
        tk.Label(self.frmISOTab, text='分割数').grid(row=row, column=2)
        tk.Label(self.frmISOTab, text='最大検索直径', fg='red').grid(row=row, column=3)

        # S
        nrow = 1
        tk.Label(self.frmISOTab, text='Sサイズ :  ').grid(row=nrow, column=0, sticky='nw')
        self.entSISOSize = UnitEntry(self.frmISOTab, unit='[mm]', width=5, default=20)
        self.entSISOSize.grid(row=nrow, column=1)
        self.cmbSISOAngle = UnitCombobox(self.frmISOTab, unit='', width=5, values=['4', '6', '8', '12', '24'], default='8')
        self.cmbSISOAngle.grid(row=nrow, column=2)
        self.entSISORadius = UnitEntry(self.frmISOTab, unit='[mm]', width=5, default=35)
        self.entSISORadius.grid(row=nrow, column=3)
        nrow = 2
        tk.Frame(self.frmISOTab, height=5).grid(row=nrow, column=0)

        ## Defeature
        self.frmHole = tk.LabelFrame(self.frmTop, text='Defeaure hole :')
        self.frmHole.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        self.frmHoleEnt = tk.Frame(self.frmHole)
        self.frmHoleEnt.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        tk.Label(self.frmHoleEnt, text='最大検索直径 :').pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=5)
        self.entHole = UnitEntry(self.frmHoleEnt, unit='[mm]', width=5, default=22)
        self.entHole.pack(side=tk.LEFT, anchor=tk.W)
        tk.Label(self.frmHole, text='＊グループで指定したボルト穴は除外されます。').pack(side=tk.TOP, anchor=tk.W)
        tk.Frame(self.frmHole, height=5).pack(side=tk.TOP, anchor=tk.NW)
        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        btnWidth = 10
        self.btnMerge = tk.Button(self.frmCtrl, text=' 作成 ', command=self.CreateMeshCtrl, width=btnWidth)
        self.btnMerge.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def CreateMeshCtrl(self):
        importlib.reload(grouputil)
        # user request :
        # angle -> division numbers
        # diameter -> radius
        isoMeshSize = float(self.entSISOSize.get())
        isoAngle = 360.0 / float(self.cmbSISOAngle.get())
        bigHoleSize = 0.5 * float(self.entSISORadius.get())
        smallHoleSize = 0.5 * float(self.entHole.get())

        importlib.reload(grouputil)
        grouputil.applyMeshControl(isoMeshSize, isoAngle, smallHoleSize, bigHoleSize)
