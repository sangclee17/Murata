from hwx import simlab
import os, sys, importlib

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

def CreateLoadCase():
    LoadCaseSetup=''' <LoadCase isObject="2" gda="" UUID="A0DB2D03-D6B5-47c5-899F-4337EF43D7CF" BCType="LoadCase" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="LoadCase1"/>
    <ID Value="1"/>
    <Loads Value=""/>
    <Solution Value=""/>
    <IsUpdateSubLoadCase Value="0"/>
    <IsLCOptionsModified Value="0"/>
    <Output/>
    </LoadCase>'''
    simlab.execute(LoadCaseSetup)