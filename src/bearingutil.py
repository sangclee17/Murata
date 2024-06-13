from hwx import simlab
import tkinter.messagebox as messagebox
import simlabutil
import propertyutil
import numpy as np
import random
import importlib
import muratautil
import assemStructure

SHELL_BEARING = "PShell"
SOLID_BEARING = "SBearing"
MAX_ID_SPRING = 'Max_ID_Spring'
# SHELL_MODEL = "SHELL_ASSY"
SPINDLE_ASSY = "SPINDLE_ASSY"

def getPlaneInfo(planarFaceId):
    return _getPlaneDataIn3Points(planarFaceId)

def _getPlaneDataIn3Points(faceId):
    modelNm = simlab.getModelName("CAD")
    if isinstance(faceId, tuple):faceId = faceId[0]
    return simlab.definePlaneFromEntity(modelNm, int(faceId))

def _getBodyFromFace(modelType, faceIds):
    modelNm = simlab.getModelName(modelType)
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+",".join(str(v) for v in faceIds)+''',</Face>
    </Entities>
    </InputFaces>
    <Option Value="Bodies"/>
    <Groupname Value="SelectBodies_4"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)
    bodyNm = simlab.getBodiesFromGroup("SelectBodies_4")
    _deleteGrp("SelectBodies_4")
    return bodyNm

def _getBodyFromEdges(edgeIds):
    modelNm = simlab.getModelName("FEM")
    SelectEdgeAssociatedEntities=''' <SelectEdgeAssociatedEntities UUID="551fdd5b-6a8c-4a30-8ab0-fbaf9257343e">
    <InputEdges Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Edge>'''+ str(edgeIds).strip("()") +'''</Edge>
    </Entities>
    </InputEdges>
    <Option Value="Faces"/>
    <Groupname Value="SelectFaces_95"/>
    </SelectEdgeAssociatedEntities>'''
    simlab.execute(SelectEdgeAssociatedEntities)

    faceIds = simlab.getEntityFromGroup("SelectFaces_95")

    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceIds).strip("()") +'''</Face>
    </Entities>
    </InputFaces>
    <Option Value="Bodies"/>
    <Groupname Value="SelectBodies_96"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)

    bodyNm = simlab.getBodiesFromGroup("SelectBodies_96")
    _deleteGrp("SelectFaces_95")
    _deleteGrp("SelectBodies_96")

    return bodyNm


def _updateModel():
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def _updateAttributes(modelType):
    modelNm = simlab.getModelName(modelType)
    UpdateAttributes=''' <UpdateFeature UUID="68cd70e3-d5ba-4cdd-9449-9ca866be5e01" CheckBox="ON" gda="">
    <tag Value="-1"/>
    <Name Value="UpdateFeature2"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <Output/>
    </UpdateFeature>'''
    simlab.execute(UpdateAttributes)

# Create a bearing from CAD

def _getConnectedEdgeEntities(edgeGrp):
    connEdgeGrps = simlab.createGroupsOfConnectedEntities(edgeGrp)
    # print(connEdgeGrps)
    if len(connEdgeGrps) > 1:
        theEdgeGrp = random.sample(connEdgeGrps, k=1)[0]
        # print(theEdgeGrp)
        theEdgeId = simlab.getEntityFromGroup(theEdgeGrp)
        
    else:
        theEdgeId = connEdgeGrps[0]

    for thisEdgeGrp in connEdgeGrps:
        _deleteGrp(thisEdgeGrp)

    return theEdgeId

def _modifyToQuadElems(bodyNms):
    modelNm = simlab.getModelName("FEM")
    ModifyElements=''' <Modify CheckBox="ON" UUID="28706164-e6e5-4544-b4a9-c052c4b6c60f">
    <Name Value="Modify4"/>
    <tag Value="-1"/>
    <Option Value="TRITOQUAD8"/>
    <QuadDominant Value="1"/>
    <Entity>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNms).replace("'",'"') +'''</Body>
    </Entities>
    </Entity>
    <IdealQuad Value="0"/>
    <UpdateAssociateRBENodes Value="1"/>
    </Modify>'''
    simlab.execute(ModifyElements)

def _createBodyFromFaces(faceIds):
    modelNm = simlab.getModelName("FEM")
    bodyNmsBefore = simlab.getBodiesWithSubString(modelNm, ["*"])
    CreateBodyFromFaces=''' <BodyFromFaces gda="" UUID="24F7C671-DC40-44e0-9B32-8A22A67F58FA">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceIds).strip("()""[]") +'''</Face>
    </Entities>
    </SupportEntities>
    <ShareBoundaryEdges Value="1"/>
    <CreateBodyFromFaceOption Value="2"/>
    <CreateBodyForEachGroup Value="false"/>
    <Group Entity="" Value=""/>
    <UseInputBodyName Value="true"/>
    </BodyFromFaces>'''
    simlab.execute(CreateBodyFromFaces)
    bodyNmsAfter = simlab.getBodiesWithSubString(modelNm, ["*"])

    return tuple(set(bodyNmsAfter) - set(bodyNmsBefore))

