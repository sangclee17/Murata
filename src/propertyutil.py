from hwx import simlab
import tkinter.messagebox as messagebox
import os
import importlib
import simlablib
import muratautil
import assemStructure

MESH_STATUS = "MESH_STATUS"
MAX_ID_PROPERTY = "MAX_ID_PROPERTY"
BODY_VOLUME_CSV_BEFORE = "volumeBefore.csv"
BODY_VOLUME_CSV_AFTER = "volumeAfter.csv"

def makeProperty(propInfo):
    propNm, entityType, matType, bodyNm = propInfo
    propId = getPropertyID()
    modelNm = simlab.getModelName("FEM")
    AnalysisProperty=''' <Property UUID="FAABD80A-7FA2-4d2a-961B-BFA06A361A4C">
    <tag Value="-1"/>
    <Name Value="'''+ propNm +'''"/>
    <Dimension Value="'''+ entityType +'''"/>
    <Type Value="Isotropic"/>
    <ID Value="'''+ str(propId) +'''"/>
    <Material Value="'''+ matType +'''"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNm).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    <UseExistingPropertyCheck Value="0"/>
    <CoordSystem Value=""/>
    <TableData>
    <WriteMaterial Value="1" Type="2"/>
    <Abaqus_Element_Type Value="0" Type="3"/>
    <OptiStruct_Explicit_Element_Type Value="0" Type="3"/>
    <Ansys_Element_Type Value="0" Type="3"/>
    <Integration_type Value="0" Type="3"/>
    </TableData>
    <Composite/>
    </Property>'''
    simlab.execute(AnalysisProperty)
    # print(AnalysisProperty)

def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def getBodyNmSet():
    uniBodyNms = []
    allBodies = simlab.getBodiesWithSubString(simlab.getModelName("FEM"),["*"])
    for thisBody in allBodies:
        splBody = thisBody.split("_")
        if len(splBody) == 1:
            if not splBody[0] in uniBodyNms:
                uniBodyNms.append(thisBody)
        elif len(splBody) > 1:
            nameTemp = [] 
            for aChuck in splBody:
                if not representsInt(aChuck):
                    nameTemp.append(aChuck)
            bodyNameOrigin = "_".join(nameTemp)
            if not bodyNameOrigin in uniBodyNms:
                uniBodyNms.append(bodyNameOrigin)
    return uniBodyNms

def substract(a, b):                              
    return "".join(a.rsplit(b))

def deleteAllProperties():
    DeleteProperty=''' <DeleteProperty UUID="5e9033a8-599c-4f42-a9d2-b3fd54c71136" CheckBox="ON">
    <Name Value=""/>
    </DeleteProperty>'''
    simlab.execute(DeleteProperty)

def getNameSeries(theBodyNm):
    modelNm = simlab.getModelName("FEM")
    bodyNms = simlab.getBodiesWithSubString(modelNm, ["{}*".format(theBodyNm)])

    bodyNmWithNum = []
    for thisBody in bodyNms:
        if len(thisBody) > len(theBodyNm):
            subNm = substract(thisBody, theBodyNm)
            spNm = subNm.split("_")
            if len(spNm) > 1:
                if representsInt(spNm[1]):
                    bodyNmWithNum.append(thisBody)
    bodyNmWithNum.append(theBodyNm)
    return bodyNmWithNum

def getPropertyID():
    if simlab.isParameterPresent(MAX_ID_PROPERTY):
        PROPERTYID = simlab.getIntParameter('$'+MAX_ID_PROPERTY) + 1
    else:
        PROPERTYID = 1
    simlablib.AddIntParameters(MAX_ID_PROPERTY, PROPERTYID)
    
    return PROPERTYID

