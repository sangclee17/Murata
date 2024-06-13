import tkinter as tk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib
from PIL import Image, ImageTk
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

BASE_NODE = 10000000
MASS_RBE = 'MASS2_'
MASS_COORDINATE = 'MASS2_'
MASS_MASS = 'MASS2_'

MAX_ID_RBE = 'Max_ID_RBE'
MAX_ID_COORDINATE = 'Max_ID_Coordinate'
MAX_ID_MASS = 'Max_ID_Mass'

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

# local import
import basedialog
import simlabutil
import simlablib
import tooltip as tp
import mass
import coordinate

def CreateCentroidNode(entityType, entity):
    modelName = simlab.getModelName('FEM')
    nodeID = simlabutil.AvailableNodeID(modelName, baseNodeID=BASE_NODE)

    simlablib.CreateNodeByCentroid(modelName, entityType, [entity], nodeID)
    xyz = simlab.getNodePositionFromNodeID(modelName, nodeID)

    return nodeID, list(xyz)

def GetAxis(edgeGrp):
    arcCenterPt, _ = simlab.getArcEdgeAttributes(edgeGrp)
    p1, p2, p3 = simlab.definePlaneFromGroup(edgeGrp, 'EDGEGROUP')

    v1 = np.array(p2) - np.array(p1)
    v2 = np.array(p3) - np.array(p1)
    n = np.cross(v2, v1)
    m = np.linalg.norm(n)
    if m < 1e-9:
        return []
    n /= m

    return list(arcCenterPt), list(n)

def ProjectAxis(xyzAxis, vecAxis, xyzProject):
    v1 = np.array(vecAxis) 
    v2 = np.array(xyzProject) - np.array(xyzAxis)
    t = np.dot(v1,v2)
    xyz = np.array(xyzAxis) + t * v1

    n = np.array(xyzProject) - xyz
    m = np.linalg.norm(n)
    if m < 1e-9:
        return []
    n /= m

    return list(xyz), list(n)

def GetAngle(v1, v2, axis):
    n1 = np.array(v1)
    n2 = np.array(v2)
    n1 = n1 / np.linalg.norm(n1)
    n2 = n2 / np.linalg.norm(n2)

    dot = np.dot(n1, n2)
    angle = np.rad2deg(np.arccos(np.clip(dot, -1.0, 1.0)))

    cross = np.cross(n1, n2)
    dot2 = np.dot(cross, axis)
    if dot2 > 0.0:
        return angle
    else:
        return angle * -1.0

