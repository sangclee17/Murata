from hwx import simlab
import tkinter.messagebox as messagebox
import numpy as np
import mpcutil
import math
import muratautil
import importlib
import simlabutil
import simlablib
import grouputil
import assemStructure

DEFAULT_MESH_SIZE = "DefaultMeshSize"
DEFAULT_MAX_ANGLE = "DefaultMaxAngle"
DEFAULT_ASPECT_RATIO = "DefaultAspectRatio"
LINEARGUIDE_ASSY = "LINEAR_GUIDE_ASSY"


def getEquidistantNodePositionsBetween(node1, node2, num):
    modelNm = simlab.getModelName("FEM")
    p1 = np.array(simlab.getNodePositionFromNodeID(modelNm, node1))
    p2 = np.array(simlab.getNodePositionFromNodeID(modelNm, node2))

    distance = np.linalg.norm(p1-p2)
    direc_12 = (p2 - p1)/distance

    nodePoints = []
    for i in range(num):
        if i+1 != num:
            aPt = p1 + direc_12 * (distance / num * (i+1))
            nodePoints.append(aPt)
    return nodePoints

def getNodePositionAwayFrom(aNodePosition, direc, dist):
    '''
        aNodePosition : np(x,y,z)
        direc : normal direction
    '''
    return list(np.array(aNodePosition) + direc * dist)
    

def getBoxCoordinates(node1, node2, node3 , node4, num = 2):
    modelNm = simlab.getModelName("FEM")
    boxCoord = {}
    p1 = np.array(simlab.getNodePositionFromNodeID(modelNm, node1))
    p2 = np.array(simlab.getNodePositionFromNodeID(modelNm, node2))
    p3 = np.array(simlab.getNodePositionFromNodeID(modelNm, node3))
    p4 = np.array(simlab.getNodePositionFromNodeID(modelNm, node4))

    # hardPoints = []

    width = np.linalg.norm(p2 - p3)
    length = np.linalg.norm(p1 - p4)
    direc23 = (p3 - p2) / width
    direc14 = (p4 - p1) / length

    p8 = getNodePositionAwayFrom(p2, direc14, length)
    # print("p8", p8)
    # for i in range(num):
    #     if i+1 != num:
    #         aPt = getNodePositionAwayFrom(p1, direc14, length / num * (i+1))
    #         bPt = getNodePositionAwayFrom(p2, direc14, length / num * (i+1))
    #         hardPoints.append(list(aPt))
    #         hardPoints.append(list(bPt))
    p9 = getNodePositionAwayFrom(p1, direc14, length / 2)
    p10 = getNodePositionAwayFrom(p2, direc14, length / 2)

    p5 = getNodePositionAwayFrom(p1, direc23, width)

    # for i in range(num):
    #     if i+1 != num:
    #         aPt = getNodePositionAwayFrom(p5, direc14, length / num * (i+1))
    #         bPt = getNodePositionAwayFrom(p3, direc14, length / num * (i+1))
    #         hardPoints.append(list(aPt))
    #         hardPoints.append(list(bPt))
    p11 = getNodePositionAwayFrom(p5, direc14, length / 2)
    p12 = getNodePositionAwayFrom(p3, direc14, length / 2)

    p6 = getNodePositionAwayFrom(p5, direc14, length)
    p7 = getNodePositionAwayFrom(p3, direc14, length)

    boxCoord["p1"] = list(p1)
    boxCoord["p2"] = list(p2)
    boxCoord["p2"] = list(p2)
    boxCoord["p3"] = list(p3)
    boxCoord["p4"] = list(p4)
    boxCoord["p5"] = list(p5)
    boxCoord["p6"] = list(p6)
    boxCoord["p7"] = list(p7)
    boxCoord["p8"] = list(p8)
    boxCoord["p9"] = list(p9)
    boxCoord["p10"] = list(p10)
    boxCoord["p11"] = list(p11)
    boxCoord["p12"] = list(p12)
    return boxCoord

def _deleteGrp(grpNm):
    if isinstance(grpNm, tuple) or isinstance(grpNm, list): grpNm = ",".join(grpNm)
    DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +''',"/>
    <Output/>
    </DeleteGroupControl>'''
    simlab.execute(DeleteGroupControl)
    
