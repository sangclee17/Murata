import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
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
import tooltip as tp
import widget
import mpcutil
import coordinate

class MPCDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('MPC作成')
        self.indepFace = '_MPC_Face_Independent'
        self.depFace = '_MPC_Face_Dependent'
        self.backup = backup
        
        self.CreateWidgets()
        self.UpdateButtonFG()
        simlab.setSelectionFilter('Body')

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.lblNote1 = tk.Label(self.frmTop, text='Tips: メッシュパターンを合わせた後にMPCを作成します。\n各面を選択した後に、[ 作成 ]ボタンを押してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmFig = tk.Frame(self.frmTop)        
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        # face
        self.frmFigFace = tk.Frame(self.frmFig, width=600)
        self.frmFigFace.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconFace = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'mpc_face.png')), master=self.frmFigFace)
        tk.Label(self.frmFigFace, image=self.iconFace).pack(side=tk.LEFT, anchor=tk.W)

        self.btnFaceIndep = tk.Button(self.frmFigFace, text='メッシュを残したい面', command=self.SelectFaceIndep)
        self.btnFaceIndep.place(x=270, y=50)        
        self.btnFaceDep = tk.Button(self.frmFigFace, text='もう片側の面', command=self.SelectFaceDep)
        self.btnFaceDep.place(x=280, y=150)        

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        ## Tolerance
        self.frmTol = tk.Frame(self.frmTop)
        self.frmTol.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X, pady=2)
        self.entTol = widget.LabelEntry(self.frmTol, text='面間のトレランス :', width=10, value=2)
        self.entTol.pack(side=tk.TOP, anchor=tk.W)

        ## MPC
        self.frmMPCProp = tk.Frame(self.frmTop)
        self.frmMPCProp.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X, padx=5, pady=2)
        self.lblMPC = tk.Label(self.frmMPCProp, text='MPC : ')        
        self.lblMPC.pack(side=tk.TOP, anchor=tk.W)

        self.frmCoord = tk.Frame(self.frmMPCProp)
        self.frmCoord.pack(side=tk.TOP, anchor=tk.W, padx=15, pady=2)
        self.lblCoord = tk.Label(self.frmCoord, text='座標系 : ')
        self.lblCoord.pack(side=tk.LEFT, anchor=tk.W)

        coords = coordinate.GetAllCoordinates()
        self.coord = tk.StringVar()
        if len(coords) != 0:
            self.coord.set(coords[0])
        self.cmbCoords = ttk.Combobox(self.frmCoord, values=coords, textvariable=self.coord, width=25, state='readonly')
        self.cmbCoords.pack(side=tk.LEFT, anchor=tk.W)

        self.cornerNodesOnly = tk.BooleanVar()
        self.cornerNodesOnly.set(False)
        self.cornerNodesOnlyChk = tk.Checkbutton(self.frmMPCProp, text="コーナー節点のみ", variable=self.cornerNodesOnly)
        self.cornerNodesOnlyChk.pack(side=tk.TOP, anchor=tk.W, padx=15, pady=2)

        self.lblDOF = tk.Label(self.frmMPCProp, text='DOF : ')
        self.lblDOF.pack(side=tk.TOP, anchor=tk.W, padx=15, pady=2)

        self.frmDOF = tk.Frame(self.frmMPCProp)
        self.frmDOF.pack(side=tk.TOP, anchor=tk.NW, padx=25, pady=2)
        self.frmDOF.grid_columnconfigure((0,1), weight=1)
        self.frmDOF.grid_rowconfigure((0,1,2), weight=1)

        self.bX = tk.BooleanVar()
        self.bY = tk.BooleanVar()
        self.bZ = tk.BooleanVar()
        self.bRx = tk.BooleanVar()
        self.bRy = tk.BooleanVar()
        self.bRz = tk.BooleanVar()
        self.bX.set(False)
        self.bY.set(False)
        self.bZ.set(False)
        self.bRx.set(False)
        self.bRy.set(False)
        self.bRz.set(False)

        self.chkX = tk.Checkbutton(self.frmDOF, text='X or Radial', variable=self.bX)
        self.chkX.grid(row=0, column=0)
        self.chkRx = tk.Checkbutton(self.frmDOF, text='Rx', variable=self.bRx)
        self.chkRx.grid(row=0, column=1, padx=10, pady=2)

        self.chkY = tk.Checkbutton(self.frmDOF, text='Y or Theta', variable=self.bY)
        self.chkY.grid(row=1, column=0)
        self.chkRy = tk.Checkbutton(self.frmDOF, text='Ry', variable=self.bRy)
        self.chkRy.grid(row=1, column=1, padx=10, pady=2)

        self.chkZ = tk.Checkbutton(self.frmDOF, text='Z or Axial', variable=self.bZ)
        self.chkZ.grid(row=2, column=0)
        self.chkRz = tk.Checkbutton(self.frmDOF, text='Rz', variable=self.bRz)
        self.chkRz.grid(row=2, column=1, padx=10, pady=2)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnCreate = tk.Button(self.frmCtrl, text=' 作成 ', compound=tk.LEFT, command=self.Create, width=btnWidth)
        self.btnCreate.pack(side=tk.LEFT, anchor=tk.NW)        
        self.btnCreate = tp.ToolTip(self.btnCreate, 'MPCを作成します。', self.master)

        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def Create(self):
        try:
            tolerance = float(self.entTol.Get())
        except:
            messagebox.showinfo('情報','トレランスには実数を指定してください。')
            return

        if not simlab.isGroupPresent(self.indepFace) or not simlab.isGroupPresent(self.depFace):
            messagebox.showinfo('情報','面を選択してください。')
            return

        self.backup.Save('MPC')
        importlib.reload(mpcutil)

        if not self.bX.get() and not self.bY.get() and not self.bZ.get() and not self.bRx.get() and not self.bRy.get() and not self.bRz.get():
            messagebox.showinfo('情報','Check DOF')
            return

        CID = coordinate.GetID(self.coord.get())
        if CID == -1:
            messagebox.showinfo('情報', "Select coordinate id")
            return

        mpcProp = CID, self.bX.get(), self.bY.get(), self.bZ.get(), self.bRx.get(), self.bRy.get(), self.bRz.get()
        entitiesProp = self.indepFace, self.depFace, tolerance

        mpcutil.createMPC(entitiesProp, mpcProp, self.cornerNodesOnly.get())

        simlablib.DeleteGroups([self.indepFace, self.depFace])
        self.UpdateButtonFG()

    def SelectFaceIndep(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.indepFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.indepFace)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectFaceDep(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.depFace)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.depFace)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def UpdateButtonFG(self):
        groups = [self.indepFace, self.depFace]
        widgets = [self.btnFaceIndep, self.btnFaceDep]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def Undo(self):
        self.backup.Load()
        self.UpdateButtonFG()

        # Since the CAD model is displayed immediately after Undo, it is confusing
        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        simlablib.DeleteGroups([self.indepFace, self.depFace])
        super().CloseDialog()
    
def getMPCCounter(paramKey):

    if simlab.isParameterPresent(paramKey):
        maxCounter = simlab.getIntParameter("${}".format(paramKey))
        maxCounter += 1
        simlablib.DeleteParameters(paramKey)
        simlablib.AddIntParameters(paramKey, maxCounter)
    else:
        simlablib.AddIntParameters(paramKey, 1)
        maxCounter = 1
    return maxCounter