# coding: utf_8
# SimLab Version 2019.2 (64-bit)
#***************************************************************
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import sys, os, importlib
from hwx import simlab, gui
import numpy as np
import csv
import tkinter.filedialog as filedialog

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

BASE_NODE = 10000000
MAX_ID_RBE = 'Max_ID_RBE'
MAX_ID_COORDINATE = 'Max_ID_Coordinate'
MAX_ID_SPRING = 'Max_ID_Spring'
MAX_ID_MPC = 'MPC_COUNTER'

BOLT1_RBE = 'Bolt_MOTOR_RBE_'
BOLT2_RBE = 'Bolt_GROUND_RBE_'
BOLT3_RBE = 'Bolt_BALL_RBE_'
BOLT2_COORDINATE = 'Bolt_GROUND_RECT_CCOORDINATE_'
BOLT3_COORDINATE = 'Bolt_BALL_RECT_CCOORDINATE_'
BOLT2_SPRING = 'Bolt_GROUND_SPRING_'
BOLT2_BEAM = 'Bolt_GROUND_BEAM_'
BOLT3_BEAM = 'Bolt_BALL_BEAM_'
BOLT3_MPC = 'Bolt_BALL_MPC_'

# local
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)
import simlablib
import simlabutil
import importlib
import basedialog
import widget as wt
import tooltip as tp
import mass
import springutil
import coordinate
import springcsv

def CreateType1Bolt(holeGrp, baseGrp, elemSize):
    holes = simlab.getEntityFromGroup(holeGrp)
    bases = simlab.getEntityFromGroup(baseGrp)
    if len(holes) == 0 or len(bases) == 0:
        return

    # merges base plane faces
    planeGrp, planeFaces = MergePlane(baseGrp)
    if len(planeFaces) == 0:
        simlablib.DeleteGroups(planeGrp)
        return

    # gets two edges(top and bottom) from hole face
    circles = GetCircleGrp(holeGrp, planeGrp)
    if len(circles) == 0:
        simlablib.DeleteGroups(planeGrp)
        return

    # Re-mesh so that node is created in the center of bottom hole
    RemeshType1(planeGrp, circles, elemSize)

    # creates RBE
    CreatType1RBE(circles, planeGrp)

def CreatType1RBE(circles, planeGrp):
    modelName = simlab.getModelName('FEM')

    planes = simlab.getEntityFromGroup(planeGrp)
    simlablib.DeleteGroups(planeGrp)

    planeBodyGrp = simlabutil.UniqueGroupName('_PlaneBody')
    simlablib.SelectAssociatedEntities(modelName, 'Face', planes, 'Body', planeBodyGrp)
    planeBodies = simlab.getBodiesFromGroup(planeBodyGrp)
    simlablib.DeleteGroups(planeBodyGrp)

    rbes = []
    for circle in circles:
        topGrp, bottomGrp = circle
        center, _ = simlabutil.GetArcEdgeAttributes(modelName, bottomGrp)

        # searches for a node near the center of the arc from the bottom
        closestNodeGrp = simlabutil.UniqueGroupName('_ClosestNode')
        ClosestEntity=''' <ClosestEntity UUID="aa6fa8bd-c62b-455c-a607-7988e5b8769e">
        <SupportEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + str(planeBodies).replace("'", '"').strip('()') + ''',</Body>
        </Entities>
        </SupportEntities>
        <Center Value="''' + str(center).strip('()') + '''"/>
        <Tolerance Value="0.1" Check="0"/>
        <EntityType Value="Node"/>
        <CreateGroup Value="1" Name="''' + closestNodeGrp + '''"/>
        </ClosestEntity>'''
        simlab.execute(ClosestEntity)

        nodes = simlab.getEntityFromGroup(closestNodeGrp)
        simlablib.DeleteGroups(closestNodeGrp)
        if len(nodes) == 0:
            simlablib.DeleteGroups([topGrp, bottomGrp])
            continue

        # independent nodes = center
        independentNode = nodes[0]

        # gets nodes from top edges
        edges = simlab.getEntityFromGroup(topGrp)
        edgeNodeGrp = simlabutil.UniqueGroupName('_EdgeNode')
        simlablib.SelectAssociatedEntities(modelName, 'Edge', edges, 'Node', edgeNodeGrp)
        topNodes = simlab.getEntityFromGroup(edgeNodeGrp)
        simlablib.DeleteGroups([topGrp, edgeNodeGrp])

        # gets nodes from bottom edges
        edges = simlab.getEntityFromGroup(bottomGrp)
        edgeNodeGrp = simlabutil.UniqueGroupName('_EdgeNode')
        simlablib.SelectAssociatedEntities(modelName, 'Edge', edges, 'Node', edgeNodeGrp)
        bottomNodes = simlab.getEntityFromGroup(edgeNodeGrp)
        simlablib.DeleteGroups([bottomGrp, edgeNodeGrp])

        # dependent nodes = top + bottom
        dependentNodes = list(set(topNodes) | set(bottomNodes))
        if len(dependentNodes) == 0:
            continue
        
        # creates RBE
        RBEID = 1
        if simlab.isParameterPresent(MAX_ID_RBE):
            RBEID = simlab.getIntParameter('$'+MAX_ID_RBE) + 1
        simlablib.AddIntParameters(MAX_ID_RBE, RBEID)
        RBEName = '__TEMP_' + str(RBEID)
        simlablib.ManualRBE(modelName, RBEName, independentNode, dependentNodes)
        rbes.append(RBEName)

    if len(rbes) > 1:
        simlablib.MergeBodies(modelName, rbes)
    newName = GetNewName(BOLT1_RBE, 1)
    simlablib.RenameBody(modelName, rbes[0], newName)

def RemeshType1(planeGrp, circles, meshSize=20):
    modelName = simlab.getModelName('FEM')

    meshCtrls = []
    for circle in circles:
        _, bottomGrp = circle
        center, _ = simlabutil.GetArcEdgeAttributes(modelName, bottomGrp)

        meshCtrlName = 'BoltType1_HardPointMeshCtrl' + str(len(meshCtrls))
        meshCtrls.append(meshCtrlName)
    
        MeshControls=''' <MeshControl isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" CheckBox="ON">
        <tag Value="-1"/>
        <MeshControlName Value="''' + meshCtrlName + '''"/>
        <MeshControlType Value="Hard Points"/>
        <Entities>
        <Group>"''' + planeGrp + '''",</Group>
        </Entities>
        <Reverse ModelIds="" Value="" EntityTypes=""/>
        <MeshColor Value=""/>
        <HardPoints>
        <Geometry Value="2"/>
        <Tolerance Value="0.1"/>
        <DataPoints Value="''' + str(center).strip('()') + ''',"/>
        <!-- To specify the csv file path , please uncomment out the below line.   -->
        <!--
        <Hard_Points_File Value="D:/Testing/HardPoints.csv" /> 
                    -->
        </HardPoints>
        </MeshControl>'''
        simlab.execute(MeshControls)

    faces = simlab.getEntityFromGroup(planeGrp)
    LocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh1"/>
    <SupportEntities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Face>''' + str(faces).strip('()') + ''',</Face>
    </Entities>
    </SupportEntities>
    <ElemType Value="1"/>
    <AverageElemSize Value="''' + str(meshSize) + '''"/>
    <MinElemSize Value="''' + str(meshSize/10.0) + '''"/>
    <PreserveBoundaryEdges Value="1"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="45"/>
    <CurvatureMinElemSize Value="10"/>
    <AspectRatio Value="10"/>
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

    for meshCtrl in meshCtrls:
        simlablib.DeleteMeshControl(meshCtrl)

def GetCircleGrp(holeGrp, planeGrp):
    modelName = simlab.getModelName('FEM')

    # gets point on plane and normal vector
    plane = simlab.definePlaneFromGroup(planeGrp, 'FACEGROUP')
    if len(plane) == 0:
        simlablib.DeleteGroups(holeGrp)
        return []

    p1, p2, p3 = plane
    v1 = np.array(p2) - np.array(p1)
    v2 = np.array(p3) - np.array(p1)
    n = np.cross(v1, v2)
    normalVector = n / np.linalg.norm(n)
    pointOnPlane = (np.array(p1) + np.array(p2) + np.array(p2)) / 3.0

    # diviedes hole faces to connected faces
    holeGrps = simlab.createGroupsOfConnectedEntities(holeGrp)
    if len(holeGrps) == 0:
        simlablib.DeleteGroups(holeGrps)
        return []

    circles = []
    for holeGrp in holeGrps:
        holes = simlab.getEntityFromGroup(holeGrp)

        boundaries = set()
        for face in holes:
            adjacentEdgeGrp = simlabutil.UniqueGroupName('_AdjacentEdgeGrp')
            simlablib.SelectAssociatedEntities(modelName, 'Face', face, 'Edge', adjacentEdgeGrp)
            adjacentEdges = simlab.getEntityFromGroup(adjacentEdgeGrp)
            simlablib.DeleteGroups(adjacentEdgeGrp)
            for edge in adjacentEdges:
                if edge in boundaries:
                    boundaries.remove(edge)
                else:
                    boundaries.add(edge)
        boundaries = list(boundaries)
        if len(boundaries) == 0:
            continue
        
        boundaryEdgeGrp = simlabutil.UniqueGroupName('_BoundaryEdgeGrp')
        simlablib.CreateGroup(modelName, 'Edge', boundaries, boundaryEdgeGrp)

        # diviedes edges to connected edges
        connectedEdgeGrps = simlab.createGroupsOfConnectedEntities(boundaryEdgeGrp)
        if len(connectedEdgeGrps) != 2:
            simlablib.DeleteGroups(connectedEdgeGrps)
            continue

        # two edges -> top and bottom
        circle0 = simlabutil.GetArcEdgeAttributes(modelName, connectedEdgeGrps[0])
        circle1 = simlabutil.GetArcEdgeAttributes(modelName, connectedEdgeGrps[1])
        if len(circle0) == 0 or len(circle1) == 0:
            continue
    
        center0, _ = circle0
        center1, _ = circle1

        # Bottom circle is near the plane, Top circle is far from plane.
        v1 = np.array(center0) - pointOnPlane
        v2 = np.array(center1) - pointOnPlane
        d1 = np.dot(v1, normalVector)
        d2 = np.dot(v2, normalVector)
        if d1 > d2:
            topGrp = connectedEdgeGrps[0]
            bottomGrp = connectedEdgeGrps[1]
        else:
            topGrp = connectedEdgeGrps[1]
            bottomGrp = connectedEdgeGrps[0]
        
        topName = simlabutil.UniqueGroupName('_TopCircle' + str(len(circles)))
        bottomName = simlabutil.UniqueGroupName('_BottomCircle' + str(len(circles)))

        simlablib.RenameGroup(topGrp, topName)
        simlablib.RenameGroup(bottomGrp, bottomName)
        circles.append([topName, bottomName])

    simlablib.DeleteGroups(holeGrps)
    return circles

def MergePlane(baseGrp):
    modelName = simlab.getModelName('FEM')

    bases = simlab.getEntityFromGroup(baseGrp)
    simlablib.DeleteGroups(baseGrp)

    planeGrp = simlabutil.UniqueGroupName('_Plane')
    ShowAdjacent=''' <ShowAdjacent gda="" UUID="EEDC5B06-8DC9-4754-AA76-F9E32643765A" clearSelection="1">
    <Name Value=""/>
    <tag Value="-1"/>
    <Show Value="0"/>
    <Select Value="1"/>
    <CheckVisibleFaces Value="1"/>
    <SupportEntities ModelIds="" Value="" EntityTypes=""/>
    <PickFaceType Value="GuideFaces"/>
    <GuideFaces>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Face>''' + str(bases).strip('()') + ''',</Face>
    </Entities>
    </GuideFaces>
    <LimitFaces ModelIds="" Value="" EntityTypes=""/>
    <AddPlanarFacestoLimitFaces Value="0"/>
    <AddCylindricalFacestoLimitFaces Value="0"/>
    <UptoNonManifoldEdges Value="0"/>
    <BreakAngle Value="1"/>
    <Angle Value="5"/>
    <NoOfLayers Value="369"/>
    <PlanePoints Value=""/>
    <CreateGroup Value="1" Name="''' + planeGrp + '''"/>
    </ShowAdjacent>'''
    simlab.execute(ShowAdjacent)
    
    faces = simlab.getEntityFromGroup(planeGrp)
    if len(faces) <= 1:
        simlablib.CreateGroup(modelName, 'Face', bases, planeGrp)
        return planeGrp, bases

    MergeFaces=''' <MergeFace UUID="D9D604CE-B512-44e3-984D-DF3E64141F8D">
    <tag Value="-1"/>
    <Name Value="MergeFace1"/>
    <SupportEntities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Face>''' + str(faces).strip('()') + ''',</Face>
    </Entities>
    </SupportEntities>
    <MergeBoundaryEdges Value="1"/>
    <SplitBoundaryEdges Value="0"/>
    <SplitEdgesBasedon Value="0"/>
    <FeatureAngle Value="45"/>
    </MergeFace>'''
    simlab.execute(MergeFaces)
    faces = simlab.getEntityFromGroup(planeGrp)
    return planeGrp, faces

def CreateType2Bolt(washerGrp, topEdgeGrp, bottomEdgeGrp, numN1, numN2, lengthN2, CID, Stiff, springName):
    circles = GetCircleEdgesType2(washerGrp, topEdgeGrp, bottomEdgeGrp)
    if len(circles) == 0:
        return

    rbeNodes = CreatType2RBE(circles)
    if len(rbeNodes) == 0:
        return

    endNode = CreateBeam(rbeNodes, numN1, numN2, lengthN2)
    if endNode < 0:
        return

    CreateGroundSpring(rbeNodes[0], endNode, CID, Stiff, springName)
    
def CreateGroundSpring(topNode, endNode, CID, Stiff, springName):
    modelName = simlab.getModelName('FEM')

    keySpringID = 1
    if simlab.isParameterPresent(MAX_ID_SPRING):
        keySpringID = simlab.getIntParameter('$'+MAX_ID_SPRING) + 1

    for item in [[1, 'X', Stiff[0]], [2, 'Y', Stiff[1]], [4, 'Z', Stiff[2]]]:
        flag, dire, stiff = item
        if stiff == 0.0:
            continue

        # ID
        springID = 1
        if simlab.isParameterPresent(MAX_ID_SPRING):
            springID = simlab.getIntParameter('$'+MAX_ID_SPRING) + 1
        simlablib.AddIntParameters(MAX_ID_SPRING, springID)

        # Name
        newName = springName + '_' + str(keySpringID) + '_' + dire

        SpringElement=''' <Spring UUID="ACA1CCC4-4687-41bd-9BA3-0C602C5B2B7D" isObject="2" CheckBox="ON" BCType="Spring">
        <tag Value="-1"/>
        <Name Value="''' + newName + '''"/>
        <SpringEntities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Node>''' + str(endNode) + ''',</Node>
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
        <Flag2 Value="0"/>
        <GndSpring Value="1"/>
        <FieldData Value="None" Index="0"/>
        </Spring>'''
        simlab.execute(SpringElement)

def CreateCoordinateForGroundSpring(originNode, nVecs):
    modelName = simlab.getModelName('FEM')

    o = np.array(simlab.getNodePositionFromNodeID(modelName, originNode))
    nx, ny, nz = nVecs

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
    newName = BOLT2_COORDINATE + str(axisID)

    CreateCoordinateSystem=''' <Coordinate UUID="b625f5cd-2925-4f9f-94a2-b58854934f8b" BCType="Coordinates" isObject="2">
    <tag Value="-1"/>
    <StackIndex Value="CoordinateXYPoint"/>
    <CoordinateXYPoint>
    <Name Value="''' + newName + '''"/>
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

