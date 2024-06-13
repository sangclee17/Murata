from hwx import simlab
import os, sys, importlib
import numpy as np

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

DEFAULT_MESH_SIZE = "DefaultMeshSize"
DEFAULT_MAX_ANGLE = "DefaultMaxAngle"
DEFAULT_ASPECT_RATIO = "DefaultAspectRatio"

# local
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

import simlablib
import simlabutil

importlib.reload(simlablib)
importlib.reload(simlabutil)

def DeleteEndCap(planeFace):
    modelName = simlab.getModelName('FEM')

    # Creates a group to remesh around the face after dividing.
    faceGrp = simlabutil.UniqueGroupName('_Plane')
    simlablib.CreateGroup(modelName, 'Face', planeFace, faceGrp)

    # Gets body and subModel.
    bodyGrp = simlabutil.UniqueGroupName('_Body')
    simlablib.SelectAssociatedEntities(modelName, 'Face', planeFace, 'Body', bodyGrp)
    body = simlab.getBodiesFromGroup(bodyGrp)
    body = body[0]
    simlablib.DeleteGroups(bodyGrp)
    subModel = GetParentSubModel(body)

    # Gets 3, 4 points on plane.
    pnts = simlab.definePlaneFromEntity(modelName, planeFace)
    points = simlabutil.Convert3PointsOnPlaneTo4Points(pnts)

    # Split face and Align plane
    SplitFace([body])
    simlablib.FindFacesByPlane(modelName, 'Body', [body], pnts, onPlane=1, above=0, below=0, tolerance=0.5)
    alignFaces = simlab.getSelectedEntities('Face')
    Align(alignFaces, points)

    # Creates face group to determine which bodies to delete
    allFaceGrp = simlabutil.UniqueGroupName('_AllFaces')
    simlablib.SelectAssociatedEntities(modelName, 'Body', [body], 'Face', allFaceGrp)    

    # Break body
    simlablib.BreakBody(modelName, [body], points)

    # Gets divied bodies
    dividedBodies = []
    allFaces = simlab.getEntityFromGroup(allFaceGrp)
    simlablib.DeleteGroups(allFaceGrp)
    candinateBodies = simlab.getBodiesWithSubString(modelName, [body + '*'])
    for subBody in candinateBodies:
        chkGrp = simlabutil.UniqueGroupName('_Check')
        simlablib.SelectAssociatedEntities(modelName, 'Body', [subBody], 'Face', chkGrp)    
        chkFaces = simlab.getEntityFromGroup(chkGrp)
        simlablib.DeleteGroups(chkGrp)
        if len(chkFaces) == 0:
            continue
        for chkFace in chkFaces:
            if chkFace in allFaces:
                break
        else:
            continue
        dividedBodies.append(subBody)

    # Moves block body to subModel, because body is placed under root by break.
    if subModel != '':
        MoveToSubModelQuuid=''' <MoveToSubModelQuuid UUID="475fe1b6-1656-44e3-9e36-2656ed16de0c">
        <SubModelName Value="''' + subModel + '''"/>
        <BodiesToMove>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>''' + str(dividedBodies).replace("'",'"').strip("[]""()") + ''',</Body>
        </Entities>
        </BodiesToMove>
        </MoveToSubModelQuuid>'''
        simlab.execute(MoveToSubModelQuuid)

    # Deletes endcap body.
    simlablib.FindBodiesByPlane(modelName, dividedBodies, pnts, onPlane=1, above=1)
    deleteBodies = simlab.getSelectedBodies()
    if len(deleteBodies) != 0:
        simlablib.DeleteBodies(modelName, deleteBodies)

    # Rename body to original name
    remainBodies = list(set(dividedBodies) - set(deleteBodies))
    if len(remainBodies) == 1:
        simlablib.RenameBody(modelName, remainBodies[0], body)

    # Gets faces for remeshing
    faces = simlab.getEntityFromGroup(faceGrp)
    afterFaceGrp = simlabutil.UniqueGroupName('_Merge')
    simlablib.GetAdjacentFacesToLimitFaces(modelName, faces, [0], afterFaceGrp, breakAngle=1, angle=45)
    remeshFaces = simlab.getEntityFromGroup(afterFaceGrp)

    # merges faces
    simlablib.MergeFaces(modelName, remeshFaces)
    mergedFaces = simlab.getEntityFromGroup(afterFaceGrp)

    remeshFaceGrp = simlabutil.UniqueGroupName('_Remesh')
    simlablib.SelectAdjacentFaces(modelName, mergedFaces, remeshFaceGrp)
    remeshFaces = simlab.getEntityFromGroup(remeshFaceGrp)

    # Rmeshs
    Remesh(remeshFaces)

    # post
    simlablib.DeleteGroups([faceGrp, afterFaceGrp, remeshFaceGrp])
    simlablib.UpdateModel()

