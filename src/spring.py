# coding: utf_8
# SimLab Version 2019.2 (64-bit)
#***************************************************************
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import sys, os, importlib
from hwx import simlab, gui

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

BASE_NODE = 10000000
MAX_ID_RBE = 'Max_ID_RBE'
MAX_ID_COORDINATE = 'Max_ID_Coordinate'
MAX_ID_SPRING = 'Max_ID_Spring'

SPRING_RBE = 'IndexGear_RBE_'
SPRING_COORDINATE = 'IndexGear_RectCoordinate_'
SPRING_SPRING = 'IndexGear_Spring_'

# local
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)
import simlablib
import simlabutil
import importlib
import basedialog
import widget as wt
import tooltip as tp
import numpy as np
import springutil
import coordinate
import springcsv

importlib.reload(simlablib)
importlib.reload(simlabutil)

def CreateGearSpring(indexNodeGrp, shaftNodeGrp, CID, stiff, names):
    modelName = simlab.getModelName('FEM')

    xyz = GetCentroid([indexNodeGrp, shaftNodeGrp]) 
    if len(xyz) == 0:
        return

    node1, rbe1 = CreateRBEForGearSpring(xyz, indexNodeGrp)
    node2, rbe2 = CreateRBEForGearSpring(xyz, shaftNodeGrp)
    simlablib.MergeBodies(modelName, [rbe1, rbe2])

    CreateSpringForGearSpring(node1, node2, CID, stiff, names)

def CreateRBEForGearSpring(xyz, nodeGrp):
    modelName = simlab.getModelName('FEM')

    # independent node
    independentNode = simlabutil.AvailableNodeID(modelName, BASE_NODE)
    simlablib.CreateNodeByXYZ(modelName, list(xyz), independentNode)

    # dependent nodes
    dependentNodes = simlab.getEntityFromGroup(nodeGrp)

    # creates RBE
    RBEID = 1
    if simlab.isParameterPresent(MAX_ID_RBE):
        RBEID = simlab.getIntParameter('$'+ MAX_ID_RBE) + 1
    simlablib.AddIntParameters(MAX_ID_RBE, RBEID)
    RBEName = SPRING_RBE + str(RBEID)
    simlablib.ManualRBE(modelName, RBEName, independentNode, dependentNodes)

    return independentNode, RBEName

def CreateSpringForGearSpring(node1, node2, CID, stiff, names):
    tname, rname = names

    # ID
    springID = 1
    if simlab.isParameterPresent(MAX_ID_SPRING):
        springID = simlab.getIntParameter('$'+MAX_ID_SPRING) + 1
    simlablib.AddIntParameters(MAX_ID_SPRING, springID)

    t, r = stiff

    # trans
    for i, direction, flag in [[0, 'X', 1], [1, 'Y', 2], [2, 'Z', 4]]:
        if t[i] == 0.0:
            continue
        name = tname + '_' + str(springID) + '_' + direction
        CreateSpringFunc(name, node1, node2, CID, t[i], flag)

    # rot
    for i, direction, flag in [[0, 'X', 8], [1, 'Y', 16], [2, 'Z', 32]]:
        if r[i] == 0.0:
            continue
        name = rname + '_' + str(springID) + '_' + direction
        CreateSpringFunc(name, node1, node2, CID, t[i], flag)