def CreateRBE(face, centerNode, axis):
    modelName = simlab.getModelName('FEM')
    axis = np.array(axis)

    edgeGrp = simlabutil.UniqueGroupName('_Edge')
    simlablib.SelectAssociatedEntities(modelName, 'Face', [face], 'Edge', edgeGrp)
    edges = simlab.getEntityFromGroup(edgeGrp)
    simlablib.DeleteGroups(edgeGrp)
    if len(edges) == 0:
        return -1
    
    rbeEdges = []
    for edge in edges:
        vtxGrp = simlabutil.UniqueGroupName('_Vertex')
        simlablib.SelectAssociatedEntities(modelName, 'Edge', [edge], 'Vertex', vtxGrp)
        vertexes = simlab.getEntityFromGroup(vtxGrp)
        simlablib.DeleteGroups(vtxGrp)
        if len(vertexes) < 2:
            continue

        v1 = vertexes[0]
        v2 = vertexes[-1]
        xyzV1 = simlab.getVertexPositionFromVertexID(modelName, v1)
        xyzV2 = simlab.getVertexPositionFromVertexID(modelName, v2)
        v = np.array(xyzV1) - np.array(xyzV2)
        n = v / np.linalg.norm(v)
        dot = np.dot(n, axis)
        if abs(dot) > 0.5:
            continue

        rbeEdges.append([edge, xyzV1, xyzV2])
    
    if len(rbeEdges) != 2:
        return -1

    elGrp = simlabutil.UniqueGroupName('_Element')
    simlablib.SelectAssociatedEntities(modelName, 'Face', [face], 'Element', elGrp)
    elements = simlab.getEntityFromGroup(elGrp)
    simlablib.DeleteGroups(elGrp)
    if len(elements) == 0:
        return -1

    ndGrp = simlabutil.UniqueGroupName('_Nodes')
    simlablib.SelectAssociatedEntities(modelName, 'Element', [elements], 'MidNode', ndGrp)
    midNodes = simlab.getEntityFromGroup(ndGrp)
    simlablib.DeleteGroups(ndGrp)
    if len(midNodes) == 0:
        return -1
    midNodes = set(midNodes)

    rbeNodes = []
    for items in rbeEdges:
        edge, xyzV1, xyzV2 = items
        ndGrp = simlabutil.UniqueGroupName('_Nodes')
        simlablib.SelectAssociatedEntities(modelName, 'Edge', [edge], 'Node', ndGrp)
        nodes = simlab.getEntityFromGroup(ndGrp)
        simlablib.DeleteGroups(ndGrp)
        if len(nodes) == 0:
            continue

        midNodeOnEdge = list(set(nodes) & midNodes)

        for xyzV in [xyzV1, xyzV2]:
            xyzV = np.array(xyzV)

            closestNode = -1
            minM = ""
            for node in midNodeOnEdge:
                xyz = simlab.getNodePositionFromNodeID(modelName, node)
                v = np.array(xyz) - xyzV
                m = np.linalg.norm(v)
                if minM == '' or minM > m:
                    closestNode = node
                    minM = m
            
            if closestNode != -1:
                rbeNodes.append(closestNode)

    if len(rbeNodes) == 0:
        return -1

    # RBE
    RBEID = 1
    if simlab.isParameterPresent(MAX_ID_RBE):
        RBEID = simlab.getIntParameter('$'+MAX_ID_RBE) + 1
    simlablib.AddIntParameters(MAX_ID_RBE, RBEID)
    RBEName = MASS_RBE + '_TEMP_' + str(RBEID)
    simlablib.ManualRBE(modelName, RBEName, centerNode, rbeNodes)

    return RBEID, RBEName

def GetNewName(key, startIndex):
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

