import tkinter as tk
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
import tooltip as tp
import widget
import simlabutil
import simlablib

# for debug
importlib.reload(simlablib)
importlib.reload(simlabutil)

def FillHole(holeGrp, meshSize, maxAngle, aspectRat):
    modelName = simlab.getModelName('FEM')
    if not simlab.isGroupPresent(holeGrp):
        return
    
    faces = simlab.getEntityFromGroup(holeGrp)
    if len(faces) == 0:
        return
    
    adjacentFaceGrp = simlabutil.UniqueGroupName('_AdjacentFaceGrp')
    simlablib.SelectAdjacentFaces(modelName, faces, adjacentFaceGrp)
    if not simlab.isGroupPresent(adjacentFaceGrp):
        return
    
    simlablib.RemoveHoles(modelName, 'Face', faces, remesh=0)

    LocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh2"/>
    <SupportEntities>
    <Group>"''' + adjacentFaceGrp + '''",</Group>
    </SupportEntities>
    <ElemType Value="1"/>
    <AverageElemSize Value="''' + str(meshSize) + '''"/>
    <MinElemSize Value="''' + str(meshSize/aspectRat)+ '''"/>
    <PreserveBoundaryEdges Value="1"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="'''+ str(maxAngle) +'''"/>
    <CurvatureMinElemSize Value="'''+ str(meshSize/2) +'''"/>
    <AspectRatio Value="'''+ str(aspectRat) +'''"/>
    <AdvancedOptions>
        <MappedMesh Value="0"/>
        <MeshPattern Value="0"/>
        <ReMeshSharedEntity Value="0"/>
        <CADLocalReMesh Value="0"/>
    </AdvancedOptions>
    </TriOption>
    <QuadOption>
    <QuadMeshType Value="0"/>
    <HM_Quad_Mesh Value="0">
        <MinimumElementSize Value=""/>
        <MaximumElementSize Value=""/>
        <MaximumDeviation Value=""/>
        <MaximumAngle Value=""/>
        <MeshType Value=""/>
        <FeatureAngle Value=""/>
        <VertexAngle Value=""/>
        <AlignedMesh Checked=""/>
        <ProjectToSelectedEntities Checked=""/>
    </HM_Quad_Mesh>
    </QuadOption>
    </NewLocalReMesh>'''
    simlab.execute(LocalRemesh)
    simlablib.DeleteGroups([holeGrp, adjacentFaceGrp])

def _getParameter(key, valueType):
    """
        valueType: "int", "double", "string"
    """
    if not simlab.isParameterPresent(key):
        return None
    
    if valueType == "int": return simlab.getIntParameter("$"+key)
    elif valueType == "double": return simlab.getDoubleParameter("$"+key)
    elif valueType == "string": return simlab.getStringParameter("$"+key)

class FillHoleDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('穴埋め')
        self.backup = backup
        self.hole = '_Fill_Hole'

        self.CreateWidgets()
        self.UpdateButtonFG()
        simlab.setSelectionFilter('CylinderFace')

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.lblNote1 = tk.Label(self.frmTop, text='Tips: 穴面を選択して、[ 穴埋め ]ボタンを押してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmFig = tk.Frame(self.frmTop)        
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X, padx=5)

        self.iconHole = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'fill_hole.png')), master=self.frmFig)
        tk.Label(self.frmFig, image=self.iconHole).pack(side=tk.LEFT, anchor=tk.W)
        self.btnHole = tk.Button(self.frmFig, text=' 穴面 ', command=self.SelectHole)
        self.btnHole.place(x=50, y=30)        

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        # Remesh
        self.frmRemesh = tk.Frame(self.frmTop)
        self.frmRemesh.pack(side=tk.TOP, anchor=tk.W)
        
        self.bRemesh = tk.BooleanVar()
        self.bRemesh.set(False)
        self.chkRemesh = tk.Checkbutton(self.frmRemesh, text='リメッシュ :', variable=self.bRemesh, command=self.ToggleRemesh)
        #self.chkRemesh.pack(side=tk.TOP, anchor=tk.W, pady=2)
        self.entRemeshSize = widget.LabelEntry(self.frmRemesh, text='要素サイズ :', width=10, value=20)
        #self.entRemeshSize.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=2)
        self.ToggleRemesh()

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnFill = tk.Button(self.frmCtrl, text=' 穴埋め ', command=self.Fill, width=btnWidth)
        self.btnFill.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def Fill(self):
        if not simlab.isGroupPresent(self.hole):
            messagebox.showinfo('情報','穴面を選択してください。')
            return
        
        meshStatus = _getParameter("MESH_STATUS", "string")
        if not meshStatus:
            messagebox.showinfo("情報", "Do surface mesh first")
            return
        
        if meshStatus != "SURFACE":
            messagebox.showinfo("情報", "Mesh status is not in the level of surface")
            return

        meshSize = _getParameter("DefaultMeshSize", "double")

        maxAngle = _getParameter("DefaultMaxAngle", "double")

        aspectRat = _getParameter("DefaultAspectRatio", "double")

        if not meshSize or not maxAngle or not aspectRat:
            messagebox.showinfo("情報", "Can't find mesh properties to re-mesh after filling holes")
            return

        self.backup.Save('Hole')
        
        FillHole(self.hole, meshSize, maxAngle, aspectRat)

        # simlablib.DeleteGroups(self.hole)
        self.UpdateButtonFG()

    def ToggleRemesh(self):
        if self.bRemesh.get():
            self.entRemeshSize.Config(state='normal')
        else:
            self.entRemeshSize.Config(state='disabled')

    def SelectHole(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','穴面を選択した後、[穴面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.hole)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.hole)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()     

    def UpdateButtonFG(self):
        groups = [self.hole ]
        widgets = [self.btnHole]

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
        simlablib.DeleteGroups([self.hole])
        super().CloseDialog()