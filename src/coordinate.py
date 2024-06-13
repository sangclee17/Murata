import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

MAX_ID_COORDINATE = 'Max_ID_Coordinate'
COORDINATE_NAME = 'Coordinate_Name_'

# local import
import basedialog
import simlabutil
import simlablib

# help function
def GetNewID():
    coordinateID = 1

    if simlab.isParameterPresent(MAX_ID_COORDINATE):
        coordinateID = simlab.getIntParameter('$'+MAX_ID_COORDINATE) + 1
    simlablib.AddIntParameters(MAX_ID_COORDINATE, coordinateID)

    return coordinateID

def GetAllCoordinates():
    if not simlab.isParameterPresent(MAX_ID_COORDINATE):
        return []

    maxID = simlab.getIntParameter('$'+MAX_ID_COORDINATE)

    coords = []
    for i in range(1, maxID+1):
        key = COORDINATE_NAME + str(i)
        if not simlab.isParameterPresent(key):
            continue

        name = simlab.getStringParameter('$' + key)
        coords.append(name)

    return coords

def GetID(name):
    if not simlab.isParameterPresent(MAX_ID_COORDINATE):
        return -1

    maxID = simlab.getIntParameter('$'+MAX_ID_COORDINATE)

    for i in range(1, maxID+1):
        key = COORDINATE_NAME + str(i)
        if not simlab.isParameterPresent(key):
            continue

        checkName = simlab.getStringParameter('$' + key)
        if name == checkName:
            ID = int(key.split('_')[-1])
            return ID
    
    return -1

def CreateRectCoordinate(name, ID, o, nx, ny):
    modelName = simlab.getModelName('FEM')
    baseNodeID = 11000000

    nz = np.cross(nx, ny)
    px = np.array(o) + nx
    pz = np.array(o) + nz

    originID = simlabutil.AvailableNodeID(modelName, baseNodeID)
    simlablib.CreateNodeByXYZ(modelName, list(o), originID)

    xID = simlabutil.AvailableNodeID(modelName, baseNodeID+1)
    simlablib.CreateNodeByXYZ(modelName, list(px), xID)

    zID = simlabutil.AvailableNodeID(modelName, baseNodeID+2)
    simlablib.CreateNodeByXYZ(modelName, list(pz), zID)

    CreateCoordinateSystem=''' <Coordinate BCType="Coordinates" isObject="2" UUID="b625f5cd-2925-4f9f-94a2-b58854934f8b">
    <tag Value="-1"/>
    <StackIndex Value="CoordinateXZPoint"/>
    <CoordinateXYPoint>
    <Name Value=""/>
    <Center EntityTypes="" Value="" ModelIds=""/>
    <PointX EntityTypes="" Value="" ModelIds=""/>
    <PointY EntityTypes="" Value="" ModelIds=""/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    <AttachToNodes Value="0"/>
    </CoordinateXYPoint>
    <CoordinateXZPoint>
    <Name Value="''' + name + '''"/>
    <Center>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(originID) + ''',</Node>
        </Entities>
    </Center>
    <PointX>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(xID) + ''',</Node>
        </Entities>
    </PointX>
    <PointZ>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(zID) + ''',</Node>
        </Entities>
    </PointZ>
    <AxisID Value="''' + str(ID) + '''"/>
    <Type Value="Rectangle" Index="0"/>
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

    simlablib.AddStringParameters(COORDINATE_NAME + str(ID), name)
    simlablib.DeleteSelectedOphanNodes(modelName, [originID, xID, zID])