def getFaceIdFromPlane(bodyNm, planeData):
    dataPointsString = ",".join(str(pt).strip("[]""()") for pt in planeData)
    # print("planeData",dataPointsString)
    modelNm = simlab.getModelName("FEM")
    groupName = "Show_Faces"
    _deleteGrp(groupName)
    FacesByPlane=''' <FacesByPlane UUID="116fb6e7-2d86-45fb-bbee-bd40e654a0bf">
    <Name Value="Show Faces"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNm).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    <Option Value="3"/>
    <RegionData Type="Plane">
    <PlaneData Value="'''+ dataPointsString +'''"/>
    </RegionData>
    <On Value="1"/>
    <Above Value="0"/>
    <Below Value="0"/>
    <Tolerance Value="1"/>
    <CreateGroup Value="1"/>
    </FacesByPlane>'''
    simlab.execute(FacesByPlane)
    # print(FacesByPlane)

    faceId = simlab.simlab.getEntityFromGroup(groupName)
    _deleteGrp(groupName)
    return faceId

def getEdgeIdFromFaceGrp(faceGrp):
    modelNm = simlab.getModelName("FEM")
    faces = simlab.getEntityFromGroup(faceGrp)
    groupNm = "SelectEdges_2"
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faces).strip("()") +'''</Face>
    </Entities>
    </InputFaces>
    <Option Value="Edges"/>
    <Groupname Value="'''+ groupNm +'''"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)
    edgeIds = simlab.getEntityFromGroup(groupNm)
    _deleteGrp(groupNm)
    _deleteGrp(faceGrp)
    return edgeIds

def createHardPointsMC(mcName, faceId, dataPoints):
    deleteMC(mcName)
    dataPoints = ",".join(str(pt).strip("[]""()") for pt in dataPoints)
    modelNm = simlab.getModelName("FEM")
    MeshControls=''' <MeshControl UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1" CheckBox="ON">
    <tag Value="-1"/>
    <MeshControlName Value="'''+ mcName +'''"/>
    <MeshControlType Value="Hard Points"/>
    <Entities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceId).strip("()") +'''</Face>
    </Entities>
    </Entities>
    <Reverse EntityTypes="" Value="" ModelIds=""/>
    <MeshColor Value=""/>
    <HardPoints>
    <Geometry Value="2"/>
    <Tolerance Value="0.01"/>
    <DataPoints Value="'''+ dataPoints +'''"/>
    <!-- To specify the csv file path , please uncomment out the below line.   -->
    <!--
    <Hard_Points_File Value="D:/Testing/HardPoints.csv" /> 
            -->
    </HardPoints>
    </MeshControl>'''
    simlab.execute(MeshControls)
    # print(MeshControls)

def deleteMC(mcName):
    DeleteMeshControl=''' <DeleteMeshControl UUID="c801afc7-a3eb-4dec-8bc1-8ac6382d4c6e" CheckBox="ON">
    <Name Value="'''+ mcName +'''"/>
    </DeleteMeshControl>'''
    simlab.execute(DeleteMeshControl)

def re_meshFace(faceId):
    avgElemSize = muratautil.getParameter(DEFAULT_MESH_SIZE, "double")
    maxAngle = muratautil.getParameter(DEFAULT_MAX_ANGLE, "double")
    aspectRatio = muratautil.getParameter(DEFAULT_ASPECT_RATIO, "double")
    if not avgElemSize or not maxAngle or not aspectRatio:
        avgElemSize = 20
        maxAngle = 45
        aspectRatio = 10

    modelNm = simlab.getModelName("FEM")
    LocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh8"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceId).strip("()") +'''</Face>
    </Entities>
    </SupportEntities>
    <ElemType Value="1"/>
    <AverageElemSize Value="'''+ str(avgElemSize) +'''"/>
    <MinElemSize Value="'''+ str(avgElemSize/aspectRatio) +'''"/>
    <PreserveBoundaryEdges Value="0"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="'''+ str(maxAngle) +'''"/>
    <CurvatureMinElemSize Value="'''+ str(avgElemSize/2) +'''"/>
    <AspectRatio Value="'''+ str(aspectRatio) +'''"/>
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

