import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib
from PIL import Image, ImageTk
import re
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = os.path.join(PROJECT_DIR,'log')
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

# local import
import basedialog
import simlabutil
import simlablib
import tooltip as tp
import backup
import messageboxWithCheckbox as mc
import muratautil
import meshutil

def simplifyBeltPulley(limit1FaceGrp, limit2FaceGrp, guideFaceGrp, numLayer):
    modelName = simlab.getModelName('FEM')

    guides = simlab.getEntityFromGroup(guideFaceGrp)
    limit1 = simlab.getEntityFromGroup(limit1FaceGrp)
    limit2 = simlab.getEntityFromGroup(limit2FaceGrp)


    if len(guides) == 0 or len(limit1) == 0 or len(limit2) == 0:
        return

    sideFaces = _getSideFaces(guides, list(set(limit1) | set(limit2)))
    if len(sideFaces) == 0:
        return

    boundaries1, boundaries2 = _getBoundaries(sideFaces, limit1, limit2)
    if len(boundaries1) == 0 or len(boundaries2) == 0:
        return

    bodyNm = getBodyNmAssociatedWithFace(guides)

    # deletes faces
    simlablib.DeleteEntities(modelName, 'Face', sideFaces)

    # creates faces
    _createFaceFromEdges(boundaries1, boundaries2, numLayer)
    
    # update MC
    updateMC(bodyNm)

    simlablib.UpdateModel()

def updateMC(bodyNm):
    # print("updating meshControl")
    if not simlab.isParameterPresent("DefaultMeshSize") or not simlab.isParameterPresent("DefaultMaxAngle") or not simlab.isParameterPresent("DefaultAspectRatio"):
        messagebox.showinfo("情報", "Remesh property parameter is missing")
        return
    
    meshSize = simlab.getDoubleParameter("$DefaultMeshSize")
    maxAngle = simlab.getDoubleParameter("$DefaultMaxAngle")
    aspectRat = simlab.getDoubleParameter("$DefaultAspectRatio")

    modelNm = simlab.getModelName("FEM")
    for thisBody in list(bodyNm):
        # print(thisBody)
        bodyPrefix = muratautil.getPrefixOfBodyNm(thisBody)
        prefixedBodies = simlab.getBodiesWithSubString(modelNm,["{}*".format(bodyPrefix)])
        meshutil.bodyMCWrapper("FEM", bodyPrefix, prefixedBodies, meshSize, maxAngle, aspectRat)

def _getSideFaces(guides, limits):
    modelName = simlab.getModelName('FEM')

    sideFaceGrp = simlabutil.UniqueGroupName('_Simplify_Side')
    simlablib.GetAdjacentFacesToLimitFaces(modelName, guides, limits, sideFaceGrp)
    if not simlab.isGroupPresent(sideFaceGrp):
        return guides

    sideFaces = simlab.getEntityFromGroup(sideFaceGrp)
    simlablib.DeleteGroups(sideFaceGrp)
    return sideFaces

def _getBoundaries(sideFaces, limit1, limit2):
    modelName = simlab.getModelName('FEM')

    sideEdgeGrp = simlabutil.UniqueGroupName('_Simplify_Edge')
    simlablib.SelectAssociatedEntities(modelName, 'Face', sideFaces, 'Edge', sideEdgeGrp)
    sideEdges = simlab.getEntityFromGroup(sideEdgeGrp)
    simlablib.DeleteGroups(sideEdgeGrp)

    limitEdgeGrp1 = simlabutil.UniqueGroupName('_Simplify_Edge')
    simlablib.SelectAssociatedEntities(modelName, 'Face', limit1, 'Edge', limitEdgeGrp1)
    limitEdges1 = simlab.getEntityFromGroup(limitEdgeGrp1)
    simlablib.DeleteGroups(limitEdgeGrp1)

    limitEdgeGrp2 = simlabutil.UniqueGroupName('_Simplify_Edge')
    simlablib.SelectAssociatedEntities(modelName, 'Face', limit2, 'Edge', limitEdgeGrp2)
    limitEdges2 = simlab.getEntityFromGroup(limitEdgeGrp2)
    simlablib.DeleteGroups(limitEdgeGrp2)

    if len(sideEdges) == 0 or len(limitEdges1) == 0 or len(limitEdges2) == 0:
        return

    boundaries1 = list(set(sideEdges) & set(limitEdges1))
    boundaries2 = list(set(sideEdges) & set(limitEdges2))
    return boundaries1, boundaries2

