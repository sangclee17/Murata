from hwx import simlab
import tkinter.messagebox as messagebox
import simlablib
import muratautil

MESH_STATUS = "MESH_STATUS"
JOIN_PREFIX = "JoinGroup_"
NON_JOIN_GROUP = "NonJoinGroup"
MESH_SIZE = "_meshSize"
MIN_MESH_SIZE = "_minLength"
CYLINDER_FACE_GROUP = "Cylinders"
KEEP_HOLE_GROUP = "Bolt_Face"
PRESERVE_FACE_GROUP = "Preserve_Face"
MERGE_FACE_GROUP = "Merge_Face"

def _groupingBodies(fillHoleRadius):
    """
        1. Create body group for joining
        2. Create body Mesh control to remove holes in body
        3. Create cylinder face group to remove holes in face
        4. Add body mesh size parameters

        return join/non-joined body dictionary
    """
    meshGroupDict = {}
    joinedBodyNms = []
    bodyHolesRev = []

    modelNm = simlab.getModelName("CAD")
    bodies = list(simlab.getBodiesWithSubString(modelNm, ["*"]))
    bodyNmDict = muratautil.arrangeBodiesByPrefix(bodies)

    defaultMeshSize = simlab.getDoubleParameter('$DefaultMeshSize')

    for bodyPrefix in bodyNmDict:

        paramKey = "{}_joinGroup".format(bodyPrefix)
        paramVal = _getParameter(paramKey,"int")
        
        bodyHoleKey = "{}_bodyHoleFill".format(bodyPrefix)
        bodyHoleVal = _getParameter(bodyHoleKey, "int")
        
        bodyMeshSize = _getParameter("{}_meshSize".format(bodyPrefix), "double")
        if paramVal:
            meshGroupKey = JOIN_PREFIX + str(paramVal)
            if not meshGroupKey in meshGroupDict:
                meshGroupDict[meshGroupKey] = []
            meshGroupDict[meshGroupKey].extend(bodyNmDict[bodyPrefix])
            
            joinedBodyNms.extend(bodyNmDict[bodyPrefix])
        
        if bodyHoleVal:
            bodyHolesRev.extend(bodyNmDict[bodyPrefix])
        
        if not bodyMeshSize:
            bodyMeshSize = "{}_meshSize".format(bodyPrefix)
            simlablib.AddRealParameters(bodyMeshSize, defaultMeshSize)
                
    for joinGrp in meshGroupDict:
        _createBodyGrp(joinGrp, meshGroupDict[joinGrp])

    meshGroupDict[NON_JOIN_GROUP] = list(set(bodies) - set(joinedBodyNms))
    _createBodyGrp(NON_JOIN_GROUP, meshGroupDict[NON_JOIN_GROUP])
    
    bodyHoleMCName = "defeatureAllHolesOnBody_MC"
    faceHolsMcName = "defeatureHoleFaces_MC"
    if bodyHolesRev:
        _defeatureHolesMC(bodyHoleMCName, bodyHolesRev, entType="body")
    _createHoleGroups(bodyHolesRev, fillHoleRadius)
    _defeatureHolesMC(faceHolsMcName, CYLINDER_FACE_GROUP)

def surfaceMesh(meshProp, fillHoleRadius):
    modelNm = simlab.getModelName("CAD")
    if not modelNm:
        return
    
    defaultMeshSize, defaultMaxAngle, defaultAspectRatio = meshProp

    if not _getParameter("DefaultMeshSize", "double"):
        simlablib.AddRealParameters("DefaultMeshSize", defaultMeshSize)
    simlablib.AddRealParameters("DefaultMaxAngle", defaultMaxAngle)
    simlablib.AddRealParameters("DefaultAspectRatio", defaultAspectRatio)
    
    # Join/non-join body groups, body/face hole defeature groups
    _groupingBodies(fillHoleRadius)
    _createIsoMCForHoles("CAD", KEEP_HOLE_GROUP, defaultMeshSize, defaultMaxAngle, defaultAspectRatio)
    # Check face merge groups
    _crateMergeFaceGroupMC(MERGE_FACE_GROUP, defaultMaxAngle, defaultAspectRatio)
    # Check preserve face edge groups
    _createPreserveGroupMC("CAD", PRESERVE_FACE_GROUP)
    # body MC
    createPrefixBodyMC("CAD", defaultMeshSize, defaultMaxAngle, defaultAspectRatio)

    meshingAllBodies(defaultMeshSize, defaultMaxAngle, defaultAspectRatio)
    _addStringParameters(MESH_STATUS, "SURFACE")

    _transferGrpToFEM()
    _createPreserveGroupMC("FEM", PRESERVE_FACE_GROUP)
    _createIsoMCForHoles("FEM", KEEP_HOLE_GROUP, defaultMeshSize, defaultMaxAngle, defaultAspectRatio)
    createPrefixBodyMC("FEM", defaultMeshSize, defaultMaxAngle, defaultAspectRatio)

    # _exportSLB("G:/Documents/Murata/DataBase/DataBase2_Master_FEM.slb")

    femBodyGrps = simlab.getGroupsWithSubString("BodyGroup", ["*_SM"])
    for thisGrp in femBodyGrps:
        if thisGrp.startswith(JOIN_PREFIX):    
            _joinGroup(thisGrp, defaultMeshSize, defaultMaxAngle, defaultAspectRatio, tol = 1.5, localRemesh = 0)
    
    fillFreeEdges()
    modifyElements("FEM")
    simlab.resetModel()
    # _exportSLB("G:/Documents/Murata/DataBase/DataBase2_Master_FEM_Remeshed.slb")

