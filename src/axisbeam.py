import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib
from PIL import Image, ImageTk
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

BASE_NODE = 10000000
BAR_PREFIX = 'BAR_'

# local import
import basedialog
import simlabutil
import simlablib
import tooltip as tp

def CreateBarByLength(node, nv, length, num):
    modelName = simlab.getModelName('FEM')

    xyz1 = np.array(simlab.getNodePositionFromNodeID(modelName, node))
    xyz2 = xyz1 + length * nv

    nodeID = simlabutil.AvailableNodeID(modelName, BASE_NODE)
    simlablib.CreateNodeByXYZ(modelName, list(xyz2), nodeID)

    CreateBarByNodes(node, nodeID, num)

def CreateBarByNodes(node1, node2, num):
    modelName = simlab.getModelName('FEM')

    xyz1 = np.array(simlab.getNodePositionFromNodeID(modelName, node1))
    xyz2 = np.array(simlab.getNodePositionFromNodeID(modelName, node2))
    vec = xyz2 - xyz1
    length = np.linalg.norm(vec)
    nv = vec / length
    step = length / num

    # first ---> last-1
    bars = []
    baseNode = node1
    baseXYZ = xyz1
    for i in range(num-1):
        xyz = baseXYZ + step * nv

        nodeID = simlabutil.AvailableNodeID(modelName, BASE_NODE)
        simlablib.CreateNodeByXYZ(modelName, list(xyz), nodeID)

        bodyName = simlabutil.UniqueBodyName(modelName, 'Bar')
        CreateBar=''' <Bar UUID="741D7A3A-1CD4-4051-ABBA-CD1603D1C545" CheckBox="ON">
        <tag Value="-1"/>
        <Name Value="''' + bodyName + '''"/>
        <SupportEntities>
        <Entities>
            <Model>''' + modelName+ '''</Model>
            <Node>''' + str(baseNode) + ',' + str(nodeID) + ''',</Node>
        </Entities>
        </SupportEntities>
        <Output/>
        </Bar>'''
        simlab.execute(CreateBar)

        baseXYZ = xyz
        baseNode = nodeID
        bars.append(bodyName)

    # last    
    bodyName = simlabutil.UniqueBodyName(modelName, 'Bar')
    CreateBar=''' <Bar UUID="741D7A3A-1CD4-4051-ABBA-CD1603D1C545" CheckBox="ON">
    <tag Value="-1"/>
    <Name Value="''' + bodyName + '''"/>
    <SupportEntities>
    <Entities>
        <Model>''' + modelName+ '''</Model>
        <Node>''' + str(baseNode) + ',' + str(node2) + ''',</Node>
    </Entities>
    </SupportEntities>
    <Output/>
    </Bar>'''
    simlab.execute(CreateBar)
    bars.append(bodyName)

    simlablib.MergeBodies(modelName, bars)
    newName = GetNewName(BAR_PREFIX, 1)
    simlablib.RenameBody(modelName, bars[0], newName)

def GetNewName(key, startIndex):
    modelName = simlab.getModelName('FEM')
    bodies = set(simlab.getBodiesWithSubString(modelName, [key + '*']))

    index = startIndex
    name = key + str(index)

    while True:
        if not name in bodies:
            break
        index += 1
        name = key + str(index)
        
    return name

class AxisDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.master.title('1D要素作成')
        self.pageIndex = 0
        self.backup = backup

        self.CreateWidgets()

        simlabutil.ClearSelection()
        simlab.setSelectionFilter('Node')

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.lblNote1 = tk.Label(self.frmTop, text='Tips: 1点と距離と方向、あるいは2点を指定してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.NW)
        btnWidth = 10

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmType = tk.Frame(self.frmTop)
        self.frmType.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmType, text='作成方法:').pack(side=tk.LEFT, anchor=tk.W)

        self.type = tk.StringVar()
        self.type.set('length')
        self.chkFace = tk.Radiobutton(self.frmType, text='方向と距離', value='length', variable=self.type, command=self.SelectType)
        self.chkFace.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.chkNode = tk.Radiobutton(self.frmType, text='2節点間', value='node', variable=self.type, command=self.SelectType)
        self.chkNode.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmSelect = tk.Frame(self.frmTop)
        self.frmSelect.pack(side=tk.TOP, anchor=tk.NW, padx=10)

        # select length
        self.frmSelLength = tk.Frame(self.frmSelect)
        self.frmSelLength.pack(side=tk.TOP, anchor=tk.NW)

        self.frmLen = tk.Frame(self.frmSelLength)
        self.frmLen.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmLen, text='長さ:').pack(side=tk.LEFT, anchor=tk.W)
        tk.Frame(self.frmLen, width=5).pack(side=tk.LEFT)
        self.entLength = tk.Entry(self.frmLen, width=10)
        self.entLength.pack(side=tk.LEFT, anchor=tk.W)
        self.entLength.insert(tk.END, 10)

        tk.Frame(self.frmSelLength, height=5).pack(side=tk.TOP)

        self.frmDir = tk.Frame(self.frmSelLength)
        self.frmDir.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmDir, text='方向:').pack(side=tk.LEFT, anchor=tk.W)
        tk.Frame(self.frmDir, width=5).pack(side=tk.LEFT)

        self.direction = tk.StringVar()
        self.direction.set('X')
        self.cmbDir = ttk.Combobox(self.frmDir, values=['X','-X','Y','-Y','Z','-Z','--'], textvariable=self.direction, width=3)
        self.cmbDir.bind('<<ComboboxSelected>>', self.SelectDirection)
        self.cmbDir.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmDir, width=5).pack(side=tk.LEFT)
        self.entNX = tk.Entry(self.frmDir, width=8)
        self.entNX.pack(side=tk.LEFT, anchor=tk.W)
        self.entNX.insert(tk.END, 1)
        tk.Frame(self.frmDir, width=2).pack(side=tk.LEFT)
        self.entNY = tk.Entry(self.frmDir, width=8)
        self.entNY.pack(side=tk.LEFT, anchor=tk.W)
        self.entNY.insert(tk.END, 0)
        tk.Frame(self.frmDir, width=2).pack(side=tk.LEFT)
        self.entNZ = tk.Entry(self.frmDir, width=8)
        self.entNZ.pack(side=tk.LEFT, anchor=tk.W)
        self.entNZ.insert(tk.END, 0)
        self.SelectDirection(None)

        # select node (no gui)
        self.frmSelNode = tk.Frame(self.frmSelect)

        tk.Frame(self.frmTop, height=10).pack(side=tk.TOP, anchor=tk.NW)

        self.frmNum = tk.Frame(self.frmTop)
        self.frmNum.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmNum, text='分割数:').pack(side=tk.LEFT, anchor=tk.W)
        self.entNum = tk.Entry(self.frmNum, width=10)
        self.entNum.pack(side=tk.LEFT, anchor=tk.W)
        self.entNum.insert(tk.END, 1)

        tk.Frame(self.frmTop, height=10).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        self.btnCreate = tk.Button(self.frmCtrl, text=' 作成 ', compound=tk.LEFT, command=self.Create, width=btnWidth)
        self.btnCreate.pack(side=tk.LEFT, anchor=tk.NW)

        self.btnUndo = tk.Button(self.frmCtrl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def SelectDirection(self, event):
        if self.direction.get() == 'X':
            nx, ny, nz = 1, 0, 0
        elif self.direction.get() == '-X':
            nx, ny, nz = -1, 0, 0
        elif self.direction.get() == 'Y':
            nx, ny, nz = 0, 1, 0
        elif self.direction.get() == '-Y':
            nx, ny, nz = 0, -1, 0
        elif self.direction.get() == 'Z':
            nx, ny, nz = 0, 0, 1
        elif self.direction.get() == '-Z':
            nx, ny, nz = 0, 0, -1
        else:
            nx, ny, nz = None, None, None

        self.entNX.config(state='normal')
        self.entNY.config(state='normal')
        self.entNZ.config(state='normal')
        if nx == None:
            return

        self.entNX.delete(0, tk.END)
        self.entNY.delete(0, tk.END)
        self.entNZ.delete(0, tk.END)

        self.entNX.insert(0, nx)
        self.entNY.insert(0, ny)
        self.entNZ.insert(0, nz)

        self.entNX.config(state='disabled')
        self.entNY.config(state='disabled')
        self.entNZ.config(state='disabled')

    def SelectType(self):
        self.frmSelLength.forget()
        self.frmSelNode.forget()
        if self.type.get() == 'length':
            self.frmSelLength.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)
        else:
            self.frmSelNode.pack(side=tk.TOP, anchor=tk.CENTER, expand=1, fill=tk.X)

    def Create(self):
        if self.type.get() == 'length':
            self.CreateByLength()
        else:
            self.CreateByNodes()
    
    def CreateByLength(self):
        nodes = simlab.getSelectedEntities('NODE')
        if len(nodes) == 0:
            messagebox.showinfo('情報','節点を選択してください。')
            return            

        try:
            nx = float(self.entNX.get())
            ny = float(self.entNY.get())
            nz = float(self.entNZ.get())
            nv = np.array([nx,ny,nz])
            nv = nv / np.linalg.norm(nv)
            length = float(self.entLength.get())
            num = int(self.entNum.get())
        except:
            messagebox.showinfo('情報','分割数は整数、方向や長さは実数で指定してください。')
            return
        
        if length <= 0:
            messagebox.showinfo('情報','長さは0以上にしてください。')
            return

        self.backup.Save('1D')
        for node in nodes:
            CreateBarByLength(node, nv,length, num)

    def CreateByNodes(self):
        nodes = simlab.getSelectedEntities('NODE')
        if len(nodes) != 2:
            messagebox.showinfo('情報','2節点を選択してください。')
            return
        
        try:
            num = int(self.entNum.get())
        except:
            messagebox.showinfo('情報','分割数は整数で指定してください。')
            return

        self.backup.Save('1D')
        CreateBarByNodes(nodes[0], nodes[1], num)

    def Undo(self):
        self.backup.Load()

        # Since the CAD model is displayed immediately after Undo, it is confusing
        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        super().CloseDialog()