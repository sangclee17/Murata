from hwx import simlab
import simlablib
import simlabutil
import linearguideutil
import numpy as np
import importlib
import bearingutil
import muratautil
import tkinter.messagebox as messagebox

ISOGROUP = "Iso_Faces_"
ISOMESHSIZE = "IsoMeshSize"
SMALLHOLESIZE = "HoleSmall"
BIGHOLESIZE = "HoleBig"
ISOANGLE = "IsoAngle"
FILLHOLEGROUP = "Hole_Fill_"
KEEPHOLEGROUP = "Bolt_Face_"
WASHER_EDGE = 'Washer_Edge_'
LOGO_FACE = 'Logo_Face_'
SHARE_FACE = "_Share_Faces_"

def createRegionMeshControl(meshProp, trimMid = False):
    modelNm = simlab.getModelName("CAD")

    mcName, bodyNm, entId1, entId2 = meshProp
    pt_A = simlab.definePlaneFromEntity(modelNm, int(entId1))
    pt_B = simlab.definePlaneFromEntity(modelNm, int(entId2))
    # print("pt_A",entId1)
    # print("pt_B", entId2)

    if not pt_A or not pt_B:
        messagebox.showinfo("情報","円弧エッジ選択してください。")
        return

    if trimMid:
        importlib.reload(linearguideutil)
        dist = linearguideutil.distanceBetweenPointAndPlane(pt_A,pt_B[0])
        n_A = linearguideutil.equationOfPlane(pt_A)
        # print("n_A",n_A)
        a,b,c,d = n_A
        x_b, y_b, z_b = pt_B[0]
        if a * x_b + b * y_b + c *z_b + d < 0:
            # print("-direction")
            n_AtoB = np.array([a, b, c])*-1
            # print("n_AtoB", n_AtoB)
        else:
            # print("positive")
            n_AtoB = np.array([a, b, c])
            # print("n_AtoB", n_AtoB)
        
        p1 = np.array(pt_A[0])
        # print("p1",p1)
        p1_t = p1 + n_AtoB * dist /2
        # print("p1_t", p1_t)

        p2 = np.array(pt_A[1])
        # print("p2",p2)
        p2_t = p2 + n_AtoB * dist /2
        # print("p2_t", p2_t)

        p3 = np.array(pt_A[2])
        # print("p3",p3)
        p3_t = p3 + n_AtoB * dist /2
        # print("p3_t", p3_t)
        
        midPoints = simlabutil.Convert3PointsOnPlaneTo4Points((p1_t, p2_t, p3_t))

        MeshControls=''' <MeshControl CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3" isObject="1">
        <tag Value="-1"/>
        <MeshControlName Value="'''+ mcName +'''"/>
        <MeshControlType Value="Region"/>
        <Entities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Body>"'''+ bodyNm +'''",</Body>
        </Entities>
        </Entities>
        <Reverse EntityTypes="" Value="" ModelIds=""/>
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
        <BreakOptions Value="2"/>
        <RType Value="578"/>
        <CreateInternalFace Value="0"/>
        <CuboidRegData/>
        <CYlRegData/>
        <PlaneRegData>
        <Plane PlanePoints="'''+ ",".join(str(v) for pt in midPoints for v in pt) +''',"/>
        </PlaneRegData>
        <SphereRegData/>
        <ConeRegData/>
        </RegionMeshControl>
        </MeshControl>'''
        simlab.execute(MeshControls)
        # print(MeshControls)
    
    else:
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

# def _getNormalVector(pt1, pt2, pt3):
#     pt1_x, pt1_y, pt1_z = pt1
#     pt2_x, pt2_y, pt2_z = pt2
#     pt3_x, pt3_y, pt3_z = pt3

#     vect_21 = pt1_x - pt2_x, pt1_y - pt2_y, pt1_z - pt2_z
#     vect_23 = pt3_x - pt2_x, pt3_y - pt2_y, pt3_z - pt2_z

#     cross_13 = np.cross(vect_21, vect_23)
#     c_x, c_y, c_z = cross_13
#     normalVect = c_x - pt2_x, c_y - pt2_y, c_z - pt2_z
#     normalVect_size = np.linalg.norm(normalVect)
#     normal_unit_vecotr = normalVect[0]/normalVect_size, normalVect[1]/normalVect_size, normalVect[2]/normalVect_size

#     return normal_unit_vecotr

def applyMeshControl(meshSize, angle, smallHoleSize, bigHoleSize):
    # Case 1: apply MC for the first time
    # Case 2: re-apply for the updated bolt holes 
    # Case 3: re-apply with new mesh control parameters
    if simlab.isParameterPresent(ISOMESHSIZE):
        # Case 2 and 3
        if getParameter(ISOMESHSIZE) == meshSize and getParameter(ISOANGLE) == angle and getParameter(SMALLHOLESIZE) == smallHoleSize and getParameter(BIGHOLESIZE) == bigHoleSize:
            # Case 2
            boltGrps = simlab.getGroupsWithSubString("FaceGroup", [KEEPHOLEGROUP+"*"])
            for thisGrp in boltGrps:
                deleteMC(thisGrp+"MC")
                if angle == 60:applyIsoMC(thisGrp, meshSize, angle, mergeFaces=1)
                else:applyIsoMC(thisGrp, meshSize, angle, mergeFaces=0)
        else:
            # Case 3
            grpsToDelete = list(simlab.getGroupsWithSubString("FaceGroup", [FILLHOLEGROUP+"*"]))
            grpsToDelete.extend(list(simlab.getGroupsWithSubString("FaceGroup", [ISOGROUP+"*"])))
            for thisGrp in grpsToDelete:
                deleteGroup(thisGrp)
                deleteMC(thisGrp+"MC")
            applyNewMeshControl(meshSize, angle, smallHoleSize, bigHoleSize)
    else:
        # Case 1
        applyNewMeshControl(meshSize, angle, smallHoleSize, bigHoleSize)