def fillFreeEdges():
    modelNm = simlab.getModelName("FEM")
    FillHoles=''' <FillHole UUID="E9B9EC99-A6C1-4626-99FF-626F38A8CE4F" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="FillHole1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <Option Value="0"/>
    <Cylindercal_Face Value="0"/>
    <Single_Face Value="0"/>
    <FillPartialLoop Value="0"/>
    <MeshSize Value="" LocalReMesh="0"/>
    </FillHole>'''
    simlab.execute(FillHoles)

def meshingAllBodies(elemSize, maxAngle, aspectRat, imprint = 0):
    modelNm = simlab.getModelName("CAD")
    meshGrading = 1.5
    minElemSize = elemSize/aspectRat
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
    <AverageElementSize Value="'''+ str(elemSize) +'''" Checked="1"/>
    <MaximumElementSize Value="28.28" Checked="0"/>
    <MinimumElementSize Value="'''+ str(minElemSize) +'''"/>
    <GradeFactor Value="'''+ str(meshGrading) +'''"/>
    <MaximumAnglePerElement Value="'''+ str(maxAngle) +'''"/>
    <CurvatureMinimumElementSize Value="'''+ str(elemSize/2) +'''"/>
    <AspectRatio Value="'''+ str(aspectRat) +'''"/>
    <AdvancedOptions>
    <IdentifyFeaturesAndMesh Checked="1"/>
    <ImprintMeshing Checked="'''+ str(imprint) +'''"/>
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

def _meshingInGroup(grpNm, elemSize, maxAngle, aspectRat, imprint = 0):
    modelNm = "{}.gda".format(grpNm)
    meshGrading = 1.5
    minElemSize = elemSize/aspectRat
    SurfaceMesh=''' <SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
    <tag Value="-1"/>
    <SurfaceMeshType Value="Tri"/>
    <SupportEntities>
    <Group>"'''+ grpNm +'''",</Group>
    </SupportEntities>
    <Tri>
    <ElementType Value="Tri6"/>
    <AverageElementSize Value="'''+ str(elemSize) +'''" Checked="1"/>
    <MaximumElementSize Value="0" Checked="0"/>
    <MinimumElementSize Value="'''+ str(minElemSize) +'''"/>
    <GradeFactor Value="'''+ str(meshGrading) +'''"/>
    <MaximumAnglePerElement Value="'''+ str(maxAngle) +'''"/>
    <CurvatureMinimumElementSize Value="'''+ str(elemSize/2) +'''"/>
    <AspectRatio Value="'''+ str(aspectRat) +'''"/>
    <AdvancedOptions>
    <IdentifyFeaturesAndMesh Checked="1"/>
    <ImprintMeshing Checked="'''+ str(imprint) +'''"/>
    <BetterGeometryApproximation Checked="0"/>
    <CoarseMesh Checked="0"/>
    <CoarseMesh_UseExistingNodes Checked="0"/>
    <CreateMeshInNewModel Checked="1"/>
    <UserDefinedModelName Value="'''+ modelNm +'''"/>
    <Tri6WithStraightEdges Checked="0"/>
    <ImproveSkewAngle Value="0"/>
    <MappedMesh Value="0"/>
    <MeshPattern Value="0"/>
    </AdvancedOptions>
    </Tri>
    </SurfaceMesh>'''
    simlab.execute(SurfaceMesh)

# def getPrefixOfBodyNm(bodyNm):
#     bodyNm_sp = bodyNm.split("_")

#     bodyNmStrOnly = []
#     for bodyNm in bodyNm_sp:
#         if not _isInt(bodyNm):
#             bodyNmStrOnly.append(bodyNm)
#     return "_".join(bodyNmStrOnly)

# def _arrangeBodyByPrefix(bodyNms):
#     nameDict = {}
#     for thisBody in bodyNms:
#         prefix = muratautil.getPrefixOfBodyNm(thisBody)
#         if not prefix in nameDict:
#             nameDict[prefix] = []
#         nameDict[prefix].append(thisBody)
#     return nameDict

def _createHoleGroups(bodyNmsToExclude, holeSizeInRadius):
    _selectHoleFeatures(bodyNmsToExclude, 0.0, holeSizeInRadius)

    cylindersEnts = simlab.getEntityFromGroup(CYLINDER_FACE_GROUP)
    boltHoleGrps = simlab.getGroupsWithSubString("FaceGroup", [KEEP_HOLE_GROUP+"_*"])
    boltEnts = []
    for thisGrp in boltHoleGrps:
        boltEnts.extend(list(simlab.getEntityFromGroup(thisGrp)))

    cylindersEnts = list(set(cylindersEnts) - set(boltEnts))
    _updateFaceGrp(CYLINDER_FACE_GROUP, cylindersEnts)
    