def CreateBeam(rbeNodes, numN1, numN2, lenN2):
    modelName = simlab.getModelName('FEM')

    topNode, bottomNode = rbeNodes

    topXYZ = simlab.getNodePositionFromNodeID(modelName, topNode)
    bottomXYZ = simlab.getNodePositionFromNodeID(modelName, bottomNode)

    vec = np.array(bottomXYZ) - np.array(topXYZ)
    magnitude = np.linalg.norm(vec)
    if magnitude < 1e-9:
        return -1

    nvec = vec / magnitude
    step = magnitude / numN1

    # Top -> Bottom-1
    bars = []
    baseXYZ = topXYZ
    baseNode = topNode
    for i in range(numN1-1):
        xyz = np.array(baseXYZ) + step * nvec

        nodeID = simlabutil.AvailableNodeID(modelName, BASE_NODE)
        simlablib.CreateNodeByXYZ(modelName, list(xyz), nodeID)

        bodyName = simlabutil.UniqueBodyName(modelName, 'Bar')
        CreateBar=''' <Bar UUID="741D7A3A-1CD4-4051-ABBA-CD1603D1C545" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value="''' + bodyName + '''"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName+ '''</Model>
            <Node>''' + str(baseNode) + ',' + str(nodeID) + ''',</Node>
        </Entities>
        </SupportEntities>
        <Output/>
        </Bar>'''
        simlab.execute(CreateBar)

        baseXYZ = xyz
        baseNode = nodeID
        bars.append(bodyName)

    # Latest -> Bottom
    bodyName = simlabutil.UniqueBodyName(modelName, 'Bar')
    CreateBar=''' <Bar UUID="741D7A3A-1CD4-4051-ABBA-CD1603D1C545" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="''' + bodyName + '''"/>
    <SupportEntities>
    <Entities>
        <Model>''' + modelName+ '''</Model>
        <Node>''' + str(baseNode) + ',' + str(bottomNode) + ''',</Node>
    </Entities>
    </SupportEntities>
    <Output/>
    </Bar>'''
    simlab.execute(CreateBar)
    bars.append(bodyName)

    if lenN2 != 0 or numN2 != 0:
        step = lenN2 / numN2

        # Latest -> Bottom
        baseXYZ = bottomXYZ
        baseNode = bottomNode
        for i in range(numN2):
            xyz = np.array(baseXYZ) + step * nvec

            nodeID = simlabutil.AvailableNodeID(modelName, BASE_NODE)
            simlablib.CreateNodeByXYZ(modelName, list(xyz), nodeID)

            bodyName = simlabutil.UniqueBodyName(modelName, 'Bar')
            CreateBar=''' <Bar UUID="741D7A3A-1CD4-4051-ABBA-CD1603D1C545" CheckBox="ON">
            <tag Value="-1"/>
            <Name Value="''' + bodyName + '''"/>
            <SupportEntities>
            <Entities>
                <Model>''' + modelName+ '''</Model>
                <Node>''' + str(baseNode) + ',' + str(nodeID) + ''',</Node>
            </Entities>
            </SupportEntities>
            <Output/>
            </Bar>'''
            simlab.execute(CreateBar)

            baseXYZ = xyz
            baseNode = nodeID
            bars.append(bodyName)

    # merges bars
    barName = bars[0]
    simlablib.MergeBodies(modelName, bars)
    newName = GetNewName(BOLT2_BEAM, 1)
    simlablib.RenameBody(modelName, barName, newName)

    # end nodes for ground spring
    if numN2 == 0:
        endNode = bottomNode
    else:
        endNode = baseNode
    return endNode

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

def CreatType2RBE(circles):
    modelName = simlab.getModelName('FEM')

    RBEID = 0
    if simlab.isParameterPresent(MAX_ID_RBE):
        RBEID = simlab.getIntParameter('$'+MAX_ID_RBE)

    innerEdges, outerEdges, bottomEdges = circles

    for edge in innerEdges:
        result = simlab.getArcEdgeAttributes(modelName, edge)
        if len(result) != 0:
            topCenter, _ = result
            break
    else:
        return []

    for edge in bottomEdges:
        result = simlab.getArcEdgeAttributes(modelName, edge)
        if len(result) != 0:
            bottomCenter, _ = result
            break
    else:
        return []

    topEdges = list(set(innerEdges) | set(outerEdges))

    topNodeGrp = simlabutil.UniqueGroupName('_TopNodes')
    bottomNodeGrp = simlabutil.UniqueGroupName('_BottomNodes')

    simlablib.SelectAssociatedEntities(modelName, 'Edge', topEdges, 'Node', topNodeGrp)
    simlablib.SelectAssociatedEntities(modelName, 'Edge', bottomEdges, 'Node', bottomNodeGrp)

    topNodes = simlab.getEntityFromGroup(topNodeGrp)
    bottomNodes = simlab.getEntityFromGroup(bottomNodeGrp)
    simlablib.DeleteGroups([topNodeGrp, bottomNodeGrp])
    if len(topNodes) == 0 or len(bottomNodes) == 0:
        return []

    topNodeID = simlabutil.AvailableNodeID(modelName, BASE_NODE)
    simlablib.CreateNodeByXYZ(modelName, list(topCenter), topNodeID)

    bottomNodeID = simlabutil.AvailableNodeID(modelName, BASE_NODE)
    simlablib.CreateNodeByXYZ(modelName, list(bottomCenter), bottomNodeID)

    RBEID += 1
    RBENameTop = GetNewName(BOLT2_RBE + 'Top_', 1)
    simlablib.ManualRBE(modelName, RBENameTop, topNodeID, topNodes)

    RBEID += 1
    RBENameBottom = GetNewName(BOLT2_RBE + 'Bottom_', 1)
    simlablib.ManualRBE(modelName, RBENameBottom, bottomNodeID, bottomNodes)

    simlablib.AddIntParameters(MAX_ID_RBE, RBEID)

    simlablib.MergeBodies(modelName, [RBENameTop, RBENameBottom])
    newName = GetNewName(BOLT2_RBE, 1)
    simlablib.RenameBody(modelName, RBENameTop, newName)

    return [topNodeID, bottomNodeID]

def GetCircleEdgesType2(washerGrp, topEdgeGrp, bottomEdgeGrp):
    modelName = simlab.getModelName('FEM')

    washerFaces = simlab.getEntityFromGroup(washerGrp)
    topEdges = simlab.getEntityFromGroup(topEdgeGrp)
    bottomEdges = simlab.getEntityFromGroup(bottomEdgeGrp)

    edgeGrp = simlabutil.UniqueGroupName('_Edge')
    simlablib.SelectAssociatedEntities(modelName, 'Face', washerFaces, 'Edge', edgeGrp)
    if not simlab.isGroupPresent(edgeGrp):
        return []

    edges = simlab.getEntityFromGroup(edgeGrp)
    outerEdges = list(set(edges) - set(topEdges))
    if len(outerEdges) == 0:
        return []

    return [topEdges, outerEdges, bottomEdges]

def CreateType3Bolt(monGrp, nutGrp, brgGrp, nums, dofs, CID, mon, nut, brg, names):
    modelName = simlab.getModelName('FEM')
    N1, N2 = nums
    monName, nutName, brgName = names
    rbes = []
    beams = []
    independs = []
    dependes = []

    # mon-nut
    monNode, monRBE = CreatType3RBE(monGrp)
    nutNode, nutRBE = CreatType3NutRBE(nutGrp)
    monBeamNode, nutBeamNode, mnBeam = ConnectType3Beam(monNode, nutNode, N1, newNode=True)
    rbes.append(monRBE)
    rbes.append(nutRBE)
    beams.append(mnBeam)
    independs.append(monBeamNode)
    independs.append(nutBeamNode)
    dependes.append(monNode)
    dependes.append(nutNode)

    CreateType3Spring(monNode, monBeamNode, CID, mon, monName)
    CreateType3Spring(nutNode, nutBeamNode, CID, nut, nutName)

    # nut-brg
    if simlab.isGroupPresent(brgGrp):
        brgNode, brgRBE = CreatType3RBE(brgGrp)
        nutBeamNode, brgBeamNode, nbBeam = ConnectType3Beam(nutNode, brgNode, N2, newNode=False)
        rbes.append(brgRBE)
        beams.append(nbBeam)
        independs.append(brgBeamNode)
        dependes.append(brgNode)
        CreateType3Spring(brgNode, brgBeamNode, CID, brg, brgName)

    CreateType3MPC(independs, dependes, CID, dofs)

    simlablib.MergeBodies(modelName, rbes)
    newRBEName = GetNewName(BOLT3_RBE, 1)
    simlablib.RenameBody(modelName, rbes[0], newRBEName)

    simlablib.MergeBodies(modelName, beams)
    newBEAMName = GetNewName(BOLT3_BEAM, 1)
    simlablib.RenameBody(modelName, beams[0], newBEAMName)

def CreateType3MPC(independs, dependes, axisID, dofs):
    modelName = simlab.getModelName('FEM')    

    # ID
    mpcID = 1
    if simlab.isParameterPresent(MAX_ID_MPC):
        mpcID = simlab.getIntParameter('$'+MAX_ID_MPC) + 1
    simlablib.AddIntParameters(MAX_ID_MPC, mpcID)

    x,y,z,r_x,r_y,r_z = dofs
    newName = BOLT3_MPC + str(mpcID)

    MPC=''' <Stress_MPC CheckBox="ON" BCType="MPC" UUID="BBCD6D76-5754-42b5-8A1B-E8FB79064EFE" isObject="2">
    <tag Value="-1"/>
    <Name Value="'''+ newName +'''"/>
    <CoordinateAxisID Value="''' + str(axisID) + '''"/>
    <BetweenEntitties Value="1"/>
    <MasterList>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(independs).strip("[]""()") +''',</Node>
    </Entities>
    </MasterList>
    <SlaveList>
    <Entities>
    <Model>'''+ modelName +'''</Model>
    <Node>'''+ str(dependes).strip("[]""()")+''',</Node>
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

def CreateType3Coordinate(originNode, nv):
    modelName = simlab.getModelName('FEM')

    o = np.array(simlab.getNodePositionFromNodeID(modelName, originNode))
    nx, ny, _ = nv

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
    newName = BOLT3_COORDINATE + str(axisID)

    CreateCoordinateSystem=''' <Coordinate UUID="b625f5cd-2925-4f9f-94a2-b58854934f8b" BCType="Coordinates" isObject="2">
    <tag Value="-1"/>
    <StackIndex Value="CoordinateXYPoint"/>
    <CoordinateXYPoint>
    <Name Value="''' + newName + '''"/>
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