def getBodyNmSet():
    temp = []
    allBodies = simlab.getBodiesWithSubString(simlab.getModelName("CAD"),["*"])
    for thisBody in allBodies:
        splBody = thisBody.split("_")
        if len(splBody) == 1:
            if not splBody[0] in temp:
                temp.append(thisBody)
        elif len(splBody) > 1:
            nameTemp = [] 
            for aChuck in splBody:
                if not representsInt(aChuck):
                    nameTemp.append(aChuck)
            bodyNameOrigin = "_".join(nameTemp)
            if not bodyNameOrigin in temp:
                temp.append(bodyNameOrigin)
    return temp 

def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def applyNewMeshControl(meshSize, angle, smallHoleSize, bigHoleSize):
    # fill small holes
    featureSel_createFillHoleGrp(FILLHOLEGROUP, smallHoleSize)
    fillHoleGrps = simlab.getGroupsWithSubString("FaceGroup", [FILLHOLEGROUP+"*"])
    for thisGrp in fillHoleGrps:
        defeatureHolesMC(thisGrp)

    # create Isoline MC
    featureSel_createIsoGrp(ISOGROUP, bigHoleSize, smallHoleSize + 0.001, angle)
    isoGrps = simlab.getGroupsWithSubString("FaceGroup", [ISOGROUP+"*"])
    for thisGrp in isoGrps:
        if angle == 60: applyIsoMC(thisGrp, meshSize, angle, mergeFaces = 1)
        else: applyIsoMC(thisGrp, meshSize, angle, mergeFaces = 0)

    # Bolt Holes MC
    boltGrps = simlab.getGroupsWithSubString("FaceGroup", [KEEPHOLEGROUP+"*"])
    for thisGrp in boltGrps:
        deleteMC(thisGrp+"MC")
        if angle == 60:applyIsoMC(thisGrp, meshSize, angle, mergeFaces=1)
        else:applyIsoMC(thisGrp, meshSize, angle, mergeFaces=0)

    createParameter(ISOMESHSIZE, meshSize)
    createParameter(ISOANGLE, angle)
    createParameter(SMALLHOLESIZE, smallHoleSize)
    createParameter(BIGHOLESIZE, bigHoleSize)
    
def createParameter(name, value):
    if simlab.isParameterPresent(name):
        deleteParam(name)
    SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
    <ParamInfo Type="real" Name="'''+ name +'''" Value="'''+ str(value) +'''"/>
    </Parameters>'''
    simlab.execute(SimLabParameters)

def featureSel_createFillHoleGrp(grpNm, radMax):
    modelNm = simlab.getModelName('CAD')
    bodyNm = simlab.getBodiesWithSubString(modelNm,['*'])
    cylGrp = grpNm + "cyl_"
    SelectFeatures=''' <SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
    <SupportEntities>
    <Entities>
    <Model>'''+ str(modelNm) +'''</Model>
    <Body>'''+ ','.join('"{}"'.format(v) for v in bodyNm) +''',</Body>
    </Entities>
    </SupportEntities>
    <Arcs MaxValue="0.0" MinValue="0.0" Value="0"/>
    <ArcsAll Value="0"/>
    <Circles MaxValue="11" MinValue="8" Value="0"/>
    <CirclesAll Value="0"/>
    <Cones MaxValue="5" MinValue="0.0" Value="0"/>
    <ConeAll Value="0"/>
    <FullCone Value="0"/>
    <ClosedPartialCone Value="0"/>
    <OpenPartialCone Value="0"/>
    <Dics MaxValue="0.0" MinValue="0.0" Value="0"/>
    <DicsAll Value="0"/>
    <HollowDics MaxValue="0.0" MinValue="0.0" Value="0"/>
    <HollowDicsAll Value="0"/>
    <Cylinders MaxValue="'''+ str(radMax) +'''" MinValue="'''+ str(0.0) +'''" Value="1"/>
    <CylindersAll Value="0"/>
    <FullCylinder Value="1"/>
    <ClosedPartialCylinder Value="1"/>
    <OpenPartialCylinder Value="0"/>
    <Fillets MaxValue="16" MinValue="0.0" Value="0"/>
    <FilletsOption Value="1"/>
    <PlanarFaces Value="0"/>
    <FourEdgedFaces Value="0"/>
    <ConnectedCoaxialFaces Value="0"/>
    <ThroughBoltHole MaxValue="10" MinValue="8" Value="0"/>
    <BlindBoltHole MaxValue="0.0" MinValue="0.0" Value="0"/>
    <BlindBoltHoleDepth MaxValue="0.0" MinValue="0.0" Value="0"/>
    <CreateGrp Name="'''+ cylGrp +'''" Value="1"/>
    <ArcLengthBased Value=""/>
    </SelectFeatures>'''
    simlab.execute(SelectFeatures)

    boltGrps = simlab.getGroupsWithSubString("FaceGroup", [KEEPHOLEGROUP + "*"])
    boltHoleEnts = []
    for thisGrp in boltGrps:
        thisEnts = list(simlab.getEntityFromGroup(thisGrp))
        boltHoleEnts.extend(thisEnts)

    if boltHoleEnts:      
        cylGrpEnts = set(simlab.getEntityFromGroup(cylGrp)) - set(boltHoleEnts)
        updateGrp("Face", cylGrp, cylGrp, tuple(cylGrpEnts))

def defeatureHolesMC(grpNm):
    mcName = grpNm + "MC"
    MeshControls=''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
    <tag Value="-1"/>
    <MeshControlName Value="'''+ mcName +'''"/>
    <MeshControlType Value="Defeature Hole"/>
    <Entities>
    <Group>"'''+ grpNm +'''",</Group>
    </Entities>
    <Reverse Value="" EntityTypes="" ModelIds=""/>
    <MeshColor Value="0,255,0,"/>
    <RemoveHoleMeshControl>
    <InputType Value="0"/>
    <AssignHoleRadiusRange Value="0"/>
    <MinRadius Value="0"/>
    <MaxRadius Value="0"/>
    </RemoveHoleMeshControl>
    </MeshControl>'''
    simlab.execute(MeshControls)