def edgeReMesh(edges):
    avgElemSize = muratautil.getParameter(DEFAULT_MESH_SIZE, "double")
    maxAngle = muratautil.getParameter(DEFAULT_MAX_ANGLE, "double")
    aspectRatio = muratautil.getParameter(DEFAULT_ASPECT_RATIO, "double")
    if not avgElemSize or not maxAngle or not aspectRatio:
        avgElemSize = 20
        maxAngle = 45
        aspectRatio = 10

    modelNm = simlab.getModelName("FEM")
    LocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh2"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Edge>'''+ str(edges).strip("()") +'''</Edge>
    </Entities>
    </SupportEntities>
    <ElemType Value="1"/>
    <AverageElemSize Value="'''+ str(avgElemSize) +'''"/>
    <MinElemSize Value="'''+ str(avgElemSize/aspectRatio) +'''"/>
    <PreserveBoundaryEdges Value="1"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="'''+ str(maxAngle) +'''"/>
    <CurvatureMinElemSize Value="'''+ str(avgElemSize/2) +'''"/>
    <AspectRatio Value="'''+ str(aspectRatio) +'''"/>
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

def getNodesInSphere(bodyNm,centerCoord):
    modelNm = simlab.getModelName("FEM")
    groupName = "Show_Nodes"
    _deleteGrp(groupName)
    counter = 1
    radius = 1
    while not simlab.simlab.isGroupPresent(groupName):
        if counter == 10:
            break
        NodesByRegion=''' <NodesByRegion UUID="ad9db725-dcb3-4f9c-abd7-0e7a8cf64d05">
        <tag Value="-1"/>
        <Name Value="Show Nodes"/>
        <SupportEntities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Body>'''+ str(bodyNm).replace("'",'"').strip("()""[]") +'''</Body>
        </Entities>
        </SupportEntities>
        <Option Value="0"/>
        <RegionData Type="Sphere">
        <SphereData>
        <SphereCenter Value="'''+ str(centerCoord).strip("()""[]") +'''"/>
        <Radius Value="'''+ str(radius) +'''"/>
        </SphereData>
        </RegionData>
        <On Value="0"/>
        <Above Value="0"/>
        <Below Value="1"/>
        <Tolerance Value="0.102874"/>
        <MaximumCount Value="5000"/>
        <ShowSurfaceNodes Value="1"/>
        <CreateGroup Value="1"/>
        </NodesByRegion>'''
        simlab.execute(NodesByRegion)
        radius += 0.5
        counter += 1

    nodeIds = simlab.getEntityFromGroup(groupName)
    if len(nodeIds)>1:
        nodeIds = tuple(nodeIds[0])
    return nodeIds

