import tkinter as tk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib
import numpy as np
from PIL import Image, ImageTk

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))
LOG_DIR = (os.path.join(PROJECT_DIR, 'log'))

MASS_COORDINATE = 'MASS1_'
MASS_MASS = 'MASS1_'
MASS_RBE = 'MASS1_'
MASS_ASSIGN = 'MASS1_'

MAX_ID_COORDINATE = 'Max_ID_Coordinate'
MAX_ID_MASS = 'Max_ID_Mass'
MAX_ID_RBE = 'Max_ID_RBE'
MAX_ID_ASSIGN = 'Max_ID_Assign'

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

# local import
import basedialog
import simlabutil
import simlablib
import tooltip as tp
import coordinate

def AssignCoordinateSystem(axisID, nodeID):
    modelName = simlab.getModelName('FEM')

    # ID
    assignID = 1
    if simlab.isParameterPresent(MAX_ID_ASSIGN):
        assignID = simlab.getIntParameter('$'+MAX_ID_ASSIGN) + 1
    simlablib.AddIntParameters(MAX_ID_ASSIGN, assignID)

    # Name
    name = MASS_ASSIGN + str(assignID)

    AssignCoordinateSystem=''' <AssignLcs BCType="AssignLCS" UUID="3c48419c-85a7-4281-a810-85dcf63c16b9" isObject="1">
    <tag Value="-1"/>
    <Name Value="''' + name + '''"/>
    <SupportEntities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(nodeID) + ''',</Node>
    </Entities>
    </SupportEntities>
    <Geometric Value="0"/>
    <Coordinate Value="''' + str(axisID) + '''" Index="1"/>
    <Output/>
    </AssignLcs>'''
    simlab.execute(AssignCoordinateSystem)

    return assignID

def CreateMass(nodeID, booleans, values, mass, axisID):
    modelName = simlab.getModelName('FEM')

    # ID
    massID = 1
    if simlab.isParameterPresent(MAX_ID_MASS):
        massID = simlab.getIntParameter('$'+MAX_ID_MASS) + 1
    simlablib.AddIntParameters(MAX_ID_MASS, massID)

    # Name
    name = MASS_MASS + str(massID)

    bIxx, bIyy, bIzz, bIxy, bIyz, bIzx = booleans
    bIxx = '1' if bIxx else '0'
    bIyy = '1' if bIyy else '0'
    bIzz = '1' if bIzz else '0'
    bIxy = '1' if bIxy else '0'
    bIyz = '1' if bIyz else '0'
    bIzx = '1' if bIzx else '0'

    Ixx, Iyy, Izz, Ixy, Iyz, Izx = values

    PointMass=''' <Mass Auto="1" isObject="2" BCType="Mass" UUID="40EFB6FC-D0CB-46da-81B2-CFA88D2679D1">
    <tag Value="81"/>
    <Name Value="''' + name + '''"/>
    <MassEntities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' +  str(nodeID) + ''',</Node>
    </Entities>
    </MassEntities>
    <AxisID Value="''' + str(axisID) + '''" Index="0"/>
    <MassValue Value="''' + str(mass) + '''"/>
    <MassOption Value="0"/>
    <CentroidX Value="0"/>
    <CentroidY Value="0"/>
    <CentroidZ Value="0"/>
    <Ixx CheckBox="''' + bIxx + '''" Value="''' + str(Ixx) + '''"/>
    <Iyy CheckBox="''' + bIyy + '''" Value="''' + str(Iyy) + '''"/>
    <Izz CheckBox="''' + bIzz + '''" Value="''' + str(Izz) + '''"/>
    <Ixy CheckBox="''' + bIxy + '''" Value="''' + str(Ixy) + '''"/>
    <Iyz CheckBox="''' + bIyz + '''" Value="''' + str(Iyz) + '''"/>
    <Izx CheckBox="''' + bIzx + '''" Value="''' + str(Izx) + '''"/>
    <Export Value="0"/>
    <ExportFileName Value=""/>
    <CalculateAndAssign flag="false"/>
    </Mass>'''
    simlab.execute(PointMass)

class MassDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.connect = '_Mass_Connect'
        self.RBEBase = '_Mass_Base'

        self.master.title('モニター/チャック簡略化')
        self.backup = backup

        self.CreateWidgets()
        self.UpdateButtonFG()

        simlab.setSelectionFilter('Body')
        simlabutil.ClearSelection()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.lblNote1 = tk.Label(self.frmTop, text='Tips: RBE接続先を[ 接続先 ]で選択してください。\n座標系原点(重心)と質量は[ ボディから計算 ]で選択してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)
        btnWidth = 10

        ## RBE
        self.frmRBE = tk.LabelFrame(self.frmTop, text='RBE:')
        self.frmRBE.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X)

        self.frmType = tk.Frame(self.frmRBE)
        self.frmType.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)
        tk.Label(self.frmType, text='従属節点の指定方法:').pack(side=tk.LEFT, anchor=tk.W)

        self.type = tk.StringVar()
        self.type.set('Face')
        self.chkFace = tk.Radiobutton(self.frmType, text='Face', value='Face', variable=self.type, command=self.SelectType)
        self.chkFace.pack(side=tk.LEFT, anchor=tk.W)
        self.chkNode = tk.Radiobutton(self.frmType, text='Node', value='Node', variable=self.type, command=self.SelectType)
        self.chkNode.pack(side=tk.LEFT, anchor=tk.W)
        self.btnConnect = tk.Button(self.frmType, text=' 接続先 ', width=btnWidth, command=self.SelectConnections)
        self.btnConnect.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        self.boolRBEAdd = tk.BooleanVar()
        self.boolRBEAdd.set(False)
        self.chkRBEAdd = tk.Checkbutton(self.frmRBE, text='従属節点を追加する', variable=self.boolRBEAdd, command=self.ToggleRBE)
        self.chkRBEAdd.pack(side=tk.TOP, anchor=tk.NW, padx=5)

        self.frmRBEAdd = tk.Frame(self.frmRBE)
        self.frmRBEAdd.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=5)

        self.frmRBEAddFace = tk.Frame(self.frmRBEAdd)
        self.frmRBEAddFace.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmRBEAddFace, text='基準面:').pack(side=tk.LEFT, anchor=tk.W)
        self.btnAddConnect = tk.Button(self.frmRBEAddFace, text=' 基準面 ', width=btnWidth, command=self.SelectRBEBase)
        self.btnAddConnect.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        tk.Frame(self.frmRBEAdd, height=5).pack()

        self.frmRBEAddLen = tk.Frame(self.frmRBEAdd)
        self.frmRBEAddLen.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmRBEAddLen, text='距離:').pack(side=tk.LEFT, anchor=tk.W)
        self.entRBELen = tk.Entry(self.frmRBEAddLen, width=10)
        self.entRBELen.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entRBELen.insert(tk.END, 0)
        tk.Frame(self.frmRBEAdd, height=5).pack()

        self.frmRBEAddRad = tk.Frame(self.frmRBEAdd)
        self.frmRBEAddRad.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmRBEAddRad, text='直径:').pack(side=tk.LEFT, anchor=tk.W)
        self.entRBERad = tk.Entry(self.frmRBEAddRad, width=10)
        self.entRBERad.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entRBERad.insert(tk.END, 0)
        self.ToggleRBE()

        ## Coordinate
        self.frmCoord = tk.LabelFrame(self.frmTop, text='座標系:')
        self.frmCoord.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        self.lblCoordDir = tk.Label(self.frmCoord, text='方向:')
        self.lblCoordDir.pack(side=tk.TOP, anchor=tk.NW, padx=5)

        self.frmCoordDir = tk.Frame(self.frmCoord)
        self.frmCoordDir.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=10)

        self.frmCoordDirX = tk.Frame(self.frmCoordDir)
        self.frmCoordDirX.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        self.lblX = tk.Label(self.frmCoordDirX, text='Nx:')
        self.lblX.pack(side=tk.LEFT, anchor=tk.W)
        self.entNXX = tk.Entry(self.frmCoordDirX, width=10)
        self.entNXX.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entNXY = tk.Entry(self.frmCoordDirX, width=10)
        self.entNXY.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entNXZ = tk.Entry(self.frmCoordDirX, width=10)
        self.entNXZ.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        tk.Frame(self.frmCoordDir, height=5).pack()

        self.frmCoordDirY = tk.Frame(self.frmCoordDir)
        self.frmCoordDirY.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        self.lblY = tk.Label(self.frmCoordDirY, text='Ny:')
        self.lblY.pack(side=tk.LEFT, anchor=tk.W)
        self.entNYX = tk.Entry(self.frmCoordDirY, width=10)
        self.entNYX.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entNYY = tk.Entry(self.frmCoordDirY, width=10)
        self.entNYY.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entNYZ = tk.Entry(self.frmCoordDirY, width=10)
        self.entNYZ.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        tk.Frame(self.frmCoordDir, height=5).pack()

        self.frmCoordDirZ = tk.Frame(self.frmCoordDir)
        self.frmCoordDirZ.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        self.lblZ = tk.Label(self.frmCoordDirZ, text='Nz:')
        self.lblZ.pack(side=tk.LEFT, anchor=tk.W)
        self.entNZX = tk.Entry(self.frmCoordDirZ, width=10)
        self.entNZX.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entNZY = tk.Entry(self.frmCoordDirZ, width=10)
        self.entNZY.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entNZZ = tk.Entry(self.frmCoordDirZ, width=10)
        self.entNZZ.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        tk.Frame(self.frmCoordDir, height=5).pack()

        self.entNXX.insert(tk.END, 1)
        self.entNXY.insert(tk.END, 0)
        self.entNXZ.insert(tk.END, 0)
        self.entNYX.insert(tk.END, 0)
        self.entNYY.insert(tk.END, 1)
        self.entNYZ.insert(tk.END, 0)
        self.entNZX.insert(tk.END, 0)
        self.entNZY.insert(tk.END, 0)
        self.entNZZ.insert(tk.END, 1)

        self.lblCoordOrig = tk.Label(self.frmCoord, text='原点:')
        self.lblCoordOrig.pack(side=tk.TOP, anchor=tk.W, padx=5)

        self.frmCoordOrigXYZ = tk.Frame(self.frmCoord)
        self.frmCoordOrigXYZ.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=10)
        self.lblZ = tk.Label(self.frmCoordOrigXYZ, text='O :')
        self.lblZ.pack(side=tk.LEFT, anchor=tk.W)
        self.entOX = tk.Entry(self.frmCoordOrigXYZ, width=10)
        self.entOX.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entOY = tk.Entry(self.frmCoordOrigXYZ, width=10)
        self.entOY.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entOZ = tk.Entry(self.frmCoordOrigXYZ, width=10)
        self.entOZ.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        self.entOX.insert(tk.END, 0)
        self.entOY.insert(tk.END, 0)
        self.entOZ.insert(tk.END, 0)

        self.btnBodies = tk.Button(self.frmCoordOrigXYZ, text=' ボディから計算 ', width=btnWidth, command=self.CalcBodies)
        self.btnBodies.pack(side=tk.LEFT, anchor=tk.W)
        tk.Frame(self.frmCoord, height=5).pack()

        ## Mass
        self.frmMass = tk.LabelFrame(self.frmTop, text='質量要素:')
        self.frmMass.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        self.frmMassVal = tk.Frame(self.frmMass)
        self.frmMassVal.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)
        self.lblMass = tk.Label(self.frmMassVal, text='質量: ')
        self.lblMass.pack(side=tk.LEFT, anchor=tk.W)
        self.entMass = tk.Entry(self.frmMassVal, width=10)
        self.entMass.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entMass.insert(tk.END, 0)
        tk.Frame(self.frmMass, height=5).pack()

        self.frmMom = tk.Frame(self.frmMass)
        self.frmMom.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)
        self.lblMom = tk.Label(self.frmMom, text='慣性質量モーメント: ')
        self.lblMom.pack(side=tk.TOP, anchor=tk.W)

        self.booleanXX = tk.BooleanVar()
        self.booleanXY = tk.BooleanVar()
        self.booleanYY = tk.BooleanVar()
        self.booleanYZ = tk.BooleanVar()
        self.booleanZZ = tk.BooleanVar()
        self.booleanZX = tk.BooleanVar()
        self.booleanXX.set(False)
        self.booleanXY.set(False)
        self.booleanYY.set(False)
        self.booleanYZ.set(False)
        self.booleanZZ.set(False)
        self.booleanZX.set(False)

        row = 0
        self.frmMomVal = tk.Frame(self.frmMass)
        self.frmMomVal.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=10)
        self.chkXX = tk.Checkbutton(self.frmMomVal, text='Ixx:', variable=self.booleanXX)
        self.chkXX.grid(row=row, column=0)
        self.entIXX = tk.Entry(self.frmMomVal, width=10)
        self.entIXX.grid(row=row, column=1)
        tk.Frame(self.frmMomVal, width=5).grid(row=row, column=2)
        self.chkXY = tk.Checkbutton(self.frmMomVal, text='Ixy:', variable=self.booleanXY)
        self.chkXY.grid(row=row, column=3)
        self.entIXY = tk.Entry(self.frmMomVal, width=10)
        self.entIXY.grid(row=row, column=4)

        tk.Frame(self.frmMomVal, height=5).grid(row=1, column=0)

        row = 2
        self.chkYY = tk.Checkbutton(self.frmMomVal, text='Iyy:', variable=self.booleanYY)
        self.chkYY.grid(row=row, column=0)
        self.entIYY = tk.Entry(self.frmMomVal, width=10)
        self.entIYY.grid(row=row, column=1)
        self.chkYZ = tk.Checkbutton(self.frmMomVal, text='Iyz:', variable=self.booleanYZ)
        self.chkYZ.grid(row=row, column=3)
        self.entIYZ = tk.Entry(self.frmMomVal, width=10)
        self.entIYZ.grid(row=row, column=4)

        tk.Frame(self.frmMomVal, height=5).grid(row=3, column=0)

        row = 4
        self.chkZZ = tk.Checkbutton(self.frmMomVal, text='Izz:', variable=self.booleanZZ)
        self.chkZZ.grid(row=row, column=0)
        self.entIZZ = tk.Entry(self.frmMomVal, width=10)
        self.entIZZ.grid(row=row, column=1)
        self.chkZX = tk.Checkbutton(self.frmMomVal, text='Izx:', variable=self.booleanZX)
        self.chkZX.grid(row=row, column=3)
        self.entIZX = tk.Entry(self.frmMomVal, width=10)
        self.entIZX.grid(row=row, column=4)

        self.entIXX.insert(tk.END, 0)
        self.entIXY.insert(tk.END, 0)
        self.entIYY.insert(tk.END, 0)
        self.entIYZ.insert(tk.END, 0)
        self.entIZZ.insert(tk.END, 0)
        self.entIZX.insert(tk.END, 0)
        self.entIXX.config(state='disabled')
        self.entIXY.config(state='disabled')
        self.entIYY.config(state='disabled')
        self.entIYZ.config(state='disabled')
        self.entIZZ.config(state='disabled')
        self.entIZX.config(state='disabled')

        self.chkXX.config(command=lambda : self.UpdateState(self.booleanXX, self.entIXX))
        self.chkXY.config(command=lambda : self.UpdateState(self.booleanXY, self.entIXY))
        self.chkYY.config(command=lambda : self.UpdateState(self.booleanYY, self.entIYY))
        self.chkYZ.config(command=lambda : self.UpdateState(self.booleanYZ, self.entIYZ))
        self.chkZZ.config(command=lambda : self.UpdateState(self.booleanZZ, self.entIZZ))
        self.chkZX.config(command=lambda : self.UpdateState(self.booleanZX, self.entIZX))

        tk.Frame(self.frmMass, height=5).pack()
        tk.Frame(self.frmTop, height=10).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        self.btnCreate = tk.Button(self.frmCtrl, text=' 作成 ', compound=tk.LEFT, command=self.Create, width=btnWidth)
        self.btnCreate.pack(side=tk.LEFT, anchor=tk.NW)
        self.btnCreate = tp.ToolTip(self.btnCreate, 'Massを作成します。', self.master)

        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def SelectType(self):
        if self.type.get() == 'Face':
            simlab.setSelectionFilter('Face')
        else:
            simlab.setSelectionFilter('Node')

    def ToggleRBE(self):
        if self.boolRBEAdd.get():
            self.btnAddConnect.config(state='normal')
            self.entRBELen.config(state='normal')
            self.entRBERad.config(state='normal')
        else:
            self.btnAddConnect.config(state='disabled')
            self.entRBELen.config(state='disabled')
            self.entRBERad.config(state='disabled')

    def SelectConnections(self):
        if self.type.get() == 'Face':
            entities = simlab.getSelectedEntities('FACE')
            if len(entities) == 0:
                messagebox.showinfo('情報','面を選択した後、[接続先] ボタンを押下してください。')
                return
        else:
            entities = simlab.getSelectedEntities('NODE')
            if len(entities) == 0:
                messagebox.showinfo('情報','節点を選択した後、[接続先] ボタンを押下してください。')
                return

        simlablib.DeleteGroups(self.connect)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, self.type.get(), entities, self.connect)

        self.UpdateDirection()

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectRBEBase(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、[基準面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.RBEBase)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.RBEBase)

        result = simlab.definePlaneFromGroup(self.RBEBase, 'FACEGROUP')
        if len(result) == 0:
            simlablib.DeleteGroups(self.RBEBase)
            messagebox.showinfo('情報','選択した面は平面ではありません。平面を選択するかAlignしてください。')

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def CalcBodies(self):
        bodies = simlab.getSelectedBodies()
        if len(bodies) < 1:
            messagebox.showinfo('情報','座標系原点（重心）と質量を計算するボディを選択してください。')
            return
        
        result = simlablib.CalculateOverallCOGAndMassFromBodies(bodies)
        if len(result) == 0:
            return

        mass, cog = result
        self.entMass.delete(0, tk.END)
        self.entOX.delete(0, tk.END)
        self.entOY.delete(0, tk.END)
        self.entOZ.delete(0, tk.END)

        self.entMass.insert(tk.END, str(mass))
        self.entOX.insert(tk.END, str(cog[0]))
        self.entOY.insert(tk.END, str(cog[1]))
        self.entOZ.insert(tk.END, str(cog[2]))

    def Create(self):
        if not self.IsValid():
            return

        self.backup.Save('Mass')

        # rect coordinate system
        nodeID, axisID = self.CreateRectCoordinate()

        # mass element
        self.CreateMass(nodeID, axisID)

        RBEID = 1
        if simlab.isParameterPresent(MAX_ID_RBE):
            RBEID = simlab.getIntParameter('$'+MAX_ID_RBE) + 1
        simlablib.AddIntParameters(MAX_ID_RBE, RBEID)

        RBEName = self.GetNewName(MASS_RBE, 1)

        # RBE
        modelName = simlab.getModelName('FEM')
        if self.type.get() == 'Face':
            faces = simlab.getEntityFromGroup(self.connect)
            nodeGrp = simlabutil.UniqueGroupName('_NodeGrp')
            simlablib.SelectAssociatedEntities(modelName, 'Face', faces, 'Node', nodeGrp)
            nodes = simlab.getEntityFromGroup(nodeGrp)
            simlablib.DeleteGroups(nodeGrp)
        else:
            nodes = simlab.getEntityFromGroup(self.connect)
        
        nodes = list(nodes)
        if self.boolRBEAdd.get():
            nodes.extend(self.GetRBENodesToAdd())

        simlablib.ManualRBE(modelName, RBEName, nodeID, nodes)

        simlablib.DeleteGroups([self.connect])
        self.UpdateButtonFG()

    def GetRBENodesToAdd(self):
        o = np.array([float(self.entOX.get()), float(self.entOY.get()), float(self.entOZ.get())])
        nx = np.array([float(self.entNXX.get()), float(self.entNXY.get()), float(self.entNXZ.get())])
        ny = np.array([float(self.entNYX.get()), float(self.entNYY.get()), float(self.entNYZ.get())])        
        nz = np.array([float(self.entNZX.get()), float(self.entNZY.get()), float(self.entNZZ.get())])
        length = float(self.entRBELen.get())
        radius = float(self.entRBERad.get()) * 0.5

        point_on_plane, _, _ = simlab.definePlaneFromGroup(self.RBEBase, 'FACEGROUP')
        vec_op = np.array(point_on_plane) - o
        dot_op = np.dot(vec_op, nz)
        point_base = o + dot_op * nz

        vec_offset = o - point_base
        nvec_offset = vec_offset / np.linalg.norm(vec_offset)
        center = point_base + length * nvec_offset

        baseNodeID = 10000300
        modelName = simlab.getModelName('FEM')

        N1 = simlabutil.AvailableNodeID(modelName, baseNodeID=baseNodeID)
        simlablib.CreateNodeByXYZ(modelName, list(center + radius * nx), N1)

        N2 = simlabutil.AvailableNodeID(modelName, baseNodeID=baseNodeID+1)
        simlablib.CreateNodeByXYZ(modelName, list(center + radius * ny), N2)

        N3 = simlabutil.AvailableNodeID(modelName, baseNodeID=baseNodeID+2)
        simlablib.CreateNodeByXYZ(modelName, list(center - radius * nx), N3)

        N4 = simlabutil.AvailableNodeID(modelName, baseNodeID=baseNodeID+3)
        simlablib.CreateNodeByXYZ(modelName, list(center - radius * ny), N4)

        return [N1, N2, N3, N4]

    def GetNewName(self, key, startIndex):
        modelName = simlab.getModelName('FEM')
        bodies = set(simlab.getBodiesWithSubString(modelName, [key + '*']))

        index = startIndex
        name = key + str(index)

        while True:
            if not name in bodies:
                break
            index += 1
            name = key + str(index)
            
        return name

    def UpdateButtonFG(self):
        groups = [self.connect, self.RBEBase]
        widgets = [self.btnConnect, self.btnAddConnect]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def UpdateState(self, val, widget):
        if val.get():
            widget.config(state='normal')
        else:
            widget.config(state='disabled')

    def UpdateDirection(self):
        result = simlabutil.GetNormalVectorFromGroup(self.type.get(), self.connect)
        if len(result) == 0:
            return
        
        nz = result

        ny = np.array([0,1,0])
        nx = np.cross(ny, nz)
        if np.linalg.norm(nx) < 1e-9:
            ny = np.array([1,0,0])
            nx = np.cross(ny, nz)
        nx /= np.linalg.norm(nx)
        ny = np.cross(nz, nx)
        ny /= np.linalg.norm(ny)

        widgets = [ self.entNXX, self.entNXY, self.entNXZ, self.entNYX, self.entNYY, self.entNYZ, self.entNZX, self.entNZY, self.entNZZ ]
        values = [ nx[0], nx[1], nx[2], ny[0], ny[1], ny[2], nz[0], nz[1], nz[2] ]
        for i in range(len(widgets)):
            widgets[i].delete(0, tk.END)
            widgets[i].insert(tk.END, round(values[i], 5))

    def IsValid(self):
        if not simlab.isGroupPresent(self.connect):
            messagebox.showinfo('情報','接続面を選択してください。')
            return False
        
        if self.boolRBEAdd.get():
            if not simlab.isGroupPresent(self.RBEBase):
                messagebox.showinfo('情報','基準面を選択してください。')
                return False
            try:
                _ = float(self.entRBELen.get())
                _ = float(self.entRBERad.get())
            except:
                messagebox.showinfo('情報','数値は実数で指定してください。')
                return False

        widgets = [self.entNXX, self.entNXY, self.entNXZ,
            self.entNYX, self.entNYY, self.entNYZ,
            self.entNZX, self.entNZY, self.entNZZ,
            self.entOX, self.entOY, self.entOZ,
            self.entMass] 
        for w in widgets:
            _ = float(w.get())

        widgets = [self.entIXX, self.entIYY, self.entIZZ,
            self.entIXY, self.entIYZ, self.entIZX]
        booleans = [self.booleanXX, self.booleanYY, self.booleanZZ,
            self.booleanXY, self.booleanYZ, self.booleanZX]
        try:
            for i in range(len(widgets)):
                if booleans[i].get():
                    _ = float(widgets[i].get())
        except:
            messagebox.showinfo('情報','数値は実数で指定してください。')
            return False

        nx = np.array([float(self.entNXX.get()), float(self.entNXY.get()), float(self.entNXZ.get())])
        ny = np.array([float(self.entNYX.get()), float(self.entNYY.get()), float(self.entNYZ.get())])
        nz = np.array([float(self.entNZX.get()), float(self.entNZY.get()), float(self.entNZZ.get())])

        for n in [nx, ny, nz]:
            m = np.linalg.norm(n)
            if m < 1e-9:
                messagebox.showinfo('情報','有効な方向を指定してください。')
                return False

        vc = np.cross(nx, ny)
        vcz = np.cross(vc, nz)
        m = np.linalg.norm(vcz)
        if m > 1e-1:
            messagebox.showinfo('情報','方向が直交していません。')
            return False

        return True

    def CreateRectCoordinate(self):
        o = np.array([float(self.entOX.get()), float(self.entOY.get()), float(self.entOZ.get())])
        nx = np.array([float(self.entNXX.get()), float(self.entNXY.get()), float(self.entNXZ.get())])
        ny = np.array([float(self.entNYX.get()), float(self.entNYY.get()), float(self.entNYZ.get())])

        baseNodeID = 10000200
        modelName = simlab.getModelName('FEM')

        originID = simlabutil.AvailableNodeID(modelName, baseNodeID=baseNodeID)
        simlablib.CreateNodeByXYZ(modelName, list(o), originID)

        CID = coordinate.GetNewID()
        name = MASS_COORDINATE + str(CID)
        coordinate.CreateRectCoordinate(name, CID, o, nx, ny)

        AssignCoordinateSystem(CID, originID)

        return originID, CID

    def CreateMass(self, nodeID, axisID):
        booleans = [self.booleanXX.get(), self.booleanYY.get(), self.booleanZZ.get(),
            self.booleanXY.get(), self.booleanYZ.get(), self.booleanZX.get()]
        values = [float(self.entIXX.get()), float(self.entIYY.get()), float(self.entIZZ.get()),
            float(self.entIXY.get()), float(self.entIYZ.get()), float(self.entIZX.get())]
        mass = float(self.entMass.get())
        return CreateMass(nodeID, booleans, values, mass, axisID)

    def Undo(self):
        self.backup.Load()

        # Since the CAD model is displayed immediately after Undo, it is confusing
        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        simlablib.DeleteGroups([self.connect, self.RBEBase])
        super().CloseDialog()