def MoveNodeRotate(p1, p2, node, angle):
    modelName = simlab.getModelName('FEM')

    p1 = str(p1).strip('[]')
    p2 = str(p2).strip('[]')
    MoveNodeRotate=''' <MoveNodeRotate UUID="0102fcc0-af8d-4a22-945e-ea030daf5ab3">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(node) + ''',</Node>
    </Entities>
    </SupportEntities>
    <Point1 Value="''' + p1 + '''"/>
    <Point2 Value="''' + p2 + '''"/>
    <Angle Value="''' + str(angle) + '''"/>
    <Copy Value="0"/>
    </MoveNodeRotate>'''
    simlab.execute(MoveNodeRotate)

def CreateCoordinate(xyzOrigin, vecAxis):
    modelName = simlab.getModelName('FEM')

    o = np.array(xyzOrigin)

    nz = np.array(vecAxis)
    ny = np.array([0,1,0])
    nx = np.cross(ny, nz)
    if np.linalg.norm(nx) < 1e-9:
        ny = np.array([1,0,0])
        nx = np.cross(ny, nz)
    nx /= np.linalg.norm(nx)
    ny = np.cross(nz, nx)
    ny /= np.linalg.norm(ny)

    CID = coordinate.GetNewID()
    name = MASS_COORDINATE + str(CID)
    coordinate.CreateRectCoordinate(name, CID, o, nx, ny)

    return CID

def CreateMass(nodes, mass, axisID):
    modelName = simlab.getModelName('FEM')

    # ID
    massID = 1
    if simlab.isParameterPresent(MAX_ID_MASS):
        massID = simlab.getIntParameter('$'+MAX_ID_MASS) + 1
    simlablib.AddIntParameters(MAX_ID_MASS, massID)

    # Name
    name = MASS_MASS + str(massID)

    PointMass=''' <Mass Auto="1" isObject="2" BCType="Mass" UUID="40EFB6FC-D0CB-46da-81B2-CFA88D2679D1">
    <tag Value="81"/>
    <Name Value="''' + name + '''"/>
    <MassEntities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' +  str(nodes).strip('[]') + ''',</Node>
    </Entities>
    </MassEntities>
    <AxisID Value="''' + str(axisID) + '''" Index="0"/>
    <MassValue Value="''' + str(mass) + '''"/>
    <MassOption Value="0"/>
    <CentroidX Value="0"/>
    <CentroidY Value="0"/>
    <CentroidZ Value="0"/>
    <Ixx CheckBox="0" Value="0"/>
    <Iyy CheckBox="0" Value="0"/>
    <Izz CheckBox="0" Value="0"/>
    <Ixy CheckBox="0" Value="0"/>
    <Iyz CheckBox="0" Value="0"/>
    <Izx CheckBox="0" Value="0"/>
    <Export Value="0"/>
    <ExportFileName Value=""/>
    <CalculateAndAssign flag="false"/>
    </Mass>'''
    simlab.execute(PointMass)
    return massID

class Mass2Dlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('ターニングヘッド簡略化')
        self.body = '_Mass_Body'
        self.base = '_Mass_Base'
        self.copy = '_Mass_Copy'
        self.axis = '_Mass_Axis'
        self.pageIndex = 0
        self.backup = backup

        self.CreateWidgets()
        self.UpdateWidgets()

        simlablib.DeleteGroups([self.body, self.base, self.copy, self.axis])
        simlabutil.ClearSelection()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.lblNote1 = tk.Label(self.frmTop, text='Tips: 画像のボディと両側の面を選択して[ 作成 ]ボタンを押してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)
        btnWidth = 10

        self.frmSelect = tk.Frame(self.frmTop)
        self.frmSelect.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        # select body
        self.frmSelBody = tk.Frame(self.frmSelect)
        self.frmSelBody.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        self.iconBody = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'mass_body.png')), master=self.frmSelBody)
        tk.Label(self.frmSelBody, image=self.iconBody).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnBody = tk.Button(self.frmSelBody, text=' ボディ ', command=self.SelectBody)
        self.btnBody.place(x=90, y=20)

        # select base
        self.frmSelBase = tk.Frame(self.frmSelect)
        self.iconBase = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'mass_base.png')), master=self.frmSelBase)
        tk.Label(self.frmSelBase, image=self.iconBase).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnBase = tk.Button(self.frmSelBase, text=' 基準面 ', command=self.SelectBase)
        self.btnBase.place(x=100, y=20)

        # select copy
        self.frmSelCopy = tk.Frame(self.frmSelect)
        self.iconCopy = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'mass_copy.png')), master=self.frmSelCopy)
        tk.Label(self.frmSelCopy, image=self.iconCopy).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnCopy = tk.Button(self.frmSelCopy, text=' 複製面 ', command=self.SelectCopy)
        self.btnCopy.place(x=120, y=145)

        # select axis
        self.frmSelAxis = tk.Frame(self.frmSelect)
        self.iconAxis = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'mass_axis.png')), master=self.frmSelAxis)
        tk.Label(self.frmSelAxis, image=self.iconAxis).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnAxis = tk.Button(self.frmSelAxis, text=' 軸を規定する円弧 ', command=self.SelectAxis)
        self.btnAxis.place(x=60, y=30)

        # select ctrl
        self.frmSelCtrl = tk.Frame(self.frmTop)
        self.frmSelCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        self.frmSelBtn = tk.Frame(self.frmTop)
        self.frmSelBtn.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconPrev = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'prev.png')), master=self.frmSelBtn)
        self.btnPrev = tk.Button(self.frmSelBtn, image=self.iconPrev, command=self.JumpPrev)
        self.btnPrev.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)
        self.iconNext = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'next.png')), master=self.frmSelBtn)
        self.btnNext = tk.Button(self.frmSelBtn, image=self.iconNext, command=self.JumpNext)
        self.btnNext.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)

        ## Mass
        self.frmMassProp = tk.Frame(self.frmTop)
        self.frmMassProp.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, pady=2)
        self.lblMassProp = tk.Label(self.frmMassProp, text='質量特性 : ')
        self.lblMassProp.pack(side=tk.LEFT, anchor=tk.W)

        self.frmCent = tk.Frame(self.frmTop)
        self.frmCent.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=10, pady=2)
        self.lblCent = tk.Label(self.frmCent, text='重心: ')
        self.lblCent.pack(side=tk.LEFT, anchor=tk.W)
        self.entOX = tk.Entry(self.frmCent, width=10)
        self.entOX.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entOY = tk.Entry(self.frmCent, width=10)
        self.entOY.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entOZ = tk.Entry(self.frmCent, width=10)
        self.entOZ.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entOX.insert(tk.END, 0)
        self.entOY.insert(tk.END, 0)
        self.entOZ.insert(tk.END, 0)

        self.frmMass = tk.Frame(self.frmTop)
        self.frmMass.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=10, pady=2)
        self.lblMass = tk.Label(self.frmMass, text='質量: ')
        self.lblMass.pack(side=tk.LEFT, anchor=tk.W)
        self.entMass = tk.Entry(self.frmMass, width=10)
        self.entMass.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entMass.insert(tk.END, 0)

        tk.Frame(self.frmTop, height=10).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        self.btnCreate = tk.Button(self.frmCtrl, text=' 作成 ', compound=tk.LEFT, command=self.Create, width=btnWidth)
        self.btnCreate.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def JumpPrev(self):
        self.pageIndex -= 1
        self.UpdateWidgets()

    def JumpNext(self):
        self.pageIndex += 1
        self.UpdateWidgets()
    
    def JumpIndex(self, idx):
        self.pageIndex = idx
        self.UpdateWidgets()

    def UpdateWidgets(self):
        self.UpdateSelectionFigure()
        self.UpdateButtonState()
        self.UpdateButtonFG()

    def UpdateSelectionFigure(self):
        self.frmSelBody.forget()
        self.frmSelBase.forget()
        self.frmSelCopy.forget()
        self.frmSelAxis.forget()
        if self.pageIndex == 0:
            self.frmSelBody.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'Body'
        elif self.pageIndex == 1:
            self.frmSelBase.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'Face'
        elif self.pageIndex == 2:
            self.frmSelCopy.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'Face'
        elif self.pageIndex == 3:
            self.frmSelAxis.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'CircleEdge'
        else:
            pass
        simlab.setSelectionFilter(selectionFilter)

    def UpdateButtonState(self):
        self.btnPrev.config(state='normal')
        self.btnNext.config(state='normal')
        if self.pageIndex == 0:
            self.btnPrev.config(state='disabled')
        elif self.pageIndex == 3:
            self.btnNext.config(state='disabled')
        else:
            pass

        self.btnCreate.config(state='normal')
        if not simlab.isGroupPresent(self.body) or not simlab.isGroupPresent(self.base) or not simlab.isGroupPresent(self.copy) or not simlab.isGroupPresent(self.axis):
            self.btnCreate.config(state='disabled')

    def UpdateButtonFG(self):
        groups = [self.body, self.base, self.copy, self.axis]
        widgets = [self.btnBody, self.btnBase, self.btnCopy, self.btnAxis]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def SelectBody(self):
        bodies = simlab.getSelectedBodies()
        if len(bodies) == 0:
            messagebox.showinfo('情報','ボディを選択した後、[ボディ] ボタンを押下してください。')
            return
        
        simlablib.DeleteGroups(self.body)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Body', bodies, self.body)

        self.CalcBodies(bodies)

        simlabutil.ClearSelection()
        self.JumpNext()

        modelName = simlab.getModelName('FEM')
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def SelectBase(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','基準面を選択した後、[基準面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.base)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.base)

        simlabutil.ClearSelection()
        self.JumpNext()

    def SelectCopy(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','複製面を選択した後、[複製面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.copy)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.copy)

        simlabutil.ClearSelection()
        self.JumpNext()

    def SelectAxis(self):
        edges = simlab.getSelectedEntities('Edge')
        if len(edges) == 0:
            messagebox.showinfo('情報','円弧を選択した後、[軸を規定する円弧] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.axis)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.axis)

        r1 = simlab.getArcEdgeAttributes(self.axis)
        r2 = simlab.definePlaneFromGroup(self.axis, 'EDGEGROUP')
        if len(r1) == 0 or len(r2) == 0:
            simlablib.DeleteGroups(self.axis)
            messagebox.showinfo('情報','軸が規定できませんでした。円弧エッジを選択してください。')
            return

        simlabutil.ClearSelection()
        self.UpdateWidgets()

    def Create(self):
        if not self.IsValid():
            return

        modelName = simlab.getModelName('FEM')

        bodies = simlab.getBodiesFromGroup(self.body)
        if len(bodies) == 0:
            messagebox.showinfo('情報','ボディを選択しなおしてください')
            return

        faces = simlab.getEntityFromGroup(self.base)
        if len(faces) == 0:
            messagebox.showinfo('情報','基準面を選択しなおしてください')
            return
        baseFace = faces[0]
        
        faces = simlab.getEntityFromGroup(self.copy)
        if len(faces) == 0:
            messagebox.showinfo('情報','複製面を選択しなおしてください')
            return

        result = GetAxis(self.axis)
        if len(result) == 0:
            messagebox.showinfo('情報','軸が規定できません。円弧を選びなおしてください')
            return
        xyzArc, vecAxis = result

        try:
            x = float(self.entOX.get())
            y = float(self.entOY.get())
            z = float(self.entOZ.get())
            xyzBody = [x,y,z]
            massValue = float(self.entMass.get())
        except:
            messagebox.showinfo('情報','実数で指定してください')
            return

        self.backup.Save('Mass2')

        nodeBase, xyzBase = CreateCentroidNode('Face', baseFace)
        simlablib.DeleteSelectedOphanNodes(modelName, [nodeBase])

        result = ProjectAxis(xyzArc, vecAxis, xyzBase)
        if len(result) == 0:
            messagebox.showinfo('情報','軸に投影できません。円弧を選びなおしてください')
            return
        _, vecBase = result

        # rotation-axis
        p1 = list(xyzArc)
        p2 = list(np.array(xyzArc) + np.array(vecAxis))

        # RBE
        massNodes = []
        rbes = []
        for face in faces:
            nodeFace, xyzFace = CreateCentroidNode('Face', face)
            result = ProjectAxis(xyzArc, vecAxis, xyzFace)
            if len(result) == 0:
                simlablib.DeleteSelectedOphanNodes(modelName, [nodeFace])
                continue
            _, vecProject = result

            angle = GetAngle(vecBase, vecProject, vecAxis)
            simlablib.DeleteSelectedOphanNodes(modelName, [nodeFace])

            copyNode = simlabutil.AvailableNodeID(modelName, baseNodeID=BASE_NODE)
            simlablib.CreateNodeByXYZ(modelName, xyzBody, copyNode)

            MoveNodeRotate(p1, p2, copyNode, angle)

            RBEID, RBEName = CreateRBE(face, copyNode, vecAxis)
            if RBEID < 0:
                simlablib.DeleteSelectedOphanNodes(modelName, [nodeFace])
                continue

            massNodes.append(copyNode)
            rbes.append(RBEName)

        if len(massNodes) == 0:
            messagebox.showinfo('情報','質量を作成できません')
            return

        # Coordinate
        axisID = CreateCoordinate(xyzArc, vecAxis)
        # Mass
        massID = CreateMass(massNodes, massValue, axisID)
        # RBE
        simlablib.MergeBodies(modelName, rbes)
        newName = GetNewName(MASS_RBE, 1)
        simlablib.RenameBody(modelName, rbes[0], newName)

        simlablib.DeleteGroups([self.body, self.base, self.copy, self.axis])
        self.JumpIndex(0)

        return massID, axisID

    def IsValid(self):
        for grp in [self.body, self.base, self.copy, self.axis]:
            if not simlab.isGroupPresent(grp):
                messagebox.showinfo('情報','全てのエンティティを選択してください。')
                return False
        
        try:
            _ = float(self.entMass.get())
        except:
            messagebox.showinfo('情報','実数を指定してください。')
            return False

        return True

    def CalcBodies(self, bodies):        
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

    def Undo(self):
        self.backup.Load()
        self.JumpIndex(self.pageIndex)

        # Since the CAD model is displayed immediately after Undo, it is confusing
        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        simlablib.DeleteGroups([self.body, self.base, self.copy, self.axis])
        super().CloseDialog()