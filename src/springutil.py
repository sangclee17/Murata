from hwx import simlab
import math
import importlib
import simlablib
import simlabutil
import bearingutil
import muratautil
import tkinter.messagebox as messagebox
import numpy as np
import random
import mpcutil

TURRENT_SPRING = "Turrent_Spring"
MAX_ID_SPRING = 'Max_ID_Spring'
MAX_ID_COORDINATE = 'Max_ID_Coordinate'
COORD_NAME = "Cylindrical_Coordinate"
MAX_ID_RBE = "MAX_ID_RBE"

def connectTwoFacesUsingSpring(springProp, onTopOfMPC, tolerance, innerFaceGrp, outerFaceGrp, threeNodesGrp):
    springName, numSpring, springStiff, coordId = springProp
    Sx, Sy, Sz = springStiff
    modelNm = simlab.getModelName("FEM")

    threeNodeIds = simlab.getEntityFromGroup(threeNodesGrp)
    threePoints = []
    for thisNodeId in threeNodeIds:
        threePoints.append(simlab.getNodePositionFromNodeID(modelNm, thisNodeId))
    if threePoints: threePoints = tuple(threePoints)

    distanceBetweenTwoFaces = tolerance
  
    _, radiusOfCircularInnerEdges  = muratautil.getArcAttGivenThreePoints(threePoints)
    innerFaceEnts = simlab.getEntityFromGroup(innerFaceGrp)
    outerFaceEnts = simlab.getEntityFromGroup(outerFaceGrp)
    # innerEdges = _associatedEdgesWithFaces(innerFaceEnts, circularEdgeOnly= True)

    if not onTopOfMPC:
        deckFaceEnts = outerFaceEnts
        gasketFaceEnts = innerFaceEnts
        importlib.reload(mpcutil)
        imprinted_ok = mpcutil.imprintGasket(deckFaceEnts, gasketFaceEnts, tolerance = tolerance)
        if not imprinted_ok:
            messagebox.showinfo("情報","Fail to match mesh")
            return

    planeTolerance = 3
    innerNodes = _getNodesOnPlane(innerFaceEnts, threePoints, tolerance = planeTolerance)

    cornerNodes = _getCornerNodes(innerNodes)
    innerCornerNodes = tuple(set(cornerNodes).intersection(set(innerNodes)))
    # simlablib.CreateGroup(modelNm, "node", innerCornerNodes, "InnerCornerNodes")

    nodesOnSpring = _getEquallyDistantNodeIdsAmongCircularNodes(numSpring, radiusOfCircularInnerEdges, innerCornerNodes)
    # simlablib.CreateGroup(modelNm, "node", nodesOnSpring, "SpringNodes")
    outerFaceEnts = simlab.getEntityFromGroup(outerFaceGrp)
    outerNodes = _getNodesOnPlane(outerFaceEnts, threePoints, tolerance = planeTolerance)
    cornerNodes = _getCornerNodes(outerNodes)
    if not outerNodes or not cornerNodes:
        messagebox.showinfo("情報","Fail to grab nodes on the outer face")
        return
    outerCornerNodes = tuple(set(cornerNodes).intersection(set(outerNodes)))
    # simlablib.CreateGroup(modelNm, "node", outerCornerNodes, "OuterCornerNodes")

    for thisNode in innerCornerNodes:
        nodeInBubble = _findTheClosestNodeIdInBubble(thisNode, outerFaceEnts, outerCornerNodes, distanceBetweenTwoFaces)
        if nodeInBubble:
            _moveANodeTo(nodeInBubble, thisNode)
            if thisNode in nodesOnSpring:
                springId = muratautil.getUniqueId(MAX_ID_SPRING)
                springNm = springName + str(springId)
                if Sx != 0:_connectTwoNodesInSpring(springNm+"_R", thisNode, nodeInBubble, coordId, Sx, constraint = "x")
                if Sy != 0:_connectTwoNodesInSpring(springNm+"_T", thisNode, nodeInBubble, coordId, Sy, constraint = "y")
                if Sz != 0:_connectTwoNodesInSpring(springNm+"_Z", thisNode, nodeInBubble, coordId, Sz, constraint = "z")