def connectTwoNodesInSpring(springNm, nodeIds, axisID, stiffness, constraint = "x"):
    modelNm = simlab.getModelName("FEM")
    if constraint == "x":flag = "1"
    elif constraint == "y":flag = "2"
    elif constraint == "z":flag = "4"
    SpringElement=''' <Spring CheckBox="ON" UUID="ACA1CCC4-4687-41bd-9BA3-0C602C5B2B7D" BCType="Spring" isObject="2">
    <tag Value="-1"/>
    <Name Value="'''+ springNm +'''"/>
    <SpringEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Node>'''+ str(nodeIds).strip("()") +'''</Node>
    </Entities>
    </SpringEntities>
    <ElementID Value="0"/>
    <AxisID Value="'''+ str(axisID) +'''"/>
    <FieldID Value=""/>
    <Type Value="Nodes" Index="0"/>
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
    # print(SpringElement)

def modifyElemToTri6(bodyNm):
    modelNm = simlab.getModelName("FEM")
    ModifyElements=''' <Modify UUID="28706164-e6e5-4544-b4a9-c052c4b6c60f" CheckBox="ON">
    <Name Value=""/>
    <tag Value="-1"/>
    <Option Value="TOHIGHER"/>
    <QuadDominant Value="1"/>
    <Entity>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNm).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </Entity>
    <IdealQuad Value="0"/>
    <UpdateAssociateRBENodes Value="1"/>
    </Modify>'''
    simlab.execute(ModifyElements)

def createBlock(centerPt, x_lenth, y_length, z_length):
    modelNm = simlab.getModelName("FEM")
    bodiesBefore = simlab.getBodiesWithSubString(modelNm,["*"])
    defaultMeshSize = muratautil.getParameter(DEFAULT_MESH_SIZE, "double")
    if not defaultMeshSize:
        defaultMeshSize = 20
    xNodesNum = int(x_lenth//defaultMeshSize) + 1
    # print("xNodesNum", xNodesNum)
    yNodesNum = int(y_length//defaultMeshSize) + 1
    # print("yNodesNum", yNodesNum)
    zNodesNum = int(z_length//defaultMeshSize) + 1
    # print("zNodesNum", zNodesNum)
    
    CreateBlock=''' <FEABlock UUID="B219E9B4-B76A-410d-8BF7-C83FC40651FC">
    <Name Value="FEABlock1"/>
    <tag Value="-1"/>
    <x_length Value="'''+ str(x_lenth) +'''"/>
    <y_length Value="'''+ str(y_length) +'''"/>
    <z_length Value="'''+ str(z_length) +'''"/>
    <x_no.ofNodes Value="'''+ str(xNodesNum)  +'''"/>
    <y_no.ofNodes Value="'''+ str(yNodesNum) +'''"/>
    <z_no.ofNodes Value="'''+ str(zNodesNum) +'''"/>
    <Origin Value="'''+ str(centerPt).strip("()""[]") +'''"/>
    <CoodinateOption Value="Center"/>
    <ElementType Value="Tri3"/>
    <ParentModelChecked Value="1"/>
    <ModelNameIndex Value="0"/>
    <Output/>
    </FEABlock>'''
    simlab.execute(CreateBlock)
    # print(CreateBlock)
    bodiesAfter = simlab.getBodiesWithSubString(modelNm, ["*"])
    newBody = tuple(set(bodiesAfter)-set(bodiesBefore))
    return newBody

def getBodyFromFace(faceIds):
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
    _deleteGrp("SelectBodies_4")
    return bodyNm

def deleteBodyEntities(bodyNm):
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

def _updateModel():
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def normalDirection(pts):
    p1,p2,p3 = pts
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)

    v1 = (p3 - p1) / np.linalg.norm(p3 - p1)
    v2 = (p2 - p1) / np.linalg.norm(p2 - p1)
    cp = np.cross(v1,v2)

    return cp / np.linalg.norm(cp)

def equationOfPlane(pts):
    '''
       return ax + by + cz + d = 0 
    '''
    _, _, p3 = pts
    p3 = np.array(p3)
    cp = normalDirection(pts)
    a, b, c = cp

    d = - np.dot(cp, p3)

    return (a, b, c, d)

def distanceBetweenPointAndPlane(planePts, aPoint):
    a,b,c,d  = equationOfPlane(planePts)
    x1, y1, z1 = aPoint 

    return abs(a*x1+b*y1+c*z1+d) / math.sqrt(math.pow(a,2)+math.pow(b,2)+math.pow(c,2))

def planeTranslation(plane, d_n):
    '''
        tranlate by d_n in the opposite direction of normal
    '''
    # a, b, c, d = equationOfPlane(pts)
    a, b, c, d = plane
    return a, b, c, d-d_n

def planeIntersect(plane1, plane2, plane3):
    '''
        turple (a,b,c,d)
        ax + by + cz + d = 0 
        a,b,c,d in order

        return the coordinate of the intersecting point
    '''
    a_vec, b_vec, c_vec = np.array(plane1[:3]), np.array(plane2[:3]), np.array(plane3[:3])

    A = np.array([a_vec, b_vec, c_vec])
    d = np.array([-plane1[-1], -plane2[-1], -plane3[-1]]).reshape(3,1)

    if np.linalg.det(A) == 0 :
        messagebox.showinfo("情報","Zero det. Can't compute inver mat")
        return

    p_inter = np.linalg.solve(A, d).T
    return list(p_inter[0])

def rotationMatrixToEulerAngles(R) :

    # assert(isRotationMatrix(R))
    
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
    
    singular = sy < 1e-6

    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0

    return np.array([math.degrees(x), math.degrees(y), math.degrees(z)])

def sameDirection(norm1, norm2):
    norm1 = np.array(norm1)
    norm2 = np.array(norm2)
    dotProd = np.dot(norm1, norm2)
    # print(dotProd)
    return abs(dotProd - 1.0) < 1e-6

def chooseZpoints(zAxis, ptsA, ptsB):
    p1_la, p2_la, p3_la = ptsA
    p1_lb, p2_lb, p3_lb = ptsB
    lnorm = normalDirection((p1_la, p2_la, p3_la))
    if sameDirection(zAxis, lnorm):
        return (p1_la, p2_la, p3_la)
    else:
        return (p1_lb, p2_lb, p3_lb)

def rotateBody(bodyNm, centerPt, rotationAxis, angleInDeg):
    modelNm = simlab.getModelName("FEM")
    Transform=''' <Transform UUID="604b2194-5dd2-4701-beb2-6784d03c5535">
    <Operation Value="Rotate"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNm).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    <Center Value="'''+ str(centerPt).strip("()""[]") +'''"/>
    <RotationAxis Value="'''+ str(rotationAxis).strip("()""[]") +'''"/>
    <Angle Value="'''+ str(angleInDeg) +'''"/>
    </Transform>'''
    simlab.execute(Transform)
    # print(Transform)

def _renameBody(modelNm, oldNm, newNm):    
    RenameBody=''' <RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(oldNm).replace("'",'"').strip("()""[]") +'''</Body>
    </Entities>
    </SupportEntities>
    <NewName Value='''+ str(newNm).replace("'",'"').strip("()""[]"",") +'''/>
    <Output/>
    </RenameBody>'''
    simlab.execute(RenameBody)