def exportCalculatedBodyVolume(volumePath_after):
    modelNm = simlab.getModelName("FEM")
    bodyNms = simlab.getBodiesWithSubString(modelNm,["*"])
    CalculateVolume=''' <CalculateVolume UUID="d39d9d77-f4b8-4578-a341-7be7ac69dd47">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNms).replace("'", '"').strip("()") +'''</Body>
    </Entities>
    </SupportEntities>
    <FileName Value="'''+ volumePath_after +'''"/>
    </CalculateVolume>'''
    simlab.execute(CalculateVolume)

def readVolumeCSV(f_name):
    aDict = {}
    with open(f_name, "r") as f:
        lines = f.readlines()
        for line in lines:
            if not line:
                continue
            if line.startswith("#"):
                continue
            # print(line)
            lineSp = line.rstrip().split(",")
            if len(lineSp) == 2:
                productName = lineSp[0]
                volume = float(lineSp[1])
                aDict[productName] = volume
    # print(aDict)
    return aDict

def createProperty():
    importlib.reload(assemStructure)
    logDir = assemStructure.getLogDIR()
    volumePath_after = os.path.join(logDir, BODY_VOLUME_CSV_AFTER)
    volumePath_before = os.path.join(logDir, BODY_VOLUME_CSV_BEFORE)
    if not os.path.exists(volumePath_before):
        messagebox.showinfo("情報","Imported volume csv not found")
        return

    if os.path.exists(volumePath_after):
        os.remove(volumePath_after)
    
    exportCalculatedBodyVolume(volumePath_after)

    if not os.path.exists(volumePath_after):
        messagebox.showinfo("情報","Calculated volume csv not found")
        return

    volume_before = readVolumeCSV(volumePath_before)
    volume_after = readVolumeCSV(volumePath_after)

    modelNm = simlab.getModelName("FEM")
    if not modelNm:
        messagebox.showinfo("情報","FEM　モデルを作成してください。")
        return
    bodyNms = simlab.getBodiesWithSubString(modelNm, ["*"])
    for thisBody in bodyNms:
        bodyPrefix = muratautil.getPrefixOfBodyNm(thisBody)
        measuredBodyMass = "{}_mass".format(bodyPrefix)
        density = "{}_density".format(bodyPrefix)
        youngs = "{}_youngs".format(bodyPrefix)

        if simlab.isParameterPresent(bodyPrefix) and simlab.isParameterPresent(youngs):
            material = simlab.getStringParameter("$"+ bodyPrefix)
            youngs = simlab.getDoubleParameter("$"+ youngs)
            density = simlab.getDoubleParameter("$"+ density)
            materialName = "{}_{}".format(material, thisBody)

            if not checkSolidBody(thisBody):
                # Shell body case
                materialInfo = materialName, youngs, density
                createMaterial(materialInfo)
            else:
                measuredDensity = None
                if simlab.isParameterPresent(measuredBodyMass):
                    if thisBody in volume_after:
                        # measured-body-mass case
                        # print("case1", thisBody)
                        bodyVolume = volume_after[thisBody]
                        # print("calVolume", str(bodyVolume))
                        bodyMass = simlab.getDoubleParameter("$"+measuredBodyMass)
                        measuredDensity = bodyMass/bodyVolume
                        # print("measuredDensity", str(measuredDensity))
                else:
                    if thisBody in volume_after and thisBody in volume_before:
                        # print("case2", thisBody)
                        bodyVolumeAfter = volume_after[thisBody]
                        bodyVolumeBefore = volume_before[thisBody]
                        bodyMass = density * bodyVolumeBefore
                        measuredDensity =  bodyMass / bodyVolumeAfter

                    elif thisBody in volume_after and bodyPrefix in volume_before:
                        bodyVolumeAfter = volume_after[thisBody]
                        bodyVolumeBefore = volume_before[bodyPrefix]
                        bodyMass = density * bodyVolumeBefore
                        measuredDensity =  bodyMass / bodyVolumeAfter

                if measuredDensity is not None:
                    materialInfo = materialName, youngs, measuredDensity
                    # print(materialInfo)
                    createMaterial(materialInfo)
                    propName = "{}_PROP".format(thisBody)
                    propInfo = propName, "Solid", materialName, thisBody
                    makeProperty(propInfo)

def checkSolidBody(bodyNm):
    modelNm = simlab.getModelName("FEM")
    groupNm = "Select3DElements_58"
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ str(bodyNm).replace("'",'"').strip("()") +'''</Body>
    </Entities>
    </InputBody>
    <Option Value="3DElements"/>
    <Groupname Value="'''+ groupNm +'''"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)
    elems3D = simlab.getEntityFromGroup(groupNm)
    _deleteGrp(groupNm)

    return True if elems3D else False

def _deleteGrp(grpNm):
    DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +'''"/>
    <Output/>
    </DeleteGroupControl>'''
    simlab.execute(DeleteGroupControl)

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
    # print(Material)