def GetParentSubModel(body):
    modelName = simlab.getModelName('FEM')

    subModels = simlab.getChildrenInAssembly(modelName, modelName, 'SUBASSEMBLIES')
    if len(subModels) == 0:
        return ''

    for subModel in subModels:
        bodies = simlab.getChildrenInAssembly(modelName, subModel, 'BODIES')
        if body in bodies:
            return subModel
    return ''

def SplitFace(bodies, angle=45):
    modelName = simlab.getModelName('FEM')
    bodies = str(bodies).replace("'",'"')
    bodies = str(bodies).strip("[]""()")
    angle = str(angle)

    SplitFace=''' <FEASplitFace UUID="F67108F4-D1EB-4fc9-9333-8B181405C673">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Body>''' + bodies + ''',</Body>
    </Entities>
    </SupportEntities>
    <FeatureAngle Value="''' + angle + '''"/>
    <Option Value="0"/>
    <CreateFloatingEdges Value="1"/>
    </FEASplitFace>'''
    simlab.execute(SplitFace)

def Align(faces, points):
    modelName = simlab.getModelName('FEM')

    p1, p2, p3, p4 = points
    p1 = str(p1).strip("[]""()")
    p2 = str(p2).strip("[]""()")
    p3 = str(p3).strip("[]""()")
    p4 = str(p4).strip("[]""()")
    faces = str(faces).strip("[]""()")

    AlignPlanar=''' <AlignPlanar CheckBox="ON" UUID="b9175a92-dd76-4c68-b31c-0c20c2afa2c3">
    <tag Value="-1"/>
    <Name Value=""/>
    <Select Value="TargetFace"/>
    <Entities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Face>''' + faces + ''',</Face>
    </Entities>
    </Entities>
    <Define PlanePoints="''' + p1 + ',' + p2 + ',' + p3 + ',' + p4 + '''" Value="Plane"/>
    <DeleteZeroAreaElement Value="1"/>
    </AlignPlanar>'''
    simlab.execute(AlignPlanar)

def Remesh(remeshFaces):
    modelName = simlab.getModelName('FEM')

    avgElemSize = 10
    maxAngle = 45
    aspectRatio = 10
    if (simlab.isGroupPresent(DEFAULT_MESH_SIZE) and
        simlab.isGroupPresent(DEFAULT_MAX_ANGLE) and
        simlab.isGroupPresent(DEFAULT_ASPECT_RATIO)):        
        avgElemSize = simlab.getDoubleParameter('$' + DEFAULT_MESH_SIZE)
        maxAngle = simlab.getDoubleParameter('$' + DEFAULT_MAX_ANGLE)
        aspectRatio = simlab.getDoubleParameter('$' + DEFAULT_ASPECT_RATIO)

    LocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh2"/>
    <SupportEntities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Face>''' + str(remeshFaces).strip('()') + ''',</Face>
    </Entities>
    </SupportEntities>
    <ElemType Value="1"/>
    <AverageElemSize Value="''' + str(avgElemSize) + '''"/>
    <MinElemSize Value="''' + str(avgElemSize * 0.1) + '''"/>
    <PreserveBoundaryEdges Value="1"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="''' + str(maxAngle) + '''"/>
    <CurvatureMinElemSize Value="''' + str(avgElemSize * 0.5) + '''"/>
    <AspectRatio Value="''' + str(aspectRatio) + '''"/>
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
