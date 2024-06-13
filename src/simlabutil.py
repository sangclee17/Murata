##
# @file simlabutil.py
# @brief SimLab utilities
from hwx import simlab, gui
import os, sys, logging, traceback, importlib, uuid
import numpy as np
from pathlib import Path

PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)
import simlablib
importlib.reload(simlablib)

##
# @brief Deletes all model
# @return nothing
def DeleteAllModel(modelType='All'):
    mdlList = simlab.getAllRootModelNames(modelType)
    for model in mdlList:
        simlablib.DeleteModel(model)

##
# @brief Gets boolean value if model exists
# @param[in] modelName Model name
# @return boolean 1:Exist, 0:Does not exist
def isModelPresent(modelName):
    mdlList = simlab.getAllRootModelNames('All')
    if modelName in mdlList:
        return True
    return False

##
# @brief Gets boolean value if group exists
# @param[in] groupName Group name
# @return boolean 1:Exist, 0:Does not exist
def isGroupPresent(groupName):
    return simlab.isGroupPresent(groupName)

##
# @brief Gets boolean value if body exists
# @param[in] modelName Model name
# @param[in] bodyName Body name
# @return boolean 1:Exist, 0:Does not exist
def isBodyPresent(modelName, bodyName):
    bdyList = simlab.getBodiesWithSubString(modelName, [bodyName])
    if len(bdyList) > 0:
        return True
    return False

##
# @brief Gets a unique name. If there is a duplicate, add a number to the suffix. 'Model.gda' -> 'Model1.gda', 'Model' -> 'Model1' 
# @param[in] sourceName Original name
# @return Unique name
def UniqueModelName(sourceName):
    candidate = sourceName
    icount = 0
    while isModelPresent(candidate):
        icount += 1
        if candidate[-4:].lower() == '.gda':
            candidate = candidate[0:-4] + str(icount) + candidate[-4:]
        else:
            candidate = sourceName + str(icount)
    
    return candidate

##
# @brief Gets a unique name. If there is a duplicate, add a number to the suffix. 'Group' -> 'Group1'
# @param[in] sourceName Original name
# @return Unique name
def UniqueGroupName(sourceName):
    candidate = sourceName
    icount = 0
    while isGroupPresent(candidate):
        icount += 1
        candidate = sourceName + str(icount)
    
    return candidate

##
# @brief Gets a unique name. If there is a duplicate, add a number to the suffix. 'Body' -> 'Body1'
# @param[in] modelName Model name
# @param[in] sourceName Original name
# @return Unique name
def UniqueBodyName(modelName, sourceName):
    candidate = sourceName
    icount = 0
    while isBodyPresent(modelName, candidate):
        icount += 1
        candidate = sourceName + str(icount)
    
    return candidate

##
# @brief Gets node ID that can be created.
# @param[in] modelName Model name
# @param[in] baseNodeID Base node ID
# @return Unique name
def AvailableNodeID(modelName, baseNodeID=1):
    nodeID = baseNodeID
    while len(simlab.getNodePositionFromNodeID(modelName, nodeID)) != 0:
        nodeID += 1
    return nodeID

##
# @brief Clear selection. 
# @note There is no command to clear the selection. So, create a temporary group and clear the selection.
# @return nothing
def ClearSelection():
    tmpName = UniqueGroupName('temp')
    simlablib.CreateEmptyGroup('Face', tmpName)
    simlablib.DeleteGroups(tmpName)

