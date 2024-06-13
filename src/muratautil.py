from hwx import simlab
import simlablib
import simlabutil
import numpy as np
import random

BASE_NODE = 10000000

def _isInt(strNum):
    result = True
    try:
        _ = int(strNum)
    except ValueError:
        result = False
    return result


def getPrefixOfBodyNm(bodyNm):
    bodyNm_sp = bodyNm.split("_")

    bodyNmStrOnly = []
    for bodyNm in bodyNm_sp:
        if not _isInt(bodyNm):
            bodyNmStrOnly.append(bodyNm)
    return "_".join(bodyNmStrOnly)

def arrangeBodiesByPrefix(bodyNms):
    nameDict = {}
    for thisBody in bodyNms:
        prefix = getPrefixOfBodyNm(thisBody)
        if not prefix in nameDict:
            nameDict[prefix] = []
        nameDict[prefix].append(thisBody)
    return nameDict

def getNormalVector(pt1, pt2, pt3):
    p1 = np.array(pt1)
    p2 = np.array(pt2)
    p3 = np.array(pt3)

    v1 = p2 - p1
    v2 = p3 - p1
    crossV = np.cross(v1, v2)
    normV = crossV/np.linalg.norm(crossV)

    return normV

def getUniqueId(keyNm):
    coordinateID = 1
    if simlab.isParameterPresent(keyNm):
        coordinateID = simlab.getIntParameter('$'+keyNm) + 1
    simlablib.AddIntParameters(keyNm, coordinateID)
    return coordinateID

def createANode(pointCoordinateXYZ):
    Px, Py, Pz= pointCoordinateXYZ

    modelNm = simlab.getModelName("FEM")

    uniqueNodeId = simlabutil.AvailableNodeID(modelNm, baseNodeID=BASE_NODE)

    NodeByXYZ=''' <NodeByXYZ UUID="F200B5A2-D615-4d01-8DE2-25596B3B1EB8">
    <tag Value="-1"/>
    <Name Value=""/>
    <LocalCoordinateSystem Value="0"/>
    <Position Value="'''+ str(Px) +''','''+ str(Py) +''','''+ str(Pz) +'''"/>
    <Node Value="'''+ str(uniqueNodeId) +'''"/>
    <UniqueNodeId Value="0"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </NodeByXYZ>'''
    simlab.execute(NodeByXYZ)
    return uniqueNodeId

def getArcAttribute(edgeId):
    modelNm = simlab.getModelName("FEM")
    if not isinstance(edgeId,int):
        return False
    arcAtt = simlab.getArcEdgeAttributes(modelNm, edgeId)
    if not arcAtt:
        return False
    cPt, rad = arcAtt

    return cPt, rad[0]


def getArcAttGivenThreePoints(threePoints):
    p1,p2,p3 = threePoints
    A = np.array(p1)
    B = np.array(p2)
    C = np.array(p3)
    # print('A=',A)
    # print('B=',B)
    # print('C=',C)
    a = np.linalg.norm(C - B)
    b = np.linalg.norm(C - A)
    c = np.linalg.norm(B - A)

    s = (a + b + c) / 2
    R = a*b*c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))
    b1 = a*a * (b*b + c*c - a*a)
    b2 = b*b * (a*a + c*c - b*b)
    b3 = c*c * (a*a + b*b - c*c)
    P = np.column_stack((A, B, C)).dot(np.hstack((b1, b2, b3)))
    P /= b1 + b2 + b3
    # print('P=',P)

    return P, R

# def getArcEdgeEntity(edgeIds, threePoints = False):
#     modelNm = simlab.getModelName("FEM")
#     edgeIds = list(edgeIds)
#     nodeIds = []

#     for thisEdge in edgeIds:
#         nodes = list(getNodeIdsFromEdgeId(thisEdge))
#         nodeIds.extend(nodes)
    
#     nodeIds = list(set(nodeIds))
#     nodeIds = random.sample(nodeIds, k=3)
#     p1 = simlab.getNodePositionFromNodeID(modelNm, nodeIds[0])
#     p2 = simlab.getNodePositionFromNodeID(modelNm, nodeIds[1])
#     p3 = simlab.getNodePositionFromNodeID(modelNm, nodeIds[2])
#     cpt, rad = getArcAttGivenThreePoints((p1,p2,p3))
   
#     arcAtt = cpt, rad
#     if threePoints:
#         return arcAtt, (p1,p2,p3)
#     return arcAtt

def getNodeIdsFromEdgeId(edgeId):
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

def getParameter(key, valueType):
    """
        valueType: "int", "double", "string"
    """
    if not simlab.isParameterPresent(key):
        return None
    
    if valueType == "int": return simlab.getIntParameter("$"+key)
    elif valueType == "double": return simlab.getDoubleParameter("$"+key)
    elif valueType == "string": return simlab.getStringParameter("$"+key)

def _deleteGrp(grpNm):
    if isinstance(grpNm, tuple) or isinstance(grpNm, list): grpNm = ",".join(grpNm)
    DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +''',"/>
    <Output/>
    </DeleteGroupControl>'''
    simlab.execute(DeleteGroupControl)