def _createFaceFromEdges(boundaries1, boundaries2, numberOfLayers):
    modelName = simlab.getModelName('FEM')
    boundaries1 = str(boundaries1).strip("[]""()")
    boundaries2 = str(boundaries2).strip("[]""()")

    CreateFaceFromEdges=''' <FaceUsing2Edges gda="" UUID="DDB1E50D-DB65-424c-8E3A-516DD1A7E058">
    <Name Value="FaceUsing2Edges1"/>
    <tag Value="-1"/>
    <No.OfLayers Value="''' + str(numberOfLayers) + '''"/>
    <EdgeLoop1>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Edge>''' + boundaries1 + ''',</Edge>
    </Entities>
    </EdgeLoop1>
    <EdgeLoop2>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Edge>''' + boundaries2 + ''',</Edge>
    </Entities>
    </EdgeLoop2>
    <FaceOnOneSide Value=""/>
    <FaceOnOtherSide Value=""/>
    <BoundaryEdgeLoop1/>
    <BoundaryEdgeLoop2/>
    <NodeList Value="" ModelIds="" EntityTypes=""/>
    <TriElemOption Value="1"/>
    <UseDirChk Value="0"/>
    <DirPoints Value=""/>
    <Output/>
    </FaceUsing2Edges>'''
    simlab.execute(CreateFaceFromEdges)

    faceGroup = '_Simplify_NextFace'
    simlablib.DeleteGroups(faceGroup)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', boundaries1, 'Face', faceGroup)

    faces = simlab.getEntityFromGroup(faceGroup)
    simlablib.DeleteGroups(faceGroup)
    if len(faces) == 0:
        return

    faces = str(faces).strip("[]""()")
    ModifyElements=''' <Modify UUID="28706164-e6e5-4544-b4a9-c052c4b6c60f" CheckBox="ON">
    <Name Value=""/>
    <tag Value="-1"/>
    <Option Value="TOHIGHER"/>
    <QuadDominant Value="1"/>
    <Entity>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Face>''' + faces + ''',</Face>
    </Entities>
    </Entity>
    <IdealQuad Value="0"/>
    <UpdateAssociateRBENodes Value="1"/>
    </Modify>'''
    simlab.execute(ModifyElements)

def simplifyFlatFace(guideGrp, limitGrp):
    guideFaces = simlab.getEntityFromGroup(guideGrp)
    limitFaces = simlab.getEntityFromGroup(limitGrp)

    if len(guideFaces) == 0 or len(limitFaces) == 0:
        return
    
    adjFaces = getAdjFaceEntities(guideFaces, limitFaces)

    if len(adjFaces) == 0:
        adjFaces = guideFaces

    bodyNm = getBodyNmAssociatedWithFace(adjFaces)
    # print(bodyNm)
    deleteFaceEntities(adjFaces)
    faceIds_before = getFaceIdsAssociatedWithBodies(bodyNm)
    fillFreeEdges(bodyNm)
    faceIds_after = getFaceIdsAssociatedWithBodies(bodyNm)
    newFace = tuple(set(faceIds_after)-set(faceIds_before))
    if not newFace:return
    faceToRemesh = selectAdjFaceEntities(newFace)
    # print(faceToRemesh)

    updateMC(bodyNm)
    remeshLocally(faceToRemesh, preserveBoundaryEdges = 1)