def _renameBody(modelNm, oldNm, newNm):
    RenameBody=''' <RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ oldNm +'''"</Body>
    </Entities>
    </SupportEntities>
    <NewName Value="'''+ newNm +'''"/>
    <Output/>
    </RenameBody>'''
    simlab.execute(RenameBody)

def _deleteBodyEntities(bodyNm):
    modelNm = simlab.getModelName("FEM")
    DeleteEntity=''' <DeleteEntity CheckBox="ON" UUID="BF2C866D-8983-4477-A3E9-2BBBC0BC6C2E">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNm).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    </DeleteEntity>'''
    simlab.execute(DeleteEntity)
    _updateModel()

def _deleteFaceEntities(modelType, faceIds):
    if isinstance(faceIds,tuple) or isinstance(faceIds,list): faceIds = ",".join(str(v) for v in faceIds)
    else: faceIds = str(faceIds)
    modelNm = simlab.getModelName(modelType)
    DeleteEntity=''' <DeleteEntity UUID="BF2C866D-8983-4477-A3E9-2BBBC0BC6C2E" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ faceIds +''',</Face>
    </Entities>
    </SupportEntities>
    </DeleteEntity>'''
    simlab.execute(DeleteEntity)
    _updateModel()

def _getFaceIdsBetweenEdges(edgeId1, edgeId2):
    adjFaceIds1 = _getFaceIdFromEdge(edgeId1)
    associatedEdgeIds = _getEdgeIDFromFace("FEM",adjFaceIds1)

    count = 0
    while not all([x in associatedEdgeIds for x in edgeId2]):
        if count == 5:return None
        adjFaceIds1 = _selectAdjacentFaces(adjFaceIds1)
        associatedEdgeIds = _getEdgeIDFromFace("FEM",adjFaceIds1)
        count += 1
    
    adjFaceIds2 = _getFaceIdFromEdge(edgeId2)
    associatedEdgeIds = _getEdgeIDFromFace("FEM",adjFaceIds2)
    count = 0    
    while not all([x in associatedEdgeIds for x in edgeId1]):
        if count == 5:return None
        adjFaceIds2 = _selectAdjacentFaces(adjFaceIds2)
        associatedEdgeIds = _getEdgeIDFromFace("FEM",adjFaceIds2)
        count += 1
    
    return tuple(set(adjFaceIds1).intersection(set(adjFaceIds2)))


def _selectAdjacentFaces(faceIds):
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
    <CreateGroup Value="1" Name="Adjacent_Group_96"/>
    </SelectAdjacent>'''
    simlab.execute(SelectAdjacent)

    faceEnts = simlab.getEntityFromGroup("Adjacent_Group_96")
    _deleteGrp("Adjacent_Group_96")

    return faceEnts

def _deleteGrp(grpNm):
    if isinstance(grpNm, tuple) or isinstance(grpNm, list): grpNm = ",".join(grpNm)
    DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +''',"/>
    <Output/>
    </DeleteGroupControl>'''
    simlab.execute(DeleteGroupControl)

# create Bearing from FEM
def _mergeFaces(faceIds):
    modelNm = simlab.getModelName("FEM")
    bodyNm = _getBodyFromFace("FEM", faceIds)
    # bodyFaces_before = _getFaceIdFromBody("FEM", bodyNm)
    MergeFaces=''' <MergeFace UUID="D9D604CE-B512-44e3-984D-DF3E64141F8D">
    <tag Value="-1"/>
    <Name Value="MergeFace3"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ ",".join(str(v) for v in faceIds) +''',</Face>
    </Entities>
    </SupportEntities>
    <MergeBoundaryEdges Value="1"/>
    <SplitBoundaryEdges Value="0"/>
    <SplitEdgesBasedon Value="0"/>
    <FeatureAngle Value="45"/>
    </MergeFace>'''
    simlab.execute(MergeFaces)
    _updateModel()
    bodyFaces_after = _getFaceIdFromBody("FEM", bodyNm)
    return list(set(bodyFaces_after).intersection(set(faceIds)))

def _changeLayersOnCylinderFace(faceEnts, bodyNm, axialElemNum, circularElemNum):
    # print("layers changed",axialElemNum,circularElemNum)
    modelNm = simlab.getModelName("FEM")
    bodyFaces_before = _getFaceIdFromBody("FEM", bodyNm)
    ChangeLayers=''' <ChangeLayers UUID="0480248b-fbe6-4da3-ba06-74147e68e9c0">
    <tag Value="-1"/>
    <Name Value="ChangeLayers7"/>
    <Type Value="1"/>
    <Feature>
    <Faces>
    <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Face>'''+ ",".join(str(v) for v in faceEnts) +''',</Face>
    </Entities>
    </Faces>
    <Axial Value="1"/>
    <AxialNumElements Value="'''+ str(axialElemNum) +'''" Checked="1"/>
    <AxialElemSize Value="5" Checked="0"/>
    <Range Value="0"/>
    <StartNode/>
    <EndNode/>
    <Circular Value="1"/>
    <CircularNumElements Value="'''+ str(circularElemNum) +'''" Checked="1"/>
    <CircularElemSize Value="5" Checked="0"/>
    <PrincipalDirection Value="0"/>
    </Feature>
    <Advanced>
    <ElementEdgeOrEdge Value="1"/>
    <MapLayersFromOneEdgeToAnother Value="0"/>
    <ElementEdgesOrEdges Value=""/>
    <Layers Value="1"/>
    <LayersEdit Value="5"/>
    <MeshSize Value="0"/>
    <MeshSizeEdit Value="5"/>
    <Node Value="0"/>
    <NodeId Value=""/>
    <SrcEdge Value=""/>
    <DesEdge Value=""/>
    <Nodes Value="0"/>
    <SrcEdgeNode Value=""/>
    <DesEdgeNode Value=""/>
    <HexElement Value="0"/>
    <ElementId Value=""/>
    <HorizontalLayers Value="5"/>
    <VerticalLayers Value="3"/>
    </Advanced>
    <Output/>
    </ChangeLayers>'''
    simlab.execute(ChangeLayers)

    bodyFaces_after = _getFaceIdFromBody("FEM", bodyNm)

    faceEnts = list(set(bodyFaces_after)-(set(bodyFaces_before)))
    return faceEnts