def _createIsoMCForHoles(modelType, isoPrefix, elemSize, anglePerElem, aspectRat):
    grpNms = simlab.getGroupsWithSubString("FaceGroup",[isoPrefix+"_*"])
    grpNms = list(grpNms)

    if modelType == "FEM":
        grpNms = [thisGrp for thisGrp in grpNms if thisGrp.endswith("_SM")]
    
    if grpNms:
        mcNm = "{}_{}_MC".format(isoPrefix, modelType)
        _deleteMC(mcNm)
        MeshControls=''' <MeshControl isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" CheckBox="ON">
        <tag Value="-1"/>
        <MeshControlName Value="'''+ mcNm +'''"/>
        <MeshControlType Value="IsoLine"/>
        <Entities>
        <Group>'''+ ",".join('"{}"'.format(v) for v in grpNms) +''',</Group>
        </Entities>
        <Reverse ModelIds="" EntityTypes="" Value=""/>
        <MeshColor Value="112,47,160,"/>
        <IsoLine>
        <UseAxialSize Value="1"/>
        <AxialSize Value="'''+ str(elemSize) +'''"/>
        <AxialNumElems Value="0"/>
        <UseCirAngle Value="1"/>
        <CirAngle Value="'''+ str(anglePerElem) +'''"/>
        <CirNumElems Value="0"/>
        <AspectRatio Value="'''+ str(aspectRat) +'''"/>
        <MinElemSize Value="'''+ str(elemSize/aspectRat) +'''"/>
        <MergeFaces Value="0"/>
        <CreateUniformMesh Value="0"/>
        <StartPointPicked Value="0"/>
        <CentreX Value="0"/>
        <CentreY Value="0"/>
        <CentreZ Value="0"/>
        <RevDirection Value="0"/>
        <ExtendLayers Value="0"/>
        </IsoLine>
        </MeshControl>'''
        simlab.execute(MeshControls)

def modifyElements(modelType):
    modelNm = simlab.getModelName(modelType)
    ModifyElements=''' <Modify CheckBox="ON" UUID="28706164-e6e5-4544-b4a9-c052c4b6c60f">
    <Name Value="Modify1"/>
    <tag Value="-1"/>
    <Option Value="TOLOWER"/>
    <QuadDominant Value="1"/>
    <Entity>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body></Body>
    </Entities>
    </Entity>
    <IdealQuad Value="0"/>
    <UpdateAssociateRBENodes Value="1"/>
    </Modify>'''
    simlab.execute(ModifyElements)
    ModifyElements=''' <Modify CheckBox="ON" UUID="28706164-e6e5-4544-b4a9-c052c4b6c60f">
    <Name Value=""/>
    <tag Value="-1"/>
    <Option Value="TOHIGHER"/>
    <QuadDominant Value="1"/>
    <Entity>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body></Body>
    </Entities>
    </Entity>
    <IdealQuad Value="0"/>
    <UpdateAssociateRBENodes Value="1"/>
    </Modify>'''
    simlab.execute(ModifyElements)


def _updateFaceGrp(grpNm, faceEnts):
    modelNm = simlab.getModelName("CAD")
    CreateGroup=''' <CreateGroup Auto="1" isObject="4" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954" CheckBox="OFF">
    <tag Value="1"/>
    <Name OldValue="'''+ grpNm +'''" Value="'''+ grpNm +'''"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ ",".join(str(v) for v in faceEnts) +''',</Face>
    </Entities>
    </SupportEntities>
    <Type Value="Face"/>
    <Color Value="0,0,0,"/>
    <Dup Value="0"/>
    </CreateGroup>'''
    simlab.execute(CreateGroup)

def _selectHoleFeatures(bodyNmsToExclude, minRad, maxRad):
    modelNm = simlab.getModelName("CAD")
    _deleteGrp(CYLINDER_FACE_GROUP)
    bodyNms = simlab.getBodiesWithSubString(modelNm, ["*"])

    bodyToSearchHoles = []
    for thisBody in bodyNms :
        if not thisBody in bodyNmsToExclude:
            bodyToSearchHoles.append(thisBody)

    SelectFeatures=''' <SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ ",".join('"{}"'.format(v) for v in bodyToSearchHoles) +''',</Body>
    </Entities>
    </SupportEntities>
    <Arcs MaxValue="0.0" Value="0" MinValue="0.0"/>
    <ArcsAll Value="76"/>
    <Circles MaxValue="0.0" Value="0" MinValue="0.0"/>
    <CirclesAll Value="0"/>
    <Cones MaxValue="10" Value="0" MinValue="0.0"/>
    <ConeAll Value="0"/>
    <FullCone Value="0"/>
    <ClosedPartialCone Value="0"/>
    <OpenPartialCone Value="0"/>
    <Dics MaxValue="0.0" Value="0" MinValue="0.0"/>
    <DicsAll Value="0"/>
    <HollowDics MaxValue="0.0" Value="0" MinValue="0.0"/>
    <HollowDicsAll Value="0"/>
    <Cylinders MaxValue="'''+ str(maxRad) +'''" Value="1" MinValue="'''+ str(minRad) +'''"/>
    <CylindersAll Value="0"/>
    <FullCylinder Value="1"/>
    <ClosedPartialCylinder Value="1"/>
    <OpenPartialCylinder Value="0"/>
    <Fillets MaxValue="0.0" Value="0" MinValue="0.0"/>
    <FilletsOption Value="1"/>
    <PlanarFaces Value="0"/>
    <FourEdgedFaces Value="0"/>
    <ConnectedCoaxialFaces Value="0"/>
    <ThroughBoltHole MaxValue="0.0" Value="0" MinValue="0.0"/>
    <BlindBoltHole MaxValue="0.0" Value="0" MinValue="0.0"/>
    <BlindBoltHoleDepth MaxValue="0.0" Value="0" MinValue="0.0"/>
    <CreateGrp Name="'''+ CYLINDER_FACE_GROUP +'''" Value="1"/>
    <ArcLengthBased Value=""/>
    </SelectFeatures>'''
    simlab.execute(SelectFeatures)
    