def connectTwoFacesUsingRbe(outerFaceGrp, innerFaceGrp, threeNodesGrp):
    numOfGreenPoint = 6
    modelNm = simlab.getModelName("FEM")

    threeNodeIds = simlab.getEntityFromGroup(threeNodesGrp)
    threePoints = []
    for thisNodeId in threeNodeIds:
        threePoints.append(simlab.getNodePositionFromNodeID(modelNm, thisNodeId))
    if threePoints: threePoints = tuple(threePoints)

    distanceBetweenTwoFaces = 1
  
    _, radiusOfCircularInnerEdges  = muratautil.getArcAttGivenThreePoints(threePoints)
    innerFaceEnts = simlab.getEntityFromGroup(innerFaceGrp)
    outerFaceEnts = simlab.getEntityFromGroup(outerFaceGrp)

    deckFaceEnts = outerFaceEnts
    gasketFaceEnts = innerFaceEnts
    importlib.reload(mpcutil)
    imprinted_ok = mpcutil.imprintGasket(deckFaceEnts, gasketFaceEnts, tolerance = distanceBetweenTwoFaces)
    if not imprinted_ok:
        messagebox.showinfo("情報","Fail to match mesh")
        return
    planeTolerance = 3

    innerNodes = _getNodesOnPlane(innerFaceEnts, threePoints, tolerance = planeTolerance)
    cornerNodes = _getCornerNodes(innerNodes)
    innerCornerNodes = tuple(set(cornerNodes).intersection(set(innerNodes)))
    # print("innerCornerNodes", innerCornerNodes)

    outerFaceEnts = simlab.getEntityFromGroup(outerFaceGrp)
    outerNodes = _getNodesOnPlane(outerFaceEnts, threePoints, tolerance = planeTolerance)
    cornerNodes = _getCornerNodes(outerNodes)
    if not outerNodes or not cornerNodes:
        messagebox.showinfo("情報","Fail to grab nodes on the outer face")
        return
    outerCornerNodes = tuple(set(cornerNodes).intersection(set(outerNodes)))
    # print("outerCornerNodes", outerCornerNodes)

    independentNodes = outerCornerNodes
    dependentNodes = innerCornerNodes
    dependentFaceEnts = innerFaceEnts

    rbeNodes = _getEquallyDistantNodeIdsAmongCircularNodes(numOfGreenPoint, radiusOfCircularInnerEdges, independentNodes)
    normV = np.array(muratautil.getNormalVector(threePoints[0], threePoints[1], threePoints[2]))
    # print("rbeNodes", rbeNodes)

    for thisNode in independentNodes:
        nodeInBubble = _findTheClosestNodeIdInBubble(thisNode, dependentFaceEnts, dependentNodes, distanceBetweenTwoFaces)
        _moveANodeTo(nodeInBubble, thisNode)
        if thisNode in rbeNodes:
            nodesToConnect = _getThreeNodesToConnect(nodeInBubble, normV)
            _manualRBE(thisNode, nodesToConnect)
            # print("greenNodeId", thisNode)
            # print("connectNodeId", nodesToConnect)

def _getThreeNodesToConnect(theNodeId, normV):                
    elemId = _getConnected2DelemFromNode(theNodeId)
    midNodes = getMidNodesFrom2Delem(elemId)
    distDict = {}
    for thisNode in midNodes:
        aDist = _distanceBetweenTwoNodes(theNodeId, thisNode)
        distDict[thisNode] = aDist
    
    sortedDist = sorted(distDict.items(), key= lambda x:x[1])

    closest4Nodes = [x[0] for x in sortedDist[:4]]

    femModel = simlab.getModelName("FEM")

    vectDict = {}
    greenNodeP = np.array(simlab.getNodePositionFromNodeID(femModel, theNodeId))
    for thisNode in closest4Nodes:
        nodeP = np.array(simlab.getNodePositionFromNodeID(femModel, thisNode))
        vect = nodeP - greenNodeP
        vect_norm = vect/np.linalg.norm(vect)
        dotVal = abs(np.dot(vect_norm, normV))
        vectDict[thisNode] = dotVal
    
    sortedVect = sorted(vectDict.items(), key = lambda x:x[1])

    nodesToConnect = [x[0] for x in sortedVect[:3]]
    
    return nodesToConnect

