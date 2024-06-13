from hwx import simlab
import os, sys, importlib
import tkinter.filedialog as filedialog

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)


def ExportBDF():
    fileType = [('Bdf Files','*.bdf')]
    initDir = PROJECT_DIR

    path = filedialog.asksaveasfilename(filetypes=fileType, initialdir=initDir)
    if not os.path.isdir(os.path.dirname(path)):
        return
    
    if os.path.splitext(path)[-1].lower() != '.bdf':
        path += '.bdf'

    modelName = simlab.getModelName('FEM')
    ExportandSolve=''' <ExportStaticSolverInput pixmap="solution" UUID="f009bc99-991f-43b7-8c87-cc606ef9c443">
    <tag Value="-1"/>
    <Name Value=""/>
    <SolverName Value="NASTRAN" Version="0"/>
    <FileName Value="''' + path + '''"/>
    <Solution Value=""/>
    <WriteMode ValueText="Default" Value="0"/>
    <LoadCase Value="Default"/>
    <Renumber Value="0"/>
    <RunSolver Value="0"/>
    <DataCheck Value="0"/>
    <RemoveOrphanNodes Value="1"/>
    <Version Value="14"/>
    <ExportOptionsVersion Value="1"/>
    <RemoteSolve Value="0"/>
    <CopyIncludeFiles Value="0"/>
    <SupportEntities>
    <Entities>
        <Model>''' + modelName + '''</Model>
        <Body></Body>
    </Entities>
    </SupportEntities>
    <AnalysisType Value="LINEAR" Index="0">
    <CATEGORY_Export_Options name="Export Options" ValueText="" key="CATEGORY_Export_Options" decoration="0"/>
    <Description name="Description" ValueText="Linear Static Step" key="Description" Value="Linear Static Step" decoration="0" type="string"/>
    <Nastran_Package name="Nastran Package" ValueText="MSC_NASTRAN" key="Nastran_Package" Value="0" decoration="0" type="int"/>
    <Format name="Format" ValueText="Large Field" key="Format" Value="1" decoration="0" type="int"/>
    <Cyclic_MPC name="Cyclic MPC" ValueText="False" key="Cyclic_MPC" Value="0" decoration="0" type="check"/>
    <Export_Sets name="Export Sets" ValueText="False" key="Export_Sets" Value="0" decoration="0" type="check"/>
    <Numbering name="Numbering" ValueText="Ascending Order" key="Numbering" Value="0" decoration="0" type="int"/>
    <Write_Linear_Elements name="Write Linear Elements" ValueText="False" key="Write_Linear_Elements" Value="0" decoration="0" type="check"/>
    <Write_Transition_Elements name="Write Transition Elements" ValueText="False" key="Write_Transition_Elements" Value="0" decoration="0" type="check"/>
    <Spring_Element_Card_Format name="Spring Element Card Format" ValueText="CELAS1" key="Spring_Element_Card_Format" Value="0" decoration="0" type="int"/>
    <Assembly_Information name="Assembly Information" ValueText="HM" key="Assembly_Information" Value="0" decoration="0" type="int"/>
    <CATEGORY_Material name="Material" ValueText="" key="CATEGORY_Material" decoration="0"/>
    <Write_Material name="Write Material" ValueText="True" key="Write_Material" Value="1" decoration="0" type="check"/>
    <External_File name="External File" ValueText="" key="External_File" Value="" decoration="32" type="string"/>
    <CATEGORY_Spawn_Solver_Options name="Spawn Solver Options" ValueText="" key="CATEGORY_Spawn_Solver_Options" decoration="0"/>
    <Additional_Arguments name="Additional_Arguments" ValueText="" key="Additional_Arguments" Value="" decoration="0" type="string"/>
    <Import_results_using_h3d_reader name="Import results using h3d reader" ValueText="False" key="Import_results_using_h3d_reader" Value="0" decoration="0" type="check"/>
    </AnalysisType>
    </ExportStaticSolverInput>'''
    simlab.execute(ExportandSolve)