def _createFaceGroupFromBodies(modelType, bodyNms, groupNm):
    modelNm = simlab.getModelName(modelType)
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ ",".join('"{}"'.format(v) for v in bodyNms) + ''',</Body>
    </Entities>
    </InputBody>
    <Option Value="Faces"/>
    <Groupname Value="'''+ groupNm +'''"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)


def _defeatureHolesMC(mcNm, entNm, entType = "group"):
    if entType == "group":
        _deleteMC(mcNm)
        MeshControls=''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
        <tag Value="-1"/>
        <MeshControlName Value="'''+ mcNm +'''"/>
        <MeshControlType Value="Defeature Hole"/>
        <Entities>
        <Group>"'''+ entNm +'''",</Group>
        </Entities>
        <Reverse EntityTypes="" Value="" ModelIds=""/>
        <MeshColor Value="112,47,160,"/>
        <RemoveHoleMeshControl>
        <InputType Value="0"/>
        <AssignHoleRadiusRange Value="0"/>
        <MinRadius Value="0"/>
        <MaxRadius Value="0"/>
        </RemoveHoleMeshControl>
        </MeshControl>'''
        simlab.execute(MeshControls)
    
    elif entType == "body":
        _deleteMC(mcNm)
        modelNm = simlab.getModelName("CAD")
        bodyNms = ",".join('"{}"'.format(v) for v in entNm)
        MeshControls=''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
        <tag Value="-1"/>
        <MeshControlName Value="'''+ mcNm +'''"/>
        <MeshControlType Value="Defeature Hole"/>
        <Entities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Body>'''+ bodyNms +''',</Body>
        </Entities>
        </Entities>
        <Reverse ModelIds="" Value="" EntityTypes=""/>
        <MeshColor Value="255,0,255,"/>
        <RemoveHoleMeshControl>
        <InputType Value="1"/>
        <AssignHoleRadiusRange Value="0"/>
        <MinRadius Value="0"/>
        <MaxRadius Value="0"/>
        </RemoveHoleMeshControl>
        </MeshControl>'''
        simlab.execute(MeshControls)

def _crateMergeFaceGroupMC(mergeFacePrefix, maxAngleElem, aspectRat):
    grpNms = simlab.getGroupsWithSubString("FaceGroup", [mergeFacePrefix + "*"])
    bodyToFaces = {}
    if grpNms:
        for thisGrp in grpNms:
            faceEnts = simlab.getEntityFromGroup(thisGrp)
            bodyNms = _associatedBodyWithFace(faceEnts)
            if bodyNms:
                if len(bodyNms) > 1:
                    for thisBody in bodyNms:
                        bodyFaces = _associatedFacesWithBody(thisBody)
                        keyBody = muratautil.getPrefixOfBodyNm(thisBody)
                        if keyBody in bodyToFaces:
                            bodyToFaces[keyBody].extend(list(set(bodyFaces).intersection(set(faceEnts))))
                        else:
                            bodyToFaces[keyBody] = list(set(bodyFaces).intersection(set(faceEnts)))
                else:
                    keyBody = muratautil.getPrefixOfBodyNm(bodyNms[0])
                    if keyBody in bodyToFaces:
                        bodyToFaces[keyBody].extend(list(faceEnts))
                    else:
                        bodyToFaces[keyBody] = list(faceEnts)
    for key in bodyToFaces:
        meshSizeParam = _getParameter(key + MESH_SIZE, "double")
        minMeshSizeParam = _getParameter(key + MIN_MESH_SIZE, "double")
        if meshSizeParam:
            mcNm = "{}_FaceMergeMC".format(key)
            if minMeshSizeParam: minElemSize = minMeshSizeParam
            else:minElemSize = meshSizeParam / aspectRat
            
            createFaceMC(mcNm, bodyToFaces[key], meshSizeParam, maxAngleElem, minElemSize)    

def createFaceMC(mcNm, faceIds, elemSize, maxAngle, minElem):
    modelNm = simlab.getModelName("CAD")
    _deleteMC(mcNm)
    MeshControls=''' <MeshControl UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1" CheckBox="ON">
    <tag Value="-1"/>
    <MeshControlName Value="'''+ mcNm +'''"/>
    <MeshControlType Value="Face"/>
    <Entities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ ",".join(str(v) for v in faceIds) +''',</Face>
    </Entities>
    </Entities>
    <Reverse ModelIds="" Value="" EntityTypes=""/>
    <MeshColor Value="255,255,0,"/>
    <FaceMeshControl>
    <AverageElementSize Value="'''+ str(elemSize) +'''"/>
    <MergeFace Value="1"/>
    <UseGlobal Value="0"/>
    <MinElemSize Value="'''+ str(minElem) +'''"/>
    <MaxAnglePerElement Value="'''+ str(maxAngle) +'''"/>
    <CurvatureMinElemSize Value="'''+ str(elemSize/2) +'''"/>
    <AspectRatio Value="'''+ str(elemSize/minElem) +'''"/>
    <SurfaceMeshGrading Value="1.5"/>
    <NoofLayer Value="0"/>
    <Isotropic Value="1"/>
    </FaceMeshControl>
    </MeshControl>'''
    simlab.execute(MeshControls)