def _flipOuterRing(bodyNm):
    faceIds = _getFaceIdFromBody("FEM", bodyNm)
    _reverseNormal(faceIds)
    _updateModel()

def _reverseNormal(faceIds):
    modelNm = simlab.getModelName("FEM")
    ReverseElements=''' <ReverseElements CheckBox="ON" UUID="E3F9157D-2D47-4d2b-9B05-750DBA0735A2" gda="">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ ",".join(str(v) for v in faceIds) +''',</Face>
    </Entities>
    </SupportEntities>
    </ReverseElements>'''
    simlab.execute(ReverseElements)

def _createShellBearing(faceId, numOfBalls, radOfBall, midNode, numElem):
    bodies = simlab.getBodiesWithSubString(simlab.getModelName("FEM"), ["*"])
    if numElem == 0:numElemCheck = 0
    else: numElemCheck = 1
    modelNm = simlab.getModelName("FEM")
    Bearings=''' <Bearing UUID="bbffbf68-fc03-48ee-ac1f-8ed010811b17">
    <Name Value="Bearing8"/>
    <SupportEntities Type="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceId) +''',</Face>
    </Entities>
    </SupportEntities>
    <BearingOption Value="1"/>
    <!-- BearingSpecFile is apllicable for BearingOption = 5 and if file is specified, bearing will be created based on the spec file. Otherwise parameters will be considered. -->
    <BearingSpecFile Value=""/>
    <OneDBearing>
    <NumBalls Value="'''+ str(numOfBalls) +'''"/>
    <BallRadius Value="'''+ str(radOfBall) +'''"/>
    <MidNode Value="'''+ str(midNode) +'''"/>
    <NumElem Check="'''+ str(numElemCheck) +'''" Value="'''+ str(numElem) +'''"/>
    </OneDBearing>
    </Bearing>'''
    simlab.execute(Bearings)
    sl_bearing_body = _getNewCreatedBodyNm("FEM", bodies)
    if sl_bearing_body:
        return sl_bearing_body[0]
    else:
        return None

def _deleteOrphanNodes():
    DeleteOrphanNodes=''' <DeleteOrphanNode UUID="16A3F8AE-EDAB-4988-9006-7FCB3952F161">
    <tag Value="-1"/>
    <Name Value="DeleteOrphanNode3"/>
    <SupportEntities Value="" EntityTypes="" ModelIds=""/>
    <All Value="1"/>
    <Selected Value="0"/>
    <UnSelected Value="0"/>
    </DeleteOrphanNode>'''
    simlab.execute(DeleteOrphanNodes)

def _getNewCreatedBodyNm(modelType, bodiesBefore):
    modelNm = simlab.getModelName(modelType)
    entireBodies = simlab.getBodiesWithSubString(modelNm, ["*"])
    newBodyNm = set(entireBodies) - set(bodiesBefore)
    return tuple(newBodyNm)

def _getVectorBetweenNodes(aNode1, aNode2):
    modelNm = simlab.getModelName("FEM")
    cpt1 = simlab.getNodePositionFromNodeID(modelNm,aNode1)
    cpt2 = simlab.getNodePositionFromNodeID(modelNm,aNode2)

    p1_x, p1_y, p1_z = cpt1
    p2_x, p2_y, p2_z = cpt2
    
    vect_21 = p1_x - p2_x, p1_y - p2_y, p1_z - p2_z

    return vect_21, np.linalg.norm(vect_21)

def _moveNode(nodeId, vect):
    modelNm = simlab.getModelName("FEM")
    px, py, pz = vect
    MoveNodeArbitrary=''' <MoveNodeArbitrary UUID="4A3524D3-E76E-42fe-BDE4-88A2336932EA">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Node>'''+ str(nodeId) +''',</Node>
    </Entities>
    </SupportEntities>
    <X Value="'''+ str(px) +'''"/>
    <Y Value="'''+ str(py) +'''"/>
    <Z Value="'''+ str(pz) +'''"/>
    <LocalCoordinateSystem Value="0"/>
    <UnitVectorMagnitude Value="0"/>
    <Copy Value="0"/>
    </MoveNodeArbitrary>'''
    simlab.execute(MoveNodeArbitrary)

def _alignNodes(outerNodes, innerNodes):
    for node1 in innerNodes:
        temp = {}
        for node2 in outerNodes:
            _, dist = _getVectorBetweenNodes(node1, node2)
            temp[node2] = dist
        minOuterNode, _ = min(temp.items(), key=lambda x: x[1])
        vect,_ = _getVectorBetweenNodes(node1, minOuterNode)
        _moveNode(minOuterNode, vect)


def _getNodeIdsFromBody(bodyNm):
    modelNm = simlab.getModelName("FEM")
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </InputBody>
    <Option Value="Nodes"/>
    <Groupname Value="SelectNodes_12"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)
    nodeEnts = simlab.getEntityFromGroup("SelectNodes_12")
    _deleteGrp("SelectNodes_12")
    return nodeEnts

def _getFaceIdFromBody(modelType, bodyNm):
    modelNm = simlab.getModelName(modelType)
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNm).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </InputBody>
    <Option Value="Faces"/>
    <Groupname Value="associatedFaceGrp"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)

    faceEnts = simlab.getEntityFromGroup("associatedFaceGrp")
    _deleteGrp("associatedFaceGrp")

    return faceEnts

def _getNodeIdFromFace(faceIds):
    modelNm = simlab.getModelName("FEM")
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ ",".join(str(v) for v in faceIds) +''',</Face>
    </Entities>
    </InputFaces>
    <Option Value="Nodes"/>
    <Groupname Value="SelectNodes_12"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)

    nodeEntities = simlab.getEntityFromGroup("SelectNodes_12")
    _deleteGrp("SelectNodes_12")
    return nodeEntities

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
    _updateModel()

