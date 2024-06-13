# coding: utf_8
# SimLab Version 2019.2 (64-bit)
#***************************************************************
from hwx import simlab
import os, sys
import tkinter as tk

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

## local import
import simlablib
import simlabutil

## Menu history (changes blue button)
class MenuHistory():
    def __init__(self, gui):
        self.name = 'MenuHistory'
        self.value = 0
        self.gui = gui
        self.enums = {
            'ModelImport'         : [1 << 0,   gui.btnImport],
            'ModelInfo'           : [1 << 1,   gui.btnModel],
            'Group'               : [1 << 2,   gui.btnGroup],
            'SurfaceMesh'         : [1 << 3,   gui.btnSurfMesh],
            'FillHole'            : [1 << 4,   gui.btnFillHole],
            'Simplify'            : [1 << 5,   gui.btnSimplify],
            'FaceMerge'           : [1 << 6,   gui.btnMerge],
            'ShareNode'           : [1 << 7,   gui.btnJoin],
            'Coordinate'          : [1 << 8,   gui.btnSys],
            'MPC'                 : [1 << 9,   gui.btnMPC],
            'Bearing'             : [1 << 10,  gui.btnBearing],
            'Bolt'                : [1 << 11,  gui.btnBolt],
            'Spring'              : [1 << 12,  gui.btnSpring],
            'LinearGuide'         : [1 << 13,  gui.btnLinearGuide],
            'Volume'              : [1 << 14,  gui.btnVolume],
            'Property'            : [1 << 15,  gui.btnProperty],
            'Mass'                : [1 << 16,  gui.btnMass],
            'Mass2'               : [1 << 17,  gui.btnMass2],
            'Axis'                : [1 << 18,  gui.btnAxis],
            'Export'              : [1 << 19,  gui.btnExport],
        }
        if simlab.isParameterPresent(self.name):
            self.value = simlab.getIntParameter('$' + self.name)
        self.Update()

    def Add(self, enumType):
        if not enumType in self.enums.keys():
            return

        n = self.enums[enumType][0]
        if self.value & n:
            return

        self.value += n
        simlablib.AddIntParameters(self.name, self.value)
        self.Update()

    def DeleteAll(self):
        self.value = 0
        simlablib.AddIntParameters(self.name, self.value)
        self.Update()   

    def Get(self):
        return self.value

    def Restore(self, value):
        self.value = value
        self.Update()

    def Update(self):
        for item in self.enums.values():
            n, widget = item
            if self.value & n:
                widget.config(fg='blue')
            else:
                widget.config(fg='SystemButtonText')