##
# @brief Gets 4 points from 3 points on the plane. (Mesh control needs 4 points.)
# @param[in] pointsOnPlane 3 points on plane. e.g. [[1,0,0],[0,1,0],[-1,0,0]]
# @param[in] sourceName Original name
# @return Unique name
def Convert3PointsOnPlaneTo4Points(pointsOnPlane, planeSize=1000.0):
    pnt1, pnt2, pnt3  = pointsOnPlane
    
    xVec = np.array(pnt2) - np.array(pnt1)
    yVec = np.array(pnt3) - np.array(pnt1)
    xnVec = xVec / np.linalg.norm(xVec)
    ynVec = yVec / np.linalg.norm(yVec)

    zVec = np.cross(xnVec, ynVec)
    znVec = zVec / np.linalg.norm(zVec)
    yVec = np.cross(znVec, xnVec)
    ynVec = yVec / np.linalg.norm(yVec)

    centerPnt = (np.array(pnt1) + np.array(pnt2) + np.array(pnt3)) / 3.0
    pp1 = centerPnt + planeSize * ( xnVec + ynVec)
    pp2 = centerPnt + planeSize * (-xnVec + ynVec)
    pp3 = centerPnt + planeSize * (-xnVec - ynVec)
    pp4 = centerPnt + planeSize * ( xnVec - ynVec)
    
    return [list(pp1), list(pp2), list(pp3), list(pp4)]

##
# @brief Gets center point of entity centroids
# @param[in] modelName Model name.
# @param[in] entityType Entity type. 'Body', 'Face' 
# @param[in] entities Number of times to take random axis. 
# @return center coordinate. e.g. [1,2,3]
def CenterOfCentroids(modelName, entityType, entities):
    numEntity = len(entities)
    if numEntity == 0:
        raise ValueError("Empty Entities.")

    startID = 1000000
    sumValue = np.array([0.0, 0.0, 0.0])

    for entity in entities:
        nodeID = AvailableNodeID(modelName, startID)
        simlablib.CreateNodeByCentroid(modelName, entityType, [entity], nodeID)

        coord = simlab.getNodePositionFromNodeID(modelName, nodeID)
        simlablib.DeleteSelectedOphanNodes(modelName, [nodeID])
        sumValue = sumValue + np.array(coord)

    center = sumValue / numEntity
    return list(center)

##
# @brief Export image files viewed from different directions by rotating at random angles and axes.
# @param[in] exportFolder Folder to export image files.
# @param[in] prefix File name prefix. e.g. prefix1.png, prefix2.png,... 
# @param[in] imageFormat Image format. 'jpg', 'png', 'bmp', 'xpm'
# @param[in] numAxis Number of times to take random axis. 
# @param[in] numAngle Number of times to take a random angle around one axis.
# @param[in] rotationCenter Center of rotation
# @param[in] bodies If specific bodies are specified, displaies only thier bodies and rotation center is set the center point of centroids of their bodies. 
# @note The number of images is numAxis x numAngle.
# @return nothing
def ExportImagesFromRandomDirection(exportFolder, prefix='', imageFormat='png', numAxis=1, numAngle=1, rotationCenter=[0,0,0], modelName='', bodies=[]):
    if not os.path.isdir(exportFolder):
        os.makedirs(exportFolder)

    extDict = {
        'jpg': '.jpg',
        'jpeg': '.jpg',
        'bmp' : '.bmp',
        'png' : '.png',
        'xpm' : '.xpm',
    }
    ext = extDict[imageFormat.lower()]

    np.random.seed(789850299)
    exportFolder = os.path.abspath(exportFolder)
    rotationCenter =rotationCenter.copy()
    bodies = bodies.copy()

    if len(bodies) != 0:
        #simlab.showOrHideEntities(bodies, 'Isolate', modelName, 'Body') # needs ver.2019.2
        rotationCenter = CenterOfCentroids(modelName, 'Body', bodies)

    suffixCount = 1
    iAxis = 0
    while iAxis < numAxis:
        x = np.random.rand() * 2.0 - 1.0
        y = np.random.rand() * 2.0 - 1.0
        z = np.random.rand() * 2.0 - 1.0
        vec = np.array([x,y,z])
        dist = np.linalg.norm(vec)
        if abs(dist) < 1.e-9:
            continue
        
        nvec = list(vec / dist)
        iAxis += 1

        iAngle = 0
        while iAngle < numAngle:
            angle = np.random.rand() * 360.0
            iAngle += 1

            # create view (View from different direction)
            viewName = str(uuid.uuid4()) 
            simlablib.CreateView(viewName, axis=nvec, angle=angle, center=rotationCenter)
            
            # export image file
            while True:
                filePath = os.path.join(exportFolder, prefix + str(suffixCount) + ext)
                suffixCount += 1
                if not os.path.isfile(filePath):
                    break
            simlablib.CaptureImage(filePath)

            # delete view
            simlablib.DeleteView([viewName])