def selectAdjFaceEntities(faceIds):
    modelNm = simlab.getModelName("FEM")

    SelectAdjacent=''' <SelectAdjacent recordable="0" UUID="06104eca-3dbf-45af-a99c-953c8fe0f4e4">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceIds).strip("()") +'''</Face>
    </Entities>
    </SupportEntities>
    <NoofLayer Value="1"/>
    <VisiblesFaceOnly Value="0"/>
    <SelectAdjacent Value="1"/>
    <CreateGroup Value="1" Name="Adjacent_Group_95"/>
    </SelectAdjacent>'''
    simlab.execute(SelectAdjacent)
    faceGrp = "Adjacent_Group_95"
    adjFaces = simlab.getEntityFromGroup(faceGrp)
    simlablib.DeleteGroups(faceGrp)

    return adjFaces

def getAdjFaceEntities(guideFaces, limitFaces):
    
    modelNm = simlab.getModelName("FEM")
    ShowAdjacent=''' <ShowAdjacent gda="" UUID="EEDC5B06-8DC9-4754-AA76-F9E32643765A" clearSelection="1">
    <Name Value=""/>
    <tag Value="-1"/>
    <Show Value="0"/>
    <Select Value="1"/>
    <CheckVisibleFaces Value="0"/>
    <SupportEntities Value="" EntityTypes="" ModelIds=""/>
    <PickFaceType Value="GuideFaces"/>
    <GuideFaces>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(guideFaces).strip("()[]") +'''</Face>
    </Entities>
    </GuideFaces>
    <LimitFaces>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(limitFaces).strip("()[]") +'''</Face>
    </Entities>
    </LimitFaces>
    <AddPlanarFacestoLimitFaces Value="0"/>
    <AddCylindricalFacestoLimitFaces Value="0"/>
    <UptoNonManifoldEdges Value="0"/>
    <BreakAngle Value="0"/>
    <Angle Value="45"/>
    <NoOfLayers Value="17235"/>
    <PlanePoints Value=""/>
    <CreateGroup Value="1" Name="Adjacent_Faces_71"/>
    </ShowAdjacent>'''
    simlab.execute(ShowAdjacent)

    adjFaces = simlab.getEntityFromGroup("Adjacent_Faces_71")
    faceGrp = "Adjacent_Faces_71"
    simlablib.DeleteGroups(faceGrp)
    return adjFaces

def deleteFaceEntities(faceIds):
    modelNm = simlab.getModelName("FEM")
    DeleteEntity=''' <DeleteEntity UUID="BF2C866D-8983-4477-A3E9-2BBBC0BC6C2E" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceIds).strip("[]()") +'''</Face>
    </Entities>
    </SupportEntities>
    </DeleteEntity>'''
    simlab.execute(DeleteEntity)
    updateModel()

def fillFreeEdges(bodyNm):
    modelNm = simlab.getModelName("FEM")
    bodyNm = str(bodyNm).replace("'",'"')
    FillHoles=''' <FillHole UUID="E9B9EC99-A6C1-4626-99FF-626F38A8CE4F" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="FillHole5"/>
    <SupportEntities>
    <Entities>
    <Model>''' + modelNm + '''</Model>
    <Body>'''+ bodyNm.strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    <Option Value="0"/>
    <Cylindercal_Face Value="0"/>
    <Single_Face Value="0"/>
    <FillPartialLoop Value="0"/>
    <MeshSize Value="" LocalReMesh="0"/>
    </FillHole>'''
    simlab.execute(FillHoles)
    updateModel()

def updateModel():
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def getBodyNmAssociatedWithFace(faceIds):
    modelNm = simlab.getModelName("FEM")
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceIds).strip("()") +'''</Face>
    </Entities>
    </InputFaces>
    <Option Value="Bodies"/>
    <Groupname Value="SelectBodies_4"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)
    bodyNm = simlab.getBodiesFromGroup("SelectBodies_4")
    simlablib.DeleteGroups("SelectBodies_4")
    return bodyNm

