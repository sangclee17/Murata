import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib
from datetime import datetime
from PIL import Image, ImageTk
import re
from xml.sax.saxutils import escape

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = os.path.join(PROJECT_DIR,'log')
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

# local import
import basedialog
import simlabutil
import widget as wt
import tooltip as tp
import backup
import messageboxWithCheckbox as mc
import simlablib
import grouputil

def duplicates(lst, item):
    return [index for index, x in enumerate(lst) if x == item]

def make_distinct_bodyName(bdyNms):
    bodyNmDict = {}
    modelNm = simlab.getModelName('CAD')
    allBdyNms = simlab.getBodiesWithSubString(modelNm,['*'])
    bdySet = set(bdyNms)

    result = []
    for this_body in bdySet:
        result.append((this_body, duplicates(allBdyNms, this_body)))
    return result


def ouputBodyList(bodyNms):
    ModelNM = simlab.getModelName('CAD')
    outputStr = []

    if len(bodyNms) > 1:
        outputStr.append('''<BodyList1>\n    <Entities>\n    <Model>'''+ str(ModelNM) +'''</Model>\n    <Body>"'''+ bodyNms[0] +'''",</Body>\n    </Entities>\n    </BodyList1>\n''')
        outputStr.append('''<BodyList2>\n    <Entities>\n    <Model>'''+ str(ModelNM) +'''</Model>\n    <Body>'''+ ','.join('"{}"'.format(v) for v in bodyNms[1:]) +''',</Body>\n    </Entities>\n    </BodyList2>''')
    
    return '    '.join(outputStr)

