from hwx import simlab
import simlabutil
import numpy as np

# BodyMC: mcType, mcName, bodyNm, elemSize, minElemSize, maxAngle, curvMin, aspRat, meshGrading 
# surfaceMesh: elemSize, minElemSize, maxAngle, curvMin, aspRat, meshGrading
MAX_ID_COORDINATE = 'Max_ID_Coordinate'
BEARING_COORDINATE = 'Bearing_CylCoordinate_'

def importCad(fileName):
    ImportParasolid=''' <ImportParasolid Type="Parasolid" CheckBox="ON" UUID="400d622c-e74a-4f87-bc0b-af51659b9b6d" gda="">
    <tag Value="1"/>
    <FileName widget="LineEdit" Value="'''+ fileName +'''" HelpStr="File name to be imported."/>
    <Units Value="MilliMeter" HelpStr="Units to which this file is to be imported into"/>
    <SolidBodyType Value="1"/>
    <SheetBodyType Value="0"/>
    <WireBodyType Value="0"/>
    <ConnectedBodyType Value="0"/>
    <ImportasFacets Value="0"/>
    <Imprint Value="1"/>
    <Groups Value="0"/>
    <Merge Value="0"/>
    <ImportAssemblyStructure Value="0"/>
    <SaveGeometryInDatabase Value="0"/>
    <FileCount Value="0" value="0"/>
    <Output widget="NULL"/>
    <ImportOption Value="1"/>
    <TransXmlFileName Value=""/>
    <TransOutFileName Value=""/>
    </ImportParasolid>'''
    simlab.execute(ImportParasolid)

def createMeshControl(meshProp):
    modelNm = simlab.getModelName("CAD")
    mcType = meshProp[0]

    if mcType.lower() == "body":
        _, mcName, bodyNm, elemSize, minElemSize, maxAngle, curvMin, aspRat, meshGrading = meshProp
        MeshControls=''' <MeshControl CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1">
        <tag Value="-1"/>
        <MeshControlName Value="'''+ mcName +'''"/>
        <MeshControlType Value="Body"/>
        <Entities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Body>"'''+ bodyNm +'''",</Body>
        </Entities>
        </Entities>
        <Reverse Value="" EntityTypes="" ModelIds=""/>
        <MeshColor Value=""/>
        <BodyMeshControl>
        <ElementType Value="0"/>
        <UseMaxElemSize Value="0"/>
        <AverageElementSize Value="'''+ str(elemSize) +'''"/>
        <MaxElemSize Value="0.02828"/>
        <MinElemSize Value="'''+ str(minElemSize) +'''"/>
        <MaxAnglePerElement Value="'''+ str(maxAngle) +'''"/>
        <CurvatureMinElemSize Value="'''+ str(curvMin) +'''"/>
        <AspectRatio Value="'''+ str(aspRat) +'''"/>
        <SurfaceMeshGrading Value="'''+ str(meshGrading) +'''"/>
        <MappedMesh Value="0"/>
        <CoarseMesh Value="0"/>
        <IdentifyFeaturesandMesh Value="0"/>
        </BodyMeshControl>
        </MeshControl>'''
        simlab.execute(MeshControls)

    elif mcType.lower() == "region":
        _, mcName, bodyNm, pt_A, pt_B = meshProp

        pt_A = simlabutil.Convert3PointsOnPlaneTo4Points(pt_A)
        pt_B = simlabutil.Convert3PointsOnPlaneTo4Points(pt_B)

        MeshControls=''' <MeshControl isObject="1" CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
        <tag Value="-1"/>
        <MeshControlName Value="'''+ mcName +'''"/>
        <MeshControlType Value="Region"/>
        <Entities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Body>"'''+ bodyNm +'''",</Body>
        </Entities>
        </Entities>
        <Reverse ModelIds="" EntityTypes="" Value=""/>
        <MeshColor Value=""/>
        <RegionMeshControl>
        <RegionType Value="2"/>
        <DefineInsideRegion Value="0"/>
        <AverageElementSize Value="0"/>
        <MinElemSize Value="0"/>
        <MaxAnglePerElement Value="45"/>
        <CurvatureMinElemSize Value="0"/>
        <AspectRatio Value="10"/>
        <SurfaceMeshGrading Value="1.5"/>
        <BreakOptions Value="1"/>
        <RType Value="546"/>
        <CreateInternalFace Value="0"/>
        <CuboidRegData/>
        <CYlRegData/>
        <PlaneRegData>
        <Plane PlanePoints="'''+ ",".join(str(v) for pt in pt_A for v in pt) +''',"/>
        <Plane PlanePoints="'''+ ",".join(str(v) for pt in pt_B for v in pt) +''',"/>
        </PlaneRegData>
        <SphereRegData/>
        <ConeRegData/>
        </RegionMeshControl>
        </MeshControl>'''
        simlab.execute(MeshControls)

def getPlaneDataIn3Points(faceId):
    modelNm = simlab.getModelName("CAD")
    if isinstance(faceId, tuple):faceId = faceId[0]
    return simlab.definePlaneFromEntity(modelNm, int(faceId))