def deleteGroup(groupNm):
    grpToDelete = ','.join(str(v) for v in groupNm) if isinstance(groupNm, tuple) or isinstance(groupNm, list) else str(groupNm)

    DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
    <tag Value="-1"/>
    <Name Value="'''+ grpToDelete +''',"/>
    <Output/>
    </DeleteGroupControl>'''
    simlab.execute(DeleteGroupControl)

def featureSel_createIsoGrp(grpNm, radMax, radMin, angle):
    cylGrp = grpNm + "cyl_"
    coneGrp = grpNm + "cone_"
    modelNm = simlab.getModelName('CAD')
    bodyNm = simlab.getBodiesWithSubString(modelNm,['*'])

    SelectFeatures=''' <SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
    <SupportEntities>
    <Entities>
    <Model>'''+ str(modelNm) +'''</Model>
    <Body>'''+ ','.join('"{}"'.format(v) for v in bodyNm) +''',</Body>
    </Entities>
    </SupportEntities>
    <Arcs MaxValue="0.0" MinValue="0.0" Value="0"/>
    <ArcsAll Value="0"/>
    <Circles MaxValue="11" MinValue="8" Value="0"/>
    <CirclesAll Value="0"/>
    <Cones MaxValue="'''+ str(radMax) +'''" MinValue="'''+ str(radMin) +'''" Value="1"/>
    <ConeAll Value="0"/>
    <FullCone Value="1"/>
    <ClosedPartialCone Value="1"/>
    <OpenPartialCone Value="0"/>
    <Dics MaxValue="0.0" MinValue="0.0" Value="0"/>
    <DicsAll Value="0"/>
    <HollowDics MaxValue="0.0" MinValue="0.0" Value="0"/>
    <HollowDicsAll Value="0"/>
    <Cylinders MaxValue="2" MinValue="0.7" Value="0"/>
    <CylindersAll Value="0"/>
    <FullCylinder Value="0"/>
    <ClosedPartialCylinder Value="0"/>
    <OpenPartialCylinder Value="0"/>
    <Fillets MaxValue="16" MinValue="0.0" Value="0"/>
    <FilletsOption Value="1"/>
    <PlanarFaces Value="0"/>
    <FourEdgedFaces Value="0"/>
    <ConnectedCoaxialFaces Value="0"/>
    <ThroughBoltHole MaxValue="10" MinValue="8" Value="0"/>
    <BlindBoltHole MaxValue="0.0" MinValue="0.0" Value="0"/>
    <BlindBoltHoleDepth MaxValue="0.0" MinValue="0.0" Value="0"/>
    <CreateGrp Name="'''+ coneGrp +'''" Value="1"/>
    <ArcLengthBased Value=""/>
    </SelectFeatures>'''
    simlab.execute(SelectFeatures)
    SelectFeatures=''' <SelectFeatures CheckBox="ON" UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E">
    <SupportEntities>
    <Entities>
    <Model>'''+ str(modelNm) +'''</Model>
    <Body>'''+ ','.join('"{}"'.format(v) for v in bodyNm) +''',</Body>
    </Entities>
    </SupportEntities>
    <Arcs MaxValue="0.0" MinValue="0.0" Value="0"/>
    <ArcsAll Value="0"/>
    <Circles MaxValue="11" MinValue="8" Value="0"/>
    <CirclesAll Value="0"/>
    <Cones MaxValue="5" MinValue="0.0" Value="0"/>
    <ConeAll Value="0"/>
    <FullCone Value="0"/>
    <ClosedPartialCone Value="0"/>
    <OpenPartialCone Value="0"/>
    <Dics MaxValue="0.0" MinValue="0.0" Value="0"/>
    <DicsAll Value="0"/>
    <HollowDics MaxValue="0.0" MinValue="0.0" Value="0"/>
    <HollowDicsAll Value="0"/>
    <Cylinders MaxValue="'''+ str(radMax) +'''" MinValue="'''+ str(radMin) +'''" Value="1"/>
    <CylindersAll Value="0"/>
    <FullCylinder Value="1"/>
    <ClosedPartialCylinder Value="1"/>
    <OpenPartialCylinder Value="0"/>
    <Fillets MaxValue="16" MinValue="0.0" Value="0"/>
    <FilletsOption Value="1"/>
    <PlanarFaces Value="0"/>
    <FourEdgedFaces Value="0"/>
    <ConnectedCoaxialFaces Value="0"/>
    <ThroughBoltHole MaxValue="10" MinValue="8" Value="0"/>
    <BlindBoltHole MaxValue="0.0" MinValue="0.0" Value="0"/>
    <BlindBoltHoleDepth MaxValue="0.0" MinValue="0.0" Value="0"/>
    <CreateGrp Name="'''+ cylGrp +'''" Value="1"/>
    <ArcLengthBased Value=""/>
    </SelectFeatures>'''
    simlab.execute(SelectFeatures)

    boltGrps = simlab.getGroupsWithSubString("FaceGroup", [KEEPHOLEGROUP + "*"])
    boltHoleEnts = []
    for thisGrp in boltGrps:
        thisEnts = list(simlab.getEntityFromGroup(thisGrp))
        boltHoleEnts.extend(thisEnts)

    if boltHoleEnts:
        conGrpEnts = set(simlab.getEntityFromGroup(coneGrp)) - set(boltHoleEnts)
        updateGrp("Face", coneGrp, coneGrp, tuple(conGrpEnts))       
        cylGrpEnts = set(simlab.getEntityFromGroup(cylGrp)) - set(boltHoleEnts)
        updateGrp("Face", cylGrp, cylGrp, tuple(cylGrpEnts))
    if angle == 60:
        splitAndCreateGrpFor60(cylGrp)
        splitAndCreateGrpFor60(coneGrp)

def applyIsoMC(grpNm, meshSize, angle, aspectRatio = 10, mergeFaces = 0):
    mcNm = grpNm +'MC'
    deleteMC(mcNm)
    MeshControls=''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
    <tag Value="-1"/>
    <MeshControlName Value="'''+ mcNm +'''"/>
    <MeshControlType Value="IsoLine"/>
    <Entities>
    <Group>"'''+ str(grpNm) +'''",</Group>
    </Entities>
    <Reverse EntityTypes="" ModelIds="" Value=""/>
    <MeshColor Value="0,206,255,"/>
    <IsoLine>
    <UseAxialSize Value="1"/>
    <AxialSize Value="'''+ str(meshSize) +'''"/>
    <AxialNumElems Value="0"/>
    <UseCirAngle Value="1"/>
    <CirAngle Value="'''+ str(angle) +'''"/>
    <CirNumElems Value="0"/>
    <AspectRatio Value="'''+ str(aspectRatio) +'''"/>
    <MinElemSize Value="'''+ str(meshSize/aspectRatio) +'''"/>
    <MergeFaces Value="'''+ str(mergeFaces) +'''"/>
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

# def splitGrpByRad():
#     ModelNM = simlab.getModelName('CAD')
#     edgeGrp = list(simlab.getGroupsWithSubString("EdgeGroup",[WASHER_EDGE+"*"]))
#     if len(edgeGrp):
#         edgeGrpDict = {}
#         for aGrp in edgeGrp:
#             grpNms = list(simlab.createGroupsOfConnectedEntities(aGrp))
#             for grpNm in grpNms:
#                 edgeEntities = list(simlab.getEntityFromGroup(grpNm))
#                 thisEdge = edgeEntities[0]
#                 _, Rad = simlab.getArcEdgeAttributes(str(ModelNM), thisEdge)
#                 washerGrpNm = '{}{}'.format(WASHER_EDGE, round(float(str(Rad).strip("(),")),2))
#                 if washerGrpNm in edgeGrpDict.keys():
#                     edgeGrpDict[washerGrpNm].extend(edgeEntities)
#                 else:
#                     edgeGrpDict[washerGrpNm] = edgeEntities
#             deleteGroup(grpNms)
#         deleteGroup(edgeGrp)

#         # Recreate Group
#         for key, value in edgeGrpDict.items():
#             createWasherGroup(key, value)

def addToWasherGrp(edgeGrpNm, tempEdgeGrp):
    edgeLst = simlab.getEntityFromGroup(tempEdgeGrp)
    edgeGrps = simlab.getGroupsWithSubString("EdgeGroup",[edgeGrpNm])
    allEdgeEnts = []
    if edgeGrps:
        for thisGrp in edgeGrps:
            edgeEntities = list(simlab.getEntityFromGroup(thisGrp))
            for thisEdge in edgeEntities:
                allEdgeEnts.append(thisEdge)
        allEdgeEnts.extend(edgeLst)
        updateGrp("Edge",thisGrp, thisGrp, allEdgeEnts)
    else:
        createWasherGroup(edgeGrpNm, edgeLst)
    deleteGroup(tempEdgeGrp)
    
def createWasherGroup(grpNm, entList):
    ModelNM = simlab.getModelName('CAD')

    edgeList = ','.join(str(v) for v in entList)
    CreateGroup=''' <CreateGroup CheckBox="OFF" isObject="4" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954">
    <tag Value="-1"/>
    <Name OldValue="" Value="'''+ grpNm +'''"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ ModelNM +'''</Model>
    <Edge>'''+ edgeList +''',</Edge>
    </Entities>
    </SupportEntities>
    <Type Value="Edge"/>
    <Color Value="255,255,0,"/>
    <Dup Value="0"/>
    </CreateGroup>'''
    simlab.execute(CreateGroup)

