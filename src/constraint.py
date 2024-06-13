import tkinter as tk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

CONSTRAINT_NAME = 'Constraint_'
MAX_ID_CONSTRAINT = 'Max_ID_Constraint'

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

# local import
import basedialog
import simlabutil
import simlablib
import tooltip as tp

# for development
importlib.reload(simlablib)
importlib.reload(simlabutil)

class ConstraintDlg(basedialog.BaseDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.face = '_Constraint_Face'
        self.master.title('拘束作成')

        self.CreateWidgets()
        self.UpdateButtonFG()

        simlab.setSelectionFilter('Face')
        simlabutil.ClearSelection()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.lblNote1 = tk.Label(self.frmTop, text='Tips: 拘束面を選択して、[ 作成 ]ボタンを押してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)
        btnWidth = 10

        ## Face
        self.frmFace = tk.Frame(self.frmTop)
        self.frmFace.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, pady=2)
        self.lblFace = tk.Label(self.frmFace, text='拘束面 : ')
        self.lblFace.pack(side=tk.LEFT, anchor=tk.W)
        self.btnFace = tk.Button(self.frmFace, text=' 拘束面 ', command=self.SelectFace, width=btnWidth)
        self.btnFace.pack(side=tk.LEFT, anchor=tk.W)

        self.TX = tk.BooleanVar()
        self.TY = tk.BooleanVar()
        self.TZ = tk.BooleanVar()
        self.RX = tk.BooleanVar()
        self.RY = tk.BooleanVar()
        self.RZ = tk.BooleanVar()
        self.TX.set(True)
        self.TY.set(True)
        self.TZ.set(True)
        self.RX.set(False)
        self.RY.set(False)
        self.RZ.set(False)

        # 平進
        self.frmTrans = tk.Frame(self.frmTop)
        self.frmTrans.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, pady=2)
        self.lblTrans= tk.Label(self.frmTrans, text='並進 : ')
        self.lblTrans.pack(side=tk.LEFT, anchor=tk.W)

        self.frmTransXYZ = tk.Frame(self.frmTop)
        self.frmTransXYZ.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=10, pady=2)
        self.chkTX = tk.Checkbutton(self.frmTransXYZ, text='X', variable=self.TX)
        self.chkTX.pack(side=tk.LEFT, anchor=tk.W, padx=10)
        self.chkTY = tk.Checkbutton(self.frmTransXYZ, text='Y', variable=self.TY)
        self.chkTY.pack(side=tk.LEFT, anchor=tk.W, padx=10)
        self.chkTZ = tk.Checkbutton(self.frmTransXYZ, text='Z', variable=self.TZ)
        self.chkTZ.pack(side=tk.LEFT, anchor=tk.W, padx=10)

        # 回転
        self.frmRot = tk.Frame(self.frmTop)
        self.frmRot.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, pady=2)
        self.lblRot = tk.Label(self.frmRot, text='回転 : ')
        self.lblRot.pack(side=tk.LEFT, anchor=tk.W)

        self.frmRotXYZ = tk.Frame(self.frmTop)
        self.frmRotXYZ.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=10, pady=2)
        self.chkRX = tk.Checkbutton(self.frmRotXYZ, text='X', variable=self.RX)
        self.chkRX.pack(side=tk.LEFT, anchor=tk.W, padx=10)
        self.chkRY = tk.Checkbutton(self.frmRotXYZ, text='Y', variable=self.RY)
        self.chkRY.pack(side=tk.LEFT, anchor=tk.W, padx=10)
        self.chkRZ = tk.Checkbutton(self.frmRotXYZ, text='Z', variable=self.RZ)
        self.chkRZ.pack(side=tk.LEFT, anchor=tk.W, padx=10)

        tk.Frame(self.frmTop, height=10).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnCreate = tk.Button(self.frmCtrl, text=' 作成 ', compound=tk.LEFT, command=self.Create, width=btnWidth)
        self.btnCreate.pack(side=tk.LEFT, anchor=tk.NW)        
        self.btnCreate = tp.ToolTip(self.btnCreate, 'MPCを作成します。', self.master)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def SelectFace(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、[拘束面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.face)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.face)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()   

    def UpdateButtonFG(self):
        groups = [self.face]
        widgets = [self.btnFace]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def Create(self):
        if not simlab.isGroupPresent(self.face):
            messagebox.showinfo('情報','拘束面を選択した後、[作成] ボタンを押下してください。')
            return

        modelName = simlab.getModelName('FEM')
        faces = simlab.getEntityFromGroup(self.face)

        constraintID = 1
        if simlab.isParameterPresent(MAX_ID_CONSTRAINT):
            constraintID = simlab.getIntParameter('$'+MAX_ID_CONSTRAINT) + 1
        simlablib.AddIntParameters(MAX_ID_CONSTRAINT, constraintID)
        constraintName = CONSTRAINT_NAME + str(constraintID)

        Tx = 1 if self.TX.get() else 0
        Ty = 1 if self.TY.get() else 0
        Tz = 1 if self.TZ.get() else 0
        Rx = 1 if self.RX.get() else 0
        Ry = 1 if self.RY.get() else 0
        Rz = 1 if self.RZ.get() else 0
        simlablib.CreateFixedConstraint(constraintName, modelName, 'Face', faces, Tx, Ty, Tz, Rx, Ry, Rz)

        simlablib.DeleteGroups([self.face])
        self.UpdateButtonFG()

    def CloseDialog(self):
        simlablib.DeleteGroups([self.face])
        super().CloseDialog()