def surfaceMesh(meshProp):
    elemSize, minElemSize, maxAngle, curvMin, aspRat, meshGrading = meshProp
    modelNm = simlab.getModelName("CAD")
    SurfaceMesh=''' <SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
    <tag Value="-1"/>
    <SurfaceMeshType Value="Tri"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <Tri>
    <ElementType Value="Tri6"/>
    <AverageElementSize Checked="1" Value="'''+ str(elemSize) +'''"/>
    <MaximumElementSize Checked="0" Value="33.936"/>
    <MinimumElementSize Value="'''+ str(minElemSize) +'''"/>
    <GradeFactor Value="'''+ str(meshGrading) +'''"/>
    <MaximumAnglePerElement Value="'''+ str(maxAngle) +'''"/>
    <CurvatureMinimumElementSize Value="'''+ str(curvMin) +'''"/>
    <AspectRatio Value="'''+ str(aspRat) +'''"/>
    <AdvancedOptions>
    <IdentifyFeaturesAndMesh Checked="1"/>
    <ImprintMeshing Checked="0"/>
    <BetterGeometryApproximation Checked="0"/>
    <CoarseMesh Checked="0"/>
    <CoarseMesh_UseExistingNodes Checked="0"/>
    <CreateMeshInNewModel Checked="1"/>
    <UserDefinedModelName Value=""/>
    <Tri6WithStraightEdges Checked="0"/>
    <ImproveSkewAngle Value="0"/>
    <MappedMesh Value="0"/>
    <MeshPattern Value="0"/>
    </AdvancedOptions>
    </Tri>
    </SurfaceMesh>'''
    simlab.execute(SurfaceMesh)

def removeHoles(bodyNm, maxRadius):
    modelNm = simlab.getModelName("FEM")
    RemoveHole=''' <ConnectHole UUID="8393e3d3-a92c-4a40-8cc0-803b4cf2169e">
    <RibOptionType Value="1"/>
    <Entity>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </Entity>
    <AllRadius Value="0"/>
    <MinRadius Value="0"/>
    <MaxRadius Value="'''+ str(maxRadius) +'''"/>
    <LocalReMesh Value="1"/>
    </ConnectHole>'''
    simlab.execute(RemoveHole)

def fillCracks():
    modelNm = simlab.getModelName("FEM")
    FillCracks=''' <FillCrack CheckBox="ON" UUID="DAE88A9F-E46D-44b7-A534-E94A5D1A716E">
    <tag Value="-1"/>
    <Name Value="FillCrack1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <RemoveNonManifoldEdges Value="0"/>
    <MaxAngle Value="110"/>
    <MinEdgeLength Value="0.1"/>
    </FillCrack>'''
    simlab.execute(FillCracks)

# INTERSECT_ELEMENT
# Fill_Hole_Faces

# Body join and seperate
def joinBodies(bodies, tol):
    modelNm = simlab.getModelName("FEM")
    Join=''' <Join CheckBox="ON" UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC">
    <tag Value="-1"/>
    <Name Value=""/>
    <Pick Value="Join"/>
    <JoinEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ ",".join("{}".format(v) for v in bodies) +''',</Body>
    </Entities>
    </JoinEntities>
    <AlignEntities ModelIds="" EntityTypes="" Value=""/>
    <PreserveEntities ModelIds="" EntityTypes="" Value=""/>
    <Tolerance Value="'''+ str(tol) +'''"/>
    <JoinType Value="GEOM_MATCHING_FACES"/>
    <MeshOrShape Value="Shape"/>
    <MeshOption Value=""/>
    <MeshParam Value=""/>
    <SplitFace Value="1"/>
    <LocalRemesh Value="1"/>
    </Join>'''
    simlab.execute(Join)

def getBodyFromFace(modelType, faceIds):
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
    deleteGrp("SelectBodies_4")
    return bodyNm

def updateModel():
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def seperateBodies(bodies):
    modelNm = simlab.getModelName("FEM")
    Separate=''' <Separate gda="" CheckBox="ON" UUID="5159E70B-B9FD-4b8b-9116-66D7CA71FF96">
    <tag Value="-1"/>
    <Name Value="Separate3"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ ",".join("{}".format(v) for v in bodies) +''',</Body>
    </Entities>
    </SupportEntities>
    <Output/>
    </Separate>'''
    simlab.execute(Separate)