def _getCornerNodes(nodeIds):
    modelNm = simlab.getModelName("FEM")
    SelectNodeAssociatedEntities=''' <SelectNodeAssociatedEntities UUID="6731d198-667e-49c9-8612-c7d980368508">
    <InputNodes Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Node>'''+ str(nodeIds).strip("()[]") +''',</Node>
    </Entities>
    </InputNodes>
    <Option Value="2Delements"/>
    <Groupname Value="Select2Delements_68"/>
    </SelectNodeAssociatedEntities>'''
    simlab.execute(SelectNodeAssociatedEntities)
    elemEnts = simlab.getEntityFromGroup("Select2Delements_68")
    _deleteGrp("Select2Delements_68")

    SelectElementAssociatedEntities=''' <SelectElementAssociatedEntities UUID="7062f057-0e48-4ccc-ad73-e60584e8ff26">
    <InputElement Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Element>'''+ str(elemEnts).strip("()[]") +''',</Element>
    </Entities>
    </InputElement>
    <Option Value="Cornernodes"/>
    <Groupname Value="SelectCornerNodes_69"/>
    </SelectElementAssociatedEntities>'''
    simlab.execute(SelectElementAssociatedEntities)
    cornerNodes = simlab.getEntityFromGroup("SelectCornerNodes_69")
    _deleteGrp("SelectCornerNodes_69")
    return cornerNodes

def _renameGroupNm(nameFrom, nameTo):
    RenameGroupControl=''' <RenameGroupControl CheckBox="ON" UUID="d3addb85-3fd0-4972-80af-e699f96e9045">
    <tag Value="-1"/>
    <Name Value="'''+ nameFrom +'''"/>
    <NewName Value="'''+ nameTo +'''"/>
    <Output/>
    </RenameGroupControl>'''
    simlab.execute(RenameGroupControl)

def _getConnected2DelemFromNode(nodeId):
    modelNm = simlab.getModelName("FEM")

    groupNm = "Select2Delements_94"

    SelectNodeAssociatedEntities=''' <SelectNodeAssociatedEntities UUID="6731d198-667e-49c9-8612-c7d980368508">
    <InputNodes Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Node>'''+ str(nodeId) +'''</Node>
    </Entities>
    </InputNodes>
    <Option Value="2Delements"/>
    <Groupname Value="'''+ groupNm +'''"/>
    </SelectNodeAssociatedEntities>'''
    simlab.execute(SelectNodeAssociatedEntities)

    elems = simlab.getEntityFromGroup(groupNm)
    _deleteGrp(groupNm)

    return elems 

def getMidNodesFrom2Delem(elemId):
    modelNm = simlab.getModelName("FEM")
    groupNm = "SelectMidNodes_95"
    SelectElementAssociatedEntities=''' <SelectElementAssociatedEntities UUID="7062f057-0e48-4ccc-ad73-e60584e8ff26">
    <InputElement Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Element>'''+ str(elemId).strip("()") +'''</Element>
    </Entities>
    </InputElement>
    <Option Value="Mid-nodes"/>
    <Groupname Value="'''+ groupNm +'''"/>
    </SelectElementAssociatedEntities>'''
    simlab.execute(SelectElementAssociatedEntities)

    midNodes = simlab.getEntityFromGroup(groupNm)
    _deleteGrp(groupNm)
    return midNodes