def getFaceIdsAssociatedWithBodies(bodyNm):
    modelNm = simlab.getModelName("FEM")
    bodyNm = str(bodyNm).replace("'",'"')
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ bodyNm.strip("()") +'''</Body>
    </Entities>
    </InputBody>
    <Option Value="Faces"/>
    <Groupname Value="associatedFaceGrp"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)
    faceEnts = simlab.getEntityFromGroup("associatedFaceGrp")
    simlablib.DeleteGroups("associatedFaceGrp")
    return faceEnts

def remeshLocally(faceIds, preserveBoundaryEdges = 0):
    modelNm = simlab.getModelName("FEM")
    if not simlab.isParameterPresent("DefaultMeshSize") or not simlab.isParameterPresent("DefaultMaxAngle") or not simlab.isParameterPresent("DefaultAspectRatio"):
        messagebox.showinfo("情報", "Re-mesh property parameter is missing")
        return
    
    meshSize = simlab.getDoubleParameter("$DefaultMeshSize")
    maxAngle = simlab.getDoubleParameter("$DefaultMaxAngle")
    aspectRat = simlab.getDoubleParameter("$DefaultAspectRatio")

    LocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh5"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceIds).strip("()""[]") +'''</Face>
    </Entities>
    </SupportEntities>
    <ElemType Value="1"/>
    <AverageElemSize Value="'''+ str(meshSize) +'''"/>
    <MinElemSize Value="'''+ str(meshSize/aspectRat) +'''"/>
    <PreserveBoundaryEdges Value="'''+ str(preserveBoundaryEdges) +'''"/>
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
    updateModel()


class SimplifyDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.backup = backup
        self.limit1 = "_Simplify_Limit1"
        self.limit2 = "_Simplify_Limit2"
        self.guide = "_Simplify_Guide"
        self.limit_flat = "_Simplify_Limit_Flat"
        self.guide_flat = "_Simplify_Guide_Flat"

        self.master.title('形状簡略化')
        self.CreateWidgets()
        self.UpdateButtonFG()

        simlab.setSelectionFilter('Face')

        simlablib.DeleteGroups([self.limit1, self.limit2, self.guide])
        simlabutil.ClearSelection()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmCyl = tk.Frame(self.nb)
        self.frmFlt = tk.Frame(self.nb)
        self.nb.add(self.frmCyl, text=' 筒状化 ')
        self.nb.add(self.frmFlt, text=' 平坦化 ')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        
        self.CreateCylTab()
        self.CreateFltTab()

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.BOTTOM, anchor=tk.NE)

        btnWidth = 10
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
        simlab.setSelectionFilter('Face')

    def CreateCylTab(self):
        self.lblNote1 = tk.Label(self.frmCyl, text='Tips: 画像の面を選択して、[ 簡略化 ]ボタンを押してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmCyl, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmFig = tk.Frame(self.frmCyl)
        self.frmFig.pack(side=tk.TOP, anchor=tk.CENTER)

        self.iconRing = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'BeltPulley.png')), master=self.frmFig)
        tk.Label(self.frmFig, image=self.iconRing).pack(side=tk.LEFT, anchor=tk.CENTER, padx=5)

        self.btnLimit1 = tk.Button(self.frmFig, text=' リミット面1 ', command=self.SelectLimit1)
        self.btnLimit1.place(x= 10, y=30)

        self.btnLimit2 = tk.Button(self.frmFig, text=' リミット面2 ', command=self.SelectLimit2)
        self.btnLimit2.place(x= 240, y=40)

        self.btnGuide = tk.Button(self.frmFig, text=' ガイド面 ', command=self.SelectGuide)
        self.btnGuide.place(x= 190, y=10)

        ## Layer
        self.frmLayer = tk.Frame(self.frmCyl)
        self.frmLayer.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, pady=2)
        self.lblLayer = tk.Label(self.frmLayer, text='要素レイヤー数 : ')
        self.lblLayer.pack(side=tk.LEFT, anchor=tk.W)
        self.entLayer = tk.Entry(self.frmLayer, width=10)
        self.entLayer.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entLayer.insert(tk.END, 4)

        tk.Frame(self.frmCyl, height=10).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrlCyl = tk.Frame(self.frmCyl)
        self.frmCtrlCyl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnMerge = tk.Button(self.frmCtrlCyl, text=' 簡略化 ', compound=tk.LEFT, command=self.Simplify, width=btnWidth)
        self.btnMerge.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnUndo = tk.Button(self.frmCtrlCyl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

    def SelectLimit1(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、[リミット面1] ボタンを押下してください。')
            return

        simlablib.DeleteGroups([self.limit1])

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.limit1)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectLimit2(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、[リミット面2] ボタンを押下してください。')
            return

        simlablib.DeleteGroups([self.limit2])

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.limit2)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectGuide(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、[ガイド面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups([self.guide])

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.guide)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def Simplify(self):
        groups = [self.limit1, self.limit2, self.guide]
        for i in range(len(groups)):
            if not simlab.isGroupPresent(groups[i]):
                messagebox.showinfo('情報','全ての面を選択した後、[簡略化] ボタンを押下してください。')
                return

        try:
            numLayer = int(self.entLayer.get())
        except:
            messagebox.showinfo('情報','正の整数を指定してください。')
            return

        self.backup.Save('Simplify')
        simplifyBeltPulley(self.limit1, self.limit2, self.guide, numLayer)
        
        simlablib.DeleteGroups([self.limit1, self.limit2, self.guide])
        self.UpdateButtonFG()

    def CreateFltTab(self):
        self.lblNote2 = tk.Label(self.frmFlt, text='Tips: 画像の面を選択して、[ 簡略化 ]ボタンを押してください。')
        self.lblNote2.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmFlt, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmFig2 = tk.Frame(self.frmFlt)
        self.frmFig2.pack(side=tk.TOP, anchor=tk.CENTER)

        self.iconRing2 = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'simp_flat.png')), master=self.frmFig)
        tk.Label(self.frmFig2, image=self.iconRing2).pack(side=tk.LEFT, anchor=tk.CENTER, padx=5)

        self.btnLimitF = tk.Button(self.frmFig2, text=' リミット面 ', command=self.SelectLimit_Flat)
        self.btnLimitF.place(x=20, y=70)

        self.btnGuideF = tk.Button(self.frmFig2, text=' ガイド面 ', command=self.SelectGuide_Flat)
        self.btnGuideF.place(x=190, y=50)

        tk.Frame(self.frmFlt, height=10).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrlFlt = tk.Frame(self.frmFlt)
        self.frmCtrlFlt.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnSim2 = tk.Button(self.frmCtrlFlt, text=' 簡略化 ', compound=tk.LEFT, command=self.Simplify_Flat, width=btnWidth)
        self.btnSim2.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnUndo2 = tk.Button(self.frmCtrlFlt, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo2.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo2)

    def SelectLimit_Flat(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、[リミット面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups([self.limit_flat])

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.limit_flat)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectGuide_Flat(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、[ガイド面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups([self.guide_flat])

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.guide_flat)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def Simplify_Flat(self):
        groups = [self.limit_flat, self.guide_flat]
        for i in range(len(groups)):
            if not simlab.isGroupPresent(groups[i]):
                messagebox.showinfo('情報','全ての面を選択した後、[簡略化] ボタンを押下してください。')
                return

        self.backup.Save('SimplifyFlat')
        importlib.reload(meshutil)
        simplifyFlatFace(self.guide_flat, self.limit_flat)
        
        simlablib.DeleteGroups([self.limit_flat, self.guide_flat])
        self.UpdateButtonFG()

    def Undo(self):
        self.backup.Load()

        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

        self.UpdateButtonFG()

    def UpdateButtonFG(self):
        groups = [self.limit1, self.limit2, self.guide, self.limit_flat, self.guide_flat]
        widgets = [self.btnLimit1, self.btnLimit2, self.btnGuide, self.btnLimitF, self.btnGuideF]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def CloseDialog(self):
        simlablib.DeleteGroups([self.limit1, self.limit2, self.guide, self.limit_flat, self.guide_flat])
        super().CloseDialog()