def CreateType3Spring(node1, node2, axisID, stiffs, keyName):
    modelName = simlab.getModelName('FEM')

    keySpringID = 1
    if simlab.isParameterPresent(MAX_ID_SPRING):
        keySpringID = simlab.getIntParameter('$'+MAX_ID_SPRING) + 1

    for item in [[1, 'X', stiffs[0]], [2, 'Y', stiffs[1]], [4, 'Z', stiffs[2]]]:
        flag, dire, stiff = item
        if stiff == 0.0:
            continue

        # ID
        springID = 1
        if simlab.isParameterPresent(MAX_ID_SPRING):
            springID = simlab.getIntParameter('$'+MAX_ID_SPRING) + 1
        simlablib.AddIntParameters(MAX_ID_SPRING, springID)

        # Name
        newName = keyName + '_' + str(keySpringID) + '_' + dire

        SpringElement=''' <Spring BCType="Spring" CheckBox="ON" UUID="ACA1CCC4-4687-41bd-9BA3-0C602C5B2B7D" isObject="2">
            <tag Value="-1"/>
            <Name Value="''' + newName + '''"/>
            <SpringEntities>
            <Entities>
                <Model>''' + modelName + '''</Model>
                <Node>''' + str(node1) + ''',''' + str(node2) + ''',</Node>
            </Entities>
            </SpringEntities>
            <ElementID Value="0"/>
            <AxisID Value="''' + str(axisID) + '''"/>
            <FieldID Value=""/>
            <Type Value="Nodes" Index="0"/>
            <SpringType Value="0"/>
            <PropertyID Value="0"/>
            <TXStiff CheckBox="0" Value="''' + str(stiff) + '''"/>
            <TYStiff CheckBox="0" Value="0.0"/>
            <TZStiff CheckBox="0" Value="0.0"/>
            <RXStiff CheckBox="0" Value="0.0"/>
            <RYStiff CheckBox="0" Value="0.0"/>
            <RZStiff CheckBox="0" Value="0.0"/>
            <Flag1 Value="''' + str(flag) + '''"/>
            <Flag2 Value="''' + str(flag) + '''"/>
            <GndSpring Value="0"/>
            <FieldData Value="None" Index="0"/>
            </Spring>'''
        simlab.execute(SpringElement)

def CreatType3RBE(faceGrp):
    modelName = simlab.getModelName('FEM')

    allBodies = simlab.getBodiesWithSubString(modelName, ['*'])

    CreateBodyFromFaces=''' <BodyFromFaces UUID="24F7C671-DC40-44e0-9B32-8A22A67F58FA" gda="">
    <SupportEntities ModelIds="" Value="" EntityTypes=""/>
    <ShareBoundaryEdges Value="1"/>
    <CreateBodyFromFaceOption Value="2"/>
    <CreateBodyForEachGroup Value="false"/>
    <Group Entity="" Value="''' + faceGrp + ''',"/>
    <UseInputBodyName Value="true"/>
    </BodyFromFaces>'''
    simlab.execute(CreateBodyFromFaces)

    postAllBodies = simlab.getBodiesWithSubString(modelName, ['*'])

    createdBodies = list(set(postAllBodies) - set(allBodies))
    if len(createdBodies) == 0:
        return -1, ''

    nodeID = simlabutil.AvailableNodeID(modelName, BASE_NODE)
    simlablib.CreateNodeByCentroid(modelName, 'Body', createdBodies, nodeID)

    simlablib.DeleteBodies(modelName, createdBodies)

    # creates RBE
    RBEID = 1
    if simlab.isParameterPresent(MAX_ID_RBE):
        RBEID = simlab.getIntParameter('$'+MAX_ID_RBE) + 1
    simlablib.AddIntParameters(MAX_ID_RBE, RBEID)
    RBEName = BOLT3_RBE + '_TEMP_' + str(RBEID)

    faces = simlab.getEntityFromGroup(faceGrp)
    simlablib.CreateRBE(modelName, RBEName, 'Face', faces, nodeID)

    return nodeID, RBEName