def _manualRBE(greenNode, nodesToConnect):
    modelNm = simlab.getModelName("FEM")
    max_rbe_num = muratautil.getUniqueId(MAX_ID_RBE)
    rbeNm = "RBE_{}".format(max_rbe_num)

    ManualRBE=''' <ManualRBE CheckBox="ON" UUID="80E2032A-27AE-493a-9162-844BD2CC0823">
    <tag Value="-1"/>
    <Name Value="'''+ rbeNm +'''"/>
    <Independent>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Node>'''+ str(greenNode).strip("()""[]") +'''</Node>
    </Entities>
    </Independent>
    <Dependent>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Node>'''+ str(nodesToConnect).strip("()""[]") +'''</Node>
    </Entities>
    </Dependent>
    <Type Value="Nodes"/>
    <Output/>
    </ManualRBE>'''
    simlab.execute(ManualRBE)

def connectRbeToBodyWithSpring(rbeEdgeGrp, HPfaceGrpNm,springProp):
    springName, SprStiff, coordId = springProp
    Sx, Sy, Sz = SprStiff
    RBE_Name = _createRBE(rbeEdgeGrp) # RBE 2
    # bearingutil.createRBEProperty(RBE_Name, "Rbe2", RBE_Name)

    rbePlanarFaces = _associatedFacesWithEdges(simlab.getEntityFromGroup(rbeEdgeGrp),"Entities")
    rbeEdgeBody = _associatedBodyWithFace(rbePlanarFaces)
    if len(rbeEdgeBody) != 1:
        messagebox.showinfo("情報","Multiple associated body or none")
        return

    rbeNodes = tuple(set(_associatedNodesWithBody(RBE_Name))-set(_associatedNodesWithBody(rbeEdgeBody[0])))
    rbeNodeCoordinates = []
    modelNm = simlab.getModelName("FEM")
    for thisNode in rbeNodes:
        nodePos = simlab.getNodePositionFromNodeID(modelNm, thisNode)
        rbeNodeCoordinates.append(nodePos)
    createHardPointsMC(HPfaceGrpNm, rbeNodeCoordinates)

    defaultMeshSize = _getParameter("DefaultMeshSize", "double")
    defaultMaxAngle = _getParameter("DefaultMaxAngle", "double")
    defaultAspectRatio = _getParameter("DefaultAspectRatio", "double")
    if not defaultMeshSize or not defaultMaxAngle or not defaultAspectRatio:
        messagebox.showinfo("情報","No default mesh parameters")
        return

    meshProp =  defaultMeshSize, defaultMaxAngle, defaultAspectRatio
    _remeshFaceGrp(meshProp, HPfaceGrpNm)

    HPface = simlab.getEntityFromGroup(HPfaceGrpNm)
    HPfaceNodes = associatedNodesWithFace(HPface)

    faceId = list(simlab.getEntityFromGroup(HPfaceGrpNm))
    faceThreePoints = simlab.definePlaneFromEntity(simlab.getModelName("FEM"), faceId[0])

    for thisNode in rbeNodes:
        dist = _getDistanceBetweenPlaneAndPoint(thisNode,faceThreePoints)
        nodeInBubble = _findTheClosestNodeIdInBubble(thisNode, HPface, HPfaceNodes, sphereRadius = dist + 1, startTolerance=0.3, increaseBubbleSizeBy=0.1)
        # print(thisNode,nodeInBubble,dist)
        if nodeInBubble:
            springId = muratautil.getUniqueId(MAX_ID_SPRING)
            springNm = springName+str(springId)
            if Sx != 0: _connectTwoNodesInSpring(springNm + "_R", thisNode, nodeInBubble, coordId, Sx, constraint = "x")
            if Sy != 0: _connectTwoNodesInSpring(springNm + "_T", thisNode, nodeInBubble, coordId, Sy, constraint = "y")
            if Sz != 0: _connectTwoNodesInSpring(springNm + "_Z", thisNode, nodeInBubble, coordId, Sz, constraint = "z")
    