def _associatedBodyWithFace(faceIds):
    """
        input-> faceIds in tuple
        return-> body name in tuple
    """
    modelNm = simlab.getModelName("CAD")
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

def _associatedFacesWithBody(bodyNm):
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>$Geometry</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </InputBody>
    <Option Value="Faces"/>
    <Groupname Value="SelectFaces_18"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)

    faceEnts = simlab.getEntityFromGroup("SelectFaces_18")
    _deleteGrp("SelectFaces_18")
    return faceEnts

def _createPreserveGroupMC(modelType, preserveGrpPrefix, preserveType = "Edges"):
    grpNms = simlab.getGroupsWithSubString("FaceGroup", [preserveGrpPrefix+"*"])
    if modelType == "FEM":
        grpNms = [thisGrp for thisGrp in grpNms if thisGrp.endswith("_SM")]
    if grpNms:
        mcNm = "{}_MC".format(preserveGrpPrefix)
        _deleteMC(mcNm)
        if preserveType == "Edges": typeValue = "2"
        elif preserveType == "Shape":typeValue = "3"
        MeshControls=''' <MeshControl UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1" CheckBox="ON">
        <tag Value="-1"/>
        <MeshControlName Value="'''+ mcNm +'''"/>
        <MeshControlType Value="Preserve Entities"/>
        <Entities>
        <Group>'''+ ",".join('"{}"'.format(v) for v in grpNms) +''',</Group>
        </Entities>
        <Reverse ModelIds="" Value="" EntityTypes=""/>
        <MeshColor Value="0,255,0,"/>
        <PreserveEntities>
        <PreserveType Value="'''+ typeValue +'''"/>
        </PreserveEntities>
        </MeshControl>'''
        simlab.execute(MeshControls)

def _createAdjacentFaceGroup(inputGrpNm, outputGrpNm, numOfLayer):
    SelectAdjacent=''' <SelectAdjacent UUID="06104eca-3dbf-45af-a99c-953c8fe0f4e4" recordable="0">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Group>"'''+ inputGrpNm +'''",</Group>
    </SupportEntities>
    <NoofLayer Value="'''+ str(numOfLayer) +'''"/>
    <VisiblesFaceOnly Value="0"/>
    <SelectAdjacent Value="0"/>
    <CreateGroup Value="1" Name="'''+ outputGrpNm +'''"/>
    </SelectAdjacent>'''
    simlab.execute(SelectAdjacent)

def _remeshSharedFaces(groupNm, elemSize, maxAngle, aspectRat, preserveBoundary = 0):
    LocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh4"/>
    <SupportEntities>
    <Group>"'''+ groupNm +'''",</Group>
    </SupportEntities>
    <ElemType Value="1"/>
    <AverageElemSize Value="'''+ str(elemSize) +'''"/>
    <MinElemSize Value="'''+ str(elemSize/aspectRat) +'''"/>
    <PreserveBoundaryEdges Value="'''+ str(preserveBoundary) +'''"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="'''+ str(maxAngle) +'''"/>
    <CurvatureMinElemSize Value="'''+ str(elemSize/2) +'''"/>
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

def _exportSLB(f_name):
    ExportSlb=''' <ExportSlb UUID="a155cd6e-8ae6-4720-8ab4-1f50d4a34d1c">
    <tag Value="-1"/>
    <Name Value=""/>
    <Option Value="1"/>
    <FileName Value="'''+ f_name +'''"/>
    </ExportSlb>'''
    simlab.execute(ExportSlb)