def createMPC(masterBody, slaveBody, tol, mpcProp):
    x, y, z, r_x, r_y, r_z = mpcProp
    modelNm = simlab.getModelName("FEM")
    MPC=''' <Stress_MPC isObject="2" BCType="MPC" CheckBox="ON" UUID="BBCD6D76-5754-42b5-8A1B-E8FB79064EFE">
    <tag Value="-1"/>
    <Name Value="MPC_2"/>
    <CoordinateAxisID Value="Global"/>
    <BetweenEntitties Value="4"/>
    <MasterList>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ ",".join(masterBody) +'''",</Body>
    </Entities>
    </MasterList>
    <SlaveList>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ ",".join(slaveBody) +'''",</Body>
    </Entities>
    </SlaveList>
    <X_or_Radial CheckBox="'''+ str(x[0]) +'''" Value="'''+ str(x[1]) +'''"/>
    <Y_or_Theta CheckBox="'''+ str(y[0]) +'''" Value="'''+ str(y[1]) +'''"/>
    <Z_or_Axial CheckBox="'''+ str(z[0]) +'''" Value="'''+ str(z[1]) +'''"/>
    <Rx CheckBox="'''+ str(r_x[0]) +'''" Value="'''+ str(r_x[1]) +'''"/>
    <Ry CheckBox="'''+ str(r_y[0]) +'''" Value="'''+ str(r_y[1]) +'''"/>
    <Rz CheckBox="'''+ str(r_z[0]) +'''" Value="'''+ str(r_z[1]) +'''"/>
    <Dept_X_or_Radial CheckBox="0" Value="1"/>
    <Dept_Y_or_Theta CheckBox="0" Value="1"/>
    <Dept_Z_or_Axial CheckBox="0" Value="1"/>
    <Dept_Rx CheckBox="0" Value="0"/>
    <Dept_Ry CheckBox="0" Value="0"/>
    <Dept_Rz CheckBox="0" Value="0"/>
    <Tolerance Value="'''+ str(tol) +'''"/>
    <MPCFaceType Value="2"/>
    <IgnoreEdgesChk Value="0"/>
    <IgnoreEdgeList ModelIds="" EntityTypes="" Value=""/>
    <MPCType Value="0"/>
    <MasterNode ModelIds="" EntityTypes="" Value=""/>
    <NoOfIndepNodes Value=""/>
    <CyclicFlag Value="0"/>
    <CyclicNodePairList1 ModelIds="" EntityTypes="" Value=""/>
    <CyclicNodePairList2 ModelIds="" EntityTypes="" Value=""/>
    <CheckCreateCons Value="0"/>
    <ConstraintId Value="0"/>
    <GapElem Value=""/>
    </Stress_MPC>'''
    simlab.execute(MPC)

# For volume Mesh
def meshCleanUp(limit_aspectRatio):
    modelNm = simlab.getModelName("FEM")
    QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
    <ElementType Value="Tri"/>
    <Option Value="Cleanup"/>
    <Quality LimitValue="''' +str(limit_aspectRatio)+ '''" Condition="G Than Or Eq" Name="Aspect Ratio"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <CleanupType Value="Modify Element"/>
    <PreserveSurfaceSkew Check="0" Value="55"/>
    </QCheck>'''
    simlab.execute(QualityCheck)

def modifyIntersection():
    modelNm = simlab.getModelName("FEM")
    ModifyIntersections=''' <Intersection UUID="9b88366a-d021-40ea-a7a4-2ff23f864a2d">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <IntersectionCheck Value="1"/>
    <Tri_TriOverlapCheck Value="0"/>
    <Edge_TriOverlapCheck Value="0"/>
    <PentrationCheck Value="0"/>
    <Tolerance Value="1e-06"/>
    <GrpName Check="0" Name="Element_Group_3"/>
    <Operation Value="Show intersection"/>
    <SkipFaceNormal flag="false"/>
    </Intersection>'''
    simlab.execute(ModifyIntersections)

def popupMsg(comment):
    simlab.messageBox.popupmsg(comment)

def volumeMesh(meshProp):
    meshSize, minQuality = meshProp
    modelNm = simlab.getModelName("FEM")
    VolumeMesh=''' <VolumeMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
    <tag Value="-1"/>
    <Name Value="VolumeMesher1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <MeshType Value="Tet10"/>
    <AverageElemSize Value="''' + str(meshSize) + '''"/>
    <MinimumElementSize Value="0"/>
    <AspectRatio Value="0"/>
    <MaxElemSize Checked="0" Value="0"/>
    <InternalGrading Value="2"/>
    <MinQuality Value="''' + str(minQuality) + '''"/>
    <LinearQuality Value="0"/>
    <MaxQuality Value="1"/>
    <QuadMinQuality Value="0.001"/>
    <QuadQuality Value="0"/>
    <QuadMaxQuality Value="1"/>
    <CadBody Value="0"/>
    <NumberofLayers Checked="1" Value="1"/>
    <LayerThickness Checked="0" Value="0"/>
    <EndFaces/>
    <AdvancedOptions>
    <MeshDensity Value="0"/>
    <CreateVol Value="0"/>
    <OutputModelName Value=""/>
    <Assembly Value="0"/>
    <PreserveFaceMesh Value="0"/>
    <MeshAsSingleBody Value="0"/>
    <Retain2DSurfaceBodies Value="0"/>
    <PreserveSurfaceSkew Checked="0" Value="55"/>
    <MixedMesh Value="0"/>
    <IdentifyFeaturesAndMeshOnCAD Value="0"/>
    </AdvancedOptions>
    </VolumeMesher>'''
    simlab.execute(VolumeMesh)

def updateAttributes(modelType):
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
def getCircularFeatureAssociated(modelType, faceId):
    modelNm = simlab.getModelName(modelType)
    assoEdgeIDs = getEdgeIDFromFace(modelType, faceId)
    
    result = None
    for edgeId in assoEdgeIDs:
        arcAtt = simlab.getArcEdgeAttributes(modelNm, edgeId)
        if arcAtt:
            result = arcAtt
            break
    
    return result

def getDistanceBetweenTwoFaces(modelType, faceId1, faceId2):
    updateAttributes(modelType)
    result1 = getCircularFeatureAssociated(modelType, faceId1)
    result2 = getCircularFeatureAssociated(modelType, faceId2)
    if not result1 or not result2: return
    cPt1, rad1 = result1
    cPt2, rad2 = result2

    pt1 = np.array(cPt1)
    pt2 = np.array(cPt2)

    height = np.sqrt(np.sum((pt1-pt2)**2))
    gap = abs(rad1[0]-rad2[0])

    return (height, gap)

def getLargerRingGrp(modelType, faceEntities, grpNm):
    createFaceGroup(modelType, grpNm, faceEntities)
    simlab.createGroupsOfConnectedEntities(grpNm)
    grpAll = simlab.getGroupsWithSubString("FaceGroup",["{}*".format(grpNm)])
    grpWithLargest = ""
    if len(grpAll) > 1:
        stats = {}
        for thisGrp in grpAll:
            thisGrpEnts = simlab.getEntityFromGroup(thisGrp)
            if thisGrpEnts:
                _, rad = getCircularFeatureAssociated(modelType, thisGrpEnts[0])
                stats[thisGrp] = rad
        key, _ = max(stats.items(), key=lambda x: x[1])
        grpWithLargest = key
    else:
        grpWithLargest = grpAll[0]
    return grpWithLargest

def modifyToQuadElems(bodyNms):
    if isinstance(bodyNms, tuple) or isinstance(bodyNms, list): bodyNms = ",".join('"{}"'.format(v) for v in bodyNms)
    else: bodyNms = '"{}"'.format(bodyNms)
    modelNm = simlab.getModelName("FEM")
    ModifyElements=''' <Modify CheckBox="ON" UUID="28706164-e6e5-4544-b4a9-c052c4b6c60f">
    <Name Value="Modify4"/>
    <tag Value="-1"/>
    <Option Value="TRITOQUAD8"/>
    <QuadDominant Value="1"/>
    <Entity>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ bodyNms +''',</Body>
    </Entities>
    </Entity>
    <IdealQuad Value="0"/>
    <UpdateAssociateRBENodes Value="1"/>
    </Modify>'''
    simlab.execute(ModifyElements)

