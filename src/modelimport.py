import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from hwx import simlab
import os, sys, importlib
from PIL import Image, ImageTk

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

# local import
import basedialog
import simlabutil
import simlablib
import boolean
import tooltip as tp
import assemStructure

class ModelImportDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, springs):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.springs = springs

        self.master.title('モデル読み込み')
        self.CreateWidgets()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.lblNote1 = tk.Label(self.frmTop, text='Tips: [インポート]ボタンを押してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmPath = tk.Frame(self.frmTop)
        self.frmPath.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        tk.Label(self.frmPath, text='CSVファイル:').grid(row=0, column=0)
        self.CSVPath = tk.StringVar()
        self.entCSVPath = tk.Entry(self.frmPath, textvariable=self.CSVPath, width=50)
        self.entCSVPath.grid(row=0, column=1, sticky='nwse')
        self.iconCSVFolder = ImageTk.PhotoImage(file=(os.path.join(IMAGE_DIR, 'openfolder.gif')))
        self.btnCSVPath = tk.Button(self.frmPath, image=self.iconCSVFolder, command=self.SelectCSV)
        self.btnCSVPath.grid(row=0, column=2)

        tk.Frame(self.frmPath, height=5).grid(row=1, column=0)

        tk.Label(self.frmPath, text='CADファイル:').grid(row=2, column=0)
        self.CADPath = tk.StringVar()
        self.entCADPath = tk.Entry(self.frmPath, textvariable=self.CADPath, width=50)
        self.entCADPath.grid(row=2, column=1, sticky='nwse')
        self.iconCADFolder = ImageTk.PhotoImage(file=(os.path.join(IMAGE_DIR, 'openfolder.gif')))
        self.btnCADPath = tk.Button(self.frmPath, image=self.iconCADFolder, command=self.SelectCAD)
        self.btnCADPath.grid(row=2, column=2)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        btnWidth = 10
        self.btnMerge = tk.Button(self.frmCtrl, text=' インポート ', command=self.ImportModel, width=btnWidth)
        self.btnMerge.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def SelectCSV(self):
        fileType = [('CSV','*.csv'), ('All files','*.*')]

        initDir = PROJECT_DIR
        if os.path.isfile(self.CSVPath.get()):
            initDir = os.path.dirname(self.CSVPath.get())
        elif os.path.isfile(self.CADPath.get()):
            initDir = os.path.dirname(self.CADPath.get())

        path = filedialog.askopenfilename(filetypes=fileType, initialdir=initDir)
        if not os.path.isfile(path):
            return

        self.CSVPath.set(path)

    def SelectCAD(self):
        fileType = [('Parasolid','*.x_t;*.xmt_txt;*x_b'), ('SimLab','*.slb'), ('All files','*.*')]

        initDir = PROJECT_DIR
        if os.path.isfile(self.CADPath.get()):
            initDir = os.path.dirname(self.CADPath.get())
        elif os.path.isfile(self.CSVPath.get()):
            initDir = os.path.dirname(self.CSVPath.get())

        path = filedialog.askopenfilename(filetypes=fileType, initialdir=initDir)
        if not os.path.isfile(path):
            return

        self.CADPath.set(path)

    def ImportModel(self):
        if not os.path.isfile(self.CSVPath.get()):
            messagebox.showinfo('情報', 'CSVファイルを指定してください。')
            return
        if not os.path.isfile(self.CADPath.get()):
            messagebox.showinfo('情報', 'CADファイルを指定してください。')
            return

        importlib.reload(simlablib)
        params = {'Imprint':1}
        simlablib.ImportFile(self.CADPath.get(), params=params)
        importlib.reload(assemStructure)
        assemStructure.importCSV(self.CSVPath.get())
        assemStructure.getBodyMass()
        self.springs.Import(self.CSVPath.get())
        simlablib.UpdateFeatures("CAD")