def _deleteOrphanNodes():
    DeleteOrphanNodes=''' <DeleteOrphanNode UUID="16A3F8AE-EDAB-4988-9006-7FCB3952F161">
    <tag Value="-1"/>
    <Name Value="DeleteOrphanNode2"/>
    <SupportEntities EntityTypes="" Value="" ModelIds=""/>
    <All Value="1"/>
    <Selected Value="0"/>
    <UnSelected Value="0"/>
    </DeleteOrphanNode>'''
    simlab.execute(DeleteOrphanNodes)

def assemblyNameAssociatedWithBodyName(bodyNm):
    modelNm = simlab.getModelName("FEM")
    bodyNm = str(bodyNm).strip("()"",""'")
    # print("bodyNm",bodyNm)
    subAssems = simlab.getChildrenInAssembly(modelNm, modelNm, "SUBASSEMBLIES")
    # print("subAssems",subAssems)
    if not subAssems:
        return None
    
    for thisSub in subAssems:
        bodies = simlab.getChildrenInAssembly(modelNm, thisSub, "BODIES")
        # print("bodies",bodies)
        if bodyNm in bodies:
            return thisSub
    
    return None

def createRail(heighFaceGrp, widthFaceGrp, lengthFaceGrp):
    hFace_A, hFace_B = simlab.getEntityFromGroup(heighFaceGrp) # height
    wFace_A, wFace_B = simlab.getEntityFromGroup(widthFaceGrp) # width
    lFace_A, lFace_B = simlab.getEntityFromGroup(lengthFaceGrp) # length
    
    modelNm = simlab.getModelName("FEM")
    p1_wa, p2_wa, p3_wa = simlab.definePlaneFromEntity(modelNm, wFace_A)
    p1_wb, _, _ = simlab.definePlaneFromEntity(modelNm, wFace_B)
    width = distanceBetweenPointAndPlane((p1_wa, p2_wa, p3_wa), p1_wb)
    # print("width", width)
    wnorm = normalDirection((p1_wa, p2_wa, p3_wa))
    # print("wnorm", wnorm)
    wPlane = equationOfPlane((p1_wa, p2_wa, p3_wa))
    # print("wPlane", wPlane)
    midWPlane = planeTranslation(wPlane, width / 2)
    # print("midWPlane", midWPlane)

    p1_ha, p2_ha, p3_ha = simlab.definePlaneFromEntity(modelNm, hFace_A)
    p1_hb, _, _ = simlab.definePlaneFromEntity(modelNm, hFace_B)
    height = distanceBetweenPointAndPlane((p1_ha, p2_ha, p3_ha), p1_hb)
    # print("height", height)
    hnorm = normalDirection((p1_ha, p2_ha, p3_ha))
    # print("hnorm", hnorm)
    hPlane = equationOfPlane((p1_ha, p2_ha, p3_ha))
    # print("hPlane",hPlane)
    midHPlane = planeTranslation(hPlane, height / 2)
    # print("midHPlane", midHPlane)

    p1_la, p2_la, p3_la = simlab.definePlaneFromEntity(modelNm, lFace_A)
    p1_lb, p2_lb, p3_lb = simlab.definePlaneFromEntity(modelNm, lFace_B)
    length = distanceBetweenPointAndPlane((p1_la, p2_la, p3_la), p1_lb)
    # print("length", length)
    lnorm = np.cross(wnorm, hnorm)
    # print("lnorm",lnorm)
    positiveZpts = chooseZpoints(lnorm, (p1_la, p2_la, p3_la),(p1_lb, p2_lb, p3_lb))
    lPlane = equationOfPlane(positiveZpts)
    # print("lplane",lPlane)
    midLPlane = planeTranslation(lPlane, length / 2)
    # print("midLplane", midLPlane)

    blockC = planeIntersect(midLPlane, midWPlane, midHPlane)
    blockBody = createBlock(blockC, width, height, length)
    modifyElemToTri6(blockBody)
    # print("blockC", blockC)
    R = np.array([wnorm, hnorm, lnorm]).T
    # print("R", R)
    eulerAngle = rotationMatrixToEulerAngles(R)
    # print("eulerAngle",eulerAngle)
    R = np.array(R)
    # print("R_x", R[:,0])
    # print("R_y", R[:,1])
    # print("R_z", R[:,2])
    rot = ((list(R[:,0]),eulerAngle[0]), (list(R[:,1]),eulerAngle[1]), (list(R[:,2]),eulerAngle[2]))
    # print(rot)
    for rotEach in rot:
        rotationAxis, angleInDeg = rotEach
        rotateBody(blockBody, blockC, rotationAxis, angleInDeg)
    
    bodyNm = getBodyFromFace(hFace_A)
    subAssemNm = assemblyNameAssociatedWithBodyName(bodyNm)
    deleteBodyEntities(bodyNm)
    _renameBody(modelNm, blockBody, bodyNm)
    # print("bodyNmOrig", bodyNm)
    # print("blockNm", blockBody)
    # print("subAssemNm",subAssemNm)
    if subAssemNm:
        assemStructure.moveBodiesToSubModel("FEM", bodyNm, subAssemNm)

    # subModels = simlab.getChildrenInAssembly(modelNm, modelNm,"SUBASSEMBLIES")
    # if LINEARGUIDE_ASSY in subModels:
    #     assemStructure.moveBodiesToSubModel("FEM", bodyNm, LINEARGUIDE_ASSY)
    # else:
    #     assemStructure.createSubModel("FEM", LINEARGUIDE_ASSY)
    #     assemStructure.moveBodiesToSubModel("FEM", bodyNm, LINEARGUIDE_ASSY)