def _getDistanceBetweenPlaneAndPoint(aNodeId, planeThreePoints):
    modelNm = simlab.getModelName("FEM")
    nodeP = simlab.getNodePositionFromNodeID(modelNm, aNodeId)

    # get plane equation for the plane
    p1,p2,p3 = planeThreePoints
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)

    v1 = p2 - p1
    v2 = p3 - p1

    cross_product = np.cross(v1,v2)

    a = cross_product[0]
    b = cross_product[1]
    c = cross_product[2]
    d = -(cross_product[0] * p1[0] + cross_product[1] * p1[1] + cross_product[2] * p1[2])

    dist = abs(a*nodeP[0] + b*nodeP[1] + c*nodeP[2] + d)/math.sqrt(a*a +b*b + c*c)
    
    return dist

def _getParameter(key, valueType):
    """
        valueType: "int", "double", "string"
    """
    if not simlab.isParameterPresent(key):
        return None
    
    if valueType == "int": return simlab.getIntParameter("$"+key)
    elif valueType == "double": return simlab.getDoubleParameter("$"+key)
    elif valueType == "string": return simlab.getStringParameter("$"+key)


def _getEquallyDistantNodeIdsAmongCircularNodes(nodeNums, Rad, nodeIds):
    st_dist = []
    for i in range(1, int(nodeNums/2) + 1):
        angle = 360/nodeNums
        radInAngle = i * angle * math.pi / 180
        dist = math.sqrt(2 * Rad * Rad - 2 * Rad * Rad * math.cos(radInAngle))
        st_dist.append(dist)
    pivotNode = nodeIds[0]
    nodeIds = nodeIds[1:]
    # print(st_dist)
    distFromPivotNode = {}
    for thisNode in nodeIds:
        dist = _distanceBetweenTwoNodes(pivotNode, thisNode)
        distFromPivotNode[thisNode] = dist
    
    minDistNodeIds = list()
    for i in range(len(st_dist)):
        tempDict = {}
        for key, value in distFromPivotNode.items():
            distDiff = abs(value - st_dist[i])
            tempDict[key] = distDiff
        sortedDist = sorted(tempDict.items(), key=lambda item: item[1])
        minDistNodeIds.append(sortedDist[0][0])
        if i != len(st_dist) - 1:
            minDistNodeIds.append(sortedDist[1][0])
        # print("{}:{}".format(st_dist[i], minDistNodeIds))
    minDistNodeIds.append(pivotNode)
    # print("PivotNode", pivotNode)
    # _deleteGrp("smallDistNodes")
    # simlablib.CreateGroup(simlab.getModelName("FEM"),"node", minDistNodeIds,"smallDistNodes")
    return minDistNodeIds

def createHardPointsMC(faceGrpNm, dataPoints):
    MAX_HARDPOINT = "MAX_HARDPOINTS_MC"
    dataPointsString = ",".join(str(pt).strip("[]""()") for pt in dataPoints)

    mcId = muratautil.getUniqueId(MAX_HARDPOINT)
    mcNm = "{}_{}".format("HardPoints_MeshControl", mcId)

    MeshControls=''' <MeshControl isObject="1" CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
    <tag Value="-1"/>
    <MeshControlName Value="'''+ mcNm +'''"/>
    <MeshControlType Value="Hard Points"/>
    <Entities>
    <Group>"'''+ faceGrpNm +'''",</Group>
    </Entities>
    <Reverse ModelIds="" EntityTypes="" Value=""/>
    <MeshColor Value=""/>
    <HardPoints>
    <Geometry Value="2"/>
    <Tolerance Value="1"/>
    <DataPoints Value="'''+ dataPointsString +''',"/>
    <!-- To specify the csv file path , please uncomment out the below line.   -->
    <!--
    <Hard_Points_File Value="D:/Testing/HardPoints.csv" /> 
            -->
    </HardPoints>
    </MeshControl>'''
    simlab.execute(MeshControls)