def CreateCylinderCoordinate(name, ID, origin, nz):
    modelName = simlab.getModelName('FEM')
    baseNodeID = 11000000

    nx = np.array([1,0,0])
    ny = np.cross(nz, nx)
    if np.linalg.norm(ny) < 1e-9:
        nx = np.array([0,1,0])
        ny = np.cross(nz, nx)
    ny /= np.linalg.norm(ny)
    nx = np.cross(ny, nz)

    px = np.array(origin) + nx
    pz = np.array(origin) + nz

    originID = simlabutil.AvailableNodeID(modelName, baseNodeID)
    simlablib.CreateNodeByXYZ(modelName, list(origin), originID)

    xID = simlabutil.AvailableNodeID(modelName, baseNodeID+1)
    simlablib.CreateNodeByXYZ(modelName, list(px), xID)

    zID = simlabutil.AvailableNodeID(modelName, baseNodeID+2)
    simlablib.CreateNodeByXYZ(modelName, list(pz), zID)
 
    CreateCoordinateSystem=''' <Coordinate BCType="Coordinates" isObject="2" UUID="b625f5cd-2925-4f9f-94a2-b58854934f8b">
    <tag Value="-1"/>
    <StackIndex Value="CoordinateXZPoint"/>
    <CoordinateXYPoint>
    <Name Value=""/>
    <Center EntityTypes="" Value="" ModelIds=""/>
    <PointX EntityTypes="" Value="" ModelIds=""/>
    <PointY EntityTypes="" Value="" ModelIds=""/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    <AttachToNodes Value="0"/>
    </CoordinateXYPoint>
    <CoordinateXZPoint>
    <Name Value="''' + name + '''"/>
    <Center>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(originID) + ''',</Node>
        </Entities>
    </Center>
    <PointX>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(xID) + ''',</Node>
        </Entities>
    </PointX>
    <PointZ>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(zID) + ''',</Node>
        </Entities>
    </PointZ>
    <AxisID Value="''' + str(ID) + '''"/>
    <Type Value="Cylindrical" Index="1"/>
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

    simlablib.AddStringParameters(COORDINATE_NAME + str(ID), name)
    simlablib.DeleteSelectedOphanNodes(modelName, [originID, xID, zID])