def createWasherMesh():
    edgeGrp = list(simlab.getGroupsWithSubString("EdgeGroup",[WASHER_EDGE+"*"]))
    if len(edgeGrp):
        for aGrp in edgeGrp:
            mcNm = aGrp + '_MC' 
            deleteMC(mcNm)
            outerRad = float(aGrp.split('_')[-1])

            MeshControls=''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
            <tag Value="-1"/>
            <MeshControlName Value="'''+ mcNm +'''"/>
            <MeshControlType Value="Washer"/>
            <Entities>
            <Group>"'''+ aGrp +'''",</Group>
            </Entities>
            <Reverse EntityTypes="" ModelIds="" Value=""/>
            <MeshColor Value=""/>
            <WasherMeshControl>
            <OptionToDefWasher Value="2"/>
            <RatioOfOuterToInnerRadius Value="1.2"/>
            <WasherWidth Value="0.5"/>
            <OuterRadus Value="'''+ str(outerRad) +'''"/>
            <NumLayers Value="1"/>
            <AssignCirRadiusRange Value="0"/>
            <MinRadius Value="0"/>
            <MaxRadius Value="0"/>
            </WasherMeshControl>
            </MeshControl>'''
            simlab.execute(MeshControls)

def getEntireGroupEntities(grpNm):
    entireGrpEntities = []
    faceGrpAll = list(simlab.getGroupsWithSubString('FaceGroup',['*']))
    thisGrp = list(simlab.getGroupsWithSubString('FaceGroup',[grpNm+'*']))
    faceGrpAll = list(set(faceGrpAll)-set(thisGrp))
    for grpName in faceGrpAll:
        grpEnt = list(simlab.getEntityFromGroup(grpName))
        entireGrpEntities.extend(grpEnt)
    return entireGrpEntities

def updateToUniqueGrpEnt(grpNm):
    grpEnt = list(simlab.getEntityFromGroup(grpNm))
    entireGrpEnt = getEntireGroupEntities(grpNm)
    uniqueEnt = [elem for elem in grpEnt if not elem in entireGrpEnt]
    if len(uniqueEnt)!= 0:
        # print('For {}, uniqueEnt len is {} grpEnt len is {}'.format(grpNm,len(uniqueEnt), len(grpEnt)))
        if len(uniqueEnt) != len(grpEnt):
            deleteGroup(grpNm)
            createFaceGroup(grpNm, uniqueEnt)
            # print('find duplicate entities in {}...recreate group with entitieis {}'.format(grpNm, set(uniqueEnt)))
    else:
        deleteGroup(grpNm)
        # print('delete no unique ent group...{}'.format(grpNm))

def splitAndCreateGrpFor60(grpNm):
    adjFaceGrp = "AdjFaceGrp"
    isoFaceGrps = simlab.createGroupsOfConnectedEntities(grpNm)
    for isoFaceGrp in isoFaceGrps:
        faceEnt = list(simlab.getEntityFromGroup(isoFaceGrp))
        if len(faceEnt) == 4:
            firstEnt = faceEnt[0]
            faceEnt.remove(firstEnt)
            if simlab.isGroupPresent(adjFaceGrp):
                deleteGroup(adjFaceGrp)
            createAdjacentGrp(adjFaceGrp,firstEnt)
            if simlab.isGroupPresent(adjFaceGrp):
                adjEnt = simlab.getEntityFromGroup(adjFaceGrp)
                for aEnt in faceEnt:
                    if aEnt in adjEnt:
                        grpNm1 = '{}_A_'.format(isoFaceGrp)
                        createFaceGroup(grpNm1, [firstEnt,aEnt])
                        faceEnt.remove(aEnt)

                        grpNm2 = '{}_B_'.format(isoFaceGrp)
                        createFaceGroup(grpNm2, faceEnt)
                        break
        deleteGroup(isoFaceGrp)
    deleteGroup(adjFaceGrp)

def getGroupAndEntities():
    faceGrpAll = set(simlab.getGroupsWithSubString('FaceGroup',['*']))
    noBearingFaceGrp = list(faceGrpAll - set(simlab.getGroupsWithSubString('FaceGroup', ['Bearing*'])))
    
    grpDict = {}
    for aGrp in noBearingFaceGrp:
        grpDict[aGrp] = list(simlab.getEntityFromGroup(aGrp))
    # print(grpDict)
    return grpDict

def updateGrp(grpType, oldGrpNm, newGrpNm, entLst):
    ModelNM = simlab.getModelName('CAD')
    CreateGroup=''' <CreateGroup CheckBox="OFF" isObject="4" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954" Auto="1">
    <tag Value="1"/>
    <Name OldValue="'''+ oldGrpNm +'''" Value="'''+ newGrpNm +'''"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ ModelNM +'''</Model>
    <'''+ grpType +'''>'''+','.join(str(v) for v in entLst)+''',</'''+ grpType +'''>
    </Entities>
    </SupportEntities>
    <Type Value="'''+ grpType +'''"/>
    <Color Value="112,47,160,"/>
    <Dup Value="0"/>
    </CreateGroup>'''
    simlab.execute(CreateGroup)