def CreateSpringFunc(name, node1, node2, CID, stiff, flag):
    modelName = simlab.getModelName('FEM')
    SpringElement=''' <Spring CheckBox="ON" UUID="ACA1CCC4-4687-41bd-9BA3-0C602C5B2B7D" BCType="Spring" isObject="2">
    <tag Value="-1"/>
    <Name Value="''' + name + '''"/>
    <SpringEntities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(node1) + ''',''' + str(node2) + ''',</Node>
    </Entities>
    </SpringEntities>
    <ElementID Value="0"/>
    <AxisID Value="''' + str(CID) + '''"/>
    <FieldID Value=""/>
    <Type Value="Nodes" Index="0"/>
    <SpringType Value="0"/>
    <PropertyID Value="0"/>
    <TXStiff Value="''' + str(stiff) + '''" CheckBox="0"/>
    <TYStiff Value="0.0" CheckBox="0"/>
    <TZStiff Value="0.0" CheckBox="0"/>
    <RXStiff Value="0.0" CheckBox="0"/>
    <RYStiff Value="0.0" CheckBox="0"/>
    <RZStiff Value="0.0" CheckBox="0"/>
    <Flag1 Value="''' + str(flag) + '''"/>
    <Flag2 Value="''' + str(flag) + '''"/>
    <GndSpring Value="0"/>
    <FieldData Value="None" Index="0"/>
    </Spring>'''
    simlab.execute(SpringElement)

def CreateCoordinateForIndexGear(originNode, nVecs):
    modelName = simlab.getModelName('FEM')

    o = np.array(simlab.getNodePositionFromNodeID(modelName, originNode))
    nx, ny, _ = nVecs

    xyzXNode = o + nx
    xNode = simlabutil.AvailableNodeID(modelName, BASE_NODE)
    simlablib.CreateNodeByXYZ(modelName, list(xyzXNode), xNode)

    xyzYNode = o + ny
    yNode = simlabutil.AvailableNodeID(modelName, BASE_NODE)
    simlablib.CreateNodeByXYZ(modelName, list(xyzYNode), yNode)
    
    # ID
    axisID = 1
    if simlab.isParameterPresent(MAX_ID_COORDINATE):
        axisID = simlab.getIntParameter('$'+MAX_ID_COORDINATE) + 1
    simlablib.AddIntParameters(MAX_ID_COORDINATE, axisID)

    # Name
    name = SPRING_COORDINATE + str(axisID)

    CreateCoordinateSystem=''' <Coordinate UUID="b625f5cd-2925-4f9f-94a2-b58854934f8b" BCType="Coordinates" isObject="2">
    <tag Value="-1"/>
    <StackIndex Value="CoordinateXYPoint"/>
    <CoordinateXYPoint>
    <Name Value="''' + name + '''"/>
    <Center>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(originNode) + ''',</Node>
        </Entities>
    </Center>
    <PointX>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(xNode) + ''',</Node>
        </Entities>
    </PointX>
    <PointY>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(yNode) + ''',</Node>
        </Entities>
    </PointY>
    <AxisID Value="''' + str(axisID) + '''"/>
    <Type Value="Rectangle" Index="0"/>
    <AttachToNodes Value="0"/>
    </CoordinateXYPoint>
    <CoordinateXZPoint>
    <Name Value=""/>
    <Center EntityTypes="" Value="" ModelIds=""/>
    <PointX EntityTypes="" Value="" ModelIds=""/>
    <PointZ EntityTypes="" Value="" ModelIds=""/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    <AttachToNodes Value="0"/>
    </CoordinateXZPoint>
    <CoordinateXZPlane>
    <Name Value=""/>
    <Center EntityTypes="" Value="" ModelIds=""/>
    <PointZ EntityTypes="" Value="" ModelIds=""/>
    <XZPlane EntityTypes="" Value="" ModelIds=""/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    <AttachToNodes Value="0"/>
    </CoordinateXZPlane>
    <CoordinateCylindrical>
    <Name Value=""/>
    <Face EntityTypes="" Value="" ModelIds=""/>
    <Node EntityTypes="" Value="" ModelIds=""/>
    <PointOnR Value="0"/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    </CoordinateCylindrical>
    <CoordinateCircular>
    <Name Value=""/>
    <Edge EntityTypes="" Value="" ModelIds=""/>
    <Node EntityTypes="" Value="" ModelIds=""/>
    <PointOnR Value="0"/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    </CoordinateCircular>
    <CoordinateFillet>
    <SupportEntities EntityTypes="" Value="" ModelIds=""/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    <FilletFaceNodes Value="0"/>
    </CoordinateFillet>
    <CoordinateRotate>
    <Point1 Value="0,0,0"/>
    <Point2 Value="0,0,0"/>
    <Angle Value="90"/>
    <AxisCoordinateID Value="1"/>
    <AxisType Value="X_AXIS"/>
    <NumCopies Value="0" Check="0"/>
    </CoordinateRotate>
    <CoordinateTranslate>
    <Magnitude Value="0"/>
    <Scale Value="0"/>
    <AxisCoordinateID Value="1"/>
    <DefineVectorCoordinateID Value="1"/>
    <AxisPoint Value="0,0,0"/>
    <NumCopies Value="0" Check="0"/>
    <TranslateUsingNodes Value="0"/>
    </CoordinateTranslate>
    <CoordinateArcPairs>
    <Name Value=""/>
    <XArc1 EntityTypes="" Value="" ModelIds=""/>
    <XArc2 EntityTypes="" Value="" ModelIds=""/>
    <YArc1 EntityTypes="" Value="" ModelIds=""/>
    <YArc2 EntityTypes="" Value="" ModelIds=""/>
    </CoordinateArcPairs>
    </Coordinate>'''
    simlab.execute(CreateCoordinateSystem)

    simlablib.DeleteSelectedOphanNodes(modelName, [xNode, yNode])
    return axisID

