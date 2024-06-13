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


def createMaterial(materialInfo):
    name, youngMod, density = materialInfo
    Material=''' <Material UUID="dd7920e8-5d0f-477b-bc7e-037a04a7ed03" Hide="1">
    <tag Value="-1"/>
    <Name Value="'''+ name +'''"/>
    <MaterialId Value="1"/>
    <Category Value="Solid"/>
    <Class Value="Metal"/>
    <Model Value="Isotropic"/>
    <SupportEntities/>
    <TableData>
    <Mechanical_Properties>
    <Elastic>
    <ITEM DISPLAYNAME="Density" KEY="Density">
    <COLUMN DATATYPE="DOUBLE" VALUE="'''+ str(density) +'''"/>
    <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
    </ITEM>
    <ITEM DISPLAYNAME="Youngs_modulus" KEY="Youngs_modulus">
    <COLUMN DATATYPE="DOUBLE" VALUE="'''+ str(youngMod) +'''"/>
    <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
    </ITEM>
    <ITEM DISPLAYNAME="Poissons_ratio" KEY="Poissons_ratio">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.30"/>
    <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
    </ITEM>
    <ITEM DISPLAYNAME="Shear_modulus" KEY="Shear_modulus"/>
    <ITEM DISPLAYNAME="Thermal_Expansion" KEY="Thermal_Expansion">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
    </ITEM>
    <ITEM DISPLAYNAME="Reference_Temperature" KEY="Reference_Temperature">
    <COLUMN DATATYPE="DOUBLE" VALUE="20"/>
    </ITEM>
    <ITEM DISPLAYNAME="Damping_coefficient" KEY="Damping_coefficient"/>
    <ITEM DISPLAYNAME="Stress_Tension" KEY="Stress_Tension">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
    </ITEM>
    <ITEM DISPLAYNAME="Stress_Compression" KEY="Stress_Compression">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
    </ITEM>
    <ITEM DISPLAYNAME="Stress_Shear" KEY="Stress_Shear">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
    </ITEM>
    <ITEM DISPLAYNAME="Mat_Cord_Sys" KEY="Mat_Cord_Sys">
    <COLUMN DATATYPE="DOUBLE" VALUE="0"/>
    </ITEM>
    </Elastic>
    <Plastic>
    <ITEM DISPLAYNAME="Yield stress-strain table" KEY="Yield_Stress">
    <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
    </ITEM>
    <ITEM DISPLAYNAME="Work hardening slope" KEY="Work_Hardening_Slope"/>
    <ITEM DISPLAYNAME="Hardening_Rule" KEY="Hardening_Rule">
    <COLUMN LIST="Isotropic Hardening" DATATYPE="INDEX" INDEX="0"/>
    <COLUMN DATATYPE="DOUBLE" VALUE="0.15"/>
    </ITEM>
    <ITEM DISPLAYNAME="Initial yield point" KEY="Initial_yield_point">
    <COLUMN DATATYPE="DOUBLE" VALUE="208000"/>
    </ITEM>
    <ITEM DISPLAYNAME="Yield Criterion" KEY="Yield_Criterion">
    <COLUMN LIST="VMISES" DATATYPE="INDEX" INDEX="0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Hardening Parameter" KEY="Hardening_Param">
    <COLUMN DATATYPE="DOUBLE" VALUE="1.00"/>
    </ITEM>
    </Plastic>
    <Visco_Plastic>
    <ITEM DISPLAYNAME="Creep_Temperature_Exponent" KEY="Creep_Temperature_Exponent"/>
    <ITEM DISPLAYNAME="Creep_Stress_Exponent" KEY="Creep_Stress_Exponent"/>
    <ITEM DISPLAYNAME="Creep_Strain_Exponent" KEY="Creep_Strain_Exponent"/>
    <ITEM DISPLAYNAME="Creep_Time_Exponent" KEY="Creep_Time_Exponent"/>
    </Visco_Plastic>
    </Mechanical_Properties>
    <Thermal_Properties>
    <ITEM DISPLAYNAME="Thermal_conductivity" KEY="Thermal_conductivity">
    <COLUMN DATATYPE="DOUBLE" VALUE="4.98100E-02"/>
    <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
    </ITEM>
    <ITEM DISPLAYNAME="Heat_capacity" KEY="Heat_capacity">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.5"/>
    <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
    </ITEM>
    <ITEM DISPLAYNAME="Free_Convection" KEY="Free_Convection">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
    </ITEM>
    <ITEM DISPLAYNAME="Dynamic_Viscosity" KEY="Dynamic_Viscosity">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
    </ITEM>
    <ITEM DISPLAYNAME="Heat_Generation" KEY="Heat_Generation">
    <COLUMN DATATYPE="DOUBLE" VALUE="1.00"/>
    </ITEM>
    <ITEM DISPLAYNAME="Reference_Enthalpy" KEY="Reference_Enthalpy">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
    </ITEM>
    <ITEM DISPLAYNAME="TCH" KEY="TCH">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
    </ITEM>
    <ITEM DISPLAYNAME="TDELTA" KEY="TDELTA">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
    </ITEM>
    <ITEM DISPLAYNAME="QLAT" KEY="QLAT">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.00"/>
    </ITEM>
    </Thermal_Properties>
    <Magnetic_Properties>
    <Permeability>
    <ITEM DISPLAYNAME="Type" KEY="Magnet_Type">
    <COLUMN LIST="None" DATATYPE="INDEX" INDEX="0"/>
    </ITEM>
    </Permeability>
    </Magnetic_Properties>
    <Fatigue_Properties>
    <Static_parameters>
    <ITEM DISPLAYNAME="Yield_Strength" KEY="Yield_Strength">
    <COLUMN DATATYPE="DOUBLE" VALUE="235"/>
    </ITEM>
    <ITEM DISPLAYNAME="Ultimate_Tensile_Strength" KEY="Ultimate_Tensile_Strength">
    <COLUMN DATATYPE="DOUBLE" VALUE="380"/>
    </ITEM>
    <ITEM DISPLAYNAME="Units" KEY="Units">
    <COLUMN LIST="MPa" DATATYPE="INDEX" INDEX="0"/>
    </ITEM>
    </Static_parameters>
    <Stress_Life_parameters>
    <ITEM DISPLAYNAME="Fatigue_strength_coefficient" KEY="Fatigue_strength_coefficient_stress">
    <COLUMN DATATYPE="DOUBLE" VALUE="1619.94"/>
    </ITEM>
    <ITEM DISPLAYNAME="First_Fatigue_strength_Exponent" KEY="First_Fatigue_strength_Exponent">
    <COLUMN DATATYPE="DOUBLE" VALUE="-0.125"/>
    </ITEM>
    <ITEM DISPLAYNAME="Endurance_Cycle_Limit_or_Transition_Point" KEY="Endurance_Cycle_Limit_or_Transition_Point">
    <COLUMN DATATYPE="DOUBLE" VALUE="1E+06"/>
    </ITEM>
    <ITEM DISPLAYNAME="Second_Fatigue_strength_Exponent" KEY="Second_Fatigue_strength_Exponent">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Fatigue_Limit" KEY="Fatigue_Limit"/>
    <ITEM DISPLAYNAME="Standard_Error_of_Log" KEY="Standard_Error_of_Log">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Findley_Constant" KEY="Findley_Constant">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.3"/>
    </ITEM>
    <ITEM DISPLAYNAME="Region_Layer" KEY="Region_Layer_stress">
    <COLUMN LIST="Worst" DATATYPE="INDEX" INDEX="0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Material_Surface_Finish" KEY="Material_Surface_Finish_Stress">
    <COLUMN LIST="None" DATATYPE="INDEX" INDEX="0"/>
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Material_Surface_Treatment" KEY="Material_Surface_Treatment_Stress">
    <COLUMN LIST="None" DATATYPE="INDEX" INDEX="0"/>
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Fatigue_Strength_Reduction_Factor" KEY="Fatigue_Strength_Reduction_Factor_Stress">
    <COLUMN DATATYPE="DOUBLE" VALUE="1.0"/>
    </ITEM>
    </Stress_Life_parameters>
    <Strain_Life_parameters>
    <ITEM DISPLAYNAME="Fatigue_strength_coefficient" KEY="Fatigue_strength_coefficient_strain">
    <COLUMN DATATYPE="DOUBLE" VALUE="570"/>
    </ITEM>
    <ITEM DISPLAYNAME="Fatigue_strength_exponent" KEY="Fatigue_strength_exponent">
    <COLUMN DATATYPE="DOUBLE" VALUE="-0.087"/>
    </ITEM>
    <ITEM DISPLAYNAME="Fatigue_ductility_exponent" KEY="Fatigue_ductility_exponent">
    <COLUMN DATATYPE="DOUBLE" VALUE="-0.58"/>
    </ITEM>
    <ITEM DISPLAYNAME="Fatigue_ductility_coefficient" KEY="Fatigue_ductility_coefficient">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.59"/>
    </ITEM>
    <ITEM DISPLAYNAME="Cyclic_strain_hardening_exponent" KEY="Cyclic_strain_hardening_exponent">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.15"/>
    </ITEM>
    <ITEM DISPLAYNAME="Cyclic_strength_coefficient" KEY="Cyclic_strength_coefficient">
    <COLUMN DATATYPE="DOUBLE" VALUE="627"/>
    </ITEM>
    <ITEM DISPLAYNAME="Reversal_Limit_Of_Endurance" KEY="Reversal_Limit_Of_Endurance">
    <COLUMN DATATYPE="DOUBLE" VALUE="2.0E8"/>
    </ITEM>
    <ITEM DISPLAYNAME="Standard_Error_of_Log_Elastic" KEY="Standard_Error_of_Log_Elastic">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Standard_Error_of_Log_Plastic" KEY="Standard_Error_of_Log_Plastic">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Shear_Fatigue_Strength_coefficient" KEY="Shear_Fatigue_Strength_coefficient"/>
    <ITEM DISPLAYNAME="Shear_Fatigue_Ductility_coefficient" KEY="Shear_Fatigue_Ductility_coefficient"/>
    <ITEM DISPLAYNAME="Shear_Fatigue_Strength_exponent" KEY="Shear_Fatigue_Strength_exponent"/>
    <ITEM DISPLAYNAME="Shear_Fatigue_Ductility_exponent" KEY="Shear_Fatigue_Ductility_exponent"/>
    <ITEM DISPLAYNAME="Strength_coefficient_factor" KEY="Strength_coefficient_factor">
    <COLUMN DATATYPE="DOUBLE" VALUE="1.2"/>
    </ITEM>
    <ITEM DISPLAYNAME="Exponent_coefficient_factor" KEY="Exponent_coefficient_factor">
    <COLUMN DATATYPE="DOUBLE" VALUE="1.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Maximum_Strain_value" KEY="Maximum_Strain_value">
    <COLUMN DATATYPE="DOUBLE" VALUE="1.002"/>
    </ITEM>
    <ITEM DISPLAYNAME="Fatemi_Socie_Constant" KEY="Fatemi_Socie_Constant">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.3"/>
    </ITEM>
    <ITEM DISPLAYNAME="Brown_Miller_Constant" KEY="Brown_Miller_Constant">
    <COLUMN DATATYPE="DOUBLE" VALUE="1.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Region_Layer" KEY="Region_Layer_strain">
    <COLUMN LIST="Worst" DATATYPE="INDEX" INDEX="0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Material_Surface_Finish" KEY="Material_Surface_Finish_Strain">
    <COLUMN LIST="None" DATATYPE="INDEX" INDEX="0"/>
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Material_Surface_Treatment" KEY="Material_Surface_Treatment_Strain">
    <COLUMN LIST="None" DATATYPE="INDEX" INDEX="0"/>
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Fatigue_Strength_Reduction_Factor" KEY="Fatigue_Strength_Reduction_Factor_Strain">
    <COLUMN DATATYPE="DOUBLE" VALUE="1.0"/>
    </ITEM>
    </Strain_Life_parameters>
    <Factor_of_Safety>
    <ITEM DISPLAYNAME="Torsion_fatigue_limit" KEY="Torsion_fatigue_limit">
    <COLUMN DATATYPE="DOUBLE" VALUE="220"/>
    <COLUMN DATATYPE="FIELD_TABLE" VALUE="none"/>
    </ITEM>
    <ITEM DISPLAYNAME="Hydrostatic_stress_sensitivity" KEY="Hydrostatic_stress_sensitivity">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.745"/>
    </ITEM>
    <ITEM DISPLAYNAME="Safe_zone_angle" KEY="Safe_zone_angle">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Shear_Threshold_Safezone" KEY="Shear_Threshold_Safezone">
    <COLUMN DATATYPE="DOUBLE" VALUE="0.0"/>
    </ITEM>
    <ITEM DISPLAYNAME="Region_Layer" KEY="Region_Layer">
    <COLUMN LIST="Worst" DATATYPE="INDEX" INDEX="0"/>
    </ITEM>
    </Factor_of_Safety>
    </Fatigue_Properties>
    </TableData>
    </Material>'''
    simlab.execute(Material)

