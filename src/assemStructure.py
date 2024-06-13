from hwx import simlab
import re
import os
import simlablib
import muratautil
import meshutil
import importlib
BODY_VOLUME_CSV_BEFORE = "volumeBefore.csv"
SOLID_ASSY = "SOLID_ASSY"
PARAMETER_XML = "murataParameters.xml"

def renameBody(oldBodyName, newBodyName):
    modelNm = simlab.getModelName("CAD")
    RenameBody=''' <RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ oldBodyName +'''",</Body>
    </Entities>
    </SupportEntities>
    <NewName Value="'''+ newBodyName +'''"/>
    <Output/>
    </RenameBody>'''
    simlab.execute(RenameBody)

def createParameters(paramType, name, value):
    if paramType == "string":
        SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Value="'''+ str(value) +'''" Type="'''+ paramType +'''" Name="'''+ name +'''"/>
        </Parameters>'''
        simlab.execute(SimLabParameters)
    elif paramType == "integer":
        SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Value="'''+ str(value) +'''" Type="'''+ paramType +'''" Name="'''+ name +'''"/>
        </Parameters>'''
        simlab.execute(SimLabParameters)
    elif paramType == "real":
        SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Value="'''+ str(value) +'''" Type="'''+ paramType +'''" Name="'''+ name +'''"/>
        </Parameters>'''
        simlab.execute(SimLabParameters)

def updateModel(modelType):
    modelNm = simlab.getModelName(modelType)
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def readCsv(f_name):
    aDict = {}
    subModelDict = {}
    readingModelCSV = False
    with open(f_name, "r") as f:
        for line in f:
            if readingModelCSV:
                # ON -> OFF: end of reading
                if line.startswith("##") and not 'model csv' in line.lower():
                    readingModelCSV = False
            else:
                # OFF -> ON: start reading
                if line.startswith("##") and 'model csv' in line.lower():
                    readingModelCSV = True
            if not readingModelCSV:
                continue

            if not line.startswith("#"):
                lineSp = line.rstrip().split(",")
                subModelName = lineSp[0].strip()
                productName = lineSp[1].strip()
                partName = lineSp[2].strip()
                material = lineSp[3].strip()
                youngs = lineSp[4].strip()
                density = lineSp[5].strip()
                mass = lineSp[6].strip()
                meshSize = lineSp[7].strip()
                minLength = lineSp[8].strip()
                groupNum = lineSp[9].strip()
                holeFill = lineSp[10].strip()

                if not subModelName in subModelDict:
                    subModelDict[subModelName] = [productName]
                else:
                    if not productName in subModelDict[subModelName]:
                        subModelDict[subModelName].append(productName)

                if not productName in aDict:
                    aDict[productName] = [partName]
                else:
                    aDict[productName].append(partName)
                
                createParameters("string", productName, material)
                
                if isNumber(youngs) and isNumber(density):
                    youngs = float(youngs) * 9.80665
                    createParameters("real", "{}_youngs".format(productName), youngs)
                    
                if isNumber(density):
                    density = float(density) * 1e-12
                    createParameters("real", "{}_density".format(productName), density)

                if isNumber(mass):
                    mass = float(mass) * 1e-3
                    createParameters("real","{}_mass".format(productName),mass)
                
                if isNumber(meshSize):createParameters("real", "{}_meshSize".format(productName) , meshSize)
                # else: createParameters("real", "{}_meshSize".format(productName) , DEFAULT_MESH_SIZE)

                if isNumber(minLength): createParameters("real", "{}_minLength".format(productName) , minLength)
                
                if isNumber(groupNum):
                    createParameters("integer", "{}_joinGroup".format(productName), groupNum)
                
                if holeFill.lower() == "true":
                    createParameters("integer", "{}_bodyHoleFill".format(productName), 1)

    return subModelDict, makeUniqueKeyValueDict(aDict)

def isNumber(cont):
    try:
        float(cont)
    except ValueError:
        return False
    return True