def _findTheClosestNodeIdInBubble(nodeId, faceIds, cornerNodes, sphereRadius, startTolerance = 1, increaseBubbleSizeBy = 1):
    _deleteGrp("Show_Nodes")
    modelNm = simlab.getModelName("FEM")
    nodePosition = simlab.getNodePositionFromNodeID(modelNm, nodeId)
    tolerance = startTolerance
    count = 1
    while not checkShowNodesInCornerNodes(cornerNodes):
        if count > 10:return None

        NodesByRegion=''' <NodesByRegion UUID="ad9db725-dcb3-4f9c-abd7-0e7a8cf64d05">
        <tag Value="-1"/>
        <Name Value="Show Nodes"/>
        <SupportEntities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Face>'''+ str(faceIds).strip("()[]") +''',</Face>
        </Entities>
        </SupportEntities>
        <Option Value="0"/>
        <RegionData Type="Sphere">
        <SphereData>
        <SphereCenter Value="'''+ str(nodePosition).strip("[]""()") +'''"/>
        <Radius Value="'''+ str(sphereRadius) +'''"/>
        </SphereData>
        </RegionData>
        <On Value="1"/>
        <Above Value="0"/>
        <Below Value="1"/>
        <Tolerance Value="'''+ str(tolerance) +'''"/>
        <MaximumCount Value="5000"/>
        <ShowSurfaceNodes Value="1"/>
        <CreateGroup Value="1"/>
        </NodesByRegion>'''
        simlab.execute(NodesByRegion)
        tolerance += increaseBubbleSizeBy
        count += 1
    nodeIds = simlab.getEntityFromGroup("Show_Nodes")
    _deleteGrp("Show_Nodes")
    for thisNode in nodeIds:
        if thisNode in cornerNodes:
            return thisNode
    return None