def GetCentroid(nodeGrpList):
    nodes = []
    for grp in nodeGrpList:
        ns = simlab.getEntityFromGroup(grp)
        nodes.extend(ns)
    
    if len(nodes) == 0:
        return []
    
    modelName = simlab.getModelName('FEM')
    xyz_sum = np.array([0,0,0])
    for node in nodes:
        p = simlab.getNodePositionFromNodeID(modelName, node)
        xyz_sum = xyz_sum + np.array(simlab.getNodePositionFromNodeID(modelName, node))

    xyz = xyz_sum / len(nodes)
    return xyz

class SpringDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup, springs):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        
        self.master.title('バネ、RBE作成')
        self.backup = backup
        self.springs = springs

        self.outerFaces = '_Outer_Faces'
        self.innerFaces = '_Inner_Faces'
        self.planeNodes = '_Plane_Nodes'
        self.indexNodes = '_Index_Nodes'
        self.shaftNodes = '_Shaft_Nodes'
        self.pageIndex = 0

        self.CreateWidgets()
        self.UpdateButtonFG()
        simlab.setSelectionFilter('Body')
        
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmType1 = tk.Frame(self.nb)
        self.frmType2 = tk.Frame(self.nb)
        self.nb.add(self.frmType1, text=' ピストン、タレット ')
        self.nb.add(self.frmType2, text=' インデックスギヤ嚙み合い部 ')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        self.nb.bind('<<NotebookTabChanged>>', self.ChangeTab)

        self.CreateType1()
        self.CreateType2()

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X)

        btnWidth = 10
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.E)

        self.UpdateType1Widgets()

    def CreateType1(self):
        # Tips
        self.lblNote = tk.Label(self.frmType1, text='Tips: スプリングを作成する箇所の面を選択して、[ 作成 ]ボタンを押してください。')
        self.lblNote.pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)
        btnWidth = 10
        
        self.frmSelect = tk.Frame(self.frmType1)
        self.frmSelect.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)

        # Select Body
        self.frmSelBody = tk.Frame(self.frmSelect)
        self.frmSelBody.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconSpBdyOut = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'spring_outer.png')), master=self.frmSelBody)
        tk.Label(self.frmSelBody, image=self.iconSpBdyOut).pack(side=tk.LEFT)
        self.iconSpBdyIn = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'spring_inner.png')), master=self.frmSelBody)
        tk.Label(self.frmSelBody, image=self.iconSpBdyIn).pack(side=tk.LEFT)
        self.btnOuterBody = tk.Button(self.frmSelBody, text=' タレットバーの内面 ', command=self.SelectOuterFaces)
        self.btnOuterBody.place(x=80, y=20)
        self.btnInnerBody = tk.Button(self.frmSelBody, text=' 内側ボディの外面 ', command=self.SelectInnerFaces)
        self.btnInnerBody.place(x=280, y=25)

        # Select Nodes
        self.frmSelNodes = tk.Frame(self.frmSelect)
        self.iconSpNodes = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'spring_node.png')), master=self.frmSelNodes)
        tk.Label(self.frmSelNodes, image=self.iconSpNodes).pack(side=tk.LEFT)
        self.btnNodes = tk.Button(self.frmSelNodes, text=' バネが乗る平面を\n規定する3節点 ', command=self.SelectNodes)
        self.btnNodes.place(x=20, y=10)

        tk.Frame(self.frmSelNodes, width=5).pack(side=tk.LEFT)

        self.frmConnect = tk.Frame(self.frmSelNodes)
        self.frmConnect.pack(side=tk.LEFT)

        self.frmConType = tk.Frame(self.frmConnect)
        self.frmConType.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmConType, text='接続タイプ:').pack(side=tk.LEFT, anchor=tk.W)

        self.ConnectionType = tk.StringVar()
        self.ConnectionType.set('Spring')
        self.radConSpring = tk.Radiobutton(self.frmConType, text='バネ', value='Spring', variable=self.ConnectionType, command=self.SelectConnectType)
        self.radConSpring.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.radConRBE = tk.Radiobutton(self.frmConType, text='RBE', value='RBE', variable=self.ConnectionType, command=self.SelectConnectType)
        self.radConRBE.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        tk.Frame(self.frmConnect, height=5).pack(side=tk.TOP)

        self.frmVal = tk.Frame(self.frmConnect)
        self.frmVal.pack(side=tk.TOP, anchor=tk.NW, padx=10)

        self.frmNumSpring = tk.Frame(self.frmVal)
        self.frmNumSpring.pack(side=tk.TOP, anchor=tk.W)
        tk.Label(self.frmNumSpring, text='バネ数 :').pack(side=tk.LEFT, anchor=tk.W)
        self.numSpring = tk.IntVar()
        self.numSpring.set(8)
        self.cmbNumSpring = ttk.Combobox(self.frmNumSpring, width=4, state='readonly', values=[6, 8, 10, 12], textvariable=self.numSpring)
        self.cmbNumSpring.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        tk.Frame(self.frmVal, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmPTCoord = tk.Frame(self.frmVal)
        self.frmPTCoord.pack(side=tk.TOP, anchor=tk.W)
        self.lblPTCoord = tk.Label(self.frmPTCoord, text='座標系 : ')
        self.lblPTCoord.pack(side=tk.LEFT, anchor=tk.W)

        coords = coordinate.GetAllCoordinates()
        self.PTCoord = tk.StringVar()
        if len(coords) != 0:
            self.PTCoord.set(coords[0])
        self.cmbPTCoords = ttk.Combobox(self.frmPTCoord, values=coords, textvariable=self.PTCoord, width=20, state='readonly')
        self.cmbPTCoords.pack(side=tk.LEFT, anchor=tk.W)

        self.frmStiff = tk.LabelFrame(self.frmVal, text='剛性')
        self.frmStiff.pack(side=tk.TOP, anchor=tk.NW)

        self.frmSpringType = tk.Frame(self.frmStiff)
        self.frmSpringType.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmSpringType, text='CSV:').pack(side=tk.LEFT, anchor=tk.W)

        self.psSpringType = tk.StringVar()
        self.cmbPSType = ttk.Combobox(self.frmSpringType, width=18, state='readonly', values=[], textvariable=self.psSpringType)
        self.cmbPSType.pack(side=tk.LEFT, anchor=tk.W)
        self.cmbPSType.bind('<<ComboboxSelected>>' , self.springs.Select)

        tk.Frame(self.frmStiff, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmSpStiff = tk.Frame(self.frmStiff)
        self.frmSpStiff.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        tk.Label(self.frmSpStiff, text='R :').grid(row=0, column=0, pady=2)
        tk.Label(self.frmSpStiff, text='θ :').grid(row=1, column=0, pady=2)
        tk.Label(self.frmSpStiff, text='Z :').grid(row=2, column=0, pady=2)
        self.entSx = tk.Entry(self.frmSpStiff, width=15)
        self.entSy = tk.Entry(self.frmSpStiff, width=15)
        self.entSz = tk.Entry(self.frmSpStiff, width=15)
        self.entSx.grid(row=0, column=1, padx=2)
        self.entSy.grid(row=1, column=1, padx=2)
        self.entSz.grid(row=2, column=1, padx=2)
        self.entSx.insert(tk.END, 0)
        self.entSy.insert(tk.END, 0)
        self.entSz.insert(tk.END, 0)

        self.springs.AppendWidget( self.cmbPSType, self.psSpringType, self.entSx, self.entSy, self.entSz)
        tk.Frame(self.frmStiff, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.boolMPC = tk.BooleanVar()
        self.boolMPC.set(False)
        self.chkMPC = ttk.Checkbutton(self.frmVal, text='MPC 作成', variable=self.boolMPC)
        self.chkMPC.pack(side=tk.TOP, anchor=tk.NW, pady=2)

        self.frmTol = tk.Frame(self.frmVal)
        self.frmTol.pack(side=tk.TOP, anchor=tk.W, pady=2)
        tk.Label(self.frmTol, text='トレランス: ').pack(side=tk.LEFT, anchor=tk.W)
        self.entTol = tk.Entry(self.frmTol, width=10)
        self.entTol.pack(side=tk.LEFT, anchor=tk.W)
        self.entTol.insert(tk.END, 1.0)

        # select ctrl
        self.frmSelCtrl = tk.Frame(self.frmType1)
        self.frmSelCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        self.frmSelBtn = tk.Frame(self.frmSelCtrl)
        self.frmSelBtn.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconPrev = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'prev.png')), master=self.frmSelBtn)
        self.btnPrev = tk.Button(self.frmSelBtn, image=self.iconPrev, command=self.JumpPrev)
        self.btnPrev.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)
        self.iconNext = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'next.png')), master=self.frmSelBtn)
        self.btnNext = tk.Button(self.frmSelBtn, image=self.iconNext, command=self.JumpNext)
        self.btnNext.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)

        self.frmType1Ctrl = tk.Frame(self.frmType1)
        self.frmType1Ctrl.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X, padx=5, pady=5)

        btnWidth = 10
        self.btnType1Create = tk.Button(self.frmType1Ctrl, text='作成', command=self.CreateConnection, width=btnWidth)
        self.btnType1Create.pack(side=tk.LEFT, anchor=tk.W, pady=2)
        self.btnType1Undo = tk.Button(self.frmType1Ctrl, text='戻す', command=self.Undo, width=btnWidth)
        self.btnType1Undo.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        self.backup.Append(self.btnType1Undo)

    def ChangeTab(self, event):
        simlabutil.ClearSelection()

        cid = self.nb.index('current')
        if cid == 0:
            self.UpdateType1Widgets()
        elif cid == 1:
            self.UpdateType2Widgets()

    def SelectConnectType(self):
        if self.ConnectionType.get() == 'Spring':
            self.cmbNumSpring.config(state='readonly')
            self.cmbPTCoords.config(state='readonly')
            self.cmbPSType.config(state='readonly')
            self.entSx.config(state='normal')
            self.entSy.config(state='normal')
            self.entSz.config(state='normal')
            self.chkMPC.config(state='normal')
            self.entTol.config(state='normal')
        else:
            self.cmbNumSpring.config(state='disabled')
            self.cmbPTCoords.config(state='disabled')
            self.cmbPSType.config(state='disabled')
            self.entSx.config(state='disabled')
            self.entSy.config(state='disabled')
            self.entSz.config(state='disabled')
            self.chkMPC.config(state='disabled')
            self.entTol.config(state='disabled')

    def JumpPrev(self):
        self.pageIndex -= 1
        self.UpdateType1Widgets()

    def JumpNext(self):
        self.pageIndex += 1
        self.UpdateType1Widgets()
    
    def JumpIndex(self, idx):
        self.pageIndex = idx
        self.UpdateType1Widgets()

    def UpdateType1Widgets(self):
        self.UpdateFig()
        self.UpdateButtonState()
        self.UpdateButtonFG()

    def UpdateFig(self):
        self.frmSelBody.forget()
        self.frmSelNodes.forget()
        selectionFilter = 'CylinderFace'
        if self.pageIndex == 0:
            self.frmSelBody.pack(side=tk.TOP, anchor=tk.CENTER)
            selectionFilter = 'CylinderFace'
        elif self.pageIndex == 1:
            self.frmSelNodes.pack(side=tk.TOP, anchor=tk.CENTER)
            selectionFilter = 'Node'
        else:
            pass
        simlab.setSelectionFilter(selectionFilter)

    def UpdateButtonState(self):
        self.btnPrev.config(state='normal')
        self.btnNext.config(state='normal')
        if self.pageIndex == 0:
            self.btnPrev.config(state='disabled')
        if self.pageIndex == 1:
            self.btnNext.config(state='disabled')
        else:
            pass

    def SelectOuterFaces(self):
        faces = simlab.getSelectedEntities('Face')
        if len(faces) == 0:
            messagebox.showinfo('情報','タレットの内面を選択した後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.outerFaces)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.outerFaces)

        simlabutil.ClearSelection()
        if simlab.isGroupPresent(self.outerFaces) and simlab.isGroupPresent(self.innerFaces):
            self.JumpNext()
        else:
            self.UpdateType1Widgets()

    def SelectInnerFaces(self):
        faces = simlab.getSelectedEntities('Face')
        if len(faces) == 0:
            messagebox.showinfo('情報','内側のボディの外面を後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.innerFaces)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.innerFaces)

        simlabutil.ClearSelection()
        if simlab.isGroupPresent(self.outerFaces) and simlab.isGroupPresent(self.innerFaces):
            self.JumpNext()
        else:
            self.UpdateType1Widgets()

    def SelectNodes(self):
        nodes = simlab.simlab.getSelectedEntities('Node')
        if len(nodes) != 3:
            messagebox.showinfo('情報','3節点を選択後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.planeNodes)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Node', nodes, self.planeNodes)

        simlabutil.ClearSelection()
        self.UpdateType1Widgets()

    def CreateConnection(self):
        if self.ConnectionType.get() == 'Spring':
            self.CreateSpring()
        else:
            self.CreateRBE()

    def CreateSpring(self):
        if not simlab.isGroupPresent(self.outerFaces) or not simlab.isGroupPresent(self.innerFaces) or not simlab.isGroupPresent(self.planeNodes):
            messagebox.showinfo('情報','エンティティを選択してください。')
            return
        try:
            numSpring = int(self.cmbNumSpring.get())
            CID = coordinate.GetID(self.PTCoord.get())
            Sx = float(self.entSx.get())
            Sy = float(self.entSy.get())
            Sz = float(self.entSz.get())
            boolMPC = self.boolMPC.get()
            tolerance = float(self.entTol.get())
        except:
            messagebox.showinfo('情報','実数を指定してください。')
            return
        
        self.backup.Save('Spring1')

        importlib.reload(springutil)

        springName = self.psSpringType.get()
        if len(springName) == 0:
            springName = 'Spring_'

        if CID == -1:
            messagebox.showinfo('情報', "Select coordinate id")
            return
    
        nodeEnts = simlab.getEntityFromGroup(self.planeNodes)
        innerFaceNodes = springutil.associatedNodesWithFace(simlab.getEntityFromGroup(self.innerFaces))
        remainder = tuple(set(nodeEnts)-set(innerFaceNodes))
        if remainder:
            messagebox.showinfo("情報", "Select three node points on the inner face group")
            return

        springStiff = Sx, Sy, Sz
        springProp = springName, numSpring, springStiff, CID
        springutil.connectTwoFacesUsingSpring(springProp, boolMPC, tolerance, self.innerFaces, self.outerFaces, self.planeNodes)
        simlablib.DeleteGroups([self.outerFaces, self.innerFaces, self.planeNodes])

        self.JumpIndex(0)

    def CreateRBE(self):
        if not simlab.isGroupPresent(self.outerFaces) or not simlab.isGroupPresent(self.innerFaces) or not simlab.isGroupPresent(self.planeNodes):
            messagebox.showinfo('情報','エンティティを選択してください。')
            return
        
        self.backup.Save('RBE')
        nodeEnts = simlab.getEntityFromGroup(self.planeNodes)
        innerFaceNodes = springutil.associatedNodesWithFace(simlab.getEntityFromGroup(self.innerFaces))
        remainder = tuple(set(nodeEnts)-set(innerFaceNodes))
        if remainder:
            messagebox.showinfo("情報", "Select three node points on the inner face group")
            return
        importlib.reload(springutil)
        springutil.connectTwoFacesUsingRbe(self.outerFaces, self.innerFaces, self.planeNodes)

        simlablib.DeleteGroups([self.outerFaces, self.innerFaces, self.planeNodes])
        self.JumpIndex(0)

    def CreateType2(self):
        # Tips
        self.lblNote2 = tk.Label(self.frmType2, text='Tips: 画面のエンティティを選択して、[ 作成 ]ボタンを押してください。')
        self.lblNote2.pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)
        btnWidth = 10
        
        self.frmType2Select = tk.Frame(self.frmType2)
        self.frmType2Select.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.iconType2Node = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'spring_index.png')), master=self.frmType2Select)
        tk.Label(self.frmType2Select, image=self.iconType2Node).pack(side=tk.LEFT, anchor=tk.W)
        
        self.btnIndex = tk.Button(self.frmType2Select, text=' インデックス側の節点 ', command=self.SelectIndex)
        self.btnIndex.place(x=70, y=45)
        self.btnShaft = tk.Button(self.frmType2Select, text=' シャフト側の節点 ', command=self.SelectShaft)
        self.btnShaft.place(x=50, y=150)

        self.frmVal = tk.Frame(self.frmType2Select)
        self.frmVal.pack(side=tk.LEFT, anchor=tk.W, expand=1, fill=tk.BOTH, padx=5)

        self.frmGRCoord = tk.Frame(self.frmVal)
        self.frmGRCoord.pack(side=tk.TOP, anchor=tk.W)
        self.lblGRCoord = tk.Label(self.frmGRCoord, text='座標系 : ')
        self.lblGRCoord.pack(side=tk.LEFT, anchor=tk.W)

        coords = coordinate.GetAllCoordinates()
        self.GRCoord = tk.StringVar()
        if len(coords) != 0:
            self.GRCoord.set(coords[0])
        self.cmbGRCoords = ttk.Combobox(self.frmGRCoord, values=coords, textvariable=self.GRCoord, width=20, state='readonly')
        self.cmbGRCoords.pack(side=tk.LEFT, anchor=tk.W)

        self.frmStiff = tk.LabelFrame(self.frmVal, text='剛性')
        self.frmStiff.pack(side=tk.TOP, anchor=tk.W, expand=0, fill=tk.X)

        tk.Label(self.frmStiff, text='T :').grid(row=0, column=0, pady=2)
        self.entType2Tx = tk.Entry(self.frmStiff, width=10)
        self.entType2Ty = tk.Entry(self.frmStiff, width=10)
        self.entType2Tz = tk.Entry(self.frmStiff, width=10)
        self.entType2Tx.grid(row=0, column=1, padx=2)
        self.entType2Ty.grid(row=0, column=2, padx=2)
        self.entType2Tz.grid(row=0, column=3, padx=2)

        self.type2TSpringType = tk.StringVar()
        self.cmbType2TSp = ttk.Combobox(self.frmStiff, width=18, state='readonly', values=[], textvariable=self.type2TSpringType)
        self.cmbType2TSp.grid(row=0, column=4, padx=2)
        self.cmbType2TSp.bind('<<ComboboxSelected>>' , self.springs.Select)

        self.springs.AppendWidget(self.cmbType2TSp, self.type2TSpringType, self.entType2Tx, self.entType2Ty, self.entType2Tz)

        tk.Label(self.frmStiff, text='R :').grid(row=1, column=0, pady=2)
        self.entType2Rx = tk.Entry(self.frmStiff, width=10)
        self.entType2Ry = tk.Entry(self.frmStiff, width=10)
        self.entType2Rz = tk.Entry(self.frmStiff, width=10)
        self.entType2Rx.grid(row=1, column=1)
        self.entType2Ry.grid(row=1, column=2)
        self.entType2Rz.grid(row=1, column=3)
        tk.Frame(self.frmStiff, height=5).grid(row=2, column=0)

        self.type2RSpringType = tk.StringVar()
        self.cmbType2RSp = ttk.Combobox(self.frmStiff, width=18, state='readonly', values=[], textvariable=self.type2RSpringType)
        self.cmbType2RSp.grid(row=1, column=4, padx=2)
        self.cmbType2RSp.bind('<<ComboboxSelected>>' , self.springs.Select)
        self.springs.AppendWidget(self.cmbType2RSp, self.type2RSpringType, self.entType2Rx, self.entType2Ry, self.entType2Rz)

        self.entType2Tx.insert(tk.END, 0)
        self.entType2Ty.insert(tk.END, 0)
        self.entType2Tz.insert(tk.END, 0)
        self.entType2Rx.insert(tk.END, 0)
        self.entType2Ry.insert(tk.END, 0)
        self.entType2Rz.insert(tk.END, 0)

        self.frmType2Ctrl = tk.Frame(self.frmType2)
        self.frmType2Ctrl.pack(side=tk.BOTTOM, anchor=tk.NE, expand=1, fill=tk.X, padx=5, pady=5)

        self.btnType2Create = tk.Button(self.frmType2Ctrl, text='作成', command=self.CreateGearSpring, width=btnWidth)
        self.btnType2Create.pack(side=tk.LEFT, anchor=tk.W, pady=2)
        self.btnType2Undo = tk.Button(self.frmType2Ctrl, text='戻す', command=self.Undo, width=btnWidth)
        self.btnType2Undo.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        self.backup.Append(self.btnType2Undo)

    def SelectShaft(self):
        nodes = simlab.simlab.getSelectedEntities('Node')
        if len(nodes) == 0:
            messagebox.showinfo('情報','節点を選択後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.shaftNodes)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Node', nodes, self.shaftNodes)

        simlabutil.ClearSelection()
        self.UpdateType2Widgets()

    def SelectIndex(self):
        nodes = simlab.simlab.getSelectedEntities('Node')
        if len(nodes) == 0:
            messagebox.showinfo('情報','節点を選択後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.indexNodes)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Node', nodes, self.indexNodes)

        simlabutil.ClearSelection()
        self.UpdateType2Widgets()

    def CreateGearSpring(self):
        if not simlab.isGroupPresent(self.indexNodes) or not simlab.isGroupPresent(self.shaftNodes):
            messagebox.showinfo('情報','エンティティを選択してください。')
            return
        try:
            CID = coordinate.GetID(self.GRCoord.get())
            t = [float(self.entType2Tx.get()), float(self.entType2Ty.get()), float(self.entType2Tz.get())]
            s = [float(self.entType2Rx.get()), float(self.entType2Ry.get()), float(self.entType2Rz.get())]
            stiff = [t,s]
        except:
            messagebox.showinfo('情報','実数を指定してください。')
            return
        
        tname = self.type2TSpringType.get()
        if len(tname) == 0:
            tname = 'Spring'
        rname = self.type2RSpringType.get()
        if len(rname) == 0:
            rname = 'Spring'
        names = [tname, rname]

        self.backup.Save('Spring2')

        CreateGearSpring(self.indexNodes, self.shaftNodes, CID, stiff, names)

    def UpdateType2Widgets(self):
        simlab.setSelectionFilter('Node')
        self.UpdateButtonFG()

    def UpdateButtonFG(self):
        groups = [self.outerFaces, self.innerFaces, self.planeNodes, self.indexNodes, self.shaftNodes]
        widgets = [self.btnOuterBody, self.btnInnerBody, self.btnNodes, self.btnIndex, self.btnShaft]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def Undo(self):
        self.backup.Load()
        self.JumpIndex(self.pageIndex)

        # Since the CAD model is displayed immediately after Undo, it is confusing
        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        simlablib.DeleteGroups([self.outerFaces, self.innerFaces, self.planeNodes, self.indexNodes, self.shaftNodes])
        super().CloseDialog()