def createPersistentFaceGroup(grpNm, faceEnt):
    grpDict = getGroupAndEntities()
    entireGrpEntities = []
    for v in grpDict.values():
        entireGrpEntities.extend(v)
    grpToUpdate = []
    if any(elem in entireGrpEntities for elem in faceEnt):
        for aGrpNm, aGrpEntLst in grpDict.items():
            if any(elem in aGrpEntLst for elem in faceEnt):
                entToUpdate = list(set(aGrpEntLst) - set(faceEnt))
                if len(entToUpdate):
                    updateGrp("Face", aGrpNm,aGrpNm, entToUpdate)
                    grpToUpdate.append(aGrpNm)
                    # print("Update Group {} with {}".format(aGrpNm, entToUpdate))
                else:
                    deleteGroup(aGrpNm)
                    deleteMC(aGrpNm+'MC')
                    # print("Delete group {}".format(aGrpNm))         

    createFaceGroup(grpNm, faceEnt)
    # print('grpToUpdate',grpToUpdate)
    return grpToUpdate

def persistentMeshCtrl(grpNm, faceEnt):
    grpsToUpdate = createPersistentFaceGroup(grpNm, faceEnt)
    if grpsToUpdate:
        for thisGrp in grpsToUpdate:
            if ISOGROUP in thisGrp or FILLHOLEGROUP in thisGrp:
                if getParameter(ISOMESHSIZE) and getParameter(ISOANGLE):
                    isoMeshsize = simlab.getDoubleParameter("${}".format(ISOMESHSIZE))
                    isoAngle = simlab.getDoubleParameter("${}".format(ISOANGLE))
                    if isoAngle == 60:applyIsoMC(thisGrp, isoMeshsize, isoAngle, mergeFaces=1)
                    else:applyIsoMC(thisGrp, isoMeshsize, isoAngle, mergeFaces=0)