def _mergeBodies(bodies, ouputBodyNm):
    modelNm = simlab.getModelName("FEM")
    MergeBodies=''' <BodyMerge gda="" UUID="FA9128EE-5E6C-49af-BADF-4016E5622020">
    <tag Value="-1"/>
    <Name Value="BodyMerge2"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip("()""[]") +'''</Body>
    </Entities>
    </SupportEntities>
    <Delete_Shared_Faces Value="0"/>
    <Output_Body_Name Value="'''+ ouputBodyNm +'''"/>
    <Output/>
    </BodyMerge>'''
    simlab.execute(MergeBodies)
    # print(MergeBodies)
    _updateModel()

def _createEdgeGrps(grpNm, edgeIds):
    modelNm = simlab.getModelName("FEM")
    CreateGroup=''' <CreateGroup UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954" CheckBox="OFF" isObject="4">
    <tag Value="-1"/>
    <Name OldValue="" Value="'''+ grpNm +'''"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Edge>'''+ str(edgeIds).strip("()") +'''</Edge>
    </Entities>
    </SupportEntities>
    <Type Value="Edge"/>
    <Color Value="255,0,255,"/>
    <Dup Value="0"/>
    </CreateGroup>'''
    simlab.execute(CreateGroup)

def drawEdgesByoffset(bodyNm, cset1, cset2, offsetBy):    
    c1, pts1 = cset1
    c2, pts2 = cset2

    c1 = np.array(c1)
    c2 = np.array(c2)

    edgeIdsDrawn = []

    # From 1 --> 2
    v_12 = c2 - c1
    n_12 = v_12 / np.linalg.norm(v_12)

    p1, p2, p3 = pts1

    p1 = p1[0] + n_12[0] * offsetBy, p1[1] + n_12[1] * offsetBy, p1[2] + n_12[2] * offsetBy

    p2 = p2[0] + n_12[0] * offsetBy, p2[1] + n_12[1] * offsetBy, p2[2] + n_12[2] * offsetBy

    p3 = p3[0] + n_12[0] * offsetBy, p3[1] + n_12[1] * offsetBy, p3[2] + n_12[2] * offsetBy

    threePoints = p1, p2, p3
    fourPoints = simlabutil.Convert3PointsOnPlaneTo4Points(threePoints)
    newEdges = _chainEdge(bodyNm, fourPoints)
    edgeIdsDrawn.append(newEdges)

    # From 2 --> 1
    
    v_21 = c1 - c2
    n_21 = v_21 / np.linalg.norm(v_21)

    p1, p2, p3 = pts2

    p1 = p1[0] + n_21[0] * offsetBy, p1[1] + n_21[1] * offsetBy, p1[2] + n_21[2] * offsetBy

    p2 = p2[0] + n_21[0] * offsetBy, p2[1] + n_21[1] * offsetBy, p2[2] + n_21[2] * offsetBy

    p3 = p3[0] + n_21[0] * offsetBy, p3[1] + n_21[1] * offsetBy, p3[2] + n_21[2] * offsetBy

    threePoints = p1, p2, p3
    fourPoints = simlabutil.Convert3PointsOnPlaneTo4Points(threePoints)
    newEdges = _chainEdge(bodyNm, fourPoints)
    edgeIdsDrawn.append(newEdges)

    return edgeIdsDrawn
        

def _getEdgesFromBody(bodyNm):
    modelNm = simlab.getModelName("FEM")
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNm).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </InputBody>
    <Option Value="Edges"/>
    <Groupname Value="SelectEdges_94"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)
    edgeIds = simlab.getEntityFromGroup("SelectEdges_94")
    _deleteGrp("SelectEdges_94")
    return edgeIds

def _chainEdge(bodyNm, pointsOnPlane):
    modelNm = simlab.getModelName("FEM")
    edgeIds_before = _getEdgesFromBody(bodyNm)
    ChainEdges=''' <ChainingEdge UUID="FA9A67DC-4EC7-4056-A0DA-585BBCF33B24" gda="">
    <Name Value="ChainingEdge11"/>
    <tag Value="-1"/>
    <AngleOrPlaneTabFocus Value="1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNm).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    <LimitAngle Checked="0"/>
    <FeatureAngle Value="5"/>
    <WithinFace Value="0"/>
    <CreateEdge Value="1"/>
    <CreateFace Value="0"/>
    <Conflict Value="0"/>
    <ConflictNodeList Value=""/>
    <OutElemEdgeList Value=""/>
    <ShowPreview Clicked="0"/>
    <PlanePoints Value="'''+ ",".join(str(v) for pt in pointsOnPlane for v in pt) +'''"/>
    <BreakEdge Value="0"/>
    <ClosedLoop Value="1"/>
    </ChainingEdge>'''
    simlab.execute(ChainEdges)
    _updateModel()
    edgeIds_after = _getEdgesFromBody(bodyNm)
    return tuple(set(edgeIds_after) - set(edgeIds_before))



def _getEdgeIDFromFace(modelType, faceIds, idsOnly = True):
    if isinstance(faceIds,tuple) or isinstance(faceIds,list): faceEnts = str(faceIds).strip("()""[]")
    else: faceEnts = str(faceIds)
    
    modelNm = simlab.getModelName(modelType)
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ faceEnts +''',</Face>
    </Entities>
    </InputFaces>
    <Option Value="Edges"/>
    <Groupname Value="edgeGrpFromFace"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)
    if idsOnly:
        edgeIds = simlab.getEntityFromGroup("edgeGrpFromFace")
        _deleteGrp("edgeGrpFromFace")
        return edgeIds
    else:
        return "edgeGrpFromFace"