def CreatType3NutRBE(faceGrp):
    modelName = simlab.getModelName('FEM')

    allBodies = simlab.getBodiesWithSubString(modelName, ['*'])

    CreateBodyFromFaces=''' <BodyFromFaces UUID="24F7C671-DC40-44e0-9B32-8A22A67F58FA" gda="">
    <SupportEntities ModelIds="" Value="" EntityTypes=""/>
    <ShareBoundaryEdges Value="1"/>
    <CreateBodyFromFaceOption Value="2"/>
    <CreateBodyForEachGroup Value="false"/>
    <Group Entity="" Value="''' + faceGrp + ''',"/>
    <UseInputBodyName Value="true"/>
    </BodyFromFaces>'''
    simlab.execute(CreateBodyFromFaces)

    postAllBodies = simlab.getBodiesWithSubString(modelName, ['*'])

    createdBodies = list(set(postAllBodies) - set(allBodies))
    if len(createdBodies) == 0:
        return -1, ''

    nodeID = simlabutil.AvailableNodeID(modelName, BASE_NODE)
    simlablib.CreateNodeByCentroid(modelName, 'Body', createdBodies, nodeID)
    simlablib.DeleteBodies(modelName, createdBodies)

    faces = simlab.getEntityFromGroup(faceGrp)

    boundaries = set()
    for face in faces:
        adjacentEdgeGrp = simlabutil.UniqueGroupName('_AdjacentEdgeGrp')
        simlablib.SelectAssociatedEntities(modelName, 'Face', face, 'Edge', adjacentEdgeGrp)
        adjacentEdges = simlab.getEntityFromGroup(adjacentEdgeGrp)
        simlablib.DeleteGroups(adjacentEdgeGrp)
        for edge in adjacentEdges:
            if edge in boundaries:
                boundaries.remove(edge)
            else:
                boundaries.add(edge)
    boundaries = list(boundaries)
    if len(boundaries) == 0:
        return -1, ''

    # creates RBE
    RBEID = 1
    if simlab.isParameterPresent(MAX_ID_RBE):
        RBEID = simlab.getIntParameter('$'+MAX_ID_RBE) + 1
    simlablib.AddIntParameters(MAX_ID_RBE, RBEID)
    RBEName = BOLT3_RBE + str(RBEID)

    faces = simlab.getEntityFromGroup(faceGrp)
    simlablib.CreateRBE(modelName, RBEName, 'Edge', boundaries, nodeID)

    return nodeID, RBEName