def _joinGroup(grpNm, defaultMeshSize, defaultMaxAngle, defaultAspectRatio, tol, localRemesh):
    joinTypes = ["GEOM_MATCHING_FACES", "GEOM_PLANAR_FACES", "CYLINDRICAL_FACES|CONICAL_FACES"]
    for thisType in joinTypes:
        meshOption = "Auto" if "CYLINDRICAL_FACES" in thisType else ""
        meshOrShape = "" if "CYLINDRICAL_FACES" in thisType else "Shape"
        Join=''' <Join UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value=""/>
        <Pick Value="Join"/>
        <JoinEntities>
        <Group>"'''+ grpNm +'''",</Group>
        </JoinEntities>
        <AlignEntities Value="" EntityTypes="" ModelIds=""/>
        <PreserveEntities Value="" EntityTypes="" ModelIds=""/>
        <Tolerance Value="'''+ str(tol) +'''"/>
        <JoinType Value="'''+ thisType +'''"/>
        <MeshOrShape Value="'''+ meshOrShape +'''"/>
        <MeshOption Value="'''+ meshOption +'''"/>
        <MeshParam Value=""/>
        <SplitFace Value="1"/>
        <LocalRemesh Value="'''+ str(localRemesh) +'''"/>
        </Join>'''
        simlab.execute(Join)
        _updateModel()
    _remeshSharedFaces(grpNm, defaultMeshSize, defaultMaxAngle, defaultAspectRatio)

def _updateModel():
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def _transferGrpToFEM():
    cadModelNm = simlab.getModelName("CAD")
    femModelNm = simlab.getModelName("FEM")
    TransferGroup=''' <TransferGroup UUID="6ee43b88-c248-427d-8107-c4144624bbab" CheckBox="ON">
    <tag Value="-1"/>
    <Method Value="CadID"/>
    <SourceBodies>
    <Entities>
    <Model>'''+ cadModelNm +'''</Model>
    <Body></Body>
    </Entities>
    </SourceBodies>
    <TargetBodies>
    <Entities>
    <Model>'''+ femModelNm +'''</Model>
    <Body></Body>
    </Entities>
    </TargetBodies>
    <RemoveEntitiesFromGroup Value="0"/>
    <Tolerance Value="0.001"/>
    </TransferGroup>'''
    simlab.execute(TransferGroup)

def _getParameter(key, valueType):
    """
        valueType: "int", "double", "string"
    """
    if not simlab.isParameterPresent(key):
        return None
    
    if valueType == "int": return simlab.getIntParameter("$"+key)
    elif valueType == "double": return simlab.getDoubleParameter("$"+key)
    elif valueType == "string": return simlab.getStringParameter("$"+key)


def createPrefixBodyMC(modelType, defaultMeshSize, defaultMaxAngle, defaultAspectRatio):
    modelNm = simlab.getModelName(modelType)
    bodyNms = simlab.getBodiesWithSubString(modelNm, ["*"])
    bodyNmsByPrefix = muratautil.arrangeBodiesByPrefix(bodyNms)
    for key in bodyNmsByPrefix:
        bodyMCWrapper(modelType, key, bodyNmsByPrefix[key], defaultMeshSize, defaultMaxAngle, defaultAspectRatio)

def bodyMCWrapper(modelType, bodyPrefix, prefixedBodies, defaultMeshSize, defaultMaxAngle, defaultAspectRatio):
    meshSizeParam = _getParameter(bodyPrefix + MESH_SIZE, "double")
    minMeshSizeParam = _getParameter(bodyPrefix + MIN_MESH_SIZE, "double")
    if not meshSizeParam:
        meshSizeParam = defaultMeshSize
    if not minMeshSizeParam:
        minMeshSizeParam = meshSizeParam/defaultAspectRatio
    mcNm = "{}_{}_BodyMC".format(bodyPrefix, modelType)
    _createBodyMC(modelType, mcNm, prefixedBodies, meshSizeParam, minMeshSizeParam, defaultMaxAngle)