def _springForBearing(springNm, slb1, slb2, axisId, stiffness, constraint):
    modelNm = simlab.getModelName("FEM")

    if constraint == "x":flag = "1"
    elif constraint == "y":flag = "2"
    elif constraint == "z":flag = "4"

    SpringElement=''' <Spring isObject="2" BCType="Spring" CheckBox="ON" UUID="ACA1CCC4-4687-41bd-9BA3-0C602C5B2B7D">
    <tag Value="-1"/>
    <Name Value="'''+ springNm +'''"/>
    <SpringEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ slb1 +'''","'''+ slb2 +'''",</Body>
    </Entities>
    </SpringEntities>
    <ElementID Value="0"/>
    <AxisID Value="'''+ str(axisId) +'''"/>
    <FieldID Value=""/>
    <Type Value="Bodies" Index="3"/>
    <SpringType Value="0"/>
    <PropertyID Value="0"/>
    <TXStiff CheckBox="0" Value="'''+ str(stiffness) +'''"/>
    <TYStiff CheckBox="0" Value="0.0"/>
    <TZStiff CheckBox="0" Value="0.0"/>
    <RXStiff CheckBox="0" Value="0.0"/>
    <RYStiff CheckBox="0" Value="0.0"/>
    <RZStiff CheckBox="0" Value="0.0"/>
    <Flag1 Value="'''+ flag +'''"/>
    <Flag2 Value="'''+ flag +'''"/>
    <GndSpring Value="0"/>
    <FieldData Value="None" Index="0"/>
    </Spring>'''
    simlab.execute(SpringElement)

def _unmergeBody(bodyNm):
    modelNm = simlab.getModelName("FEM")
    UnmergeBody=''' <UnMerge gda="" UUID="B4A72790-34D2-4ac0-9820-84ED4F33E27E">
    <tag Value="-1"/>
    <Name Value="UnMerge1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </SupportEntities>
    <Output/>
    </UnMerge>'''
    simlab.execute(UnmergeBody)

def _getFaceIdFromEdge(edgeIds):
    modelNm = simlab.getModelName("FEM")
    SelectEdgeAssociatedEntities=''' <SelectEdgeAssociatedEntities UUID="551fdd5b-6a8c-4a30-8ab0-fbaf9257343e">
    <InputEdges Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Edge>'''+ ",".join(str(v) for v in edgeIds) +''',</Edge>
    </Entities>
    </InputEdges>
    <Option Value="Faces"/>
    <Groupname Value="SelectFaces_20"/>
    </SelectEdgeAssociatedEntities>'''
    simlab.execute(SelectEdgeAssociatedEntities)

    faceIds = simlab.getEntityFromGroup("SelectFaces_20")
    _deleteGrp("SelectFaces_20")
    return faceIds

def _equivalenceNodes(bodies):
    modelNm = simlab.getModelName("FEM")

    EquivalenceNodes=''' <FemNodeEquivalence UUID="7a5431cd-a2da-4f61-b8ef-9abf3306dd0c">
    <tag Value="-1"/>
    <Name Value="FemNodeEquivalence1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip("()""[]") +'''</Body>
    </Entities>
    </SupportEntities>
    <FaceNodes Value="1"/>
    <EdgeNodes Value="0"/>
    <VertexNodes Value="0"/>
    <RBERadialNodes Value="0"/>
    <SingleBody Value="0"/>
    <RBECenterBarFreeNode Value="0"/>
    <SmallerNodeId Value="1"/>
    <LargerNodeId Value="0"/>
    <ToMidPosition Value="0"/>
    <Tolerance Value="0.1"/>
    <Show Clicked="0" Value=""/>
    <RBECenterOrphanNodeMass Value="0"/>
    <PreserverRbePos Value="1"/>
    <PreserverRbeID Value="1"/>
    <Output/>
    </FemNodeEquivalence>'''
    simlab.execute(EquivalenceNodes)

def _createFacesFromEdges(edge1Entities, edge2Entities, bodyNm, numElemLayers = 4):
    bodyFaces_before = _getFaceIdFromBody("FEM", bodyNm)
    _createFaceFromEdges(edge1Entities, edge2Entities, numElemLayers)
    bodyFaces_after = _getFaceIdFromBody("FEM", bodyNm)
    faceEnts = tuple(set(bodyFaces_after) - set(bodyFaces_before))
    _deleteGrp(simlab.getGroupsWithSubString("EdgeGroup",["edgeGrpFromFace*"]))
    return faceEnts

def _alignCylinder(faceId, cPt, threePoints, rad):
    modelNm = simlab.getModelName("FEM")
    p1,p2,p3 = threePoints
    normV = muratautil.getNormalVector(p1,p2,p3)
    axisP1 = np.array(cPt)
    axisP2 = axisP1 + normV
    AlignCylinder=''' <AlignCylinder CheckBox="ON" UUID="5D271AC4-A0CE-411f-9E60-E7B17CB8B1B7">
    <tag Value="-1"/>
    <Name Value=""/>
    <Entities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceId).strip("()") +'''</Face>
    </Entities>
    </Entities>
    <Axis Point1="'''+ str(list(axisP1)).strip("()""[]") +'''," Point2="'''+ str(list(axisP2)).strip("()[]") +'''" Value="Select"/>
    <Radius Value="'''+ str(rad) +'''"/>
    <ProjectMidNodes Value="1"/>
    <EntityType Value="1"/>
    </AlignCylinder>'''
    simlab.execute(AlignCylinder)
    # print(AlignCylinder)