def createLogoMc():
    mcNm = 'DefeatureLogo_MC'
    deleteMC(mcNm)

    logoGrps = list(simlab.getGroupsWithSubString("FaceGroup",[LOGO_FACE+"*"]))
    if len(logoGrps):
        mcNm = 'DefeatureLogo_MC'

        MeshControls=''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
        <tag Value="-1"/>
        <MeshControlName Value="'''+ mcNm +'''"/>
        <MeshControlType Value="Defeature Logo"/>
        <Entities>
        <Group>'''+ ','.join('"{}"'.format(v) for v in logoGrps) +''',</Group>
        </Entities>
        <Reverse EntityTypes="" ModelIds="" Value=""/>
        <MeshColor Value="255,206,0,"/>
        <RemoveLogo/>
        </MeshControl>'''
        simlab.execute(MeshControls)

def createAdjacentGrp(adjFaceGrp,firstEnt):
    modelNm = simlab.getModelName('CAD')

    SelectAdjacent=''' <SelectAdjacent recordable="0" UUID="06104eca-3dbf-45af-a99c-953c8fe0f4e4">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ str(modelNm) +'''</Model>
    <Face>'''+ str(firstEnt) +''',</Face>
    </Entities>
    </SupportEntities>
    <NoofLayer Value="1"/>
    <VisiblesFaceOnly Value="1"/>
    <SelectAdjacent Value="1"/>
    <CreateGroup Name="'''+ adjFaceGrp +'''" Value="1"/>
    </SelectAdjacent>'''
    simlab.execute(SelectAdjacent)

def createFaceGroup(grpNm, FaceEntitiesList, modelType = "CAD"):
    ModelNM = simlab.getModelName(modelType)

    CreateGroup=''' <CreateGroup CheckBox="OFF" isObject="4" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954">
    <tag Value="-1"/>
    <Name OldValue="" Value="'''+ grpNm +'''"/>
    <SupportEntities>
    <Entities>
        <Model>'''+ ModelNM +'''</Model>
        <Face>'''+ ','.join(str(v) for v in FaceEntitiesList)+''',</Face>
    </Entities>
    </SupportEntities>
    <Type Value="Face"/>
    <Color Value="0,206,255,"/>
    <Dup Value="0"/>
    </CreateGroup>'''
    simlab.execute(CreateGroup)

def deleteMC(mcName):
    DeleteMeshControl=''' <DeleteMeshControl CheckBox="ON" UUID="c801afc7-a3eb-4dec-8bc1-8ac6382d4c6e">
    <Name Value="'''+ mcName +'''"/>
    </DeleteMeshControl>'''
    simlab.execute(DeleteMeshControl)

def uniqueGroupName(sourceName):
    icount = 1
    candidate = sourceName + str(icount)
    while simlab.isGroupPresent(candidate) or simlab.isGroupPresent(candidate+'_A') or simlab.isGroupPresent(candidate+'_B'):
        icount += 1
        candidate = sourceName + str(icount)
    return candidate

def renameGroup(fromName, toName):
    RenameGroupControl=''' <RenameGroupControl CheckBox="ON" UUID="d3addb85-3fd0-4972-80af-e699f96e9045">
    <tag Value="-1"/>
    <Name Value="''' + fromName + '''"/>
    <NewName Value="''' + toName + '''"/>
    <Output/>
    </RenameGroupControl>'''
    simlab.execute(RenameGroupControl)

def deleteParam(paramNm):
    if simlab.isParameterPresent(paramNm):
        DeleteParameters=''' <DeleteParameters UUID="57a0affc-2283-4c6b-9da2-f4b5de469440">
        <ParameterNames Value="'''+ paramNm +'''"/>
        <!-- If Value attribute is empty,it deletes all global parameters. -->
        </DeleteParameters>'''
        simlab.execute(DeleteParameters)

def getParameter(name):
    return simlab.getDoubleParameter("${}".format(name)) if simlab.isParameterPresent(name) else None