def renameBody(oldBodyName, newBodyName):
    RenameBody=''' <RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
    <SupportEntities>
    <Entities>
    <Model>$Geometry</Model>
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
    with open(f_name, "r") as f:
        for line in f:
            if not line.startswith("#"):
                lineSp = line.rstrip().split(",")
                productName = lineSp[0].rstrip()
                partName = lineSp[1].rstrip()
                material = lineSp[2].rstrip()
                meshSize = lineSp[5].rstrip()
                if not productName in aDict:
                    aDict[productName] = [partName]
                else:
                    aDict[productName].append(partName)

                if meshSize != "-":
                    createParameters("real", "{}_meshSize".format(productName) , meshSize)

                if not material == "-":
                    youngs = lineSp[3].rstrip()
                    density = lineSp[4].rstrip()
                    try:
                        youngs_si = float(youngs) * 9.80665
                        density_si = float(density) * 1e-12
                    except ValueError:
                        continue
                    else:
                        materialInfo = (material, youngs_si, density_si)
                        if not simlab.isParameterPresent(material):
                            createMaterial(materialInfo)
                            createParameters("integer", material, 1)
                        if not simlab.isParameterPresent(productName):
                            createParameters("string", productName, material)

    return makeUniqueKeyValueDict(aDict)

def makeUniqueKeyValueDict(aDict):
    temp = {}
    for key, value in aDict.items():
        numOfParts = len(value)
        if numOfParts == 1:
            temp[key] = value[0]
        else:
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
        
def importCSV(csvPath):
    modelName = simlab.getModelName("CAD")
    deleteAllMaterials()
    csvDict = readCsv(csvPath)
    # with open("csv_origin.txt", "w") as f:
    #     for thisPart in csvDict:
    #         f.write("{}\n".format(thisPart))
    #     f.write(str(len(csvDict)))

    allBodies = []
    structure = []
    for x in walk(modelName):
        parent, children = x
        structure.append((parent,children))

    for thisStructure in structure:
        assem, subAssem = thisStructure

        assemBodies = simlab.getChildrenInAssembly(modelName, assem, "ALLBODIES")
        for thisBody in assemBodies:
            allBodies.append(thisBody)

        for thisAssem in subAssem:
            subAssemBodies = simlab.getChildrenInAssembly(modelName, thisAssem, "ALLBODIES")
            for thisBody in subAssemBodies:
                allBodies.append(thisBody)
    
    allBodies = list(set(allBodies))

    pairedBodies = {}

    for _, partNm in csvDict.items():
        bodyLst = getBodyNamesFromList(partNm, allBodies)
        pairedBodies[partNm] = bodyLst

    return pairedBodies

    # with open("allBodies.txt", "w") as f:
    #     for thisBody in allBodies:
    #         f.write("{}\n".format(thisBody))
    #     f.write(str(len(allBodies)))
   
    # with open("bodyRenamed.txt", "w") as f:
    #     for thisBody in bodyRenamed:
    #         f.write("{}\n".format(thisBody))
    #     f.write(str(len(bodyRenamed)))

    # bodyUnchanged = list(set(allBodies) - set(bodyRenamed))
    # with open("bodyUnchanged.txt", "w") as f:
    #     for thisBody in bodyUnchanged:
    #         f.write("{}\n".format(thisBody))
    #     f.write(str(len(bodyUnchanged)))
    # deleteEntities(bodyUnchanged)

def importCAD2(pairedBodies):
    cadModelNm = simlab.getModelName("CAD")
    allBodies = simlab.getBodiesWithSubString(cadModelNm, ["*"])
    bodyRenamed = []

    for key, value in pairedBodies.items():
        theKey = getKeyByValue(key, csvDict)
        if theKey:
            for i, thisBody in enumerate(value):
                if i > 0:
                    newBodyName = "{}_{}".format(theKey, i)
                    renameBody(thisBody, newBodyName)
                    bodyRenamed.append(thisBody)
                else:
                    renameBody(thisBody, theKey)
                    bodyRenamed.append(thisBody)
    bodyUnchanged = list(set(allBodies) - set(bodyRenamed))
    deleteEntities(bodyUnchanged)