def EditCoordinate(name, ID, CType):
    index = 0
    if CType == 'Cylindrical':
        index = 1

    CreateCoordinateSystem=''' <Coordinate BCType="Coordinates" Auto="1" isObject="2" UUID="b625f5cd-2925-4f9f-94a2-b58854934f8b">
    <tag Value="1060"/>
    <StackIndex Value="CoordinateXZPoint"/>
    <CoordinateXYPoint>
    <Name Value=""/>
    <Center EntityTypes="" Value="" ModelIds=""/>
    <PointX EntityTypes="" Value="" ModelIds=""/>
    <PointY EntityTypes="" Value="" ModelIds=""/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    <AttachToNodes Value="0"/>
    </CoordinateXYPoint>
    <CoordinateXZPoint>
    <Name Value="''' + name + '''"/>
    <Center EntityTypes="" Value="" ModelIds=""/>
    <PointX EntityTypes="" Value="" ModelIds=""/>
    <PointZ EntityTypes="" Value="" ModelIds=""/>
    <AxisID Value="''' + str(ID) + '''"/>
    <Type Value="''' + CType + '''" Index="''' + str(index) + '''"/>
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

    simlablib.AddStringParameters(COORDINATE_NAME + str(ID), name)

def DeleteCoordinate(name):
    DeleteLBCControl=''' <DeleteLBCControl CheckBox="ON" UUID="b37a621e-e984-4cee-a307-3a80317852ae">
    <Output/>
    <Name Value="''' + name + '''" Type="Coordinates"/>
    </DeleteLBCControl>'''
    simlab.execute(DeleteLBCControl)

    ID = GetID(name)
    simlablib.DeleteParameters(COORDINATE_NAME + str(ID))

class CoordinateDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('座標系作成')
        self.backup = backup

        self.CreateWidgets()

        simlab.setSelectionFilter('Node')
        simlabutil.ClearSelection()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmCreate = tk.Frame(self.nb)
        self.frmEdit = tk.Frame(self.nb)
        self.frmDelete = tk.Frame(self.nb)
        self.nb.add(self.frmCreate, text=' 作成 ')
        self.nb.add(self.frmEdit, text=' 編集 ')
        self.nb.add(self.frmDelete, text=' 削除 ')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        self.nb.bind('<<NotebookTabChanged>>', self.ChangeTab)

        self.CreateCreatingTab()
        self.CreateEdittingTab()
        self.CreateDeletingTab()

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def ChangeTab(self, event):
        simlabutil.ClearSelection()
        self.UpdateCoords()

    def CreateCreatingTab(self):
        self.frmCreateTop= tk.Frame(self.frmCreate)
        self.frmCreateTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.frmCName = tk.Frame(self.frmCreateTop)
        self.frmCName.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmCName, text='名前: ').pack(side=tk.LEFT, anchor=tk.W)
        self.entName = tk.Entry(self.frmCName, width=25)
        self.entName.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmCreateTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCType= tk.Frame(self.frmCreateTop)
        self.frmCType.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmCType, text='座標系タイプ: ').pack(side=tk.LEFT, anchor=tk.W)

        self.CType = tk.StringVar()
        self.CType.set('Rectangle')
        self.chkFace = tk.Radiobutton(self.frmCType, text='直交座標系', value='Rectangle', variable=self.CType, command=self.SelectCType)
        self.chkFace.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.chkNode = tk.Radiobutton(self.frmCType, text='円筒座標系', value='Cylindrical', variable=self.CType, command=self.SelectCType)
        self.chkNode.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        tk.Frame(self.frmCreateTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCSelTop = tk.Frame(self.frmCreateTop)
        self.frmCSelTop.pack(side=tk.TOP, anchor=tk.NW, padx=10)

        btnWidth = 10
        entWidth = 10

        # Rect
        self.frmRect = tk.Frame(self.frmCSelTop)
        self.frmRect.pack(side=tk.TOP, anchor=tk.NW)

        self.frmRectVals = tk.Frame(self.frmRect)
        self.frmRectVals.pack(side=tk.TOP, anchor=tk.NW)

        tk.Label(self.frmRectVals, text='原点 :').grid(row=0, column=0, pady=2)
        self.entOx = tk.Entry(self.frmRectVals, width=entWidth)
        self.entOy = tk.Entry(self.frmRectVals, width=entWidth)
        self.entOz = tk.Entry(self.frmRectVals, width=entWidth)
        self.entOx.grid(row=0, column=1, padx=2)
        self.entOy.grid(row=0, column=2, padx=2)
        self.entOz.grid(row=0, column=3, padx=2)
        self.entOx.insert(tk.END, 0)
        self.entOy.insert(tk.END, 0)
        self.entOz.insert(tk.END, 0)
        self.btnOrigin = tk.Button(self.frmRectVals, text='節点から入力', command=lambda: self.SetXYZFromNode(self.entOx, self.entOy, self.entOz))
        self.btnOrigin.grid(row=0, column=4, padx=2)

        tk.Label(self.frmRectVals, text='X軸 :').grid(row=1, column=0, pady=2)
        self.entNxx = tk.Entry(self.frmRectVals, width=entWidth)
        self.entNxy = tk.Entry(self.frmRectVals, width=entWidth)
        self.entNxz = tk.Entry(self.frmRectVals, width=entWidth)
        self.entNxx.grid(row=1, column=1, padx=2)
        self.entNxy.grid(row=1, column=2, padx=2)
        self.entNxz.grid(row=1, column=3, padx=2)
        self.entNxx.insert(tk.END, 1)
        self.entNxy.insert(tk.END, 0)
        self.entNxz.insert(tk.END, 0)

        tk.Label(self.frmRectVals, text='Y軸 :').grid(row=2, column=0, pady=2)
        self.entNyx = tk.Entry(self.frmRectVals, width=entWidth)
        self.entNyy = tk.Entry(self.frmRectVals, width=entWidth)
        self.entNyz = tk.Entry(self.frmRectVals, width=entWidth)
        self.entNyx.grid(row=2, column=1)
        self.entNyy.grid(row=2, column=2)
        self.entNyz.grid(row=2, column=3)
        self.entNyx.insert(tk.END, 0)
        self.entNyy.insert(tk.END, 1)
        self.entNyz.insert(tk.END, 0)

        tk.Frame(self.frmRect, height=5).pack(side=tk.TOP, anchor=tk.NW)

        # Rect-Ctrl
        self.frmRectCtrl = tk.Frame(self.frmRect)
        self.frmRectCtrl.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        self.btnRectCreate = tk.Button(self.frmRectCtrl, text='作成', command=self.CreateRect, width=btnWidth)
        self.btnRectCreate.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        # Cylinder
        self.frmCylinder = tk.Frame(self.frmCSelTop)

        self.frmCylinderVals = tk.Frame(self.frmCylinder)
        self.frmCylinderVals.pack(side=tk.TOP, anchor=tk.NW)

        tk.Label(self.frmCylinderVals, text='原点 :').grid(row=0, column=0, pady=2)
        self.entCOx = tk.Entry(self.frmCylinderVals, width=entWidth)
        self.entCOy = tk.Entry(self.frmCylinderVals, width=entWidth)
        self.entCOz = tk.Entry(self.frmCylinderVals, width=entWidth)
        self.entCOx.grid(row=0, column=1, padx=2)
        self.entCOy.grid(row=0, column=2, padx=2)
        self.entCOz.grid(row=0, column=3, padx=2)
        self.entCOx.insert(tk.END, 0)
        self.entCOy.insert(tk.END, 0)
        self.entCOz.insert(tk.END, 0)
        self.btnCircle = tk.Button(self.frmCylinderVals, text='円弧から入力', command=self.SelectArc)
        self.btnCircle.grid(row=0, column=4, padx=2)

        tk.Label(self.frmCylinderVals, text='Z軸 :').grid(row=1, column=0, pady=2)
        self.entCZx = tk.Entry(self.frmCylinderVals, width=entWidth)
        self.entCZy = tk.Entry(self.frmCylinderVals, width=entWidth)
        self.entCZz = tk.Entry(self.frmCylinderVals, width=entWidth)
        self.entCZx.grid(row=1, column=1, padx=2)
        self.entCZy.grid(row=1, column=2, padx=2)
        self.entCZz.grid(row=1, column=3, padx=2)
        self.entCZx.insert(tk.END, 0)
        self.entCZy.insert(tk.END, 0)
        self.entCZz.insert(tk.END, 1)

        tk.Frame(self.frmCylinder, height=5).pack(side=tk.TOP, anchor=tk.NW)

        # Rect-Ctrl
        self.frmCylCtrl = tk.Frame(self.frmCylinder)
        self.frmCylCtrl.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        self.btnCylCreate = tk.Button(self.frmCylCtrl, text='作成', command=self.CreateCylinder, width=btnWidth)
        self.btnCylCreate.pack(side=tk.LEFT, anchor=tk.W, padx=5)

    def SelectCType(self):
        self.frmRect.forget()
        self.frmCylinder.forget()
        if self.CType.get() == 'Rectangle':
            self.frmRect.pack(side=tk.TOP, anchor=tk.NW)
            simlab.setSelectionFilter('Node')
        else:
            self.frmCylinder.pack(side=tk.TOP, anchor=tk.NW)
            simlab.setSelectionFilter('CircleEdge')

    def SetXYZFromNode(self, entX, entY, entZ):
        nodes = simlab.simlab.getSelectedEntities('Node')
        if len(nodes) == 0:
            messagebox.showinfo('情報','節点を選択してください。')
            return

        modelName = simlab.getModelName('FEM')
        xyz = simlab.getNodePositionFromNodeID(modelName, nodes[0])
        entX.delete(0, tk.END)
        entY.delete(0, tk.END)
        entZ.delete(0, tk.END)
        entX.insert(tk.END, xyz[0])
        entY.insert(tk.END, xyz[1])
        entZ.insert(tk.END, xyz[2])

    def CreateRect(self):
        name = self.entName.get()
        if not self.IsValidName(name):
            messagebox.showinfo('情報','重複しない名前を指定してください。')
            return
        
        try:
            ox = float(self.entOx.get())
            oy = float(self.entOy.get())
            oz = float(self.entOz.get())
            o = np.array([ox,oy,oz])

            nxx = float(self.entNxx.get()) 
            nxy = float(self.entNxy.get()) 
            nxz = float(self.entNxz.get())
            nx = np.array([nxx,nxy,nxz])

            nyx = float(self.entNyx.get()) 
            nyy = float(self.entNyy.get()) 
            nyz = float(self.entNyz.get())
            ny = np.array([nyx,nyy,nyz])
        except:
            messagebox.showinfo('情報','実数を指定してください。')
            return

        #self.backup.Save('Coordinate')
        CreateRectCoordinate(name, GetNewID(), o, nx, ny)
        self.entName.delete(0, tk.END)

    def SelectArc(self):
        edges = simlab.getSelectedEntities('Edge')
        if len(edges) == 0:
            messagebox.showinfo('情報','円弧エッジを選択してください。')
            return

        modelName = simlab.getModelName('FEM')
        circleEdge = -1
        circleResult = -1
        for edge in edges:
            circleResult = simlab.getArcEdgeAttributes(modelName, edge)
            if len(circleResult) != 0:
                circleEdge = edge
                break

        if circleEdge < 0:
            messagebox.showinfo('情報','円弧情報が取れません。円弧エッジを選びなおすか、Alignしてから選択しなおしてください。')
            return

        center, _ = circleResult
        self.entCOx.delete(0, tk.END)
        self.entCOy.delete(0, tk.END)
        self.entCOz.delete(0, tk.END)
        self.entCOx.insert(tk.END, center[0])
        self.entCOy.insert(tk.END, center[1])
        self.entCOz.insert(tk.END, center[2])

        result = simlab.definePlaneFromEntity(modelName, circleEdge)
        if len(result) == 0:
            return

        p1, p2, p3 = result
        p1 = np.array(p1)
        p2 = np.array(p2)
        p3 = np.array(p3)

        v2 = p2 - p1
        v3 = p3 - p1
        v = np.cross(v2, v3)
        nv = v / np.linalg.norm(v)

        self.entCZx.delete(0, tk.END)
        self.entCZy.delete(0, tk.END)
        self.entCZz.delete(0, tk.END)
        self.entCZx.insert(tk.END, nv[0])
        self.entCZy.insert(tk.END, nv[1])
        self.entCZz.insert(tk.END, nv[2])

    def CreateCylinder(self):
        name = self.entName.get()
        if not self.IsValidName(name):
            messagebox.showinfo('情報','重複しない名前を指定してください。')
            return

        try:
            x = float(self.entCOx.get())
            y = float(self.entCOy.get())
            z = float(self.entCOz.get())
            o = np.array([x,y,z])

            zx = float(self.entCZx.get())
            zy = float(self.entCZy.get())
            zz = float(self.entCZz.get())
            vz = np.array([zx,zy,zz])
            nz = vz / np.linalg.norm(vz)
        except:
            messagebox.showinfo('情報','実数を指定してください。')
            return

        CreateCylinderCoordinate(name, GetNewID(), o, nz)
        self.entName.delete(0, tk.END)

    def CreateEdittingTab(self):
        self.frmEditTop= tk.Frame(self.frmEdit)
        self.frmEditTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.frmEName = tk.Frame(self.frmEditTop)
        self.frmEName.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmEName, text='現在の名前: ').pack(side=tk.LEFT, anchor=tk.W)

        coords = GetAllCoordinates()
        self.editCoord = tk.StringVar()
        if len(coords) != 0:
            self.editCoord.set(coords[0])

        self.cmbECoords = ttk.Combobox(self.frmEName, values=coords, textvariable=self.editCoord, width=25, state='readonly')
        self.cmbECoords.pack(side=tk.LEFT, anchor=tk.W)
        self.cmbECoords.bind('<<ComboboxSelected>>', self.SelectECoord)

        tk.Frame(self.frmEditTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmENewName = tk.Frame(self.frmEditTop)
        self.frmENewName.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmENewName, text='新しい名前: ').pack(side=tk.LEFT, anchor=tk.W)
        self.entENewName = tk.Entry(self.frmENewName, width=25)
        self.entENewName.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmEditTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCCType= tk.Frame(self.frmEditTop)
        self.frmCCType.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmCCType, text='座標系タイプ: ').pack(side=tk.LEFT, anchor=tk.W)

        self.CEditType = tk.StringVar()
        self.CEditType.set('Rectangle')
        self.chkCR = tk.Radiobutton(self.frmCCType, text='直交座標系', value='Rectangle', variable=self.CEditType)
        self.chkCR.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.chkCC = tk.Radiobutton(self.frmCCType, text='円筒座標系', value='Cylindrical', variable=self.CEditType)
        self.chkCC.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        tk.Frame(self.frmEditTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        # edit
        btnWidth = 10
        self.frmEditCtrl = tk.Frame(self.frmEditTop)
        self.frmEditCtrl.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        self.btnEdit = tk.Button(self.frmEditCtrl, text='編集', command=self.EditCoordinate, width=btnWidth)
        self.btnEdit.pack(side=tk.LEFT, anchor=tk.W, padx=5)

    def SelectECoord(self, event):
        name = self.editCoord.get()
        self.entENewName.delete(0, tk.END)
        self.entENewName.insert(tk.END, name)

    def EditCoordinate(self):
        currentName = self.editCoord.get()
        newName = self.entENewName.get()

        if not self.IsValidName(newName, currentName):
            messagebox.showinfo('情報','重複しない名前を指定してください。')
            return
        
        ID = GetID(currentName)
        CType = self.CEditType.get()

        EditCoordinate(newName, ID, CType)
        self.UpdateCoords()

    def CreateDeletingTab(self):
        self.frmDeleteTop= tk.Frame(self.frmDelete)
        self.frmDeleteTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.frmDName = tk.Frame(self.frmDeleteTop)
        self.frmDName.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmDName, text='名前: ').pack(side=tk.LEFT, anchor=tk.W)

        coords = GetAllCoordinates()
        self.deleteCoord = tk.StringVar()
        if len(coords) != 0:
            self.deleteCoord.set(coords[0])

        self.cmbDCoords = ttk.Combobox(self.frmDName, values=coords, textvariable=self.deleteCoord, width=25, state='readonly')
        self.cmbDCoords.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmDeleteTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        # delete
        btnWidth = 10
        self.frmDelCtrl = tk.Frame(self.frmDeleteTop)
        self.frmDelCtrl.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        self.btnDelete = tk.Button(self.frmDelCtrl, text='削除', command=self.DeleteCoordinate, width=btnWidth)
        self.btnDelete.pack(side=tk.LEFT, anchor=tk.W, padx=5)

    def DeleteCoordinate(self):
        name = self.deleteCoord.get()
        if len(name) == 0:
            return

        DeleteCoordinate(name)
        self.UpdateCoords()

    def IsValidName(self, name, ignore=''):
        if len(name) == 0:
            return False

        coords = GetAllCoordinates()
        if len(ignore) != 0:
            coords.remove(ignore)

        if coords.count(name) > 0:
            return False

        return True

    def UpdateCoords(self):
        coords = GetAllCoordinates()
        self.cmbDCoords.config(values=coords)
        self.cmbECoords.config(values=coords)
        self.entENewName.delete(0, tk.END)

        if len(coords) != 0:
            self.deleteCoord.set(coords[0])
            self.editCoord.set(coords[0])
            self.entENewName.insert(tk.END, coords[0])
        else:
            self.deleteCoord.set('')
            self.editCoord.set('')

    def Undo(self):
        self.backup.Load()

        # Since the CAD model is displayed immediately after Undo, it is confusing
        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        super().CloseDialog()