def createBodyFromFaces(grpNm):
    CreateBodyFromFaces=''' <BodyFromFaces UUID="24F7C671-DC40-44e0-9B32-8A22A67F58FA" gda="">
    <SupportEntities ModelIds="" Value="" EntityTypes=""/>
    <ShareBoundaryEdges Value="1"/>
    <CreateBodyFromFaceOption Value="2"/>
    <CreateBodyForEachGroup Value="false"/>
    <Group Entity="" Value="'''+ grpNm +''',"/>
    <UseInputBodyName Value="true"/>
    </BodyFromFaces>'''
    simlab.execute(CreateBodyFromFaces)

def createCylinderFace(face1Ent, face2Ent, contactFace, axialElems, circularElems):

    cpt1, _ = getCircularFeatureAssociated("CAD", face1Ent)
    cpt2, _ = getCircularFeatureAssociated("CAD", face2Ent)
    
    height, _ = getDistanceBetweenTwoFaces("CAD", face1Ent, face2Ent)

    _, rad = getCircularFeatureAssociated("CAD", contactFace)

    p1_x, p1_y, p1_z = cpt1
    p2_x, p2_y, p2_z = cpt2
    
    vect_12 = p2_x - p1_x, p2_y - p1_y, p2_z - p1_z
    # vect_12_norm = vect_12/np.linalg.norm(vect_12)

    r_x, r_y, r_z = vect_12

    CreateCylinderFace=''' <CylindricalFace gda="" UUID="E58D5E41-2E4E-405a-811D-960EFF5DBD7D">
    <Name Value="Cylindrical1"/>
    <tag Value="-1"/>
    <Element_type Value="Tri6"/>
    <Radius Value="'''+ str(rad[0]) +'''"/>
    <Height Value="'''+ str(height) +'''"/>
    <Segment_no.ofNodes Value="'''+ str(circularElems//4) +'''"/>
    <Vertical_no.ofNodes Value="'''+ str(axialElems) +'''"/>
    <Origin Value="'''+ str(p1_x) +''','''+ str(p1_y) +''','''+ str(p1_z) +'''"/>
    <Point1 Value="'''+ str(p1_x) +''','''+ str(p1_y) +''','''+ str(p1_z) +'''"/>
    <Point2 Value="'''+ str(p1_x+r_x) +''','''+ str(p1_y+r_y) +''','''+ str(p1_z+r_z) +'''"/>
    <Output/>
    </CylindricalFace>'''
    simlab.execute(CreateCylinderFace)

def replaceAllBodyNms(fromChr, toChr):
    modelNm = simlab.getModelName("CAD")
    allBodies = simlab.getBodiesWithSubString(modelNm,["*"])
    for this_body in allBodies:
        if "-" in this_body:renameBody(modelNm, this_body, this_body.replace(fromChr, toChr))

def renameBody(modelNm, oldNm, newNm):
    RenameBody=''' <RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
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

def deleteBodyEntities(modelNm, bodyNm):
    DeleteEntity=''' <DeleteEntity CheckBox="ON" UUID="BF2C866D-8983-4477-A3E9-2BBBC0BC6C2E">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </SupportEntities>
    </DeleteEntity>'''
    simlab.execute(DeleteEntity)
    updateModel()

def deleteFaceEntities(modelNm, faceIds):
    DeleteEntity=''' <DeleteEntity UUID="BF2C866D-8983-4477-A3E9-2BBBC0BC6C2E" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ ",".join(str(v) for v in faceIds) +''',</Face>
    </Entities>
    </SupportEntities>
    </DeleteEntity>'''
    simlab.execute(DeleteEntity)
    updateModel()

def transferBodies(bodyToDelete, targetModel, destinationModel):
    deleteBodyEntities(destinationModel, bodyToDelete)
    renameBody(targetModel, "Body 1", bodyToDelete)
    TransferBodies=''' <TransferBodies UUID="25823352-f737-4a92-a54d-7c7c2e4c60f2">
    <Input>
    <Entities>
    <Model>'''+ targetModel +'''</Model>
    <Body></Body>
    </Entities>
    </Input>
    <DestinationModel Value="'''+ destinationModel +'''"/>
    <DestinationSubModel Value=""/>
    </TransferBodies>'''
    simlab.execute(TransferBodies)
    updateModel()

def getInnerRingFaceIdsFromFEMBody(bodyNm, plane_A, plane_B):
    modelNm = simlab.getModelName("FEM")
    for ind, planePts in enumerate([plane_A, plane_B]):
        pt1, pt2, pt3 = planePts
        FacesByPlane=''' <FacesByPlane UUID="116fb6e7-2d86-45fb-bbee-bd40e654a0bf">
        <Name Value="Show Faces"/>
        <SupportEntities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Body>"'''+ bodyNm +'''",</Body>
        </Entities>
        </SupportEntities>
        <Option Value="3"/>
        <RegionData Type="Plane">
        <PlaneData Value="'''+ ",".join(str(v) for pt in [pt1, pt2, pt3] for v in pt) +'''"/>
        </RegionData>
        <On Value="1"/>
        <Above Value="0"/>
        <Below Value="1"/>
        <Tolerance Value="0.001"/>
        <CreateGroup Value="1"/>
        </FacesByPlane>'''
        simlab.execute(FacesByPlane)
        faceEnts = simlab.getEntityFromGroup("Show_Faces")
        createFaceGroup("FEM", "FaceGrp_{}".format(ind + 1), faceEnts)
        
    faceEntA = set(simlab.getEntityFromGroup("FaceGrp_1"))
    deleteGrp("FaceGrp_1")
    faceEntB = set(simlab.getEntityFromGroup("FaceGrp_2"))
    deleteGrp("FaceGrp_2")
    deleteGrp("Show_Faces")
    
    return getLargerRingGrp("FEM", list(faceEntA.intersection(faceEntB)), "innerRing")

def createFaceGroup(modelType, grpNm, FaceEntitiesList):
    modelNm = simlab.getModelName(modelType)
    deleteGrp(grpNm)
    CreateGroup=''' <CreateGroup CheckBox="OFF" isObject="4" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954">
    <tag Value="-1"/>
    <Name OldValue="" Value="'''+ grpNm +'''"/>
    <SupportEntities>
    <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Face>'''+ ','.join(str(v) for v in FaceEntitiesList)+''',</Face>
    </Entities>
    </SupportEntities>
    <Type Value="Face"/>
    <Color Value="183,168,107,"/>
    <Dup Value="0"/>
    </CreateGroup>'''
    simlab.execute(CreateGroup)

def deleteGrp(grpNm):
    DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +''',"/>
    <Output/>
    </DeleteGroupControl>'''
    simlab.execute(DeleteGroupControl)

def renameGrp(grpNm, newGrpNm):
    RenameGroupControl=''' <RenameGroupControl CheckBox="ON" UUID="d3addb85-3fd0-4972-80af-e699f96e9045">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +'''"/>
    <NewName Value="'''+ newGrpNm +'''"/>
    <Output/>
    </RenameGroupControl>'''
    simlab.execute(RenameGroupControl)

# create Bearing from FEM
def mergeFaces(faceIds):
    modelNm = simlab.getModelName("FEM")
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
    updateModel()

def changeLayers(faceId, onAxial, onCircular):
    modelNm = simlab.getModelName("FEM")
    if isinstance(faceId, tuple) or isinstance(faceId, list): faceId = ",".join(str(v) for v in faceId)
    else: faceId = str(faceId)
    ChangeLayers=''' <ChangeLayers UUID="0480248b-fbe6-4da3-ba06-74147e68e9c0">
    <tag Value="-1"/>
    <Name Value="ChangeLayers1"/>
    <Type Value="1"/>
    <Feature>
    <Faces>
    <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Face>'''+ faceId +''',</Face>
    </Entities>
    </Faces>
    <Axial Value="1"/>
    <AxialNumElements Checked="1" Value="'''+ str(onAxial) +'''"/>
    <AxialElemSize Checked="0" Value="5"/>
    <Range Value="0"/>
    <StartNode/>
    <EndNode/>
    <Circular Value="1"/>
    <CircularNumElements Checked="1" Value="'''+ str(onCircular) +'''"/>
    <CircularElemSize Checked="0" Value="15"/>
    <PrincipalDirection Value="1"/>
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
    updateModel()

def flipOuterRing(bodyNm):
    faceIds = getFaceIdFromBody("FEM", bodyNm)
    reverseNormal(faceIds)
    updateModel()

def reverseNormal(faceIds):
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

def makeShellBearingWithSpring(bearingProp, coordId, springStiff):
    innerFaceId, outerFaceId, numOfBalls, radOfBall, midNode, numElem = bearingProp

    bodies = simlab.getBodiesWithSubString(simlab.getModelName("FEM"), ["*"])
    createBearing(innerFaceId[0], numOfBalls, radOfBall, midNode, numElem)
    innerBearingBody = getNewCreatedBodyNm("FEM", bodies)

    bodies = simlab.getBodiesWithSubString(simlab.getModelName("FEM"), ["*"])
    createBearing(outerFaceId[0], numOfBalls, radOfBall, midNode, numElem)
    outerBearingBody = getNewCreatedBodyNm("FEM", bodies)

    # create Coordinate
    createCoordSys(outerFaceId[0])
    coordinateID = simlab.getIntParameter('$'+MAX_ID_COORDINATE)

    createSpring(innerBearingBody, outerBearingBody, coordinateID, springStiff)

def createShellBearing(faceId, numOfBalls, radOfBall, midNode, numElem):
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

def deleteOrphanNodes():
    DeleteOrphanNodes=''' <DeleteOrphanNode UUID="16A3F8AE-EDAB-4988-9006-7FCB3952F161">
    <tag Value="-1"/>
    <Name Value="DeleteOrphanNode3"/>
    <SupportEntities Value="" EntityTypes="" ModelIds=""/>
    <All Value="1"/>
    <Selected Value="0"/>
    <UnSelected Value="0"/>
    </DeleteOrphanNode>'''
    simlab.execute(DeleteOrphanNodes)

def getNewCreatedBodyNm(modelType, bodiesBefore):
    modelNm = simlab.getModelName(modelType)
    entireBodies = simlab.getBodiesWithSubString(modelNm, ["*"])
    newBodyNm = set(entireBodies) - set(bodiesBefore)
    return newBodyNm.pop()

def getNodeIdsFromBody(bodyNm):
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
    deleteGrp("SelectNodes_12")
    return nodeEnts

def getFaceIdFromBody(modelType, bodyNm):
    modelNm = simlab.getModelName(modelType)
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </InputBody>
    <Option Value="Faces"/>
    <Groupname Value="associatedFaceGrp"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)

    faceEnts = simlab.getEntityFromGroup("associatedFaceGrp")
    deleteGrp("associatedFaceGrp")

    return faceEnts

def getEdgeIdFromBody(modelType, bodyNm):
    modelNm = simlab.getModelName(modelType)
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </InputBody>
    <Option Value="Edges"/>
    <Groupname Value="edgeGrpFromBody"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)

    edgeEnts = simlab.getEntityFromGroup("edgeGrpFromBody")
    deleteGrp("edgeGrpFromBody")
    return edgeEnts

# def getCircularEdges(edgeIds):
#     modelNm = simlab.getModelName("FEM")
#     updateAttributes()

#     circularEdges = []
#     for thisEdge in edgeIds:
#         try:
#             _,_=simlab.getArcEdgeAttributes(modelNm,thisEdge)
#             circularEdges.append(thisEdge)
#         except ValueError:
#             pass
    
#     return circularEdges

def getEdgesOnPlane(bodyNm, pointsOnPlane, increaseTolBy = 0.1):
    pt1, pt2, pt3 = pointsOnPlane
    modelNm = simlab.getModelName("FEM")
    tol = 0.1
    while not simlab.isGroupPresent("Show_Edges"):
        if tol== 2:break
        EdgesByPlane=''' <EdgesByPlane UUID="94ea9e4e-c496-4d6a-950e-66585ed62a28">
        <Name Value="Show Edges"/>
        <SupportEntities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Body>"'''+ bodyNm +'''",</Body>
        </Entities>
        </SupportEntities>
        <Option Value="2"/>
        <RegionData Type="Plane">
        <PlaneData Value="'''+ ",".join(str(v) for pt in [pt1, pt2, pt3] for v in pt) +'''"/>
        </RegionData>
        <On Value="1"/>
        <Above Value="0"/>
        <Below Value="0"/>
        <Tolerance Value="'''+ str(tol) +'''"/>
        <CreateGroup Value="1"/>
        </EdgesByPlane>'''
        simlab.execute(EdgesByPlane)
        tol += increaseTolBy

    edgeEnts = simlab.getEntityFromGroup("Show_Edges")
    deleteGrp("Show_Edges")
    return edgeEnts

def getBearingContactFaceEntities(bodyNm, planes):
    sideEdges = []
    for this_plane in planes:
        sideEdges.extend(list(getEdgesOnPlane(bodyNm, this_plane)))

    faceIds = getFaceIdFromBody("FEM", bodyNm)
    newFaceIds = _getMiddleFaceEnts(faceIds, sideEdges)          
    return newFaceIds 

# def getBearingContactFaceEntities(bodyNm, sideEdges):
   
#     faceIds = getFaceIdFromBody("FEM", bodyNm)
#     contactFaceIds = _getMiddleFaceEnts(faceIds, sideEdges)
             
#     return contactFaceIds 

def _getMiddleFaceEnts(faceIds, sideEdges):
    newfaceIds = []
    for this_face in faceIds:
        thisEdgeIds = getEdgeIDFromFace("FEM", this_face)
        if not set(thisEdgeIds) & set(sideEdges): 
            newfaceIds.append(this_face)
    return newfaceIds

def mergeBodies(bodies, ouputBodyNm):
    modelNm = simlab.getModelName("FEM")
    MergeBodies=''' <BodyMerge gda="" UUID="FA9128EE-5E6C-49af-BADF-4016E5622020">
    <tag Value="-1"/>
    <Name Value="BodyMerge2"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ ",".join('"{}"'.format(v) for v in bodies) +''',</Body>
    </Entities>
    </SupportEntities>
    <Delete_Shared_Faces Value="0"/>
    <Output_Body_Name Value="'''+ ouputBodyNm +'''"/>
    <Output/>
    </BodyMerge>'''
    simlab.execute(MergeBodies)

def drawEdgeFromOffset(bodyNm, planes, offsetBy):
    planeEdges = []
    for this_plane in planes:
        edges = getEdgesOnPlane(bodyNm, this_plane)
        planeEdges.extend(list(edges))
        print("Edges:{}".format(edges))
        fillHolesWithEdges(edges)
        pt1, pt2, pt3 = simlab.definePlaneFromGroup('Fill_Hole_Faces', "FACEGROUP")
        print(pt1, pt2, pt3)
        faceIds = getFaceIdFromEdge("FEM", edges)
        print("faceIds:{}".format(faceIds))
        directPt1, directPt2 = getNormalPointsToPlane(pt1, pt2, pt3)
        print("direct1:{}".format(directPt1))
        print("direct2:{}".format(directPt2))
        createEdgeByoffset(faceIds, edges, directPt1, directPt2, offsetBy)
        deleteFaceEntities(simlab.getModelName("FEM"), simlab.getEntityFromGroup('Fill_Hole_Faces'))
        updateModel()

def getNormalPointsToPlane(pt1, pt2, pt3):
    pt1_x, pt1_y, pt1_z = pt1
    pt2_x, pt2_y, pt2_z = pt2
    pt3_x, pt3_y, pt3_z = pt3

    vect_21 = pt1_x - pt2_x, pt1_y - pt2_y, pt1_z - pt2_z
    vect_23 = pt3_x - pt2_x, pt3_y - pt2_y, pt3_z - pt2_z

    cross_13 = np.cross(vect_21, vect_23)

    return tuple(cross_13), pt2

def getElementIdFromFEMFace(femFaceId):
    modelNm = simlab.getModelName("FEM")
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(femFaceId) +''',</Face>
    </Entities>
    </InputFaces>
    <Option Value="Elements"/>
    <Groupname Value="fillHoleElements"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)

    elemIds = simlab.getEntityFromGroup("fillHoleElements")
    deleteGrp("fillHoleElements")

    return elemIds

def getCornerNodesFromElem(elemId):
    modelNm = simlab.getModelName("FEM")
    SelectElementAssociatedEntities=''' <SelectElementAssociatedEntities UUID="7062f057-0e48-4ccc-ad73-e60584e8ff26">
    <InputElement Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Element>'''+ str(elemId) +''',</Element>
    </Entities>
    </InputElement>
    <Option Value="Cornernodes"/>
    <Groupname Value="cornerNodes"/>
    </SelectElementAssociatedEntities>'''
    simlab.execute(SelectElementAssociatedEntities)

    nodeIds = simlab.getEntityFromGroup("cornerNodes")
    deleteGrp("cornerNodes")

    return nodeIds

def fillHolesWithEdges(edgeIds):
    modelNm = simlab.getModelName("FEM")
    deleteGrp('Fill_Hole_Faces')

    FillHoles=''' <FillHole UUID="E9B9EC99-A6C1-4626-99FF-626F38A8CE4F" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="FillHole1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Edge>'''+ ",".join(str(v) for v in edgeIds) +''',</Edge>
    </Entities>
    </SupportEntities>
    <Option Value="2"/>
    <Cylindercal_Face Value="0"/>
    <Single_Face Value="1"/>
    <FillPartialLoop Value="0"/>
    <MeshSize Value="0.0" LocalReMesh="0"/>
    </FillHole>'''
    simlab.execute(FillHoles)

    # holeFaceId = simlab.getEntityFromGroup("Fill_Hole_Faces")
    # deleteGrp("Fill_Hole_Faces")
    # return holeFaceId
def createEdgeByoffset(faceIds, edges, directPt1, directPt2, offsetBy):
    modelNm = simlab.getModelName("FEM")
    CreateEdgeByEdgeOffset=''' <EdgeOffset gda="" UUID="6d4a36ce-1c18-456d-a3cb-910cb85efdb5">
    <Name Value="EdgeOffset4"/>
    <Faces>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ ",".join(str(v) for v in faceIds) +''',</Face>
    </Entities>
    </Faces>
    <Edges>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Edge>'''+ ",".join(str(v) for v in edges) +''',</Edge>
    </Entities>
    </Edges>
    <GuideEdge Value="" ModelIds="" EntityTypes=""/>
    <OffsetDistance Value="'''+ str(offsetBy) +'''"/>
    <OffsetOption Value="Selected Edges"/>
    <Direction Value="1"/>
    <DirectionPoint1 Value="'''+ ",".join(str(v) for v in directPt1) +'''"/>
    <DirectionPoint2 Value="'''+ ",".join(str(v) for v in directPt2) +'''"/>
    <MoveGuideEdge Value="0"/>
    <ExistingMesh Value="0"/>
    <LayerOption Value="Tri"/>
    <NoOfLayers Value="1"/>
    <EdgeAtVertices Value="0"/>
    <LocalRemesh Value="0"/>
    <MeshSize Value=""/>
    <FloatingEdge_DirectionPt1 Value="0"/>
    <FloatingEdge_DirectionPt2 Value="0"/>
    <Output/>
    </EdgeOffset>'''
    simlab.execute(CreateEdgeByEdgeOffset)
    updateModel()

def getFaceIdFromEdge(modelType, edges):
    modelNm = simlab.getModelName(modelType)
    SelectEdgeAssociatedEntities=''' <SelectEdgeAssociatedEntities UUID="551fdd5b-6a8c-4a30-8ab0-fbaf9257343e">
    <InputEdges Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Edge>'''+ ",".join(str(v) for v in edges) +''',</Edge>
    </Entities>
    </InputEdges>
    <Option Value="Faces"/>
    <Groupname Value="faceGroupAssociatedWithEdges"/>
    </SelectEdgeAssociatedEntities>'''
    simlab.execute(SelectEdgeAssociatedEntities)

    faceIds = simlab.getEntityFromGroup("faceGroupAssociatedWithEdges")
    deleteGrp("faceGroupAssociatedWithEdges")

    return faceIds

def getEdgeIDFromFace(modelType, faceIds):
    faceEnts = ",".join(str(v) for v in faceIds) if isinstance(faceIds,tuple) or isinstance(faceIds, list) else faceIds
    modelNm = simlab.getModelName(modelType)
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceEnts) +''',</Face>
    </Entities>
    </InputFaces>
    <Option Value="Edges"/>
    <Groupname Value="edgeGrpFromFace"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)

    edgeIds = simlab.getEntityFromGroup("edgeGrpFromFace")
    deleteGrp("edgeGrpFromFace")
    return edgeIds

def createSpring(slb1, slb2, axisId, stiffness):
    modelNm = simlab.getModelName("FEM")
    SpringElement=''' <Spring isObject="2" BCType="Spring" CheckBox="ON" UUID="ACA1CCC4-4687-41bd-9BA3-0C602C5B2B7D">
    <tag Value="-1"/>
    <Name Value="BodySpring_34"/>
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
    <Flag1 Value="1"/>
    <Flag2 Value="1"/>
    <GndSpring Value="0"/>
    <FieldData Value="None" Index="0"/>
    </Spring>'''
    simlab.execute(SpringElement)

def AddIntParameters(name, value):
    SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Name="''' + name + '''" Value="'''+ str(value) + '''" Type="integer"/>
        </Parameters>'''
    simlab.execute(SimLabParameters)