def makeUniqueKeyValueDict(aDict):
    temp = {}
    for key, value in aDict.items():
        numOfParts = len(value)
        if numOfParts == 1:
            temp[key] = value[0]
        elif numOfParts > 1:
            for num in range(numOfParts):
                newKey = "{}_{}".format(key, num+1)
                temp[newKey] = value[num]
    return temp

def getKeyByValue(theValue, aDict):
    for key, value in aDict.items():
        if value == theValue:
            return key
    return None

def getBodyNamesFromList(bodyName, aList):
    temp = []
    for thisBody in aList:
        if bodyName in thisBody:
            temp.append(thisBody)
    return list(set(temp))

def deleteAllMaterials():
    DeleteMaterial=''' <DeleteMaterial UUID="0a0b8b68-e63e-40b3-82c6-4e7a5b01936b" CheckBox="ON">
    <Name Value=""/>
    </DeleteMaterial>'''
    simlab.execute(DeleteMaterial)

def deleteEntities(bodyNms):
    modelNm = simlab.getModelName("CAD")
    DeleteEntity=''' <DeleteEntity UUID="BF2C866D-8983-4477-A3E9-2BBBC0BC6C2E" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ ",".join('"{}"'.format(v) for v in bodyNms) +'''",</Body>
    </Entities>
    </SupportEntities>
    </DeleteEntity>'''
    simlab.execute(DeleteEntity)
    updateModel("CAD")

def getBodyMass():
    importlib.reload(meshutil)
    modelType = "CAD"
    modelNm = simlab.getModelName(modelType)
    # create FEM model 
    defaultMeshSize = 20
    defaultMaxAngle = 45
    defaultAspectRatio = 10
    meshutil.createPrefixBodyMC(modelType, defaultMeshSize, defaultMaxAngle, defaultAspectRatio)
    meshutil.meshingAllBodies(defaultMeshSize, defaultMaxAngle, defaultAspectRatio, imprint = 0)

    # calculate body volume
    modelType = "FEM"
    modelNm = simlab.getModelName(modelType)
    bodyNms = simlab.getBodiesWithSubString(modelNm, ["*"])
    logDir = getLogDIR()
    volumePath = os.path.join(logDir, BODY_VOLUME_CSV_BEFORE)
    if os.path.exists(volumePath):
        os.remove(volumePath)

    CalculateVolume=''' <CalculateVolume UUID="d39d9d77-f4b8-4578-a341-7be7ac69dd47">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNms).replace("'", '"').strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    <FileName Value="'''+ volumePath +'''"/>
    </CalculateVolume>'''
    simlab.execute(CalculateVolume)
    deleteModel(modelNm)

def deleteModel(modelNm):
    DeleteModel=''' <DeleteModel CheckBox="ON" updategraphics="0" UUID="AE031126-6421-4633-8FAE-77C8DE10C18F">
    <ModelName Value="'''+ modelNm +'''"/>
    </DeleteModel>'''
    simlab.execute(DeleteModel)

def createSubModel(modelType, subModelName):
    modelNm = simlab.getModelName(modelType)
    CreateSubModelQuuid=''' <CreateSubModelQuuid UUID="e9d719a4-0e49-42a2-9973-15acab8ab987">
    <SubModelName Value="'''+ subModelName +'''"/>
    <ModelName Value="'''+ modelNm +'''"/>
    <ParentSubModelName Value=""/>
    </CreateSubModelQuuid>'''
    simlab.execute(CreateSubModelQuuid)

def moveBodiesToSubModel(modelType, bodies, subModelName):
    modelNm = simlab.getModelName(modelType)
    MoveToSubModelQuuid=''' <MoveToSubModelQuuid UUID="475fe1b6-1656-44e3-9e36-2656ed16de0c">
    <SubModelName Value="'''+ subModelName +'''"/>
    <BodiesToMove>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodies).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </BodiesToMove>
    </MoveToSubModelQuuid>'''
    simlab.execute(MoveToSubModelQuuid)

def moveSubModelToSubModel(modelType, subModelFrom, subModelTo):
    modelNm = simlab.getModelName(modelType)
    MoveSubModelToSubModel=''' <MoveSubModelToSubModel UUID="caf8a068-8749-4189-bb89-624aa42c0efc">
    <ModelName Value="'''+ modelNm +'''"/>
    <Source_SubModelName Value="'''+ subModelFrom +'''"/>
    <Destination_SubModelName Value="'''+ subModelTo +'''"/>
    </MoveSubModelToSubModel>'''
    simlab.execute(MoveSubModelToSubModel)

def exportParameterXML(fName):
    ExportParameters=''' <ExportParameters UUID="1086e028-93d9-44a3-bbd5-1d4bbf0919c3s">
    <FileName Value="'''+ fName +'''"/>
    </ExportParameters>'''
    simlab.execute(ExportParameters)

def importParmeterXML(fName):
    ImportParameters=''' <ImportParameters UUID="1c7910a2-2c5a-4618-a496-02b4bce9fc3d">
    <FileName Value="'''+ fName +'''"/>
    </ImportParameters>'''
    simlab.execute(ImportParameters)

def getLogDIR():
    logDir = os.path.join(os.path.dirname(__file__), 'log')
    if not os.path.isdir(logDir):
        os.mkdir(logDir)
    return logDir

def getSubModelNm(bodyPrefix, subModelDict):
    for subModel in subModelDict:
        if bodyPrefix in subModelDict[subModel]:
            return subModel


def subModelBodies(modelNm, bodyNm, subModelNm):
    subModels = simlab.getChildrenInAssembly(modelNm, modelNm, "SUBASSEMBLIES")
    if subModelNm in subModels:
        moveBodiesToSubModel("CAD", bodyNm, subModelNm)
    else:
        createSubModel("CAD", subModelNm)
        moveBodiesToSubModel("CAD", bodyNm, subModelNm)

def importCSV(csvPath):
    subModelDict, csvDict = readCsv(csvPath)
    # print("subModelDict",subModelDict)
    # print("csvDict", csvDict)
    deleteAllMaterials()
    modelName = simlab.getModelName("CAD")
    allBodies = simlab.getBodiesWithSubString(modelName, ["*"])

    pairedBodies = {}

    for _, partNm in csvDict.items():
        bodyLst = getBodyNamesFromList(partNm, allBodies)
        pairedBodies[partNm] = bodyLst
    # print("pairedBodies", pairedBodies)

    bodyRenamed = []

    for partNm, partNmLst in pairedBodies.items():
        prodNm = getKeyByValue(partNm, csvDict)
        if prodNm:
            for i, thisPartNm in enumerate(partNmLst):
                bodyNm = prodNm
                if simlab.getBodiesWithSubString(modelName,[bodyNm]):
                    bodyNm = "{}_{}".format(bodyNm, i)
                renameBody(thisPartNm, bodyNm)
                bodyRenamed.append(thisPartNm)
                bodyPrefix = muratautil.getPrefixOfBodyNm(bodyNm)
                subModelNm = getSubModelNm(bodyPrefix, subModelDict)
                subModelBodies(modelName, bodyNm, subModelNm)

    bodyUnchanged = list(set(allBodies) - set(bodyRenamed))
    deleteEntities(bodyUnchanged)    
    updateModel("CAD")
    
    # export parameters
    logDir = getLogDIR()
    paramPath = os.path.join(logDir, PARAMETER_XML)
    if os.path.exists(paramPath):
        os.remove(paramPath)
    exportParameterXML(paramPath)

    Reload()


def Reload():
    logDir = getLogDIR()
    # export temp file.
    tmpFile = os.path.join(logDir, 'CAD.xmt_txt')
    simlablib.ExportParasolid(tmpFile)

    # discard current db and create new db.
    simlab.closeActiveDocument()
    simlab.newDocument()

    # read temp file.
    params = {'ImportAssemblyStructure':1,
            'SaveGeometryInDatabase':0,
            'Imprint':0    
            }
    simlablib.ImportFile(tmpFile, params=params)
    #os.remove(tmpFile)
    # import parameter xml
    paramPath = os.path.join(logDir, PARAMETER_XML)
    if os.path.exists(paramPath):
        importParmeterXML(paramPath)