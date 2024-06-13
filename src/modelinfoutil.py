from hwx import simlab

def createBodyMeshControl(meshProp):
    modelNm = simlab.getModelName("CAD")
    mcName, bodyNm, elemSize, minElemSize, maxAngle, curvMin, aspRat, meshGrading = meshProp
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
    <ElementType Value="1"/>
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

def renameBody(modelType, oldNm, newNm):
    modelNm = simlab.getModelName(modelType)
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