def createRBEProperty(propNm, propType, bodyNm):

    modelNm = simlab.getModelName("FEM")
    propId = propertyutil.getPropertyID()
    # Rbe3
    AnalysisProperty=''' <Property UUID="FAABD80A-7FA2-4d2a-961B-BFA06A361A4C">
    <tag Value="-1"/>
    <Name Value="'''+ propNm +'''"/>
    <Dimension Value="RigidBar"/>
    <Type Value="'''+ propType +'''"/>
    <ID Value="'''+ str(propId) +'''"/>
    <Material Value="None"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </SupportEntities>
    <UseExistingPropertyCheck Value="0"/>
    <CoordSystem Value="3"/>
    <TableData>
    <DOF Type="1" Value="123456"/>
    <Weight Type="4" Value="1.0"/>
    <Abaqus_Element_Type Type="3" Value="0"/>
    <OptiStruct_Independent_Nodes_DOF Type="1" Value="123" table=""/>
    </TableData>
    <Composite/>
    </Property>'''
    simlab.execute(AnalysisProperty)

def _getNodeIdsFromEdgeId(edgeId):
    modelNm = simlab.getModelName("FEM")
    SelectEdgeAssociatedEntities=''' <SelectEdgeAssociatedEntities UUID="551fdd5b-6a8c-4a30-8ab0-fbaf9257343e">
    <InputEdges Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Edge>'''+ str(edgeId) +''',</Edge>
    </Entities>
    </InputEdges>
    <Option Value="Nodes"/>
    <Groupname Value="SelectNodes_74"/>
    </SelectEdgeAssociatedEntities>'''
    simlab.execute(SelectEdgeAssociatedEntities)
    nodeIds = simlab.getEntityFromGroup("SelectNodes_74")
    _deleteGrp("SelectNodes_74")
    return nodeIds

def _getNodePointsOfEdge(edgeIds, numPoints):
    modelNm = simlab.getModelName("FEM")
    edgeIds = list(edgeIds)
    nodeIds = []

    for thisEdge in edgeIds:
        nodes = list(_getNodeIdsFromEdgeId(thisEdge))
        nodeIds.extend(nodes)
    nodeIds = list(set(nodeIds))
    nodeIds = random.sample(nodeIds, k=numPoints)

    p1 = simlab.getNodePositionFromNodeID(modelNm, nodeIds[0])
    p2 = simlab.getNodePositionFromNodeID(modelNm, nodeIds[1])
    p3 = simlab.getNodePositionFromNodeID(modelNm, nodeIds[2])
    return p1,p2,p3    