def ConnectType3Beam(node1, node2, num, newNode=True):
    modelName = simlab.getModelName('FEM')

    xyz1 = simlab.getNodePositionFromNodeID(modelName, node1)
    xyz2 = simlab.getNodePositionFromNodeID(modelName, node2)

    vec = np.array(xyz2) - np.array(xyz1)
    magnitude = np.linalg.norm(vec)
    if magnitude < 1e-9:
        return -1, -1, ''

    nvec = vec / magnitude
    step = magnitude / num

    bars = []
    baseXYZ = xyz1
    if newNode:
        startNode = baseNode = simlabutil.AvailableNodeID(modelName, BASE_NODE)
        simlablib.CreateNodeByXYZ(modelName, list(baseXYZ), baseNode)
    else:
        startNode = baseNode = node1

    for i in range(num-1):
        xyz = np.array(baseXYZ) + step * nvec

        nodeID = simlabutil.AvailableNodeID(modelName, BASE_NODE)
        simlablib.CreateNodeByXYZ(modelName, list(xyz), nodeID)

        bodyName = simlabutil.UniqueBodyName(modelName, 'Bar')
        CreateBar=''' <Bar UUID="741D7A3A-1CD4-4051-ABBA-CD1603D1C545" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value="''' + bodyName + '''"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName+ '''</Model>
            <Node>''' + str(baseNode) + ',' + str(nodeID) + ''',</Node>
        </Entities>
        </SupportEntities>
        <Output/>
        </Bar>'''
        simlab.execute(CreateBar)

        baseXYZ = xyz
        baseNode = nodeID
        bars.append(bodyName)

    endXYZ = xyz2
    endNode = simlabutil.AvailableNodeID(modelName, BASE_NODE)
    simlablib.CreateNodeByXYZ(modelName, list(endXYZ), endNode)

    bodyName = simlabutil.UniqueBodyName(modelName, 'Bar')
    CreateBar=''' <Bar UUID="741D7A3A-1CD4-4051-ABBA-CD1603D1C545" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="''' + bodyName + '''"/>
    <SupportEntities>
    <Entities>
        <Model>''' + modelName+ '''</Model>
        <Node>''' + str(baseNode) + ',' + str(endNode) + ''',</Node>
    </Entities>
    </SupportEntities>
    <Output/>
    </Bar>'''
    simlab.execute(CreateBar)
    bars.append(bodyName)

    # merges bars
    barName = bars[0]
    simlablib.MergeBodies(modelName, bars)
    newName = simlabutil.UniqueBodyName(modelName, 'Bar')
    simlablib.RenameBody(modelName, barName, newName)

    return startNode, endNode, newName

class BoltDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup, springs):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        
        self.master.title('ボルト作成')
        self.backup = backup
        self.springs = springs

        self.Type1Hole = '_Type1_Hole'
        self.Type1Base = '_Type1_Base'
        self.Type1PageIndex = 0

        self.Type2Washer = '_Type2_Washer'
        self.Type2TopEdge = '_Type2_TopEdge'
        self.Type2BottomEdge = '_Type2_BottomEdge'
        self.Type2PageIndex = 0

        self.Type3Mon = '_Type3_Mon'
        self.Type3Nut = '_Type3_Nut'
        self.Type3Brg = '_Type3_Brg'

        self.Type4ArcEdges = '_Type4_ArcEdges'
        self.Type4BaseFaces = '_Type4_BaseFaces'
        self.Type4PageIndex = 0

        self.CreateWidgets()
        self.UpdateButtonFG()
        
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmType1 = tk.Frame(self.nb)
        self.frmType2 = tk.Frame(self.nb)
        self.frmType3 = tk.Frame(self.nb)
        self.frmType4 = tk.Frame(self.nb)
        self.nb.add(self.frmType1, text=' モーター取付 ')
        self.nb.add(self.frmType2, text=' 接地バネ付 ')
        self.nb.add(self.frmType3, text=' ボールネジ ')
        self.nb.add(self.frmType4, text=' タレット取付 ')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        self.nb.bind('<<NotebookTabChanged>>', self.ChangeTab)

        self.CreateType1Tab()
        self.CreateType2Tab()
        self.CreateType3Tab()
        self.CreateType4Tab()

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.BOTTOM, anchor=tk.NE)

        btnWidth = 10
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

        self.UpdateType4Widgets()
        self.UpdateType3Widgets()
        self.UpdateType2Widgets()
        self.UpdateType1Widgets()

    def CreateType1Tab(self):
        self.frmType1Top = tk.Frame(self.frmType1)
        self.frmType1Top.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        # Tips
        self.lblNote1 = tk.Label(self.frmType1Top, text='Tips: 穴面と設置面を選択して、[ 作成 ]ボタンを押してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmType1Top, height=5).pack(side=tk.TOP, anchor=tk.NW)
        btnWidth = 10
        
        self.frmTyp1Select = tk.Frame(self.frmType1Top)
        self.frmTyp1Select.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        # Select holes
        self.frmType1Hole = tk.Frame(self.frmTyp1Select)
        self.frmType1Hole.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        self.iconBolt1Hole = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bolt1_1.png')), master=self.frmType1Hole)
        tk.Label(self.frmType1Hole, image=self.iconBolt1Hole).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnType1Hole = tk.Button(self.frmType1Hole, text='ボルト穴面', command=self.SelectType1Hole)
        self.btnType1Hole.place(x=145, y=85)

        # Select base
        self.frmType1Base = tk.Frame(self.frmTyp1Select)
        self.iconBolt1Base = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bolt1_2.png')), master=self.frmType1Hole)
        tk.Label(self.frmType1Base, image=self.iconBolt1Base).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnType1Base = tk.Button(self.frmType1Base, text='設置面', command=self.SelectType1Base)
        self.btnType1Base.place(x=120, y=80)

        # select ctrl
        self.frmType1SelCtrl = tk.Frame(self.frmType1Top)
        self.frmType1SelCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        self.frmType1SelBtn = tk.Frame(self.frmType1SelCtrl)
        self.frmType1SelBtn.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconType1Prev = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'prev.png')), master=self.frmType1SelBtn)
        self.btnType1Prev = tk.Button(self.frmType1SelBtn, image=self.iconType1Prev, command=self.JumpPrevType1)
        self.btnType1Prev.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)
        self.iconType1Next = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'next.png')), master=self.frmType1SelBtn)
        self.btnType1Next = tk.Button(self.frmType1SelBtn, image=self.iconType1Next, command=self.JumpNextType1)
        self.btnType1Next.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)

        tk.Frame(self.frmType1Top, height=5).pack(side=tk.TOP, anchor=tk.NW)

        ## Mass
        self.frmType1BaseProp = tk.Frame(self.frmType1Top)
        self.frmType1BaseProp.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, pady=2)
        self.lblType1BaseProp = tk.Label(self.frmType1BaseProp, text='設置面 : ')
        self.lblType1BaseProp.pack(side=tk.LEFT, anchor=tk.W)

        self.frmType1BaseSize = tk.Frame(self.frmType1Top)
        self.frmType1BaseSize.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=10, pady=2)
        self.lblType1BaseSize = tk.Label(self.frmType1BaseSize, text='要素サイズ: ')
        self.lblType1BaseSize.pack(side=tk.LEFT, anchor=tk.W)
        self.entType1BaseSize = tk.Entry(self.frmType1BaseSize, width=10)
        self.entType1BaseSize.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entType1BaseSize.insert(tk.END, 20)

        tk.Frame(self.frmType1Top, height=10).pack(side=tk.TOP, anchor=tk.NW)

        # Ctrl
        self.frmType1Ctrl = tk.Frame(self.frmType1Top)
        self.frmType1Ctrl.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        self.btnType1Create = tk.Button(self.frmType1Ctrl, text='作成', command=self.CreateBolt1, width=btnWidth)
        self.btnType1Create.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        self.btnType1Undo = tk.Button(self.frmType1Ctrl, text='戻す', command=self.Undo, width=btnWidth)
        self.btnType1Undo.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        self.backup.Append(self.btnType1Undo)

        tk.Frame(self.frmType1, height=5).pack(side=tk.TOP, anchor=tk.NW)

    def JumpPrevType1(self):
        self.Type1PageIndex -= 1
        self.UpdateType1Widgets()

    def JumpNextType1(self):
        self.Type1PageIndex += 1
        self.UpdateType1Widgets()
    
    def JumpIndexType1(self, idx):
        self.Type1PageIndex = idx
        self.UpdateType1Widgets()

    def UpdateType1Widgets(self):
        self.UpdateType1Fig()
        self.UpdateType1ButtonState()
        self.UpdateButtonFG()

    def UpdateType1Fig(self):
        self.frmType1Hole.forget()
        self.frmType1Base.forget()
        if self.Type1PageIndex == 0:
            self.frmType1Hole.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'CylinderFace'
        elif self.Type1PageIndex == 1:
            self.frmType1Base.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'Face'
        else:
            pass
        simlab.setSelectionFilter(selectionFilter)

    def UpdateType1ButtonState(self):
        self.btnType1Prev.config(state='normal')
        self.btnType1Next.config(state='normal')
        if self.Type1PageIndex == 0:
            self.btnType1Prev.config(state='disabled')
        elif self.Type1PageIndex == 1:
            self.btnType1Next.config(state='disabled')
        else:
            pass

        self.btnType1Create.config(state='normal')
        if not simlab.isGroupPresent(self.Type1Hole) or not simlab.isGroupPresent(self.Type1Base):
            self.btnType1Create.config(state='disabled')

    def CreateType2Tab(self):
        self.frmType2Top = tk.Frame(self.frmType2)
        self.frmType2Top.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        # Tips
        btnWidth = 10       

        self.frmTyp2Select = tk.Frame(self.frmType2Top)
        self.frmTyp2Select.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        # Select washer
        self.frmType2Whasher = tk.Frame(self.frmTyp2Select)
        self.frmType2Whasher.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        tk.Label(self.frmType2Whasher, text='Tips: ワッシャー面を選択してボタンを押してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmType2Whasher, height=5).pack(side=tk.TOP, anchor=tk.NW)
        self.iconBolt2Washer = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bolt2_1.png')), master=self.frmType2Whasher)
        tk.Label(self.frmType2Whasher, image=self.iconBolt2Washer).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnType2Washer = tk.Button(self.frmType2Whasher, text='ワッシャー面', command=self.SelectType2Washer)
        self.btnType2Washer.place(x=90, y=35)

        # Select top arc edge
        self.frmType2TopEdge = tk.Frame(self.frmTyp2Select)
        tk.Label(self.frmType2TopEdge, text='Tips: ボルト穴の上の円弧エッジを選択してボタンを押してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmType2TopEdge, height=5).pack(side=tk.TOP, anchor=tk.NW)
        self.iconBolt2TopEdge = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bolt2_2.png')), master=self.frmType2TopEdge)
        tk.Label(self.frmType2TopEdge, image=self.iconBolt2TopEdge).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnType2TopEdge = tk.Button(self.frmType2TopEdge, text='上の円弧エッジ', command=self.SelectType2TopEdge)
        self.btnType2TopEdge.place(x=90, y=50)

        # Select bottom arc edge
        self.frmType2BottomEdge = tk.Frame(self.frmTyp2Select)
        tk.Label(self.frmType2BottomEdge, text='Tips: ボルト穴の下の円弧エッジを選択してボタンを押してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmType2BottomEdge, height=5).pack(side=tk.TOP, anchor=tk.NW)
        self.iconBolt2BottomEdge = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bolt2_3.png')), master=self.frmType2BottomEdge)
        tk.Label(self.frmType2BottomEdge, image=self.iconBolt2BottomEdge).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnType2BottomEdge = tk.Button(self.frmType2BottomEdge, text='下の円弧エッジ', command=self.SelectType2BottomEdge)
        self.btnType2BottomEdge.place(x=90, y=215)

        # Specify values
        self.frmType2Val = tk.Frame(self.frmTyp2Select)
        tk.Label(self.frmType2Val, text='Tips: パラメータを指定して[作成]を押してください。').pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Frame(self.frmType2Val, height=5).pack(side=tk.TOP, anchor=tk.NW)        
        self.frmType2ValFV = tk.Frame(self.frmType2Val)
        self.frmType2ValFV.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)
        self.iconBolt2Val = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bolt2_4.png')), master=self.frmType2ValFV)
        tk.Label(self.frmType2ValFV, image=self.iconBolt2Val).pack(side=tk.LEFT, anchor=tk.NW, padx=5)

        self.frmType2ValV = tk.LabelFrame(self.frmType2ValFV, text=' Beam ')
        self.frmType2ValV.pack(side=tk.TOP, anchor=tk.NW, expand=0, fill=tk.X)

        tk.Label(self.frmType2ValV, text='N1 : ').grid(row=0, column=0, pady=2)
        tk.Label(self.frmType2ValV, text='分割数 : ').grid(row=0, column=1)
        self.entType2N1 = tk.Entry(self.frmType2ValV, width=5)
        self.entType2N1.grid(row=0, column=2)
        self.entType2N1.insert(tk.END, 6)

        tk.Label(self.frmType2ValV, text='N2 : ').grid(row=1, column=0, pady=2)
        tk.Label(self.frmType2ValV, text='分割数 : ').grid(row=1, column=1)
        self.entType2N2 = tk.Entry(self.frmType2ValV, width=5)
        self.entType2N2.grid(row=1, column=2)
        tk.Label(self.frmType2ValV, text='長さ : ').grid(row=2, column=1)
        self.entType2N2D = tk.Entry(self.frmType2ValV, width=5)
        self.entType2N2D.grid(row=2, column=2)
        self.entType2N2.insert(tk.END, 2)
        self.entType2N2D.insert(tk.END, 10)

        tk.Frame(self.frmType2ValV, height=5).grid(row=3, column=0)

        self.frmType2Sp = tk.LabelFrame(self.frmType2ValFV, text=' Spring ')
        self.frmType2Sp.pack(side=tk.TOP, anchor=tk.NW, expand=0, fill=tk.X)

        self.frmType2Coord = tk.Frame(self.frmType2Sp)
        self.frmType2Coord.pack(side=tk.TOP, anchor=tk.W)
        self.lblType2Coord = tk.Label(self.frmType2Coord, text='座標系 : ')
        self.lblType2Coord.pack(side=tk.LEFT, anchor=tk.W)

        coords = coordinate.GetAllCoordinates()
        self.type2Coord = tk.StringVar()
        if len(coords) != 0:
            self.type2Coord.set(coords[0])
        self.cmbType2Coords = ttk.Combobox(self.frmType2Coord, values=coords, textvariable=self.type2Coord, width=20, state='readonly')
        self.cmbType2Coords.pack(side=tk.LEFT, anchor=tk.W)

        tk.Label(self.frmType2Sp, text='剛性 : ').pack(side=tk.TOP, anchor=tk.NW)
        self.frmType2SpT = tk.Frame(self.frmType2Sp)
        self.frmType2SpT.pack(side=tk.TOP, anchor=tk.NW, padx=5)

        tk.Label(self.frmType2SpT, text='CSV : ').pack(side=tk.LEFT, anchor=tk.W)
        self.type2Type = tk.StringVar()
        self.cmbType2Type = ttk.Combobox(self.frmType2SpT, width=18, state='readonly', values=[], textvariable=self.type2Type)
        self.cmbType2Type.pack(side=tk.LEFT, anchor=tk.W, pady=2)
        self.cmbType2Type.bind('<<ComboboxSelected>>' , self.springs.Select)

        self.frmType2SpG = tk.Frame(self.frmType2Sp)
        self.frmType2SpG.pack(side=tk.TOP, anchor=tk.NW, padx=5, pady=2)
        tk.Label(self.frmType2SpG, text='Sx :').grid(row=0, column=0, pady=2)
        tk.Label(self.frmType2SpG, text='Sy :').grid(row=1, column=0, pady=2)
        tk.Label(self.frmType2SpG, text='Sz :').grid(row=2, column=0, pady=2)
        self.entType2Sx = tk.Entry(self.frmType2SpG, width=15)
        self.entType2Sy = tk.Entry(self.frmType2SpG, width=15)
        self.entType2Sz = tk.Entry(self.frmType2SpG, width=15)
        self.entType2Sx.grid(row=0, column=1, padx=2)
        self.entType2Sy.grid(row=1, column=1, padx=2)
        self.entType2Sz.grid(row=2, column=1, padx=2)

        self.entType2Sx.insert(tk.END, 0)
        self.entType2Sy.insert(tk.END, 0)
        self.entType2Sz.insert(tk.END, 0)

        self.springs.AppendWidget(self.cmbType2Type, self.type2Type, self.entType2Sx, self.entType2Sy, self.entType2Sz)

        tk.Frame(self.frmType2Sp, height=2).pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmType2Top, height=5).pack(side=tk.TOP, anchor=tk.NW)

        # select ctrl
        self.frmType2SelCtrl = tk.Frame(self.frmType2Top)
        self.frmType2SelCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        self.frmType2SelBtn = tk.Frame(self.frmType2SelCtrl)
        self.frmType2SelBtn.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconType2Prev = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'prev.png')), master=self.frmType2SelBtn)
        self.btnType2Prev = tk.Button(self.frmType2SelBtn, image=self.iconType2Prev, command=self.JumpPrevType2)
        self.btnType2Prev.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)
        self.iconType2Next = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'next.png')), master=self.frmType2SelBtn)
        self.btnType2Next = tk.Button(self.frmType2SelBtn, image=self.iconType2Next, command=self.JumpNextType2)
        self.btnType2Next.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)

        tk.Frame(self.frmType2Top, height=5).pack(side=tk.TOP, anchor=tk.NW)

        # Ctrl
        self.frmType2Ctrl = tk.Frame(self.frmType2Top)
        self.frmType2Ctrl.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        self.btnType2Create = tk.Button(self.frmType2Ctrl, text='作成', command=self.CreateBolt2, width=btnWidth)
        self.btnType2Create.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        self.btnType2Undo = tk.Button(self.frmType2Ctrl, text='戻す', command=self.Undo, width=btnWidth)
        self.btnType2Undo.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        self.backup.Append(self.btnType2Undo)

        tk.Frame(self.frmType1, height=5).pack(side=tk.TOP, anchor=tk.NW)

    def JumpPrevType2(self):
        self.Type2PageIndex -= 1
        self.UpdateType2Widgets()

    def JumpNextType2(self):
        self.Type2PageIndex += 1
        self.UpdateType2Widgets()
    
    def JumpIndexType2(self, idx):
        self.Type2PageIndex = idx
        self.UpdateType2Widgets()

    def UpdateType2Widgets(self):
        self.UpdateType2Fig()
        self.UpdateType2ButtonState()
        self.UpdateButtonFG()

    def UpdateType2Fig(self):
        self.frmType2Whasher.forget()
        self.frmType2TopEdge.forget()
        self.frmType2BottomEdge.forget()
        self.frmType2Val.forget()
        if self.Type2PageIndex == 0:
            self.frmType2Whasher.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'Face'
        elif self.Type2PageIndex == 1:
            self.frmType2TopEdge.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'CircleEdge'
        elif self.Type2PageIndex == 2:
            self.frmType2BottomEdge.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'CircleEdge'
        elif self.Type2PageIndex == 3:
            self.frmType2Val.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'Face'
        else:
            pass
        simlab.setSelectionFilter(selectionFilter)

    def UpdateType2ButtonState(self):
        self.btnType2Prev.config(state='normal')
        self.btnType2Next.config(state='normal')
        if self.Type2PageIndex == 0:
            self.btnType2Prev.config(state='disabled')
        elif self.Type2PageIndex == 3:
            self.btnType2Next.config(state='disabled')
        else:
            pass

        self.btnType2Create.config(state='normal')
        if not simlab.isGroupPresent(self.Type2Washer) or not simlab.isGroupPresent(self.Type2TopEdge) or not simlab.isGroupPresent(self.Type2BottomEdge):
            self.btnType2Create.config(state='disabled')
    
    def ChangeTab(self, event):
        simlabutil.ClearSelection()

        cid = self.nb.index('current')
        if cid == 0:
            self.UpdateType1Widgets()
        elif cid == 1:
            self.UpdateType2Widgets()
        elif cid == 2:
            self.UpdateType3Widgets()
        elif cid == 3:
            self.UpdateType4Widgets()

    def SelectType1Hole(self):
        faces = simlab.getSelectedEntities('Face')
        if len(faces) == 0:
            messagebox.showinfo('情報','ボルト穴面を選択した後、[ボルト穴面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.Type1Hole)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.Type1Hole)

        simlabutil.ClearSelection()
        self.JumpNextType1()

    def SelectType1Base(self):
        faces = simlab.getSelectedEntities('Face')
        if len(faces) == 0:
            messagebox.showinfo('情報','設置面を選択した後、[設置面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.Type1Base)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.Type1Base)

        simlabutil.ClearSelection()
        self.UpdateType1Widgets()

    def CreateBolt1(self):
        if not simlab.isGroupPresent(self.Type1Hole) or not simlab.isGroupPresent(self.Type1Base):
            messagebox.showinfo('情報','両面を選択してください。')
            return
        try:
            elemSize = float(self.entType1BaseSize.get())
        except:
            messagebox.showinfo('情報','実数を指定してください。')
            return
        
        self.backup.Save('Bolt1')

        CreateType1Bolt(self.Type1Hole, self.Type1Base, elemSize)

        simlablib.DeleteGroups([self.Type1Hole, self.Type1Base])
        self.JumpIndexType1(0)

    def SelectType2Washer(self):
        faces = simlab.getSelectedEntities('Face')
        if len(faces) == 0:
            messagebox.showinfo('情報','ワッシャー面を選択した後、[ワッシャー面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.Type2Washer)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.Type2Washer)

        simlabutil.ClearSelection()
        self.JumpNextType2()

    def SelectType2TopEdge(self):
        edges = simlab.getSelectedEntities('Edge')
        if len(edges) == 0:
            messagebox.showinfo('情報','上の円弧を選択した後、[上の円弧エッジ] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.Type2TopEdge)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.Type2TopEdge)

        result = simlabutil.GetArcEdgeAttributes(modelName, self.Type2TopEdge)
        if len(result) == 0:
            simlablib.DeleteGroups(self.Type2TopEdge)
            messagebox.showinfo('情報','円弧情報を取得できません。円弧エッジを選択してください。')
            return

        simlabutil.ClearSelection()
        self.JumpNextType2()

    def SelectType2BottomEdge(self):
        edges = simlab.getSelectedEntities('Edge')
        if len(edges) == 0:
            messagebox.showinfo('情報','上の円弧を選択した後、[上の円弧エッジ] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.Type2BottomEdge)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.Type2BottomEdge)

        result = simlabutil.GetArcEdgeAttributes(modelName, self.Type2BottomEdge)
        if len(result) == 0:
            simlablib.DeleteGroups(self.Type2BottomEdge)
            messagebox.showinfo('情報','円弧情報を取得できません。円弧エッジを選択してください。')
            return

        simlabutil.ClearSelection()
        self.JumpNextType2()

    def CreateBolt2(self):
        if not simlab.isGroupPresent(self.Type2Washer) or not simlab.isGroupPresent(self.Type2TopEdge) or not simlab.isGroupPresent(self.Type2BottomEdge):
            messagebox.showinfo('情報','面、エッジを選択してください。')
            return

        try:
            numN1 = int(self.entType2N1.get())
            numN2 = int(self.entType2N2.get())
            lenN2 = float(self.entType2N2D.get())
            CID = coordinate.GetID(self.type2Coord.get())
            s = np.array([
                float(self.entType2Sx.get()),
                float(self.entType2Sy.get()),
                float(self.entType2Sz.get()),
            ])
        except:
            messagebox.showinfo('情報','実数で指定してください。')
            return
        
        self.backup.Save('Bolt2')

        springName = self.type2Type.get()
        if len(springName) == 0:
            springName = BOLT2_SPRING

        CreateType2Bolt(self.Type2Washer, self.Type2TopEdge, self.Type2BottomEdge, numN1, numN2, lenN2, CID, s, springName)

        simlablib.DeleteGroups([self.Type2Washer, self.Type2TopEdge, self.Type2BottomEdge])
        self.JumpIndexType2(0)

    def CreateType3Tab(self):
        self.frmType3Top = tk.Frame(self.frmType3)
        self.frmType3Top.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        # Tips
        self.lblNote3 = tk.Label(self.frmType3Top, text='Tips: 固定する面（BRGは任意）を選択して、[ 作成 ]ボタンを押してください。')
        self.lblNote3.pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmType3Top, height=5).pack(side=tk.TOP, anchor=tk.NW)
        btnWidth = 10
        
        self.frmTyp3Select = tk.Frame(self.frmType3Top)
        self.frmTyp3Select.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        # Select holes
        self.frmType3Hole = tk.Frame(self.frmTyp3Select)
        self.frmType3Hole.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        self.iconBolt3Hole = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bolt3_mon.png')), master=self.frmType3Hole)
        tk.Label(self.frmType3Hole, image=self.iconBolt3Hole).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnType3Mon = tk.Button(self.frmType3Hole, text='MOTOR', command=self.SelectType3Mon)
        self.btnType3Mon.place(x=210, y=0)
        self.btnType3Nut = tk.Button(self.frmType3Hole, text='NUT', command=self.SelectType3Nut)
        self.btnType3Nut.place(x=130, y=25)
        self.btnType3Brg = tk.Button(self.frmType3Hole, text='SUPPORT BRG', command=self.SelectType3Brg)
        self.btnType3Brg.place(x=25, y=30)

        tk.Frame(self.frmType3Top, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmType3Val = tk.Frame(self.frmType3Top)
        self.frmType3Val.pack(side=tk.TOP, anchor=tk.NW, padx=5)

        self.frmType3BM = tk.Frame(self.frmType3Val)
        self.frmType3BM.pack(side=tk.TOP, anchor=tk.NW)

        self.frmType3Coord = tk.Frame(self.frmType3BM)
        self.frmType3Coord.pack(side=tk.TOP, anchor=tk.W)
        self.lblType3Coord = tk.Label(self.frmType3Coord, text='座標系 : ')
        self.lblType3Coord.pack(side=tk.LEFT, anchor=tk.W)

        coords = coordinate.GetAllCoordinates()
        self.type3Coord = tk.StringVar()
        if len(coords) != 0:
            self.type3Coord.set(coords[0])
        self.cmbType3Coords = ttk.Combobox(self.frmType3Coord, values=coords, textvariable=self.type3Coord, width=20, state='readonly')
        self.cmbType3Coords.pack(side=tk.LEFT, anchor=tk.W)

        self.frmType3Beam = tk.LabelFrame(self.frmType3BM, text='Beam:')
        self.frmType3Beam.pack(side=tk.LEFT, anchor=tk.NW, padx=5)

        self.frmType3BeamN1 = tk.Frame(self.frmType3Beam)
        self.frmType3BeamN1.pack(side=tk.TOP, anchor=tk.NW, pady=2)
        tk.Label(self.frmType3BeamN1, text='N1:分割数:').pack(side=tk.LEFT, anchor=tk.W)
        self.entType3NumN1 = tk.Entry(self.frmType3BeamN1, width=5)
        self.entType3NumN1.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entType3NumN1.insert(tk.END, 10)

        self.frmType3BeamN2 = tk.Frame(self.frmType3Beam)
        self.frmType3BeamN2.pack(side=tk.TOP, anchor=tk.NW, pady=2)
        tk.Label(self.frmType3BeamN2, text='N2:分割数:').pack(side=tk.LEFT, anchor=tk.W)
        self.entType3NumN2 = tk.Entry(self.frmType3BeamN2, width=5)
        self.entType3NumN2.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entType3NumN2.insert(tk.END, 10)

        self.frmType3MPC = tk.LabelFrame(self.frmType3BM, text='MPC:')
        self.frmType3MPC.pack(side=tk.LEFT, anchor=tk.NW, padx=5)

        self.bType3MPCX = tk.BooleanVar()
        self.bType3MPCY = tk.BooleanVar()
        self.bType3MPCZ = tk.BooleanVar()
        self.bType3MPCRX = tk.BooleanVar()
        self.bType3MPCRY = tk.BooleanVar()
        self.bType3MPCRZ = tk.BooleanVar()
        self.bType3MPCX.set(False)
        self.bType3MPCY.set(False)
        self.bType3MPCZ.set(False)
        self.bType3MPCRX.set(False)
        self.bType3MPCRY.set(False)
        self.bType3MPCRZ.set(False)

        self.chkType3MPCX = tk.Checkbutton(self.frmType3MPC, text='X', variable=self.bType3MPCX)
        self.chkType3MPCX.grid(row=0, column=0)
        self.chkType3MPCRX = tk.Checkbutton(self.frmType3MPC, text='Rx', variable=self.bType3MPCRX)
        self.chkType3MPCRX.grid(row=0, column=1, padx=10, pady=2)

        self.chkType3MPCY = tk.Checkbutton(self.frmType3MPC, text='Y', variable=self.bType3MPCY)
        self.chkType3MPCY.grid(row=1, column=0)
        self.chkType3MPCRY = tk.Checkbutton(self.frmType3MPC, text='Ry', variable=self.bType3MPCRY)
        self.chkType3MPCRY.grid(row=1, column=1, padx=10, pady=2)

        self.chkType3MPCZ = tk.Checkbutton(self.frmType3MPC, text='Z', variable=self.bType3MPCZ)
        self.chkType3MPCZ.grid(row=2, column=0)
        self.chkType3MPCRZ = tk.Checkbutton(self.frmType3MPC, text='Rz', variable=self.bType3MPCRZ)
        self.chkType3MPCRZ.grid(row=2, column=1, padx=10, pady=2)

        self.frmType3Sp = tk.LabelFrame(self.frmType3Top, text='Spring 剛性:')
        self.frmType3Sp.pack(side=tk.TOP, anchor=tk.NW, padx=5)

        r = 1
        tk.Label(self.frmType3Sp, text='MOTOR:').grid(row=r, column=0, pady=2, sticky='w')
        self.entType3MonStiffX = tk.Entry(self.frmType3Sp, width=8)
        self.entType3MonStiffX.grid(row=r, column=1, padx=2)
        self.entType3MonStiffX.insert(tk.END, 0)

        self.entType3MonStiffY = tk.Entry(self.frmType3Sp, width=8)
        self.entType3MonStiffY.grid(row=r, column=2, padx=2)
        self.entType3MonStiffY.insert(tk.END, 0)

        self.entType3MonStiffZ = tk.Entry(self.frmType3Sp, width=8)
        self.entType3MonStiffZ.grid(row=r, column=3, padx=2)
        self.entType3MonStiffZ.insert(tk.END, 0)

        self.type3MonType = tk.StringVar()
        self.cmbType3MonType = ttk.Combobox(self.frmType3Sp, width=18, state='readonly', values=[], textvariable=self.type3MonType)
        self.cmbType3MonType.grid(row=r, column=4, padx=2)
        self.cmbType3MonType.bind('<<ComboboxSelected>>' , self.springs.Select)

        self.springs.AppendWidget(self.cmbType3MonType, self.type3MonType, self.entType3MonStiffX, self.entType3MonStiffY, self.entType3MonStiffZ)

        r += 1
        tk.Label(self.frmType3Sp, text='NUT:').grid(row=r, column=0, pady=2, sticky='w')
        self.entType3NutStiffX = tk.Entry(self.frmType3Sp, width=8)
        self.entType3NutStiffX.grid(row=r, column=1, padx=2)
        self.entType3NutStiffX.insert(tk.END, 0)

        self.entType3NutStiffY = tk.Entry(self.frmType3Sp, width=8)
        self.entType3NutStiffY.grid(row=r, column=2, padx=2)
        self.entType3NutStiffY.insert(tk.END, 0)

        self.entType3NutStiffZ = tk.Entry(self.frmType3Sp, width=8)
        self.entType3NutStiffZ.grid(row=r, column=3, padx=2)
        self.entType3NutStiffZ.insert(tk.END, 0)

        self.type3NutType = tk.StringVar()
        self.cmbType3NutType = ttk.Combobox(self.frmType3Sp, width=18, state='readonly', values=[], textvariable=self.type3NutType)
        self.cmbType3NutType.grid(row=r, column=4, padx=2)
        self.cmbType3NutType.bind('<<ComboboxSelected>>' , self.springs.Select)

        self.springs.AppendWidget( self.cmbType3NutType, self.type3NutType, self.entType3NutStiffX, self.entType3NutStiffY, self.entType3NutStiffZ)

        r += 1
        tk.Label(self.frmType3Sp, text='BRG:').grid(row=r, column=0, pady=2, sticky='w')
        self.entType3BrgStiffX = tk.Entry(self.frmType3Sp, width=8)
        self.entType3BrgStiffX.grid(row=r, column=1, padx=2)
        self.entType3BrgStiffX.insert(tk.END, 0)

        self.entType3BrgStiffY = tk.Entry(self.frmType3Sp, width=8)
        self.entType3BrgStiffY.grid(row=r, column=2, padx=2)
        self.entType3BrgStiffY.insert(tk.END, 0)

        self.entType3BrgStiffZ = tk.Entry(self.frmType3Sp, width=8)
        self.entType3BrgStiffZ.grid(row=r, column=3, padx=2)
        self.entType3BrgStiffZ.insert(tk.END, 0)

        self.type3BrgType = tk.StringVar()
        self.cmbType3BrgType = ttk.Combobox(self.frmType3Sp, width=18, state='readonly', values=[], textvariable=self.type3BrgType)
        self.cmbType3BrgType.grid(row=r, column=4, padx=2)
        self.cmbType3BrgType.bind('<<ComboboxSelected>>' , self.springs.Select)

        self.springs.AppendWidget( self.cmbType3BrgType, self.type3BrgType, self.entType3BrgStiffX, self.entType3BrgStiffY, self.entType3BrgStiffZ)

        tk.Frame(self.frmType3Sp, height=5).grid(row=4)

        tk.Frame(self.frmType3Top, height=5).pack(side=tk.TOP, anchor=tk.NW)

        # Ctrl
        self.frmType3Ctrl = tk.Frame(self.frmType3Top)
        self.frmType3Ctrl.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        self.btnType3Create = tk.Button(self.frmType3Ctrl, text='作成', command=self.CreateBolt3, width=btnWidth)
        self.btnType3Create.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        self.btnType3Undo = tk.Button(self.frmType3Ctrl, text='戻す', command=self.Undo, width=btnWidth)
        self.btnType3Undo.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        self.backup.Append(self.btnType3Undo)

    def SelectType3Mon(self):
        faces = simlab.getSelectedEntities('Face')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.Type3Mon)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.Type3Mon)

        simlabutil.ClearSelection()
        self.UpdateType3Widgets()

    def SelectType3Nut(self):
        faces = simlab.getSelectedEntities('Face')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.Type3Nut)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.Type3Nut)

        simlabutil.ClearSelection()
        self.UpdateType3Widgets()

    def SelectType3Brg(self):
        faces = simlab.getSelectedEntities('Face')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.Type3Brg)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.Type3Brg)

        simlabutil.ClearSelection()
        self.UpdateType3Widgets()

    def UpdateType3Widgets(self):
        self.UpdateButtonFG()

        self.btnType3Create.config(state='normal')
        if not simlab.isGroupPresent(self.Type3Mon) or not simlab.isGroupPresent(self.Type3Nut):
            self.btnType3Create.config(state='disabled')

        simlab.setSelectionFilter('CylinderFace')

    def CreateBolt3(self):
        if not simlab.isGroupPresent(self.Type3Mon) or not simlab.isGroupPresent(self.Type3Nut):
            messagebox.showinfo('情報','MOTOR, NUTは選択してください。')
            return

        try:
            numN1 = int(self.entType3NumN1.get())
            numN2 = int(self.entType3NumN2.get())
            nums = [numN1, numN2]

            bX = self.bType3MPCX.get()
            bY = self.bType3MPCY.get()
            bZ = self.bType3MPCZ.get()
            bRX = self.bType3MPCRX.get()
            bRY = self.bType3MPCRY.get()
            bRZ = self.bType3MPCRZ.get()
            dofs = [bX, bY, bZ, bRX, bRY, bRZ]

            CID = coordinate.GetID(self.type3Coord.get())

            monX = float(self.entType3MonStiffX.get())
            monY = float(self.entType3MonStiffY.get())
            monZ = float(self.entType3MonStiffZ.get())
            mon = np.array([monX,monY,monZ])

            nutX = float(self.entType3NutStiffX.get())
            nutY = float(self.entType3NutStiffY.get())
            nutZ = float(self.entType3NutStiffZ.get())
            nut = np.array([nutX,nutY,nutZ])

            brgX = float(self.entType3BrgStiffX.get())
            brgY = float(self.entType3BrgStiffY.get())
            brgZ = float(self.entType3BrgStiffZ.get())
            brg = np.array([brgX,brgY,brgZ])
        except:
            messagebox.showinfo('情報','整数を指定してください。')
            return

        self.backup.Save('Bolt3')

        springNameMon = self.type3MonType.get()
        if len(springNameMon) == 0:
            springNameMon = 'MOTOR_'
        springNameNut = self.type3NutType.get()
        if len(springNameNut) == 0:
            springNameNut = 'NUT_'
        springNameBrg = self.type3BrgType.get()
        if len(springNameBrg) == 0:
            springNameBrg = 'BRG_'
        names = [springNameMon, springNameNut, springNameBrg]

        CreateType3Bolt(self.Type3Mon, self.Type3Nut, self.Type3Brg, nums, dofs, CID, mon, nut, brg, names)

        simlablib.DeleteGroups([self.Type3Mon, self.Type3Nut, self.Type3Brg])
        self.UpdateType3Widgets()

    def CreateType4Tab(self):
        self.frmType4Top = tk.Frame(self.frmType4)
        self.frmType4Top.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        # Tips
        self.lblNote4 = tk.Label(self.frmType4Top, text='Tips: 穴底の円弧エッジと設置面を選択して、[ 作成 ]ボタンを押してください。')
        self.lblNote4.pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmType1Top, height=5).pack(side=tk.TOP, anchor=tk.NW)
        btnWidth = 10
        
        self.frmTyp4Select = tk.Frame(self.frmType4Top)
        self.frmTyp4Select.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)

        # Select holes
        self.frmType4Hole = tk.Frame(self.frmTyp4Select)
        self.frmType4Hole.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X)
        self.iconBolt4Hole = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bolt4_turret.png')), master=self.frmTyp4Select)
        tk.Label(self.frmType4Hole, image=self.iconBolt4Hole).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnType4Hole = tk.Button(self.frmType4Hole, text='円弧エッジ', command=self.SelectType4ArcEdges)
        self.btnType4Hole.place(x=185, y=85)

        # Select base
        self.frmType4Base = tk.Frame(self.frmTyp4Select)
        self.iconBolt4Base = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bolt4_cup.png')), master=self.frmTyp4Select)
        tk.Label(self.frmType4Base, image=self.iconBolt4Base).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnType4Base = tk.Button(self.frmType4Base, text='設置面', command=self.SelectType4BaseFaces)
        self.btnType4Base.place(x=150, y=100)

        # select ctrl
        self.frmType4SelCtrl = tk.Frame(self.frmType4Top)
        self.frmType4SelCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        self.frmType4SelBtn = tk.Frame(self.frmType4SelCtrl)
        self.frmType4SelBtn.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconType4Prev = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'prev.png')), master=self.frmType4SelBtn)
        self.btnType4Prev = tk.Button(self.frmType4SelBtn, image=self.iconType4Prev, command=self.JumpPrevType4)
        self.btnType4Prev.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)
        self.iconType4Next = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'next.png')), master=self.frmType4SelBtn)
        self.btnType4Next = tk.Button(self.frmType4SelBtn, image=self.iconType4Next, command=self.JumpNextType4)
        self.btnType4Next.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)

        tk.Frame(self.frmType4Top, height=10).pack(side=tk.TOP, anchor=tk.NW)

        ## spring
        self.frmType4Sp = tk.LabelFrame(self.frmType4Top, text='Spring :')
        self.frmType4Sp.pack(side=tk.TOP, anchor=tk.NW, padx=5)

        self.frmType4Coord = tk.Frame(self.frmType4Sp)
        self.frmType4Coord.pack(side=tk.TOP, anchor=tk.W)
        self.lblType4Coord = tk.Label(self.frmType4Coord, text='座標系 : ')
        self.lblType4Coord.pack(side=tk.LEFT, anchor=tk.W)

        coords = coordinate.GetAllCoordinates()
        self.type4Coord = tk.StringVar()
        if len(coords) != 0:
            self.type4Coord.set(coords[0])
        self.cmbType4Coords = ttk.Combobox(self.frmType4Coord, values=coords, textvariable=self.type4Coord, width=20, state='readonly')
        self.cmbType4Coords.pack(side=tk.LEFT, anchor=tk.W)

        self.frmType4SpSti = tk.LabelFrame(self.frmType4Sp, text='剛性:')
        self.frmType4SpSti.pack(side=tk.TOP, anchor=tk.NW, padx=5)

        self.frmType4SpType = tk.Frame(self.frmType4SpSti)
        self.frmType4SpType.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmType4SpType, text='CSV:').pack(side=tk.LEFT, anchor=tk.W)

        self.type4Type = tk.StringVar()
        self.cmbType4Type = ttk.Combobox(self.frmType4SpType, width=18, state='readonly', values=[], textvariable=self.type4Type)
        self.cmbType4Type.pack(side=tk.LEFT, anchor=tk.W)
        self.cmbType4Type.bind('<<ComboboxSelected>>' , self.springs.Select)

        tk.Frame(self.frmType4SpSti, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmType4SpStiffR = tk.Frame(self.frmType4SpSti)
        self.frmType4SpStiffR.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmType4SpStiffR, text='R:').pack(side=tk.LEFT, anchor=tk.W)        
        self.entType4SpStiffR = tk.Entry(self.frmType4SpStiffR, width=10)
        self.entType4SpStiffR.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entType4SpStiffR.insert(tk.END, 0.0)

        self.frmType4SpStiffT = tk.Frame(self.frmType4SpSti)
        self.frmType4SpStiffT.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmType4SpStiffT, text='θ:').pack(side=tk.LEFT, anchor=tk.W)        
        self.entType4SpStiffT = tk.Entry(self.frmType4SpStiffT, width=10)
        self.entType4SpStiffT.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entType4SpStiffT.insert(tk.END, 0.0)

        self.frmType4SpStiffZ = tk.Frame(self.frmType4SpSti)
        self.frmType4SpStiffZ.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmType4SpStiffZ, text='Z:').pack(side=tk.LEFT, anchor=tk.W)        
        self.entType4SpStiffZ = tk.Entry(self.frmType4SpStiffZ, width=10)
        self.entType4SpStiffZ.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entType4SpStiffZ.insert(tk.END, 0.0)

        self.springs.AppendWidget(self.cmbType4Type, self.type4Type, self.entType4SpStiffR, self.entType4SpStiffT, self.entType4SpStiffZ)

        tk.Frame(self.frmType4Sp, height=5).pack(side=tk.TOP, anchor=tk.NW)

        tk.Frame(self.frmType4Top, height=10).pack(side=tk.TOP, anchor=tk.NW)

        # Ctrl
        self.frmType4Ctrl = tk.Frame(self.frmType4Top)
        self.frmType4Ctrl.pack(side=tk.TOP, anchor=tk.NW, padx=5)
        self.btnType4Create = tk.Button(self.frmType4Ctrl, text='作成', command=self.CreateBolt4, width=btnWidth)
        self.btnType4Create.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        self.btnType4Undo = tk.Button(self.frmType4Ctrl, text='戻す', command=self.Undo, width=btnWidth)
        self.btnType4Undo.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        self.backup.Append(self.btnType4Undo)

        tk.Frame(self.frmType4, height=5).pack(side=tk.TOP, anchor=tk.NW)

    def JumpPrevType4(self):
        self.Type4PageIndex -= 1
        self.UpdateType4Widgets()

    def JumpNextType4(self):
        self.Type4PageIndex += 1
        self.UpdateType4Widgets()
    
    def JumpIndexType4(self, idx):
        self.Type4PageIndex = idx
        self.UpdateType4Widgets()

    def UpdateType4Widgets(self):
        self.UpdateType4Fig()
        self.UpdateType4ButtonState()
        self.UpdateButtonFG()

    def UpdateType4Fig(self):
        self.frmType4Hole.forget()
        self.frmType4Base.forget()
        if self.Type4PageIndex == 0:
            self.frmType4Hole.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'CircleEdge'
        elif self.Type4PageIndex == 1:
            self.frmType4Base.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
            selectionFilter = 'Face'
        else:
            pass
        simlab.setSelectionFilter(selectionFilter)

    def UpdateType4ButtonState(self):
        self.btnType4Prev.config(state='normal')
        self.btnType4Next.config(state='normal')
        if self.Type4PageIndex == 0:
            self.btnType4Prev.config(state='disabled')
        elif self.Type4PageIndex == 1:
            self.btnType4Next.config(state='disabled')
        else:
            pass

        self.btnType4Create.config(state='normal')
        if not simlab.isGroupPresent(self.Type4ArcEdges) or not simlab.isGroupPresent(self.Type4BaseFaces):
            self.btnType4Create.config(state='disabled')

    def SelectType4ArcEdges(self):
        edges = simlab.getSelectedEntities('Edge')
        if len(edges) == 0:
            messagebox.showinfo('情報','円弧エッジを選択した後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.Type4ArcEdges)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.Type4ArcEdges)

        simlabutil.ClearSelection()
        self.JumpNextType4()

    def SelectType4BaseFaces(self):
        faces = simlab.getSelectedEntities('Face')
        if len(faces) == 0:
            messagebox.showinfo('情報','面を選択した後、ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.Type4BaseFaces)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Face', faces, self.Type4BaseFaces)

        simlabutil.ClearSelection()
        self.UpdateType4Widgets()
    
    def CreateBolt4(self):
        if not simlab.isGroupPresent(self.Type4ArcEdges) or not simlab.isGroupPresent(self.Type4BaseFaces):
            messagebox.showinfo('情報','エンティティを選択してください。')
            return

        try:
            CID = coordinate.GetID(self.type4Coord.get())
            stiffR = float(self.entType4SpStiffR.get())
            stiffT = float(self.entType4SpStiffT.get())
            stiffZ = float(self.entType4SpStiffZ.get())
        except:
            messagebox.showinfo('情報','実数を指定してください。')
            return

        self.backup.Save('Bolt4')

        springName = self.type4Type.get()
        if len(springName) == 0:
            springName = 'TURRET_COUPLING'

        importlib.reload(springutil)
        stiff = (stiffR, stiffT, stiffZ)

        if CID == -1:
            messagebox.showinfo('情報', "Select coordinate id")
            return
        springProp = springName, stiff, CID
        springutil.connectRbeToBodyWithSpring(self.Type4ArcEdges, self.Type4BaseFaces, springProp)

        self.JumpIndexType4(0)

    def UpdateButtonFG(self):
        groups = [self.Type1Hole, self.Type1Base, self.Type2Washer, self.Type2TopEdge, self.Type2BottomEdge, self.Type3Mon, self.Type3Nut, self.Type3Brg, self.Type4ArcEdges, self.Type4BaseFaces]
        widgets = [self.btnType1Hole, self.btnType1Base, self.btnType2Washer, self.btnType2TopEdge, self.btnType2BottomEdge, self.btnType3Mon, self.btnType3Nut, self.btnType3Brg, self.btnType4Hole, self.btnType4Base]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def Undo(self):
        self.backup.Load()

        # Since the CAD model is displayed immediately after Undo, it is confusing
        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        simlablib.DeleteGroups([self.Type1Hole, self.Type1Base, self.Type2Washer, self.Type2TopEdge, self.Type2BottomEdge, self.Type3Mon, self.Type3Nut, self.Type3Brg, self.Type4ArcEdges, self.Type4BaseFaces])
        super().CloseDialog()