def createBodySplitMeshControl(meshCtrlName, planeFace, offset):
    modelName = simlab.getModelName('CAD')
    
    planePoints = simlab.definePlaneFromEntity(modelName, planeFace)
    threePoints =simlab.offsetPlane(planePoints[0], planePoints[1], planePoints[2], -1 * offset)
    fourPoints = simlabutil.Convert3PointsOnPlaneTo4Points(threePoints)

    bodyGrpName = simlabutil.UniqueGroupName('_TempBodyGrp')
    simlablib.SelectAssociatedEntities(modelName, 'Face', [planeFace], 'Body', bodyGrpName)
    body = simlab.getBodiesFromGroup(bodyGrpName)[0]
    simlablib.DeleteGroups(bodyGrpName)

    MeshControls=''' <MeshControl isObject="1" CheckBox="ON" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
        <tag Value="-1"/>
        <MeshControlName Value="''' + meshCtrlName + '''"/>
        <MeshControlType Value="Region"/>
        <Entities>
        <Entities>
            <Model>''' + modelName + '''</Model>
            <Body>"''' + body + '''",</Body>
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
        <BreakOptions Value="2"/>
        <RType Value="578"/>
        <CreateInternalFace Value="0"/>
        <CuboidRegData/>
        <CYlRegData/>
        <PlaneRegData>
            <Plane PlanePoints="''' + ",".join(str(v) for pt in fourPoints for v in pt) + ''',"/>
        </PlaneRegData>
        <SphereRegData/>
        <ConeRegData/>
        </RegionMeshControl>
        </MeshControl>'''
    simlab.execute(MeshControls)

def _createAdjcentFaceGrp(grpNmFrom, numOfLayer):
    SelectAdjacent=''' <SelectAdjacent recordable="0" UUID="06104eca-3dbf-45af-a99c-953c8fe0f4e4">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Group>"'''+ grpNmFrom +'''",</Group>
    </SupportEntities>
    <NoofLayer Value="'''+ str(numOfLayer) +'''"/>
    <VisiblesFaceOnly Value="0"/>
    <SelectAdjacent Value="0"/>
    <CreateGroup Name="Adjacent_Group_72" Value="1"/>
    </SelectAdjacent>'''
    simlab.execute(SelectAdjacent)

    return "Adjacent_Group_72"

def _remeshGrp(grpNm, meshProp):
    elemSize, maxAngle, aspectRat = meshProp
    LocalRemesh=''' <NewLocalReMesh UUID="83ab93df-8b5e-4a48-a209-07ed417d75bb">
    <tag Value="-1"/>
    <Name Value="NewLocalReMesh1"/>
    <SupportEntities>
    <Group>"'''+ grpNm +'''",</Group>
    </SupportEntities>
    <ElemType Value="1"/>
    <AverageElemSize Value="'''+ str(elemSize) +'''"/>
    <MinElemSize Value="'''+ str(elemSize/aspectRat) +'''"/>
    <PreserveBoundaryEdges Value="1"/>
    <NumberOfSolidLayersToUpdate Value="3"/>
    <TriOption>
    <GradeFactor Value="1.5"/>
    <MaxAnglePerElem Value="'''+ str(maxAngle) +'''"/>
    <CurvatureMinElemSize Value="10"/>
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

def gasketJoinGrp(grp1, grp2, tol):
    imprintFaceGrpNm = "ImprintedFace"
    deleteGroup(imprintFaceGrpNm)
    ImprintGasket=''' <GasketImprint gda="" UUID="1dd925d8-8b5b-4994-aa6b-fe9807711ed5">
    <tag Value="-1"/>
    <Name Value="GasketImprint1"/>
    <Entity>
    <Group>"'''+ grp1 +'''",</Group>
    </Entity>
    <DeckFace>
    <Group>"'''+ grp2 +'''",</Group>
    </DeckFace>
    <Tolerance Value="'''+ str(tol) +'''"/>
    <PreservePatterns Value="1"/>
    <MeshSize Value="0" Checked="0"/>
    <EquivalenceNodes Value="1"/>
    <Output/>
    </GasketImprint>'''
    simlab.execute(ImprintGasket)
    imprintGasketGrp = simlab.getGroupsWithSubString("FaceGroup",["Gasket_Imprint"])
    if not imprintGasketGrp:
        messagebox.showinfo("情報","Fail to imprint faces")
        return
    _renameGrp("Gasket_Imprint", imprintFaceGrpNm)

    # if joinFace:
    #     imprintFace = simlab.getEntityFromGroup(imprintFaceGrpNm)
    #     sharedFaceIds = _getSharedFaces(imprintFace)

    #     createFaceGroup("tempSharedFace", sharedFaceIds, modelType="FEM")
    #     _joinFaceGrp("tempSharedFace", tol)
    #     afterJoin = simlab.getEntityFromGroup("tempSharedFace")
    #     if len(afterJoin)< len(sharedFaceIds):
    #         _renameGrp("tempSharedFace", "JoinedFace")
    #     else:
    #         # deleteGroup("tempSharedFace")
    #         messagebox.showinfo("情報","Fail to join faces")

def _joinFaceGrp(grpNm, tol):
    Join=''' <Join CheckBox="ON" UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC">
    <tag Value="-1"/>
    <Name Value=""/>
    <Pick Value="Join"/>
    <JoinEntities>
    <Group>"'''+ grpNm +'''",</Group>
    </JoinEntities>
    <AlignEntities EntityTypes="" Value="" ModelIds=""/>
    <PreserveEntities EntityTypes="" Value="" ModelIds=""/>
    <Tolerance Value="'''+ str(tol) +'''"/>
    <JoinType Value="GEOM_PLANAR_FACES"/>
    <MeshOrShape Value="Shape"/>
    <MeshOption Value=""/>
    <MeshParam Value=""/>
    <SplitFace Value="1"/>
    <LocalRemesh Value="0"/>
    </Join>'''
    simlab.execute(Join)

# def _joinFaceEnts(faceIds, tol):
#     modelNm = simlab.getModelName("FEM")
#     Join=''' <Join CheckBox="ON" UUID="93BDAC5E-9059-42b6-BDC3-EFA346D3DDEC">
#     <tag Value="-1"/>
#     <Name Value=""/>
#     <Pick Value="Join"/>
#     <JoinEntities>
#     <Entities>
#     <Model>'''+ modelNm +'''</Model>
#     <Face>'''+ str(faceIds).strip("()") +'''</Face>
#     </Entities>
#     </JoinEntities>
#     <AlignEntities EntityTypes="" Value="" ModelIds=""/>
#     <PreserveEntities EntityTypes="" Value="" ModelIds=""/>
#     <Tolerance Value="'''+ str(tol) +'''"/>
#     <JoinType Value="GEOM_PLANAR_FACES"/>
#     <MeshOrShape Value="Shape"/>
#     <MeshOption Value=""/>
#     <MeshParam Value=""/>
#     <SplitFace Value="1"/>
#     <LocalRemesh Value="0"/>
#     </Join>'''
#     simlab.execute(Join)