def _createContactFaceForBearing(edge1, edge2, elementProp, flipFace = False, bearingType = "shell"):
    NUM_ELEMENTS_ON_AXIAL, NUM_ELEMENTS_ON_CIRCULAR = elementProp
    bodyNmOnEdge = _getBodyFromEdges(edge1)
    arcAtt1 = muratautil.getArcAttribute(edge1[0])
    points1 = _getNodePointsOfEdge(edge1,3)
    cPt1, Rad1= arcAtt1
    # print("cPt1", cPt1)

    arcAtt2 = muratautil.getArcAttribute(edge2[0])
    points2 = _getNodePointsOfEdge(edge2,3)
    cPt2, Rad2= arcAtt2
    # print("cPt2", cPt2)
    
    width = np.linalg.norm(np.array(cPt1)-np.array(cPt2))
    faceEnts = _getFaceIdsBetweenEdges(edge1, edge2)
    if not faceEnts:
        messagebox.showinfo("情報", "Fail to create new outer faces from edges") 
        return False
    # print("faceEntsTodelete",faceEnts)
    _deleteFaceEntities("FEM", faceEnts)
    newFaceEnts = _createFacesFromEdges(edge1, edge2, bodyNmOnEdge ,NUM_ELEMENTS_ON_AXIAL)

    minRad = min(Rad1, Rad2)
    # print("newFaceEnts", newFaceEnts)
    
    
    _alignCylinder(newFaceEnts, cPt1, points1, minRad)

    newFaceEnts = _changeLayersOnCylinderFace(newFaceEnts, bodyNmOnEdge, axialElemNum=NUM_ELEMENTS_ON_AXIAL, circularElemNum= NUM_ELEMENTS_ON_CIRCULAR)
    if not newFaceEnts:
        messagebox.showinfo("情報", "Change-layers for the cylindrial faces failed")
        return False

    if bearingType == "solid":
        return bodyNmOnEdge, newFaceEnts, minRad

    newFaceEnts = _mergeFaces(newFaceEnts)
    createdBodyNm = _createBodyFromFaces(newFaceEnts)

    if flipFace:
        _flipOuterRing(createdBodyNm)
    _modifyToQuadElems(createdBodyNm)
    _deleteOrphanNodes()
    # print("createdBodyNm", createdBodyNm)
    newEdges = drawEdgesByoffset(createdBodyNm, (cPt1, points1), (cPt2, points2), offsetBy = width/NUM_ELEMENTS_ON_AXIAL)
    # print("newEdges", newEdges)
    # raise("0")
    if not newEdges:
        messagebox.showinfo("情報","Fail to draw edges by offset")
        return False

    contactFace = _getFaceIdsBetweenEdges(newEdges[0], newEdges[1])
    return bodyNmOnEdge, contactFace, minRad

def createShellBearing(outputBodyNm, innerEdgeGrps, outerEdgeGrps, coordId, elementProp, springProp):
    _deleteBodyEntities(outputBodyNm)
    outputBodyNm = str(outputBodyNm).strip("()"",""'")
    innerEdgeGrps = simlab.createGroupsOfConnectedEntities(innerEdgeGrps)
    if len(innerEdgeGrps) != 2:
        messagebox.showinfo("情報", "re-select innerEdges")
        return
    innerEdgeGrp1, innerEdgeGrp2 = innerEdgeGrps
    innerEdge1 = simlab.getEntityFromGroup(innerEdgeGrp1)
    innerEdge2 = simlab.getEntityFromGroup(innerEdgeGrp2)
    innerResult = _createContactFaceForBearing(innerEdge1, innerEdge2, elementProp, flipFace = False)
    if not innerResult:
        return
    outerBody, innerFace, innerRad = innerResult

    outerEdgeGrps = simlab.createGroupsOfConnectedEntities(outerEdgeGrps)
    if len(outerEdgeGrps) != 2:
        messagebox.showinfo("情報", "re-select innerEdges")
        return
    outerEdgeGrp1, outerEdgeGrp2 = outerEdgeGrps
    outerEdge1 = simlab.getEntityFromGroup(outerEdgeGrp1)
    outerEdge2 = simlab.getEntityFromGroup(outerEdgeGrp2)
    outerResult = _createContactFaceForBearing(outerEdge1, outerEdge2, elementProp, flipFace = True)
    if not outerResult:
        return
    innerBody, outerFace, outerRad = outerResult
    # print(innerResult)
    # print(outerResult)
    dist = outerRad - innerRad
    # print("innerFace", innerFace)
    # print("outerFace", outerFace)
    # print("dist", dist)
    # print("coordId", coordId)
    # print("springProp", springProp)
    # raise("1")
    create1dbearing(innerFace, outerFace, dist, coordId, springProp, outputBodyNm=outputBodyNm)
    importlib.reload(assemStructure)
    modelNm = simlab.getModelName("FEM")
    subModels = simlab.getChildrenInAssembly(modelNm, modelNm,"SUBASSEMBLIES")
    if SPINDLE_ASSY in subModels:
        assemStructure.moveBodiesToSubModel("FEM", outputBodyNm, SPINDLE_ASSY)
    _equivalenceNodes(tuple([outputBodyNm]) + outerBody)
    _equivalenceNodes(tuple([outputBodyNm]) + innerBody)