def createSpring(nodeGrps, bodyGrps, springstiff, CID):
    nodeGrp1, nodeGrp2, nodeGrp3, nodeGrp4 = nodeGrps
    sliderGrp, railGrp = bodyGrps
    # sliderGrp, railGrp = "_springBlockBody","_springRailBody"
    sx, sy, sz = springstiff
    node1 = int(str(simlab.getEntityFromGroup(nodeGrp1)).strip("()"","))
    node2 = int(str(simlab.getEntityFromGroup(nodeGrp2)).strip("()"","))
    node3 = int(str(simlab.getEntityFromGroup(nodeGrp3)).strip("()"","))
    node4 = int(str(simlab.getEntityFromGroup(nodeGrp4)).strip("()"","))
    
    boxCoord = getBoxCoordinates(node1, node2, node3 , node4, num = 2)
    # print("boxCoord", boxCoord)
    slideBody = simlab.getBodiesFromGroup(sliderGrp)
    railBody = simlab.getBodiesFromGroup(railGrp)
    # print("slider", slideBody)
    # print("rail", railBody)
    mcName = "linearSlide_MC"

    for i in range(2):
        if i == 0:
            planePoints = ([boxCoord["p3"],boxCoord["p5"], boxCoord["p6"]])
            hardPoints = (boxCoord["p11"],boxCoord["p12"])
        elif i == 1:
            planePoints = (boxCoord["p1"],boxCoord["p2"], boxCoord["p4"])
            hardPoints = (boxCoord["p9"],boxCoord["p10"])
        slideFace = getFaceIdFromPlane(slideBody, planePoints)
        railFace = getFaceIdFromPlane(railBody, planePoints)
        # print("slideFace", slideFace)
        # print("railFace", railFace)
        if not slideFace:
                messagebox.showinfo("情報","Can't find a slider face to a given plane info.")
                return
        if not railFace:
                messagebox.showinfo("情報","Can't find a rail face to a given plane info.")
                return

        createHardPointsMC(mcName,slideFace,hardPoints)
        re_meshFace(slideFace)

        importlib.reload(mpcutil)
        imprinted_ok = None
        if len(railFace) > 1:
            for thisFace in railFace:
                thisRailFace = tuple([thisFace])
                print("thisRailFaceFace", thisRailFace)
                imprinted_ok = mpcutil.imprintGasket(deckFaceId=thisRailFace, gasketFaceId=slideFace)
                if imprinted_ok:
                    break
        else:
            imprinted_ok = mpcutil.imprintGasket(deckFaceId=railFace, gasketFaceId=slideFace)
        
        if not imprinted_ok:
                messagebox.showinfo("情報","Face imprinting failed..")
                return

    for thisPoint in boxCoord:
        centerPt = boxCoord[thisPoint]
        nodeFromSlider = getNodesInSphere(slideBody, centerPt)
        nodeFromBlock = getNodesInSphere(slideBody, centerPt)
        # print("nodeFromSlider",nodeFromSlider)
        # print("nodeFromBlock",nodeFromBlock)
        nodes = nodeFromBlock+nodeFromSlider
        if len(nodes)==2:
            springId = muratautil.getUniqueId("MAX_SPRING_ID")
            springNm = "linearSpring{}".format(springId)
            if sx != 0:connectTwoNodesInSpring(springNm+"_R",nodes,CID,sx, constraint= "x")
            if sy != 0:connectTwoNodesInSpring(springNm+"_T",nodes,CID,sy, constraint= "y")
            if sz != 0:connectTwoNodesInSpring(springNm+"_Z",nodes,CID,sz, constraint= "z")