def CreateCoordinate(oNodeID, xNodeID, yNodeID):
    modelName = simlab.getModelName('FEM')

    # ID
    coordinateID = 1
    if simlab.isParameterPresent(MAX_ID_COORDINATE):
        coordinateID = simlab.getIntParameter('$'+MAX_ID_COORDINATE) + 1
    AddIntParameters(MAX_ID_COORDINATE, coordinateID)

    # Name
    name = BEARING_COORDINATE + str(coordinateID)

    CreateCoordinateSystem=''' <Coordinate UUID="b625f5cd-2925-4f9f-94a2-b58854934f8b" BCType="Coordinates" isObject="2">
    <tag Value="-1"/>
    <StackIndex Value="CoordinateXYPoint"/>
    <CoordinateXYPoint>
    <Name Value="''' + name + '''"/>
    <Center>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(oNodeID) + ''',</Node>
        </Entities>
    </Center>
    <PointX>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(xNodeID) + ''',</Node>
        </Entities>
    </PointX>
    <PointY>
        <Entities>
        <Model>''' + modelName + '''</Model>
        <Node>''' + str(yNodeID) + ''',</Node>
        </Entities>
    </PointY>
    <AxisID Value="''' + str(coordinateID) + '''"/>
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

    return coordinateID

def createCoordSys(faceId):
    modelNm = simlab.getModelName('FEM')

    # ID
    coordinateID = 1
    if simlab.isParameterPresent(MAX_ID_COORDINATE):
        coordinateID = simlab.getIntParameter('$'+MAX_ID_COORDINATE) + 1
    AddIntParameters(MAX_ID_COORDINATE, coordinateID)

    # Name
    coordName = BEARING_COORDINATE + str(coordinateID)

    modelNm = simlab.getModelName("FEM")
    CreateCoordinateSystem=''' <Coordinate isObject="2" BCType="Coordinates" UUID="b625f5cd-2925-4f9f-94a2-b58854934f8b">
    <tag Value="-1"/>
    <StackIndex Value="CoordinateCylindrical"/>
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
    <Name Value=""/>
    <Center ModelIds="" EntityTypes="" Value=""/>
    <PointX ModelIds="" EntityTypes="" Value=""/>
    <PointZ ModelIds="" EntityTypes="" Value=""/>
    <AxisID Value="1"/>
    <Type Value="Rectangle"/>
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
    <Name Value="'''+ coordName +'''"/>
    <Face>
    <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Face>'''+ str(faceId) +''',</Face>
    </Entities>
    </Face>
    <Node ModelIds="" EntityTypes="" Value=""/>
    <PointOnR Value="0"/>
    <AxisID Value="'''+ str(coordinateID) +'''"/>
    <Type Value="Cylindrical" Index="1"/>
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
    <NumCopies Check="0" Value="0"/>
    </CoordinateRotate>
    <CoordinateTranslate>
    <Magnitude Value="0"/>
    <Scale Value="0"/>
    <AxisCoordinateID Value="1"/>
    <DefineVectorCoordinateID Value="1"/>
    <AxisPoint Value="0,0,0"/>
    <NumCopies Check="0" Value="0"/>
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