def associatedBodies(faceIds):
    modelNm = simlab.getModelName("FEM")
    bodyGroupName = "SelectBodies_51"
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceIds).strip("()") +'''</Face>
    </Entities>
    </InputFaces>
    <Option Value="Bodies"/>
    <Groupname Value="'''+ bodyGroupName +'''"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)
    bodyNm = simlab.getBodiesFromGroup(bodyGroupName)
    _deleteGrp(bodyGroupName)
    return bodyNm

def create1dbearing(innerFaceIds, outerFaceIds, distance, coordId, springProp, bearingType = "shell", outputBodyNm = SHELL_BEARING):
    springNm, numOfBallBearing, dof = springProp
    stiff_R, stiff_T, stiff_z = dof

    if len(innerFaceIds) > 1:
        mergedInnerFaceId = _mergeFaces(innerFaceIds)
    else:
        mergedInnerFaceId = innerFaceIds

    if len(outerFaceIds) > 1:
        mergedOuterFaceId = _mergeFaces(outerFaceIds)
    else:
        mergedOuterFaceId = outerFaceIds
    
    if not mergedInnerFaceId or not mergedOuterFaceId:
        return None
    
    if bearingType == "shell":
        bodies = associatedBodies(innerFaceIds+outerFaceIds)
        _mergeBodies(bodies, ouputBodyNm = "mergedBody")

    slb_inner = _createShellBearing(faceId = mergedInnerFaceId[0], 
                                    numOfBalls = numOfBallBearing,
                                    radOfBall = distance/2,
                                    midNode = 0,
                                    numElem = 0)
    innerNodes = list(set(_getNodeIdsFromBody(slb_inner)) - set(_getNodeIdFromFace(mergedInnerFaceId)))
    slb_outer = _createShellBearing(faceId = mergedOuterFaceId[0], 
                                    numOfBalls = numOfBallBearing,
                                    radOfBall = distance/2,
                                    midNode = 0,
                                    numElem = 0)
    outerNodes = list(set(_getNodeIdsFromBody(slb_outer)) - set(_getNodeIdFromFace(mergedOuterFaceId)))
    _alignNodes(outerNodes, innerNodes)
    springId = muratautil.getUniqueId(MAX_ID_SPRING)
    springNm = springNm + str(springId)
    # Spring creation for bearing
    if stiff_R != 0.0 : _springForBearing(springNm+"_R", slb_inner, slb_outer, coordId, stiff_R, "x")
    if stiff_T != 0.0 : _springForBearing(springNm+"_T", slb_inner, slb_outer, coordId, stiff_T, "y")
    if stiff_z != 0.0 : _springForBearing(springNm+"_Z", slb_inner, slb_outer, coordId, stiff_z, "z")

    bodiesToMerge = (slb_inner, slb_outer)

    mergedSlb = bodiesToMerge[0]
    _mergeBodies(bodiesToMerge, mergedSlb)

    if bearingType == "shell":
        # shellId = muratautil.getUniqueId(SHELL_BEARING)
        # outputBodyNm = "{}_{}".format(outputNm, shellId)
        _renameBody(simlab.getModelName("FEM"), "mergedBody", outputBodyNm)
        # return outputBodyNm

def createSolidBearing(innerEdgeGrps, outerEdgeGrps, coordId, elementProp, springProp):
    innerEdgeGrps = simlab.createGroupsOfConnectedEntities(innerEdgeGrps)
    if len(innerEdgeGrps) != 2:
        messagebox.showinfo("情報", "re-select innerEdges")
        return
    innerEdgeGrp1, innerEdgeGrp2 = innerEdgeGrps
    innerEdge1 = simlab.getEntityFromGroup(innerEdgeGrp1)
    innerEdge2 = simlab.getEntityFromGroup(innerEdgeGrp2)
    innerResult = _createContactFaceForBearing(innerEdge1, innerEdge2, elementProp, bearingType="solid")
    if not innerResult:
        return
    _, innerFaceEnts, innerRad = innerResult

    # print("innerFaceEnts", innerFaceEnts)
    # print("innerRad", innerRad)

    outerEdgeGrps = simlab.createGroupsOfConnectedEntities(outerEdgeGrps)
    if len(outerEdgeGrps) != 2:
        messagebox.showinfo("情報", "re-select outerEdges")
        return
    outerEdgeGrp1, outerEdgeGrp2 = outerEdgeGrps
    outerEdge1 = simlab.getEntityFromGroup(outerEdgeGrp1)
    outerEdge2 = simlab.getEntityFromGroup(outerEdgeGrp2)
    outerResult = _createContactFaceForBearing(outerEdge1, outerEdge2, elementProp, bearingType="solid")
    if not outerResult:
        return
    _, outerFaceEnts, outerRad = outerResult
    dist = outerRad - innerRad
    # print("outerFaceEnts", outerFaceEnts)
    # print("outerRad", outerRad)

    create1dbearing(innerFaceEnts, outerFaceEnts, dist, coordId, springProp, bearingType="solid")