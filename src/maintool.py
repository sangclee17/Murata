# coding: utf_8
# SimLab Version 2019.2 (64-bit)
#***************************************************************
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import sys, os
from PIL import Image, ImageTk
import win32gui
import importlib
from hwx import simlab

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))
LOG_DIR = (os.path.join(PROJECT_DIR, 'log'))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

## local import
import tooltip
import history
import configreader
import backup
import modelimport
import modelinfo
import boolean
import groupinfo
import meshctrl
import surfmesh
import simplify
import fillhole
import bearing
import coordinate
import mpc
import mass
import mass2
import bolt
import spring
import volumemesh
import prop
import propertyutil
import export
import simlablib
import axisbeam
import facemerge
import springcsv
import linearguide

## Main Tool Widget
class MainTool(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        # member
        self.dialog = None
        self.config = configreader.ConfigReader()
        self.backup = backup.ModelBackup(self.config)
        self.springs = springcsv.SpringCSV()

        # gui static const
        self.btnWidth = 25
        self.dummyHeight = 10
        self.dummyWidth = 10

        # dialog attribute
        self.master.title('モデリングツール')
        self.master.resizable(width=False, height=False)
        self.master.attributes("-topmost", True)
        self.master.protocol("WM_DELETE_WINDOW", self.CloseDialog)
        _, _, (x,y) = win32gui.GetCursorInfo()
        self.master.wm_geometry("+%d+%d" % (x, y))

        # widget
        self.CreateWidgets()
        self.history = history.MenuHistory(self)

    def CreateWidgets(self):
        self.grid_columnconfigure((0), weight=1)
        self.grid_rowconfigure((0), weight=1)

        self.frmTop = tk.Frame(self)
        self.frmTop.grid(row=0, column=0, sticky='nwse', padx=5, pady=5)
        self.frmTop.grid_columnconfigure((0,2), weight=1)
        self.frmTop.grid_rowconfigure((0,2,4), weight=1)

        self.CreateMeshingWidget()
        self.CreateShapeCorrection()
        self.CreateLinkWidget()
        self.CreateAnalysisWidget()
        self.CreateIconWidget()
        self.CreateLines()

    def CreateMeshingWidget(self):
        self.frmMeshLeft = tk.Frame(self.frmTop)
        self.frmMeshLeft.grid(row=0, column=0, sticky='nwse')

        self.lblCAD = tk.Label(self.frmMeshLeft, text='モデリング :   ')
        self.lblCAD.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmTop, width=self.dummyWidth).grid(row=0, column=1, sticky='nwse')

        self.frmMeshRight = tk.Frame(self.frmTop)
        self.frmMeshRight.grid(row=0, column=2, sticky='nwse')
        self.frmMeshRight.grid_columnconfigure(0, weight=1)

        self.frmMeshBtn = tk.Frame(self.frmMeshRight)
        self.frmMeshBtn.grid(row=1, column=0, sticky='nwse')
        self.frmMeshBtn.grid_columnconfigure((0,1), weight=1)

        self.btnImport = tk.Button(self.frmMeshBtn, text='モデル読み込み', command=self.LaunchModelImportDialog, width=self.btnWidth)
        self.btnImport.grid(row=0, column=0, sticky='nwse')
        self.btnModel = tk.Button(self.frmMeshBtn, text='モデル情報確認', command=self.LaunchModelInfoDialog, width=self.btnWidth)
        self.btnModel.grid(row=0, column=1, sticky='nwse')
        self.btnGroup = tk.Button(self.frmMeshBtn, text='グループ', command=self.LaunchGroupDialog, width=self.btnWidth)
        self.btnGroup.grid(row=1, column=0, sticky='nwse')
        self.btnSurfMesh = tk.Button(self.frmMeshBtn, text='サーフェイスメッシュ作成', command=self.LaunchSurfaceMeshDialog, width=self.btnWidth)
        self.btnSurfMesh.grid(row=1, column=1, sticky='nwse')

    def CreateShapeCorrection(self):
        tk.Frame(self.frmTop, height=self.dummyHeight).grid(row=1, column=0, sticky='nwse')

        self.frmSCLeft = tk.Frame(self.frmTop)
        self.frmSCLeft.grid(row=2, column=0, sticky='nwse')

        self.lblSC = tk.Label(self.frmSCLeft, text='形状補正 :   ')
        self.lblSC.pack(side=tk.TOP, anchor=tk.NW)

        self.frmSCRight = tk.Frame(self.frmTop)
        self.frmSCRight.grid(row=2, column=2, sticky='nwse')
        self.frmSCRight.grid_columnconfigure((0,1), weight=1)

        self.btnFillHole = tk.Button(self.frmSCRight, text='穴埋め', command=self.LaunchFillHoleDialog, width=self.btnWidth)
        self.btnFillHole.grid(row=0, column=0, sticky='nwse')
        self.btnSimplify = tk.Button(self.frmSCRight, text='形状簡略化', command=self.LaunchSimplifyDialog, width=self.btnWidth)
        self.btnSimplify.grid(row=0, column=1, sticky='nwse')
        self.btnMerge = tk.Button(self.frmSCRight, text='面結合', command=self.LaunchMergeDialog, width=self.btnWidth)
        self.btnMerge.grid(row=1, column=0, sticky='nwse')
        self.btnJoin = tk.Button(self.frmSCRight, text='節点共有', command=self.LaunchShareNodeDialog, width=self.btnWidth)
        self.btnJoin.grid(row=1, column=1, sticky='nwse')

    def CreateLinkWidget(self):
        tk.Frame(self.frmTop, height=self.dummyHeight).grid(row=3, column=0, sticky='nwse')

        self.frmLLeft = tk.Frame(self.frmTop)
        self.frmLLeft.grid(row=4, column=0, sticky='nwse')

        self.lblLC = tk.Label(self.frmLLeft, text='リンク要素 :   ')
        self.lblLC.pack(side=tk.TOP, anchor=tk.NW)

        self.frmLCRight = tk.Frame(self.frmTop)
        self.frmLCRight.grid(row=4, column=2, sticky='nwse')
        self.frmLCRight.grid_columnconfigure((0,1), weight=1)

        self.btnSys = tk.Button(self.frmLCRight, text='座標系作成', command=self.LaunchSysDialog, width=self.btnWidth)
        self.btnSys.grid(row=0, column=0, sticky='nwse')
        self.btnMPC = tk.Button(self.frmLCRight, text='MPC作成', command=self.LaunchMPCDialog, width=self.btnWidth)
        self.btnMPC.grid(row=0, column=1, sticky='nwse')
        self.btnBearing = tk.Button(self.frmLCRight, text='ベアリング作成', command=self.LaunchBearingDialog, width=self.btnWidth)
        self.btnBearing.grid(row=1, column=0, sticky='nwse')
        self.btnBolt = tk.Button(self.frmLCRight, text='ボルト作成', command=self.LaunchBoltDialog, width=self.btnWidth)
        self.btnBolt.grid(row=1, column=1, sticky='nwse')
        self.btnSpring = tk.Button(self.frmLCRight, text='バネ、RBE作成', command=self.LaunchSpringDialog, width=self.btnWidth)
        self.btnSpring.grid(row=2, column=0, sticky='nwse')
        self.btnLinearGuide = tk.Button(self.frmLCRight, text='リニアガイド', command=self.LaunchLinearGuideDialog, width=self.btnWidth)
        self.btnLinearGuide.grid(row=2, column=1, sticky='nwse')
        self.btnVolume = tk.Button(self.frmLCRight, text='ボリュームメッシュ作成', command=self.LaunchVolumeMeshDialog, width=self.btnWidth)
        self.btnVolume.grid(row=3, column=0, sticky='nwse')

    def CreateAnalysisWidget(self):
        tk.Frame(self.frmTop, height=self.dummyHeight).grid(row=5, column=0, sticky='nwse')

        self.frmAnLeft = tk.Frame(self.frmTop)
        self.frmAnLeft.grid(row=6, column=0, sticky='nwse')

        self.lblAn = tk.Label(self.frmAnLeft, text='解析設定 :   ')
        self.lblAn.pack(side=tk.TOP, anchor=tk.NW)

        self.frmAnRight = tk.Frame(self.frmTop)
        self.frmAnRight.grid(row=6, column=2, sticky='nwse')
        self.frmAnRight.grid_columnconfigure((0,1), weight=1)

        self.btnProperty  = tk.Button(self.frmAnRight, text='物性値作成', command=self.LaunchPropertyDialog, width=self.btnWidth)
        self.btnProperty.grid(row=0, column=0, sticky='nwse')
        self.btnMass = tk.Button(self.frmAnRight, text='モーター/チャック簡略化', command=self.LaunchMassDialog, width=self.btnWidth)
        self.btnMass.grid(row=0, column=1, sticky='nwse')
        self.btnMass2 = tk.Button(self.frmAnRight, text='ターニングヘッド簡略化', command=self.LaunchMass2Dialog, width=self.btnWidth)
        self.btnMass2.grid(row=1, column=0, sticky='nwse')
        self.btnAxis = tk.Button(self.frmAnRight, text='1D作成', command=self.LaunchAxisDialog, width=self.btnWidth)
        self.btnAxis.grid(row=1, column=1, sticky='nwse')
        self.btnExport = tk.Button(self.frmAnRight, text='エクスポート', command=self.Export, width=self.btnWidth)
        self.btnExport.grid(row=2, column=0, sticky='nwse')

    def CreateIconWidget(self):
        self.frmIcon = tk.Frame(self.frmAnLeft)
        self.frmIcon.pack(side=tk.BOTTOM, anchor=tk.SW)

        self.iconEraser = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'eraser.png')), master=self.frmIcon)
        self.btnEraser = tk.Button(self.frmIcon, image=self.iconEraser, command=self.DeleteHistories)
        self.btnEraser.pack(side=tk.LEFT, anchor=tk.SW)
        self.tipEraser = tooltip.ToolTip(self.btnEraser, 'メニュー履歴（青）を消します。', self.master)

        self.iconUndo = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'undo-16.png')), master=self.frmIcon)
        self.btnUndo = tk.Button(self.frmIcon, image=self.iconUndo, command=self.Undo)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.SW)
        self.tipUndo = tooltip.ToolTip(self.btnUndo, '操作を戻します。', self.master)
        self.backup.Append(self.btnUndo)

    def CreateLines(self):
        self.master.update()

        h = 5
        y = self.frmSCLeft.winfo_y()
        w = self.winfo_width()
        self.canvas1 = tk.Canvas(self)
        self.canvas1.place(x=0, y=y-3, width=w, height=h)
        self.canvas1.create_line(0, 2, w, 2, fill='#C0C0C0')

        h = 5
        y = self.frmLLeft.winfo_y()
        w = self.winfo_width()
        self.canvas2 = tk.Canvas(self)
        self.canvas2.place(x=0, y=y-3, width=w, height=h)
        self.canvas2.create_line(0, 2, w, 2, fill='#C0C0C0')

        h = 5
        y = self.frmAnLeft.winfo_y()
        w = self.winfo_width()
        self.canvas3 = tk.Canvas(self)
        self.canvas3.place(x=0, y=y-3, width=w, height=h)
        self.canvas3.create_line(0, 2, w, 2, fill='#C0C0C0')

        w = 5
        x = self.frmMeshRight.winfo_x()
        h = self.winfo_height()
        self.canvas4 = tk.Canvas(self)
        self.canvas4.place(x=x-3, y=0, width=w, height=h)
        self.canvas4.create_line(2, 0, 2, h, fill='#C0C0C0')

    def LaunchModelImportDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('ModelImport')

        importlib.reload(modelimport)
        self.dialog = tk.Toplevel()
        app = modelimport.ModelImportDlg(master=self.dialog, parent=self.master, springs=self.springs)
        app.mainloop()

    def LaunchModelInfoDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('ModelInfo')

        importlib.reload(modelinfo)
        self.dialog = tk.Toplevel()
        app = modelinfo.ModelInfo(master=self.dialog, parent=self.master)
        app.mainloop()

    def LaunchCADBodyMergeDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('CADBodyMerge')

        importlib.reload(boolean)
        self.dialog = tk.Toplevel()
        app = boolean.CADBodyMergeDlg(master=self.dialog, parent=self.master, backup=self.backup)
        app.mainloop()

    def LaunchGroupDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Group')

        importlib.reload(groupinfo)
        self.dialog = tk.Toplevel()
        app = groupinfo.GroupInfo(master=self.dialog, parent=self.master)
        app.mainloop()

    def LaunchMeshCtrlDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('MeshCtrl')

        importlib.reload(meshctrl)
        self.dialog = tk.Toplevel()
        app = meshctrl.MeshCtrlDlg(master=self.dialog, parent=self.master)
        app.mainloop()

    def LaunchSurfaceMeshDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('SurfaceMesh')

        importlib.reload(surfmesh)
        self.dialog = tk.Toplevel()
        app = surfmesh.SurfMeshDlg(master=self.dialog, parent=self.master)
        app.mainloop()

    def LaunchMergeDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('FaceMerge')

        importlib.reload(facemerge)
        self.dialog = tk.Toplevel()
        app = facemerge.FaceMergeDlg(master=self.dialog, parent=self.master, backup=self.backup, config=self.config)
        app.mainloop()

    def LaunchShareNodeDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('ShareNode')

        importlib.reload(boolean)
        self.dialog = tk.Toplevel()
        app = boolean.ShareNodeDlg(master=self.dialog, parent=self.master, backup=self.backup, config=self.config)
        app.mainloop()

    def LaunchSimplifyDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Simplify')

        importlib.reload(simplify)
        self.dialog = tk.Toplevel()
        app = simplify.SimplifyDlg(master=self.dialog, parent=self.master, backup=self.backup)
        app.mainloop()

    def LaunchFillHoleDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('FillHole')

        importlib.reload(fillhole)
        self.dialog = tk.Toplevel()
        app = fillhole.FillHoleDlg(master=self.dialog, parent=self.master, backup=self.backup)
        app.mainloop()

    def LaunchBearingDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Bearing')

        importlib.reload(bearing)
        self.dialog = tk.Toplevel()
        app = bearing.BearingDlg(master=self.dialog, parent=self.master, backup=self.backup, springs=self.springs)
        app.mainloop()

    def LaunchSysDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Coordinate')

        importlib.reload(coordinate)
        self.dialog = tk.Toplevel()
        app = coordinate.CoordinateDlg(master=self.dialog, parent=self.master, backup=self.backup)
        app.mainloop()

    def LaunchMPCDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('MPC')

        importlib.reload(mpc)
        self.dialog = tk.Toplevel()
        app = mpc.MPCDlg(master=self.dialog, parent=self.master, backup=self.backup)
        app.mainloop()

    def LaunchMassDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Mass')

        importlib.reload(mass)
        self.dialog = tk.Toplevel()
        app = mass.MassDlg(master=self.dialog, parent=self.master, backup=self.backup)
        app.mainloop()

    def LaunchMass2Dialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Mass2')

        importlib.reload(mass2)
        self.dialog = tk.Toplevel()
        app = mass2.Mass2Dlg(master=self.dialog, parent=self.master, backup=self.backup)
        app.mainloop()

    def LaunchBoltDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Bolt')

        importlib.reload(bolt)
        self.dialog = tk.Toplevel()
        app = bolt.BoltDlg(master=self.dialog, parent=self.master, backup=self.backup, springs=self.springs)
        app.mainloop()

    def LaunchSpringDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Spring')

        importlib.reload(spring)
        self.dialog = tk.Toplevel()
        app = spring.SpringDlg(master=self.dialog, parent=self.master, backup=self.backup, springs=self.springs)
        app.mainloop()

    def LaunchLinearGuideDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('LinearGuide')

        importlib.reload(linearguide)
        self.dialog = tk.Toplevel()
        app = linearguide.LinearGuideDlg(master=self.dialog, parent=self.master, backup=self.backup, springs=self.springs)
        app.mainloop()

    def LaunchVolumeMeshDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Volume')

        importlib.reload(volumemesh)
        self.dialog = tk.Toplevel()
        app = volumemesh.VolumeMeshDlg(master=self.dialog, parent=self.master)
        app.mainloop()

    def LaunchPropertyDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Property')
        importlib.reload(propertyutil)
        propertyutil.createProperty()
        
    def LaunchAxisDialog(self):
        self.CloseChildDialog()
        self.AddToHistory('Axis')

        importlib.reload(axisbeam)
        self.dialog = tk.Toplevel()
        app = axisbeam.AxisDlg(master=self.dialog, parent=self.master, backup=self.backup)
        app.mainloop()

    def Export(self):
        self.CloseChildDialog()
        self.AddToHistory('Export')

        importlib.reload(export)
        export.ExportBDF()

    def Undo(self):
        self.backup.Load()

    def AddToHistory(self, enumType):
        self.history.Add(enumType)

    def DeleteHistories(self):
        self.history.DeleteAll()

    def CloseChildDialog(self):
        try:
            self.dialog.destroy()
        except:
            pass

    def CloseDialog(self):
        self.CloseChildDialog()
        try:
            self.master.destroy()
        except:
            pass