def _createBodyMC(modelType, mcNm, bodyNms, meshSize, minLength, maxAngle):
    """
        input-> bodyNms in tuple or list
    """
    if not bodyNms:
        return
    _deleteMC(mcNm)
    modelNm = simlab.getModelName(modelType)
    MeshControls=''' <MeshControl isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" CheckBox="ON">
    <tag Value="-1"/>
    <MeshControlName Value="'''+ mcNm +'''"/>
    <MeshControlType Value="Body"/>
    <Entities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ ",".join('"{}"'.format(v) for v in bodyNms) +'''",</Body>
    </Entities>
    </Entities>
    <Reverse Value="" ModelIds="" EntityTypes=""/>
    <MeshColor Value=""/>
    <BodyMeshControl>
    <ElementType Value="11"/>
    <UseMaxElemSize Value="0"/>
    <AverageElementSize Value="'''+ str(meshSize) +'''"/>
    <MaxElemSize Value="14.14"/>
    <MinElemSize Value="'''+ str(minLength) +'''"/>
    <MaxAnglePerElement Value="'''+ str(maxAngle) +'''"/>
    <CurvatureMinElemSize Value="'''+ str(meshSize/2) +'''"/>
    <AspectRatio Value="''' + str(meshSize/minLength) + '''"/>
    <SurfaceMeshGrading Value="1.5"/>
    <MappedMesh Value="0"/>
    <CoarseMesh Value="0"/>
    <IdentifyFeaturesandMesh Value="0"/>
    </BodyMeshControl>
    </MeshControl>'''
    simlab.execute(MeshControls)

def _deleteMC(mcNm):
    DeleteMeshControl=''' <DeleteMeshControl UUID="c801afc7-a3eb-4dec-8bc1-8ac6382d4c6e" CheckBox="ON">
    <Name Value="'''+ mcNm +'''"/>
    </DeleteMeshControl>'''
    simlab.execute(DeleteMeshControl)

# def _getBodyNmsWithPrefix(bodyNm, bodiesWithSubString):
#     if len(bodiesWithSubString)== 1:
#         return bodiesWithSubString
#     bodyNmWithPrefix = []
#     prefix = bodyNm
#     for thisBody in bodiesWithSubString:
#         nameNoPrefix = _remove_prefix(thisBody, prefix)
#         if nameNoPrefix:
#             nameNoPrefix_sp = nameNoPrefix.split("_")
#             if len(nameNoPrefix_sp)>1:
#                 restNms = nameNoPrefix_sp[1:]
#                 if len(restNms)==1:
#                     if _isInt(restNms[0]):
#                         bodyNmWithPrefix.append(thisBody)
#     for thisNm in bodiesWithSubString:
#         if thisNm == bodyNm:
#             bodyNmWithPrefix.append(bodyNm)
#     return bodyNmWithPrefix

def _remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def _createBodyGrp(grpNm, bodyNms, modelType = "CAD"):
    _deleteGrp(grpNm)
    modelNm = simlab.getModelName(modelType)
    CreateGroup=''' <CreateGroup isObject="4" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954" CheckBox="OFF">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +'''" OldValue=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ ",".join('"{}"'.format(v) for v in bodyNms) +''',</Body>
    </Entities>
    </SupportEntities>
    <Type Value="Body"/>
    <Color Value="0,30,94,"/>
    <Dup Value="0"/>
    </CreateGroup>'''
    simlab.execute(CreateGroup)

def _deleteGrp(grpNm):
    if isinstance(grpNm, tuple) or isinstance(grpNm, list): grpNm = ",".join(grpNm)
    DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +''',"/>
    <Output/>
    </DeleteGroupControl>'''
    simlab.execute(DeleteGroupControl)

def _mergeModels(modelNms, outputModelNm = None):
    MergeModels = ''' <MergeModels gda="" UUID="D630B49E-5180-456e-A2BF-58688DC76D4A">
    <tag Value="-1"/>
    <Name Value="MergeModels2"/>
    <SupportEntities>'''

    for thisModel in modelNms:
        MergeModels +='''
        <Entities>
        <Model>'''+ thisModel +'''</Model>
        <Body></Body>
        </Entities>'''

    MergeModels += '''
    </SupportEntities>
    <Output/>
    </MergeModels>'''
    simlab.execute(MergeModels)

    currentModelName = simlab.getModelName("FEM")

    if outputModelNm:
        newModelNm = "{}.gda".format(outputModelNm)
        RenameModelQuuid=''' <RenameModelQuuid UUID="895c167e-fcf4-44dc-98cb-47e2328c7733" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value=""/>
        <ModelId Value=""/>
        <ModelName Value="'''+ currentModelName +'''"/>
        <NewName Value="'''+ newModelNm +'''"/>
        <Output/>
        </RenameModelQuuid>'''
        simlab.execute(RenameModelQuuid)

def meshCleanUp(volumeBodies, limit_aspectRatio):
    modelNm = simlab.getModelName("FEM")
    QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
    <ElementType Value="Tri"/>
    <Option Value="Cleanup"/>
    <Quality LimitValue="''' +str(limit_aspectRatio)+ '''" Condition="G Than Or Eq" Name="Aspect Ratio"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ ",".join('"{}"'.format(v) for v in volumeBodies) +''',</Body>
    </Entities>
    </SupportEntities>
    <CleanupType Value="Modify Element"/>
    <PreserveSurfaceSkew Check="0" Value="55"/>
    </QCheck>'''
    simlab.execute(QualityCheck)

def modifyIntersection(volumeBodies, tolVal):
    modelNm = simlab.getModelName("FEM")
    ModifyIntersections=''' <Intersection UUID="9b88366a-d021-40ea-a7a4-2ff23f864a2d">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ ",".join('"{}"'.format(v) for v in volumeBodies) +''',</Body>
    </Entities>
    </SupportEntities>
    <IntersectionCheck Value="1"/>
    <Tri_TriOverlapCheck Value="0"/>
    <Edge_TriOverlapCheck Value="0"/>
    <PentrationCheck Value="0"/>
    <Tolerance Value="'''+ str(tolVal) +'''"/>
    <GrpName Check="0" Name="Element_Group_3"/>
    <Operation Value="Show intersection"/>
    <SkipFaceNormal flag="false"/>
    </Intersection>'''
    simlab.execute(ModifyIntersections)

def addIntParameters(name, value):
    SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Name="''' + name + '''" Value="'''+ str(value) + '''" Type="integer"/>
        </Parameters>'''
    simlab.execute(SimLabParameters)

def _addStringParameters(name, value):
    if simlab.isParameterPresent(name):
        _deleteParameters(name)
    _createStringParameters(name, value)

