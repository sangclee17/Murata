# coding: utf_8
# SimLab Version 2019.2 (64-bit)
#***************************************************************
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import os, sys, importlib
from hwx import simlab, gui
import csv

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

import basedialog
import simlablib
import simlabutil
import grouputil
import modelinfoutil

## struct of body-parameter
class BodyInfoWidget():
    def __init__(self, frm, i, bodyName, elementSize, material, materialList):
        self.bodyName = tk.Entry(frm, width=20)
        self.bodyName.insert(tk.END, bodyName)
        self.bodyName.grid(row=i+1, column=0, sticky='nwse')
        self.bodyName.configure(state='readonly')

        self.elementSize = tk.Entry(frm, width=5)
        self.elementSize.insert(tk.END, elementSize)
        self.elementSize.grid(row=i+1, column=1, sticky='nwse')

        self.materialName = tk.StringVar()
        self.materialName.set(material)
        self.material = ttk.Combobox(frm, width=10, state='readonly', values=materialList, textvariable=self.materialName)
        self.material.grid(row=i+1, column=2, sticky='nwse')

    def GetWidgets(self):
        return [self.bodyName, self.elementSize, self.material]

    def GetValues(self):
        return [self.bodyName.get(), self.elementSize.get(), self.material.get()]

    def Grid(self, i):
        self.bodyName.grid(row=i, column=0, sticky='nwse')
        self.elementSize.grid(row=i, column=1, sticky='nwse')
        self.material.grid(row=i, column=2, sticky='nwse')