def flattenCurvedFaces(baseGrp, adjGrp):
    modelNm = simlab.getModelName("FEM")
    baseFaceEnts = simlab.getEntityFromGroup(baseGrp)
    adjFaceEnts = simlab.getEntityFromGroup(adjGrp)

    FlattenFace=''' <FlattenFace UUID="23c5a4b3-c33b-49b0-bbeb-f7b74fdc2a6c">
    <tag Value="-1"/>
    <Name Value="FlattenFace5"/>
    <BaseFaceList>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(baseFaceEnts).strip("()") +'''</Face>
    </Entities>
    </BaseFaceList>
    <Thickness Value="5"/>
    <Collapse Value="0"/>
    <RemoveTinyFaceList>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(adjFaceEnts).strip("()") +'''</Face>
    </Entities>
    </RemoveTinyFaceList>
    </FlattenFace>'''
    simlab.execute(FlattenFace)
    importlib.reload(grouputil)
    mergeFaces = baseFaceEnts + adjFaceEnts
    # print(mergeFaces)
    _deleteGrp(baseGrp)
    _deleteGrp(adjGrp)
    grouputil.mergeFaces(mergeFaces)

def alignFaces(alignFaceGrp, refFaceGrp):
    alignFaces = simlab.getEntityFromGroup(alignFaceGrp)
    refFaces = simlab.getEntityFromGroup(refFaceGrp)
    refFaces = int(str(refFaces).strip("()"","))
    # print(refFaces)
    modelNm = simlab.getModelName("FEM")
    pts = simlab.definePlaneFromEntity(modelNm, refFaces)
    pts = simlabutil.Convert3PointsOnPlaneTo4Points(pts)

    AlignPlanar=''' <AlignPlanar UUID="b9175a92-dd76-4c68-b31c-0c20c2afa2c3" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <Select Value="TargetFace"/>
    <Entities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(alignFaces).strip("()") +'''</Face>
    </Entities>
    </Entities>
    <Define Value="Plane" PlanePoints="'''+ ",".join(str(v) for pt in pts for v in pt) +'''"/>
    <DeleteZeroAreaElement Value="1"/>
    </AlignPlanar>'''
    simlab.execute(AlignPlanar)
    # print(AlignPlanar)
    importlib.reload(grouputil)
    mergeFaces = list(alignFaces)
    # mergeFaces.append(refFaces)
    mergeGrp = "mergedFaceTemp"
    _deleteGrp(mergeGrp)
    simlablib.CreateGroup(modelNm,"Face", mergeFaces, mergeGrp)
    grouputil.mergeFaces(mergeFaces)
    edges = getEdgeIdFromFaceGrp(mergeGrp)
    # print("edgeId", edges)
    edgeReMesh(edges)
    _deleteOrphanNodes()
    
    