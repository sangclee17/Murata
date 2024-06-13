from hwx import simlab
import tkinter.messagebox as messagebox
import springutil
import importlib
import muratautil

MPC_COUNTER = "MPC_COUNTER"

def _getElemEntitiesFromFace(faceIds):
    modelNm = simlab.getModelName("FEM")
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ ",".join(str(v) for v in faceIds) +''',</Face>
    </Entities>
    </InputFaces>
    <Option Value="Elements"/>
    <Groupname Value="SelectElements_9"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)
    elemEnts = simlab.getEntityFromGroup("SelectElements_9")
    _deleteGrp("SelectElements_9")
    return elemEnts

def _getCornerNodeEntitiesFromElement(elemIds):
    modelNm = simlab.getModelName("FEM")
    SelectElementAssociatedEntities=''' <SelectElementAssociatedEntities UUID="7062f057-0e48-4ccc-ad73-e60584e8ff26">
    <InputElement Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Element>'''+ ",".join(str(v) for v in elemIds) +''',</Element>
    </Entities>
    </InputElement>
    <Option Value="Cornernodes"/>
    <Groupname Value="SelectCornerNodes_11"/>
    </SelectElementAssociatedEntities>'''
    simlab.execute(SelectElementAssociatedEntities)
    nodeIds = simlab.getEntityFromGroup("SelectCornerNodes_11")
    _deleteGrp("SelectCornerNodes_11")
    return nodeIds

def _createMPCBetweenNodes(mpcProp, masterNodes, slaveNodes):
    coordId, x, y, z, r_x, r_y, r_z = mpcProp

    masterBody = _getAssociatedBodyFromNodes(masterNodes)
    slaveBody = _getAssociatedBodyFromNodes(slaveNodes)

    masterBody = str(masterBody).strip("()"",""'")
    slaveBody = str(slaveBody).strip("()"",""'")

    mpcID = muratautil.getUniqueId(MPC_COUNTER)
    mpcName = "{}_{}_{}".format(masterBody, slaveBody, mpcID)

    modelNm = simlab.getModelName("FEM")
    MPC=''' <Stress_MPC CheckBox="ON" BCType="MPC" UUID="BBCD6D76-5754-42b5-8A1B-E8FB79064EFE" isObject="2">
    <tag Value="-1"/>
    <Name Value="'''+ mpcName +'''"/>
    <CoordinateAxisID Value="'''+ str(coordId) +'''"/>
    <BetweenEntitties Value="1"/>
    <MasterList>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Node>'''+ str(masterNodes).strip("[]""()") +''',</Node>
    </Entities>
    </MasterList>
    <SlaveList>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Node>'''+ str(slaveNodes).strip("[]""()")+''',</Node>
    </Entities>
    </SlaveList>
    <X_or_Radial CheckBox="'''+ str(1 if x else 0) +'''" Value="'''+ str(1) +'''"/>
    <Y_or_Theta CheckBox="'''+ str(1 if y else 0) +'''" Value="'''+ str(1) +'''"/>
    <Z_or_Axial CheckBox="'''+ str(1 if z else 0) +'''" Value="'''+ str(1) +'''"/>
    <Rx CheckBox="'''+ str(1 if r_x else 0) +'''" Value="'''+ str(1) +'''"/>
    <Ry CheckBox="'''+ str(1 if r_y else 0) +'''" Value="'''+ str(1) +'''"/>
    <Rz CheckBox="'''+ str(1 if r_z else 0) +'''" Value="'''+ str(1) +'''"/>
    <Dept_X_or_Radial CheckBox="0" Value="1"/>
    <Dept_Y_or_Theta CheckBox="0" Value="1"/>
    <Dept_Z_or_Axial CheckBox="0" Value="1"/>
    <Dept_Rx CheckBox="0" Value="0"/>
    <Dept_Ry CheckBox="0" Value="0"/>
    <Dept_Rz CheckBox="0" Value="0"/>
    <Tolerance Value="1"/>
    <MPCFaceType Value="2"/>
    <IgnoreEdgesChk Value="0"/>
    <IgnoreEdgeList EntityTypes="" ModelIds="" Value=""/>
    <MPCType Value="0"/>
    <MasterNode EntityTypes="" ModelIds="" Value=""/>
    <NoOfIndepNodes Value=""/>
    <CyclicFlag Value="0"/>
    <CyclicNodePairList1 EntityTypes="" ModelIds="" Value=""/>
    <CyclicNodePairList2 EntityTypes="" ModelIds="" Value=""/>
    <CheckCreateCons Value="0"/>
    <ConstraintId Value="0"/>
    <GapElem Value=""/>
    </Stress_MPC>'''
    simlab.execute(MPC)
    # print(MPC)

def _getAssociatedBodyFromNodes(nodeIds):
    modelNm = simlab.getModelName("FEM")
    bodyGroup ="SelectBodies_50"
    SelectNodeAssociatedEntities=''' <SelectNodeAssociatedEntities UUID="6731d198-667e-49c9-8612-c7d980368508">
    <InputNodes Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Node>'''+ str(nodeIds).strip("()") +'''</Node>
    </Entities>
    </InputNodes>
    <Option Value="Bodies"/>
    <Groupname Value="'''+ bodyGroup +'''"/>
    </SelectNodeAssociatedEntities>'''
    simlab.execute(SelectNodeAssociatedEntities)

    bodyNms = simlab.getBodiesFromGroup(bodyGroup)
    _deleteGrp(bodyGroup)
    return bodyNms

def _updateModel():
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def _deleteGrp(grpNm):
    DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +''',"/>
    <Output/>
    </DeleteGroupControl>'''
    simlab.execute(DeleteGroupControl)

def imprintGasket(deckFaceId, gasketFaceId, tolerance=1):
    modelNm = simlab.getModelName("FEM")
    imprintFaceGrp = "imprintedFace"
    _deleteGrp(imprintFaceGrp)

    ImprintGasket=''' <GasketImprint gda="" UUID="1dd925d8-8b5b-4994-aa6b-fe9807711ed5">
    <tag Value="-1"/>
    <Name Value="GasketImprint2"/>
    <Entity>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(gasketFaceId).strip("[]()") +''',</Face>
    </Entities>
    </Entity>
    <DeckFace>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(deckFaceId).strip("[]()") +''',</Face>
    </Entities>
    </DeckFace>
    <Tolerance Value="'''+ str(tolerance) +'''"/>
    <PreservePatterns Value="1"/>
    <MeshSize Value="14.8761" Checked="0"/>
    <EquivalenceNodes Value="0"/>
    <Output/>
    </GasketImprint>'''
    simlab.execute(ImprintGasket)

    if simlab.isGroupPresent("Gasket_Imprint"):
        _renameGroupNm("Gasket_Imprint", imprintFaceGrp)
    else:
        return None
    return True

def _renameGroupNm(nameFrom, nameTo):
    RenameGroupControl=''' <RenameGroupControl CheckBox="ON" UUID="d3addb85-3fd0-4972-80af-e699f96e9045">
    <tag Value="-1"/>
    <Name Value="'''+ nameFrom +'''"/>
    <NewName Value="'''+ nameTo +'''"/>
    <Output/>
    </RenameGroupControl>'''
    simlab.execute(RenameGroupControl)


def createMPC(entitiesProp, mpcProp, cornerNodeOnly):
    masterGrp, slaveGrp, tolerance = entitiesProp

    _createFaceMPC_UsingImprintGasket(masterGrp, slaveGrp, tolerance, mpcProp, cornerNodeOnly)

def _createFaceMPC_UsingImprintGasket(masterGrp, slaveGrp, tolerance, mpcProp, conerNodesOnly):
    masterEnts = simlab.getEntityFromGroup(masterGrp)
    slaveEnts = simlab.getEntityFromGroup(slaveGrp)
    if not masterEnts or not slaveEnts:
        messagebox.showinfo("情報","Empty group entities!!")
        return
    
    deckFace = slaveEnts
    gasketFace = masterEnts
    
    imprinted_ok = imprintGasket(deckFace, gasketFace, tolerance = tolerance)
    if not imprinted_ok:
        messagebox.showinfo("情報","Face imprinting failed..")
        return

    masterEnts = simlab.getEntityFromGroup(masterGrp)
    slaveEnts = simlab.getEntityFromGroup(slaveGrp)
    if conerNodesOnly:
        masterElemEntities = _getElemEntitiesFromFace(masterEnts)
        masterNodes = _getCornerNodeEntitiesFromElement(masterElemEntities)

        slaveElemEntities = _getElemEntitiesFromFace(slaveEnts)
        slaveNodes = _getCornerNodeEntitiesFromElement(slaveElemEntities)
    else:
        masterNodes = _getNodesFromFace(masterEnts)
        slaveNodes = _getNodesFromFace(slaveEnts)

    _createMPCBetweenNodes(mpcProp, masterNodes, slaveNodes)

def _getNodesFromFace(faceIds):
    modelNm = simlab.getModelName("FEM")
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceIds).strip("()[]") +''',</Face>
    </Entities>
    </InputFaces>
    <Option Value="Nodes"/>
    <Groupname Value="SelectNodes_38"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)

    nodeIds = simlab.getEntityFromGroup("SelectNodes_38")
    _deleteGrp("SelectNodes_38")
    return nodeIds