def save_file(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    fileSavePath = os.path.join(dir_name, "BooleanMae_{}.slb".format(now))
    ExportSlb=''' <ExportSlb UUID="a155cd6e-8ae6-4720-8ab4-1f50d4a34d1c">
    <tag Value="-1"/>
    <Name Value=""/>
    <Option Value="1"/>
    <FileName Value="'''+ fileSavePath +'''"/>
    </ExportSlb>'''
    simlab.execute(ExportSlb)
    return fileSavePath

def import_file(fileImportPath):
    if os.path.exists(fileImportPath):
        ImportSlb=''' <ImportSlb CheckBox="ON" UUID="C806F6DF-56FA-4134-9AD1-1010BF292183" gda="">
        <tag Value="1"/>
        <Name Value="'''+ fileImportPath +'''"/>
        <FileName Value="'''+ fileImportPath +'''"/>
        <ImportOrOpen Value="1"/>
        <Output/>
        </ImportSlb>'''
        simlab.execute(ImportSlb)
        return 1
    else:
        #print("File doesn't exists. Check the file path")
        return 0

def deleteModel(modelNM):
    DeleteModel=''' <DeleteModel CheckBox="ON" updategraphics="0" UUID="AE031126-6421-4633-8FAE-77C8DE10C18F">
    <ModelName Value="'''+ str(modelNM) +'''"/>
    </DeleteModel>'''
    simlab.execute(DeleteModel)
    
def booleanAssemble(bodyNms, genBody = 1):

    Boolean=''' <BodyUnion UUID="83ff924f-a248-479c-b159-f6266f6d6db7">
    <tag Value="-1"/>
    <Name Value="BodyUnion1"/>
    <BodyType Value="1"/>
    <Operation Value="1"/>
    <Retain Value="0"/>
    <BodyUnionType Value="2"/>
    <PreserveFacesOnAllBodies Value="0"/>
    <LocalRemesh Value="0"/>
    <Merge Value="0"/>
    <CreateGeneralBodies Value="'''+ str(genBody) +'''"/>
    <FaceList1 EntityTypes="" ModelIds="" Value=""/>
    '''+ ouputBodyList(bodyNms) +'''
    <Output/>
    </BodyUnion>'''
    simlab.execute(Boolean)

def renameBody(oldNm, newNm):
    modelNm = simlab.getModelName('CAD')
    RenameBody=''' <RenameBody UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8" CheckBox="ON">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ oldNm +'''",</Body>
    </Entities>
    </SupportEntities>
    <NewName Value="'''+ newNm +'''"/>
    <Output/>
    </RenameBody>'''
    simlab.execute(RenameBody)

def checkSameBdyNms():
    ModelNM = simlab.getModelName('CAD')
    BodyNMs = list(simlab.getBodiesWithSubString(ModelNM, ['*']))
    NameChanged = False

    for this_body in BodyNMs:
        # There is a function that uses the body name in the SimLab Parameter name.
        # SimLab Parameter must always start with an alphabet, so change the body name to a possible name
        newBodyName = re.sub(re.compile("[ -/:-@[-`{-~]"), '_', this_body)
        if len(newBodyName) != 0:
            firstChar = newBodyName[0]
            if not firstChar.isalpha():
                if firstChar == '_':
                    newBodyName = 'B' + newBodyName
                else:
                    newBodyName = 'B_' + newBodyName

        if this_body != newBodyName:
            escaped_this_body = escape(this_body)
            renameBody(escaped_this_body, newBodyName)
            NameChanged = True

    if NameChanged:
        BodyNMs = list(simlab.getBodiesWithSubString(ModelNM, ['*']))

    uniqueBodyNMs = list(set(BodyNMs))

    if len(BodyNMs) != len(uniqueBodyNMs):
        #simlabutil.DeleteAllModel()
        duplicateBodies = [x for x in set(uniqueBodyNMs) if BodyNMs.count(x) > 1]
        messagebox.showinfo('情報', '同じ名前のボディが存在します。CADまたは、Inspireで異なる名前に変更してから読み込みなおしてください。\n\n' + str(duplicateBodies).strip('[]'))


def joinAssemble(joinType, bodies, tolerance):    
    ModelNM = simlab.getModelName('FEM') 

    if joinType == "plane":
        Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value=""/>
        <Pick Value="Join"/>
        <JoinEntities>
        <Entities>
        <Model>'''+ ModelNM +'''</Model>
        <Body>'''+ str(bodies).replace("'", '"').strip("()") +'''</Body>
        </Entities>
        </JoinEntities>
        <AlignEntities ModelIds="" Value="" EntityTypes=""/>
        <PreserveEntities ModelIds="" Value="" EntityTypes=""/>
        <Tolerance Value="'''+ str(tolerance) +'''"/>
        <JoinType Value="GEOM_PLANAR_FACES"/>
        <MeshOrShape Value="Shape"/>
        <MeshOption Value=""/>
        <MeshParam Value=""/>
        <SplitFace Value="1"/>
        <LocalRemesh Value="0"/>
        </Join>'''
        simlab.execute(Join)

    elif joinType == "cylinder":
        Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value=""/>
        <Pick Value="Join"/>
        <JoinEntities>
        <Entities>
        <Model>'''+ ModelNM +'''</Model>
        <Body>'''+ str(bodies).replace("'", '"').strip("()") +'''</Body>
        </Entities>
        </JoinEntities>
        <AlignEntities ModelIds="" Value="" EntityTypes=""/>
        <PreserveEntities ModelIds="" Value="" EntityTypes=""/>
        <Tolerance Value="'''+ str(tolerance) +'''"/>
        <JoinType Value="CYLINDRICAL_FACES|CONICAL_FACES"/>
        <MeshOrShape Value="Shape"/>
        <MeshOption Value="Auto"/>
        <MeshParam Value=""/>
        <SplitFace Value="1"/>
        <LocalRemesh Value="0"/>
        </Join>'''
        simlab.execute(Join)
        
    elif joinType == "auto":
        Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value=""/>
        <Pick Value="Join"/>
        <JoinEntities>
        <Entities>
        <Model>'''+ ModelNM +'''</Model>
        <Body>'''+ str(bodies).replace("'", '"').strip("()") +'''</Body>
        </Entities>
        </JoinEntities>
        <AlignEntities ModelIds="" Value="" EntityTypes=""/>
        <PreserveEntities ModelIds="" Value="" EntityTypes=""/>
        <Tolerance Value="'''+ str(tolerance) +'''"/>
        <JoinType Value="GEOM_PLANAR_FACES"/>
        <MeshOrShape Value="Shape"/>
        <MeshOption Value=""/>
        <MeshParam Value=""/>
        <SplitFace Value="1"/>
        <LocalRemesh Value="0"/>
        </Join>'''
        simlab.execute(Join)
        
        Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value=""/>
        <Pick Value="Join"/>
        <JoinEntities>
        <Entities>
        <Model>'''+ ModelNM +'''</Model>
        <Body>'''+ str(bodies).replace("'", '"').strip("()") +'''</Body>
        </Entities>
        </JoinEntities>
        <AlignEntities ModelIds="" Value="" EntityTypes=""/>
        <PreserveEntities ModelIds="" Value="" EntityTypes=""/>
        <Tolerance Value="'''+ str(tolerance) +'''"/>
        <JoinType Value="CYLINDRICAL_FACES|CONICAL_FACES"/>
        <MeshOrShape Value="Shape"/>
        <MeshOption Value="Auto"/>
        <MeshParam Value=""/>
        <SplitFace Value="1"/>
        <LocalRemesh Value="0"/>
        </Join>'''
        simlab.execute(Join)

    if not areSharedEntities(bodies):
        messagebox.showinfo("情報","No common faces are found")
        return
    updateModel()
    remeshLocally(bodies)
    

def areSharedEntities(bodies):
    modelNm = simlab.getModelName("FEM")
    if simlab.isGroupPresent('Shared Faces'):
        simlablib.DeleteGroups('Shared Faces')

    SharedEntities=''' <SharedEntities UUID="2dc7ae98-62c3-4926-bbde-d08da48208ad" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="SharedEntities2"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    <Faces Value="1"/>
    <Edges Value="0"/>
    </SharedEntities>'''
    simlab.execute(SharedEntities)

    if simlab.isGroupPresent('Shared Faces'):
        simlablib.DeleteGroups('Shared Faces')
        return True
    return False
    

def remeshLocally(bodies):
    modelNm = simlab.getModelName("FEM")
    if not simlab.isParameterPresent("DefaultMeshSize") or not simlab.isParameterPresent("DefaultMaxAngle") or not simlab.isParameterPresent("DefaultAspectRatio"):
        messagebox.showinfo("情報", "Re-mesh property parameter is missing")
        return
    
    meshSize = simlab.getDoubleParameter("$DefaultMeshSize")
    maxAngle = simlab.getDoubleParameter("$DefaultMaxAngle")
    aspectRat = simlab.getDoubleParameter("$DefaultAspectRatio")

    LocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodies).replace("'", '"').strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    <ElemType Value="1"/>
    <AverageElemSize Value="'''+ str(meshSize) +'''"/>
    <MinElemSize Value="'''+ str(meshSize/aspectRat) +'''"/>
    <PreserveBoundaryEdges Value="0"/>
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

def updateModel():
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def joinFaces(faceIds, tol):
    modelNm = simlab.getModelName("FEM")
    Join=''' <Join CheckBox="ON" UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC">
    <tag Value="-1"/>
    <Name Value=""/>
    <Pick Value="Join"/>
    <JoinEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+",".join(str(v) for v in faceIds)+''',</Face>
    </Entities>
    </JoinEntities>
    <AlignEntities ModelIds="" EntityTypes="" Value=""/>
    <PreserveEntities ModelIds="" EntityTypes="" Value=""/>
    <Tolerance Value="'''+ str(tol) +'''"/>
    <JoinType Value="GENERAL_FACES"/>
    <MeshOrShape Value=""/>
    <MeshOption Value=""/>
    <MeshParam Value=""/>
    <SplitFace Value="1"/>
    <LocalRemesh Value="1"/>
    </Join>'''
    simlab.execute(Join)

def updateFeatures():
    ModelNM = simlab.getModelName('CAD')
    UpdateAttributes=''' <UpdateFeature UUID="68cd70e3-d5ba-4cdd-9449-9ca866be5e01" CheckBox="ON" gda="">
    <tag Value="-1"/>
    <Name Value="UpdateFeature3"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ ModelNM +'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <Output/>
    </UpdateFeature>'''
    simlab.execute(UpdateAttributes)

class CADBodyMergeDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.backup = backup
        self.master.title('CADボディ結合')
        self.CreateWidgets()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.lblNote1 = tk.Label(self.frmTop, text='Tips: 結合したいボディを選択して、[ 結合 ]ボタンを押してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.NW)

        self.lblNote2 = tk.Label(self.frmTop, text='結合できない面は、2Dメッシュ作成後にFEM共有面結合で結合してください。')
        self.lblNote2.pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnMerge = tk.Button(self.frmCtrl, text=' ボディ結合 ', compound=tk.LEFT, command=self.Merge, width=btnWidth)
        self.btnMerge.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.tpMerge = tp.ToolTip(self.btnMerge, '選択したボディを結合します。', self.master)
        self.tpUndo = tp.ToolTip(self.btnUndo, '操作を戻します。', self.master)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def Merge(self):
        bodies = simlab.getSelectedBodies()
        if len(bodies) < 2:
            messagebox.showinfo('情報','結合したいCADボディを2つ以上選択してください。')
            return
        
        self.backup.Save('Merge')

        ModelNM = simlab.getModelName('CAD')
        beforeBoolean = len(simlab.getBodiesWithSubString(ModelNM,['*']))            
        booleanAssemble(bodies, genBody= 1)
        afterBoolean = len(simlab.getBodiesWithSubString(ModelNM,['*']))
        
        if beforeBoolean <= afterBoolean:
            messagebox.showinfo('情報','ブーリアン結合に失敗しました。')
            return

        updateFeatures()
        if not simlab.isParameterPresent('BOOLEAN'):
            SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
            <ParamInfo Name="BOOLEAN" Value="1" Type="integer"/>
            </Parameters>'''
            simlab.execute(SimLabParameters)

        message = 'CADボディの結合が終了しました。結果を確認してください。'
        message += '\n\n結合できなかった場合は、表面メッシュを作成した後で\nFEMの共有面を結合してください。'
        message += '\n\n異常があった場合は[戻す] ボタンを押してください。'

        msgbox = mc.MessageBoxWithCheckBox(self.master)
        msgbox.ShowInfoIfNeeded('情報', message, 0)

    def Undo(self):
        self.backup.Load()
        modelName = simlab.getModelName('FEM')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

class ShareNodeDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup, config):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.backup = backup
        self.config = config
        self.faces1 = '_Share_Faces_1'
        self.faces2 = '_Share_Faces_2'

        self.master.title('節点共有')
        self.CreateWidgets()

        simlab.setSelectionFilter('Body')

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmBody = tk.Frame(self.nb)
        self.frmFace = tk.Frame(self.nb)
        self.nb.add(self.frmBody, text=' ボディ ')
        self.nb.add(self.frmFace, text=' 面 ')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        self.nb.bind('<<NotebookTabChanged>>', self.ChangeTab)

        self.CreateBodyTab()
        self.CreateFaceTab()

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def ChangeTab(self, event):
        simlabutil.ClearSelection()

        cid = self.nb.index('current')
        if cid == 0:
            simlab.setSelectionFilter('Body')
        else:
            simlab.setSelectionFilter('Face')
            self.UpdateButtonFG()

    def CreateBodyTab(self):
        self.lblNoteB = tk.Label(self.frmBody, text='Tips: 共有面にしたいボディを選択して、[ 節点共有 ]ボタンを押してください。')
        self.lblNoteB.pack(side=tk.TOP, anchor=tk.W)

        tk.Frame(self.frmBody, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCType = tk.LabelFrame(self.frmBody, text='接続タイプ')
        self.frmCType.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        
        self.bodyJoinType = tk.StringVar()
        self.bodyJoinType.set('auto')

        self.rbtnAuto = tk.Radiobutton(self.frmCType, value='auto', variable=self.bodyJoinType, text=' 自動 ')
        self.rbtnAuto.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        self.rbtnPlane = tk.Radiobutton(self.frmCType, value='plane', variable=self.bodyJoinType, text=' 平面 ')
        self.rbtnPlane.pack(side=tk.LEFT, anchor=tk.W)

        self.rbtnCylinder = tk.Radiobutton(self.frmCType, value='cylinder', variable=self.bodyJoinType, text=' 円筒 ')
        self.rbtnCylinder.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        tk.Frame(self.frmBody, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmTol = tk.Frame(self.frmBody)
        self.frmTol.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        tk.Label(self.frmTol, text='トレランス: ').pack(side=tk.LEFT, anchor=tk.W)
        self.entTolBody = tk.Entry(self.frmTol, width=8)
        self.entTolBody.insert(tk.END, 1.0)
        self.entTolBody.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        tk.Frame(self.frmBody, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrlBody = tk.Frame(self.frmBody)
        self.frmCtrlBody.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        
        btnWidth = 10
        self.btnMerge = tk.Button(self.frmCtrlBody, text=' 節点共有 ', compound=tk.LEFT, command=self.ShareNodesUsingBoies, width=btnWidth)
        self.btnMerge.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnUndoBody = tk.Button(self.frmCtrlBody, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndoBody.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndoBody)

        tk.Frame(self.frmBody, height=5).pack(side=tk.TOP, anchor=tk.NW)

    def ShareNodesUsingBoies(self):
        bodies = simlab.getSelectedBodies()
        joinType = self.bodyJoinType.get()
        tolerance = self.entTolBody.get()

        self.backup.Save('ShareNode')
        joinAssemble(joinType, bodies, tolerance)

    def CreateFaceTab(self):
        self.lblNoteF = tk.Label(self.frmFace, text='Tips: 共有したい面をそれぞれ登録後、[節点共有]を押してください。')
        self.lblNoteF.pack(side=tk.TOP, anchor=tk.W)

        tk.Frame(self.frmFace, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmEnt = tk.Frame(self.frmFace)
        self.frmEnt.pack(side=tk.TOP, anchor=tk.W, padx=5)
        tk.Label(self.frmEnt, text='エンティティ: ').pack(side=tk.LEFT, anchor=tk.W)

        self.btnFace1 = tk.Button(self.frmEnt, text=' 共有したい面1 ', command=self.SelectFaces1)
        self.btnFace1.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmEnt, width=5).pack(side=tk.LEFT, anchor=tk.W)

        self.btnFace2 = tk.Button(self.frmEnt, text=' 共有したい面2 ', command=self.SelectFaces2)
        self.btnFace2.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmFace, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmTol = tk.Frame(self.frmFace)
        self.frmTol.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        tk.Label(self.frmTol, text='トレランス: ').pack(side=tk.LEFT, anchor=tk.W)
        self.entTol = tk.Entry(self.frmTol, width=8)
        self.entTol.insert(tk.END, 1.0)
        self.entTol.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        tk.Frame(self.frmFace, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrlFace = tk.Frame(self.frmFace)
        self.frmCtrlFace.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        
        btnWidth = 10
        self.btnMerge = tk.Button(self.frmCtrlFace, text=' 節点共有 ', compound=tk.LEFT, command=self.ShareNodesUsingFaces, width=btnWidth)
        self.btnMerge.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnUndo = tk.Button(self.frmCtrlFace, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

    def SelectFaces1(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押下してください。')
            return
        
        simlablib.DeleteGroups(self.faces1)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.faces1)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectFaces2(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.faces2)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.faces2)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def ShareNodesUsingFaces(self):
        if not simlab.isGroupPresent(self.faces1) or not simlab.isGroupPresent(self.faces1):
            messagebox.showinfo('情報','面を選択した後、ボタンを押下してください。')
            return
        
        importlib.reload(grouputil)
        try:
            tolerance = float(self.entTol.get())
        except:
            messagebox.showinfo('情報','実数で指定してください。')
            return

        self.backup.Save('ShareNode')

        grouputil.gasketJoinGrp(self.faces1, self.faces2, tolerance)

        simlablib.DeleteGroups([self.faces1, self.faces2])
        self.UpdateButtonFG()

    def Undo(self):
        self.backup.Load()
    
        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def UpdateButtonFG(self):
        groups = [self.faces1, self.faces2]
        widgets = [self.btnFace1, self.btnFace2]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)       

    def CloseDialog(self):
        simlablib.DeleteGroups([self.faces1, self.faces2])
        simlabutil.ClearSelection()
        super().CloseDialog()