def _createStringParameters(name, value):
    SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Name="''' + name + '''" Value="'''+ value+ '''" Type="string"/>
        </Parameters>'''
    simlab.execute(SimLabParameters)

def _deleteParameters(name):
    DeleteParameters=''' <DeleteParameters UUID="57a0affc-2283-4c6b-9da2-f4b5de469440">
        <ParameterNames Value="''' + name + '''"/>
        <!-- If Value attribute is empty,it deletes all global parameters. -->
        </DeleteParameters>'''
    simlab.execute(DeleteParameters)

def _checkVolumeBodyNamesByPrefix(bodyNm, noVolumeBodyPrefix):
    for thisPrefix in noVolumeBodyPrefix:
        if bodyNm.startswith(thisPrefix):
            return False
    return True

def _volumeMeshAllBodies(bodyNms, meshSize, stretchMinVal):
    modelNm = simlab.getModelName("FEM")
    VolumeMesh=''' <VolumeMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
    <tag Value="-1"/>
    <Name Value="VolumeMesher1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNms).replace("'",'"').strip("[]""()") +'''</Body>
    </Entities>
    </SupportEntities>
    <MeshType Value="Tet10"/>
    <AverageElemSize Value="''' + str(meshSize) + '''"/>
    <MinimumElementSize Value="0"/>
    <AspectRatio Value="0"/>
    <MaxElemSize Checked="0" Value="0"/>
    <InternalGrading Value="2"/>
    <MinQuality Value="'''+ str(stretchMinVal) +'''"/>
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
    # print(VolumeMesh)
    simlab.execute(VolumeMesh)

def resolveFreeEdges(bodyNms):
    modelNm = simlab.getModelName("FEM")

    FillHoles=''' <FillHole UUID="E9B9EC99-A6C1-4626-99FF-626F38A8CE4F" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="FillHole1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNms).replace("'", '"').strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    <Option Value="0"/>
    <Cylindercal_Face Value="0"/>
    <Single_Face Value="0"/>
    <FillPartialLoop Value="0"/>
    <MeshSize LocalReMesh="0" Value=""/>
    </FillHole>'''
    simlab.execute(FillHoles)

def _getBodyNmsFromFace(modelType, faceId):
    modelNm = simlab.getModelName(modelType)
    bodyGrpNm = "SelectBodies_95"
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ str(faceId).strip("()") +'''</Face>
    </Entities>
    </InputFaces>
    <Option Value="Bodies"/>
    <Groupname Value="'''+ bodyGrpNm +'''"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)
    bodyNms = simlab.getBodiesFromGroup(bodyGrpNm)
            
    _deleteGrp(bodyGrpNm)
    return bodyNms

def volumeMesh(meshSize, stretchMinVal):
    modelNm = simlab.getModelName("FEM")
    if not modelNm:return

    meshStatus = _getParameter(MESH_STATUS, "string")
    if not meshStatus:
        messagebox.showinfo("情報", "The surface meshed model is required to continue to volume mesh")
        return
    
    bodies = list(simlab.getBodiesWithSubString(modelNm, ["*"]))
    bodyNmDict = muratautil.arrangeBodiesByPrefix(bodies)
    volumeBodies = []
    for thisPrefix in bodyNmDict:
        if simlab.isParameterPresent(thisPrefix):
            volumeBodies.extend(bodyNmDict[thisPrefix])
    
    # split bodies
    bodySplitFaceGrps = simlab.getGroupsWithSubString("FaceGroup",["Body_Split_Face*"])
    bodySplitFaceGrpsInCAd = [thisGrp for thisGrp in bodySplitFaceGrps if not thisGrp.endswith("_SM")]
    # print("bodySplitFaceGrps", bodySplitFaceGrpsInCAd)
    splitBodies = []
    for thisFaceGrp in bodySplitFaceGrpsInCAd:
        faceEnts = simlab.getEntityFromGroup(thisFaceGrp)
        bodyNm = _getBodyNmsFromFace("CAD",faceEnts)
        bodyNm = str(bodyNm).strip("()"",""'")
        # print("bodyNm", bodyNm+"*")
        femBodies = list(simlab.getBodiesWithSubString(modelNm,[bodyNm+"*"]))
        # print("femBodies",femBodies)
        splitBodies.extend(femBodies)
        
    # print("splitBodies", splitBodies)

    volumeBodies = list(set(volumeBodies) - set(splitBodies))

    # print("volumeBodies", volumeBodies)
     
    _deleteGrp("INTERSECT_ELEMENT")
    modifyIntersection(volumeBodies, 1e-06)
    intersectElemGrp = simlab.getGroupsWithSubString("ElementGroup",["INTERSECT_ELEMENT*"])
    if intersectElemGrp:
        messagebox.showinfo("情報","Resolve intersecting elements")
        return
    
    meshCleanUp(volumeBodies, 100)
    
    _volumeMeshAllBodies(volumeBodies, meshSize, stretchMinVal)

    for thisBody in splitBodies:
        _volumeMeshAllBodies((thisBody,), meshSize, stretchMinVal)

    _addStringParameters(MESH_STATUS, "VOLUME")