## model info gui class
class ModelInfo(basedialog.BaseDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.selectedIndex = -1
        self.bodyInfoList = []
        self.materialList = self.ReadMaterials()

        self.master.title('モデル情報')
        self.master.resizable(width=True, height=True)
        self.CreateWidgets()

    def ReadMaterials(self):
        productNames = self.GetProductNames()
        
        exists = set()
        for pName in productNames:
            if simlab.isParameterPresent(pName):
                exists.add(simlab.getStringParameter('$' + pName))

        materials = list(exists)
        materials.sort()
        return materials

    def GetProductNames(self):
        modelName = simlab.getModelName('CAD')
        bodies = list(simlab.getBodiesWithSubString(modelName,['*']))
        bodies.sort()

        exists = set()
        for body in bodies:
            exists.add(self.ParseProductName(body))

        names = list(exists)
        names.sort()
        return names

    def ParseProductName(self, bodyName):
        items = bodyName.split('_')

        while len(items) > 0:
            endStr = items[-1]
            if not endStr.isdecimal():
                break
            items = items[:-1]
        
        if len(items) == 0:
            return None

        return '_'.join(items)

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)
        self.lblNote = tk.Label(self.frmTop, text='Tips:  対象ボディを選択後、行から選んでパラメータ適用を押してください。')
        self.lblNote.pack(side=tk.TOP, anchor=tk.NW, expand=False, fill=tk.X)
        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmDefault = tk.Frame(self.frmTop)
        self.frmDefault.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmDefault, text='デフォルト平均要素サイズ:').pack(side=tk.LEFT, anchor=tk.W)
        self.defaultElementSize = tk.Entry(self.frmDefault, width=10)
        defaultElemSize = self.getDefaultMeshSize()
        self.defaultElementSize.insert(tk.END, str(defaultElemSize))
        self.defaultElementSize.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.btnDefaultElementSize = tk.Button(self.frmDefault, text='デフォルト更新', width=12, command=self.UpdateParameters)
        self.btnDefaultElementSize.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.CreateTableWidgets()
        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.CreateCtrlWidgets()

        self.ImportParameters(defaultElemSize)

    def CreateTableWidgets(self):
        self.frmTable = tk.Frame(self.frmTop)
        self.frmTable.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        self.frmTable.rowconfigure(0, weight=1)
        self.frmTable.columnconfigure(0, weight=1)

        # Remark:
        # Treeview object as table-class of tkinter can not be edited directly. 
        # So I created a table with mulitiple entries like other project.
        # And tkinter's frame can not be moved with the scrollbar.
        # As a solution, once I creates a canvas, and creates frame and entries on it.
        self.canvas = tk.Canvas(self.frmTable, height=500)
        self.canvas.grid(row=0, column=0, sticky='nwse')

        self.bar = tk.Scrollbar(self.frmTable, orient=tk.VERTICAL)
        self.bar.grid(row=0, column=1, sticky='nwse')
        self.bar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.bar.set)

        self.frmTab = tk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0,0), window=self.frmTab, anchor=tk.NW)
        self.frmTab.bind("<Configure>", self.OnFrameConfigure)
        self.canvas.bind('<Configure>', self.FrameWidth)

        self.frmTab.grid_columnconfigure((0,1,2), weight=1)

        # header
        tk.Label(self.frmTab, text='ボディ名:', borderwidth=2, relief="groove").grid(row=0, column=0, sticky='nwse')
        tk.Label(self.frmTab, text='平均要素長:', borderwidth=2, relief="groove").grid(row=0, column=1, sticky='nwse')
        tk.Label(self.frmTab, text='材料名:', borderwidth=2, relief="groove").grid(row=0, column=2, sticky='nwse')

    def FrameWidth(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width = canvas_width)

    def OnFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def CreateCtrlWidgets(self):
        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=False, fill=tk.X)
        btnWidth = 12

        self.frmCtrl1 = tk.Frame(self.frmTop)
        self.frmCtrl1.pack(side=tk.TOP, anchor=tk.NW, expand=False, fill=tk.X)
        self.btnAdd = tk.Button(self.frmCtrl1, text=' 追加 ', width=btnWidth, command=self.AddRowManual)
        self.btnAdd.pack(side=tk.LEFT, anchor=tk.NE)
        self.btnDelete = tk.Button(self.frmCtrl1, text=' 削除 ', width=btnWidth, command=self.DeleteRowManual)
        self.btnDelete.pack(side=tk.LEFT, anchor=tk.NE)

        tk.Frame(self.frmTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        self.frmCtrl2 = tk.Frame(self.frmTop)
        self.frmCtrl2.pack(side=tk.TOP, anchor=tk.NW, expand=False, fill=tk.X)

        self.btnClose = tk.Button(self.frmCtrl2, text=' 閉じる ', width=btnWidth, command=self.CloseDialog)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
        self.btnImport = tk.Button(self.frmCtrl2, text=' パラメータ適用 ',  width=btnWidth, command=self.ApplyParameter)
        self.btnImport.pack(side=tk.LEFT, anchor=tk.NW)

    def AddRow(self, parameters, moveview=True):
        if len(self.materialList) == 0:
            return

        i = len(self.bodyInfoList)

        bodyName = parameters[0]
        elementSize = parameters[1]
        material = parameters[2]
        if material == "":
            material = self.materialList[0]

        bodyWidget = BodyInfoWidget(self.frmTab, i, bodyName, elementSize, material, self.materialList)
        self.bodyInfoList.append(bodyWidget)

        for w in bodyWidget.GetWidgets():
            w.bind('<Button-1>', self.SelectRow)

        if moveview:
            self.canvas.update()
            self.canvas.yview_moveto(1)

    def DeleteRow(self):
        index = self.selectedIndex

        # move param[i+1] to param[i] ( from idx to end )
        for i in range(index+1, len(self.bodyInfoList)):
            self.bodyInfoList[i].Grid(i)

        # delete param[idx]
        for w in self.bodyInfoList[index].GetWidgets():
            w.destroy()
        del self.bodyInfoList[index]

        self.selectedIndex = -1

    def AddRowManual(self):
        if len(self.materialList) == 0:
            return

        body = simlab.getSelectedBodies()
        if len(body) != 1:
            messagebox.showinfo('情報', 'ボディを１つ選択してください')
            return

        body = body[0]
        mat = self.materialList[0]

        if simlab.isParameterPresent(mat):
            mat = simlab.getStringParameter('$' + body)

        parameters = [body, self.defaultElementSize.get(), mat]
        self.AddRow(parameters, moveview=True)

    def DeleteRowManual(self):
        index = self.selectedIndex
        if index < 0:
            messagebox.showinfo('情報', '１行選択した後、押下してください。')
            return

        ret = messagebox.askokcancel('質問', '選択した行を削除しますか？')
        if not ret:
            return

        self.DeleteRow()

    def DeleteAllRow(self):
        for i in range(len(self.bodyInfoList)-1, -1, -1):
            self.selectedIndex = i
            self.DeleteRow()
        self.selectedIndex = -1

    def SelectRow(self, event):
        self.selectedIndex = -1
        for i in range(len(self.bodyInfoList)):
            isSelected = False
            ws = self.bodyInfoList[i].GetWidgets()
            for w in ws:
                if event != None and w == event.widget:
                    isSelected = True
                    self.selectedIndex = i
                    break

            bg = 'SystemWindow'
            if isSelected:
                bg = 'lightblue'
            if ws[0].cget(key="background") == 'gray':
                bg = 'gray'

            for w in ws:
                w.config(background=bg)
    
    def getDefaultMeshSize(self):
        if simlab.isParameterPresent("DefaultMeshSize"):
            meshSize = simlab.getDoubleParameter("$DefaultMeshSize")
        else:
            meshSize = 20
        return meshSize
    
    def UpdateParameters(self):
        try:
            defaultMeshSize = float(self.defaultElementSize.get())
            self.defaultElementSize.delete(0,tk.END)
            self.defaultElementSize.insert(tk.END, "{}".format(defaultMeshSize))
            simlablib.AddRealParameters("DefaultMeshSize", defaultMeshSize)

            self.ImportParameters(defaultMeshSize)
        except ValueError:
            pass

    def ImportParameters(self, defaultMeshSize):        
        self.DeleteAllRow()

        productNames = self.GetProductNames()
        for pName in productNames:
            if not simlab.isParameterPresent(pName):
                continue

            if simlab.isParameterPresent(pName + '_meshSize'):
                meshSize = simlab.getDoubleParameter('$' + pName + '_meshSize')
            else:
                meshSize = defaultMeshSize

            mat = simlab.getStringParameter('$' + pName)

            self.AddRow([pName, meshSize, mat], moveview=False)

    def ApplyParameter(self):
        defaultMeshSize = float(self.defaultElementSize.get())

        for bodyInfo in self.bodyInfoList:
            bodyName, elementSize, materailName = bodyInfo.GetValues()
            try:
                if defaultMeshSize != float(elementSize):
                    simlablib.AddRealParameters(bodyName + '_meshSize', float(elementSize))
                elif defaultMeshSize == float(elementSize):
                    simlablib.DeleteParameters(bodyName + '_meshSize')
                simlablib.AddStringParameters(bodyName, materailName)
            except ValueError:
                pass