def _renameGrp(fromName, toName):
    RenameGroupControl=''' <RenameGroupControl CheckBox="ON" UUID="d3addb85-3fd0-4972-80af-e699f96e9045">
    <tag Value="-1"/>
    <Name Value="'''+ fromName +'''"/>
    <NewName Value="'''+ toName +'''"/>
    <Output/>
    </RenameGroupControl>'''
    simlab.execute(RenameGroupControl)

def _getSharedFaces(faceId):
    modelNm = simlab.getModelName("FEM")
    faceId = str(faceId).strip("()")
    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ faceId +'''</Face>
    </Entities>
    </InputFaces>
    <Option Value="Nodes"/>
    <Groupname Value="SelectNodes_73"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)
    nodeIds = simlab.getEntityFromGroup("SelectNodes_73")
    deleteGroup("SelectNodes_73")

    SelectFaceAssociatedEntities=''' <SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
    <InputFaces Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ faceId +'''</Face>
    </Entities>
    </InputFaces>
    <Option Value="Edges"/>
    <Groupname Value="SelectEdges_75"/>
    </SelectFaceAssociatedEntities>'''
    simlab.execute(SelectFaceAssociatedEntities)
    edgeIds = simlab.getEntityFromGroup("SelectEdges_75")
    deleteGroup("SelectEdges_75")

    SelectEdgeAssociatedEntities=''' <SelectEdgeAssociatedEntities UUID="551fdd5b-6a8c-4a30-8ab0-fbaf9257343e">
    <InputEdges Values="">
    <Entities>
    <Model>Merged_Model.gda</Model>
    <Edge>'''+ str(edgeIds).strip("()") +''',</Edge>
    </Entities>
    </InputEdges>
    <Option Value="Nodes"/>
    <Groupname Value="SelectNodes_76"/>
    </SelectEdgeAssociatedEntities>'''
    simlab.execute(SelectEdgeAssociatedEntities)
    nodeIdsOnEdges = simlab.getEntityFromGroup("SelectNodes_76")
    deleteGroup("SelectNodes_76")

    nodes = tuple(set(nodeIds) - set(nodeIdsOnEdges))

    SelectNodeAssociatedEntities=''' <SelectNodeAssociatedEntities UUID="6731d198-667e-49c9-8612-c7d980368508">
    <InputNodes Values="">
    <Entities>
    <Model>Merged_Model.gda</Model>
    <Node>'''+ str(nodes).strip("()") +'''</Node>
    </Entities>
    </InputNodes>
    <Option Value="Faces"/>
    <Groupname Value="SelectFaces_77"/>
    </SelectNodeAssociatedEntities>'''
    simlab.execute(SelectNodeAssociatedEntities)

    sharedFaceIds = simlab.getEntityFromGroup("SelectFaces_77")
    deleteGroup("SelectFaces_77")

    return sharedFaceIds

def _updateModel():
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def mergeFaces(faceIds):
    meshSize = getParameter("DefaultMeshSize")
    maxAngle = getParameter("DefaultMaxAngle")
    aspectRat = getParameter("DefaultAspectRatio")
    
    faceGrpNm = "MergeFace"
    deleteGroup(faceGrpNm)

    createFaceGroup(faceGrpNm, faceIds, modelType="FEM")
    MergeFaces=''' <MergeFace UUID="D9D604CE-B512-44e3-984D-DF3E64141F8D">
    <tag Value="-1"/>
    <Name Value="MergeFace5"/>
    <SupportEntities>
    <Group>"'''+ faceGrpNm +'''",</Group>
    </SupportEntities>
    <MergeBoundaryEdges Value="1"/>
    <SplitBoundaryEdges Value="0"/>
    <SplitEdgesBasedon Value="0"/>
    <FeatureAngle Value="45"/>
    </MergeFace>'''
    simlab.execute(MergeFaces)
    
    # adjFaceGrpNm = _createAdjcentFaceGrp(faceGrpNm, numOfLayer = 1)

    if not meshSize or not maxAngle or not aspectRat:
        meshSize = 20
        maxAngle = 45
        aspectRat = 10

    meshProp = meshSize, maxAngle, aspectRat
    _remeshGrp(faceGrpNm, meshProp)

    deleteGroup([faceGrpNm])

    _updateModel()
    
        
        