##
# @brief Gets normal vector from group
# @param[in] entityType Entity type. 'Face', 'Edge', 'Node'
# @param[in] groupName Group name. 
# @return normal vector. e.g. [1,2,3]. If the plane cannot be defined, an empty list is returned.
def GetNormalVectorFromGroup(entityType, groupName):
    entityType = entityType.lower()
    keyDict = {
        'face': 'FACEGROUP',
        'edge': 'EDGEGROUP',
        'node': 'NODEGROUP',
    }
    key = keyDict[entityType]

    if not simlab.isGroupPresent(groupName):
        return []

    if entityType == 'node':
        nodes = simlab.getEntityFromGroup(groupName)
        if len(nodes) < 3:
            return []
        modelName = simlab.getModelName('FEM')

        result = []
        result.append(simlab.getNodePositionFromNodeID(modelName, nodes[0]))
        result.append(simlab.getNodePositionFromNodeID(modelName, nodes[1]))

        p1 = np.array(result[0])
        p2 = np.array(result[1])

        v1 = p2 - p1
        for i in range(2, len(nodes)):
            xyz = simlab.getNodePositionFromNodeID(modelName, nodes[i])
            p3 = np.array(xyz)
            v2 = p3 - p1
            n = np.cross(v1, v2)
            m = np.linalg.norm(n)
            if m > 1e-9:
                result.append(xyz)
                break
    else:
        result = simlab.definePlaneFromGroup(groupName, key)

    if len(result) != 3:
        return []

    p1 = np.array(result[0])
    p2 = np.array(result[1])
    p3 = np.array(result[2])

    v1 = p2 - p1
    v2 = p3 - p1
    n = np.cross(v1, v2)
    m = np.linalg.norm(n)
    if m < 1e-9:
        return []

    n /= m
    return n

##
# @brief Get arc edge attributes. If arc attribute was not found in group, search one by one.
# @param[in] modelName Model name. 
# @param[in] groupName Group name. 
# @return ((center xyz), radius). If arc attribute was not found in group, return empty.
def GetArcEdgeAttributes(modelName, groupName):
    result = simlab.getArcEdgeAttributes(groupName)
    if len(result) != 0:
        return result
    
    edges = simlab.getEntityFromGroup(groupName)
    for edge in edges:
        result = simlab.getArcEdgeAttributes(modelName, edge)
        if len(result) != 0:
            return result
    return []

##
# @brief Get cylinder attributes. If cylinder attribute was not found in group, search one by one.
# @param[in] modelName Model name. 
# @param[in] groupName Group name. 
# @return ((center xyz), radius). If cylinder attribute was not found in group, return empty.
def GetCylindricalFaceAttributes(modelName, groupName):
    result = simlab.getCylindricalFaceAttributes(groupName)
    if len(result) != 0:
        return result
    
    faces = simlab.getEntityFromGroup(groupName)
    for face in faces:
        result = simlab.getCylindricalFaceAttributes(modelName, face)
        if len(result) != 0:
            return result
    return []

##
# @brief Get cylinder attributes. If cylinder attribute was not found in group, search one by one.
# @param[in] modelName Model name. 
# @param[in] groupName Group name. 
# @return ((center xyz), radius). If cylinder attribute was not found in group, return empty.
def GetCylindricalFaceAttributes(modelName, groupName):
    result = simlab.getCylindricalFaceAttributes(groupName)
    if len(result) != 0:
        return result
    
    faces = simlab.getEntityFromGroup(groupName)
    for face in faces:
        result = simlab.getCylindricalFaceAttributes(modelName, face)
        if len(result) != 0:
            return result
    return []

if __name__ == '__main__':
    print("Load SimLabUtil") 