def _getNodesOnPlane(faceId, threePoints, tolerance):
    _deleteGrp("Show_Nodes")
    modelNm = simlab.getModelName("FEM")
    NodesByRegion=''' <NodesByRegion UUID="ad9db725-dcb3-4f9c-abd7-0e7a8cf64d05">
    <tag Value="-1"/>
    <Name Value="Show Nodes"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceId).strip("[]()") +''',</Face>
    </Entities>
    </SupportEntities>
    <Option Value="0"/>
    <RegionData Type="Plane">
    <PlaneData Value="'''+ ",".join(str(v) for pt in threePoints for v in pt) +'''"/>
    </RegionData>
    <On Value="1"/>
    <Above Value="0"/>
    <Below Value="0"/>
    <Tolerance Value="''' + str(tolerance)+ '''"/>
    <MaximumCount Value="5000"/>
    <ShowSurfaceNodes Value="1"/>
    <CreateGroup Value="1"/>
    </NodesByRegion>'''
    simlab.execute(NodesByRegion)
    nodeIds = simlab.getEntityFromGroup("Show_Nodes")
    _deleteGrp("Show_Nodes")
    return nodeIds if nodeIds else None

def checkShowNodesInCornerNodes(cornerNodes):
    checked = False
    if simlab.isGroupPresent("Show_Nodes"):
        nodeIds = simlab.getEntityFromGroup("Show_Nodes")
        for thisNode in nodeIds:
            if thisNode in cornerNodes:
                checked = True
    return checked


def createCylindricalCoordinate(coordPrefix, coordinateID, cNodeId, xNodeId, zNodeId):

    coordinateName = coordinateName = "{}_{}".format(coordPrefix,coordinateID)

    modelNm = simlab.getModelName("FEM")
    CreateCoordinateSystem=''' <Coordinate UUID="b625f5cd-2925-4f9f-94a2-b58854934f8b" isObject="2" BCType="Coordinates">
    <tag Value="-1"/>
    <StackIndex Value="CoordinateXZPoint"/>
    <CoordinateXYPoint>
    <Name Value=""/>
    <Center ModelIds="" EntityTypes="" Value=""/>
    <PointX ModelIds="" EntityTypes="" Value=""/>
    <PointY ModelIds="" EntityTypes="" Value=""/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    <AttachToNodes Value="0"/>
    </CoordinateXYPoint>
    <CoordinateXZPoint>
    <Name Value="'''+ coordinateName +'''"/>
    <Center>
    <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Node>'''+ str(cNodeId) +''',</Node>
    </Entities>
    </Center>
    <PointX>
    <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Node>'''+ str(xNodeId) +'''</Node>
    </Entities>
    </PointX>
    <PointZ>
    <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Node>'''+ str(zNodeId) +'''</Node>
    </Entities>
    </PointZ>
    <AxisID Value="'''+ str(coordinateID) +'''"/>
    <Type Value="Cylindrical" Index="1"/>
    <AttachToNodes Value="0"/>
    </CoordinateXZPoint>
    <CoordinateXZPlane>
    <Name Value=""/>
    <Center ModelIds="" EntityTypes="" Value=""/>
    <PointZ ModelIds="" EntityTypes="" Value=""/>
    <XZPlane ModelIds="" EntityTypes="" Value=""/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    <AttachToNodes Value="0"/>
    </CoordinateXZPlane>
    <CoordinateCylindrical>
    <Name Value=""/>
    <Face ModelIds="" EntityTypes="" Value=""/>
    <Node ModelIds="" EntityTypes="" Value=""/>
    <PointOnR Value="0"/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    </CoordinateCylindrical>
    <CoordinateCircular>
    <Name Value=""/>
    <Edge ModelIds="" EntityTypes="" Value=""/>
    <Node ModelIds="" EntityTypes="" Value=""/>
    <PointOnR Value="0"/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
    </CoordinateCircular>
    <CoordinateFillet>
    <SupportEntities ModelIds="" EntityTypes="" Value=""/>
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
    <XArc1 ModelIds="" EntityTypes="" Value=""/>
    <XArc2 ModelIds="" EntityTypes="" Value=""/>
    <YArc1 ModelIds="" EntityTypes="" Value=""/>
    <YArc2 ModelIds="" EntityTypes="" Value=""/>
    </CoordinateArcPairs>
    </Coordinate>'''
    simlab.execute(CreateCoordinateSystem)

def _moveANodeTo(nodeIdFrom, nodeIdTo):
    """
        input-> nodeIdToMove in int, nodeIdTo in int 
    """
    modelNm = simlab.getModelName('FEM')
    absPosition = simlab.getNodePositionFromNodeID(modelNm, nodeIdTo)
    p_x, p_y, p_z = absPosition
    NodeAbsolute=''' <NodeAbsolute UUID="8560C8D3-ED6E-4919-AA96-E301AA0747EE">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>T75_TOPASSY_21229_1901291_SM.gda</Model>
    <Node>'''+ str(nodeIdFrom) +''',</Node>
    </Entities>
    </SupportEntities>
    <DeltaX Value="'''+ str(p_x) +'''"/>
    <DeltaY Value="'''+ str(p_y) +'''"/>
    <DeltaZ Value="'''+ str(p_z) +'''"/>
    <Copy Value="0"/>
    </NodeAbsolute>'''
    simlab.execute(NodeAbsolute)

def _connectTwoNodesInSpring(springNm, node1, node2, axisID, stiffness, constraint = "x"):
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
    <Node>'''+ str(node1) +''','''+ str(node2) +''',</Node>
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

def _remeshFaceGrp(meshProp, faceGrpNm, preserveBoundaryEdge = 1):
    """
        elementSize, maxAnglePerElem, aspectRat = meshProp (tuple)
        faceGrpNm (string)
    """
    elementSize, maxAnglePerElem, aspectRat = meshProp
    LocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh1"/>
    <SupportEntities>
    <Group>"'''+ faceGrpNm +'''",</Group>
    </SupportEntities>
    <ElemType Value="1"/>
    <AverageElemSize Value="'''+ str(elementSize) +'''"/>
    <MinElemSize Value="'''+ str(int(elementSize/10)) +'''"/>
    <PreserveBoundaryEdges Value="'''+ str(preserveBoundaryEdge) +'''"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="'''+ str(maxAnglePerElem) +'''"/>
    <CurvatureMinElemSize Value="'''+ str(int(elementSize/2)) +'''"/>
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
    _updateModel()

def _associatedBodyWithFace(faceIds):
    """
        input-> faceIds in tuple
        return-> body name in tuple
    """
    modelNm = simlab.getModelName("FEM")
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

def _updateModel():
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def _associatedFacesWithEdges(edges, outputOption = "Group"):
    """
        input-> edgeIds in tuple, outputOption ("Group" or "Entities")
        return -> group name in string or faceEntities in tuple
    """
    modelNm = simlab.getModelName("FEM")

    _deleteGrp("adjFacesAlongEdges")
    SelectEdgeAssociatedEntities=''' <SelectEdgeAssociatedEntities UUID="551fdd5b-6a8c-4a30-8ab0-fbaf9257343e">
    <InputEdges Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Edge>'''+ ",".join(str(v) for v in edges) +''',</Edge>
    </Entities>
    </InputEdges>
    <Option Value="Faces"/>
    <Groupname Value="adjFacesAlongEdges"/>
    </SelectEdgeAssociatedEntities>'''
    simlab.execute(SelectEdgeAssociatedEntities)

    if outputOption == "Entities":
        faceEnts = simlab.getEntityFromGroup('adjFacesAlongEdges')
        _deleteGrp("adjFacesAlongEdges")
        return faceEnts
    return "adjFacesAlongEdges"

def _distanceBetweenTwoNodes(Node1, Node2):
    femModel = simlab.getModelName("FEM")
    c1_x, c1_y, c1_z = simlab.getNodePositionFromNodeID(femModel,Node1)
    c2_x, c2_y, c2_z =simlab.getNodePositionFromNodeID(femModel,Node2)
    return math.sqrt(math.pow((c1_x - c2_x),2) + math.pow((c1_y - c2_y),2) + math.pow((c1_z - c2_z),2))


def _deleteGrp(grpNm):
    if isinstance(grpNm, tuple) or isinstance(grpNm, list): grpNm = ",".join(grpNm)
    DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +''',"/>
    <Output/>
    </DeleteGroupControl>'''
    simlab.execute(DeleteGroupControl)
    
def _createRBE(edgeGrp, connectionType = 0):
    '''
        RBE2: connectionType = 0 
        RBE3: connectionType = 1
    '''
    max_rbe_num = muratautil.getUniqueId(MAX_ID_RBE)
    rbeNm = "RBE_{}".format(max_rbe_num)

    CreateRBE=''' <RBE CheckBox="ON" UUID="27FFA2F5-6388-4d38-A5FA-6DCC883C1094">
    <tag Value="-1"/>
    <Name Value="'''+ rbeNm +'''"/>
    <InputEntities>
    <Group>"'''+ edgeGrp +'''",</Group>
    </InputEntities>
    <Group Value=""/>
    <CenterSupportNodes ModelIds="" EntityTypes="" Value=""/>
    <CenterSupportEdges ModelIds="" EntityTypes="" Value=""/>
    <BodyAllNodes Value="1"/>
    <BodyFewNodes Value="0"/>
    <CenterNodeId Value=""/>
    <ConnectionType Value="'''+ str(connectionType) +'''"/>
    <RadiusLimit Value="0.0" Check="0"/>
    <CenterNodeSupport Value="0"/>
    <IgnoreMidNodes Value="0"/>
    <CreateRBE_eachRegion Value="1"/>
    <Output/>
    </RBE>'''
    simlab.execute(CreateRBE)
    return rbeNm

def associatedNodesWithFace(faceId):
    if isinstance(faceId, tuple) or isinstance(faceId, list): faceId = str(faceId).strip("()""[]")
    else: faceId = str(faceId)
    modelNm = simlab.getModelName("FEM")
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ faceId +''',</Face>
    </Entities>
    </InputFaces>
    <Option Value="Nodes"/>
    <Groupname Value="SelectNodes_25"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)

    nodeIds = simlab.getEntityFromGroup("SelectNodes_25")
    _deleteGrp("SelectNodes_25")
    return nodeIds
    
def _associatedNodesWithBody(bodyNm):
    modelNm = simlab.getModelName("FEM")
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </InputBody>
    <Option Value="Nodes"/>
    <Groupname Value="SelectNodes_20"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)
    allBodyEdges = simlab.getEntityFromGroup("SelectNodes_20")
    _deleteGrp("SelectNodes_20")
    return allBodyEdges


