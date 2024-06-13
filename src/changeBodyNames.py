from hwx import simlab
import re

def walk(top):
    CadMaster=simlab.getModelName("CAD")
    dirs=[]
    for name in simlab.getChildrenInAssembly(CadMaster, top, "SUBASSEMBLIES"):
        dirs.append(name)
    if dirs:
        yield top, dirs

    for name in dirs:
        for x in walk(name):
            yield x

def importSolidWorks(fPath):
    ImportSolidWorks=''' <ImportSolidWorks UUID="75f886ce-f9f4-4924-a1b2-faaa32632c9e">
    <FileName Value="'''+ fPath +'''"/>
    <BodyName Value="1"/>
    <Sheet Value="1"/>
    <SketchWireframe Value="0"/>
    <Color Value="0"/>
    <AssemblyStructure Value="1"/>
    <Facets Value="0"/>
    <Regenerate Value="0"/>
    <RegenModelId Value="0"/>
    <DesignParameters Value="0"/>
    <Path Value=""/>
    </ImportSolidWorks>'''
    simlab.execute(ImportSolidWorks)

def renameSubModel(modelType, subModelNm, newName):
    modelNm = simlab.getModelName(modelType)

    RenameSubModelQuuid=''' <RenameSubModelQuuid UUID="e7ce1956-8807-45cb-90fe-05a2411c529d">
    <SubModelName Value="'''+ subModelNm +'''"/>
    <ModelName Value="'''+ modelNm +'''"/>
    <NewName Value="'''+ newName +'''"/>
    </RenameSubModelQuuid>'''
    simlab.execute(RenameSubModelQuuid)

def renameBody(modelType, oldBodyName, newBodyName):
    modelNm = simlab.getModelName(modelType)
    RenameBody=''' <RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
    <SupportEntities>
    <Entities>
    <Model>"'''+ modelNm +'''"</Model>
    <Body>"'''+ oldBodyName +'''",</Body>
    </Entities>
    </SupportEntities>
    <NewName Value="'''+ newBodyName +'''"/>
    <Output/>
    </RenameBody>'''
    simlab.execute(RenameBody)

def hasChildAssembly(assemblyName, structure):
    for thisStructure in structure:
        parent, _ = thisStructure
        if parent == assemblyName:
            return True
    return False

def replaceToUnderbar(subAssemblies):
    parent, children = subAssemblies
    newChildrenName = []
    if "-" in parent:
        newName = re.sub(re.compile("[ -/:-@[-`{-~]"), '_', parent) 
        renameSubModel("CAD", parent, newName)
        parent = newName
    for child in children:
        if "-" in child:
            newChildName = re.sub(re.compile("[ -/:-@[-`{-~]"), '_', parent)
            renameSubModel("CAD", child, newChildName)
            newChildrenName.append(newChildName)
        else:
            newChildrenName.append(child)
    return parent, newChildrenName


def makeUniqueSubModel(childSubs):
    if len(set(childSubs)) != len(childSubs):
        count = 1
        uniqueSubNames = []
        for thisSub in childSubs:
            newSubName = "{}_{}".format(thisSub, count)
            renameSubModel("CAD", thisSub, newSubName)
            uniqueSubNames.append(newSubName)
            count += 1
        return uniqueSubNames
    else:
        return childSubs

def updateModel(modelType):
    modelNm = simlab.getModelName(modelType)
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value="'''+ modelNm +'''"/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)
        
def main():
    modelName = simlab.getModelName("CAD")

    partNms = []
    with open("assemStructure.txt", "w") as f:
        structure = []
        for x in walk(modelName):
            parent, children = replaceToUnderbar(x)
            if x[0] != modelName:
                structure.append((parent, makeUniqueSubModel(children)))
        assemBodies = {}
        for thisStructure in structure:
            parent, children = thisStructure
            parentBodies = simlab.getChildrenInAssembly(modelName, parent, "ALLBODIES")
            for child in children:
                childBodies = simlab.getChildrenInAssembly(modelName, child, "ALLBODIES")
                if childBodies:
                    assemBodies[child] = childBodies
                    if not child in partNms:partNms.append(child)
                parentBodies = tuple(set(parentBodies) - set(childBodies))
                if parentBodies:
                    assemBodies[parent] = parentBodies
                 
        for key in assemBodies:
            f.write("{}:{}\n".format(key, assemBodies[key]))
    
if __name__ == "__main__":
    main()