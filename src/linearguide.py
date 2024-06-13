import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import sys, os, importlib
from hwx import simlab, gui

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

# local
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

import basedialog
import simlablib
import simlabutil
import coordinate
import linearguideutil
import linearguideendcap

importlib.reload(linearguideendcap)

class LinearGuideDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup, springs):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        
        self.master.title('リニアガイド')
        self.backup = backup
        self.springs = springs

        self.railRadialFaces = '_railRadialFaces'
        self.railHorizontalFaces = '_railHorizontalFaces'
        self.railDriveFaces = '_railDriveFaces'
        self.ReilPageIndex = 0

        self.alignBaseFaces = '_alignBaseFaces'
        self.alignTargetFaces = '_alignTargetFaces'

        self.springNode1 = '_springNode1'
        self.springNode2 = '_springNode2'
        self.springNode3 = '_springNode3'
        self.springNode4 = '_springNode4'
        self.springBlockBody = '_springBlockBody'
        self.springRaidBody = '_springRailBody'

        self.CreateWidgets()

        self.groups = [self.railRadialFaces, self.railHorizontalFaces, self.railDriveFaces,\
            self.alignBaseFaces, self.alignTargetFaces,\
            self.springNode1, self.springNode2, self.springNode3,\
            self.springNode4, self.springBlockBody, self.springRaidBody,\
        ]
        self.buttons = [self.btnRailRad, self.btnRailHzn, self.btnRailDrv,\
            self.btnAlignBase, self.btnAlignTarget,\
            self.btnSpringNode1, self.btnSpringNode2, self.btnSpringNode3,\
            self.btnSpringNode4, self.btnSpringBlock, self.btnSpringRail,
        ]
        self.UpdateWidgets()
        
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmRail = tk.Frame(self.nb)
        self.frmAlign = tk.Frame(self.nb)
        self.frmEndCap = tk.Frame(self.nb)
        self.frmSpring = tk.Frame(self.nb)
        self.nb.add(self.frmRail, text=' レール簡略化 ')
        self.nb.add(self.frmAlign, text=' ブロック簡略化 ')
        self.nb.add(self.frmEndCap, text=' エンドキャップ ')
        self.nb.add(self.frmSpring, text=' バネ作成 ')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        self.nb.bind('<<NotebookTabChanged>>', self.ChangeTab)

        self.CreateRailTab()
        self.CreateEndCaplTab()
        self.CreateAlignTab()
        self.CreateSpringTab()

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.BOTTOM, anchor=tk.NE)

        btnWidth = 10
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def ChangeTab(self, event):
        simlabutil.ClearSelection()

        cid = self.nb.index('current')
        entity = 'Face'

        if cid == 0:
            entity = 'Face'
        elif cid == 1:
            entity = 'Face'
        elif cid == 2:
            entity = 'Face'
        elif cid == 3:
            entity = 'Node'
        
        simlab.setSelectionFilter(entity)

    def SelectEntity(self, entityType, groupName):
        entities = simlab.getSelectedEntities(entityType)
        if len(entities) == 0:
            messagebox.showinfo('情報','エンティティを選択してください。')
            return

        simlablib.DeleteGroups(groupName)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, entityType, entities, groupName)

        simlabutil.ClearSelection()
        self.UpdateWidgets()

    def CreateRailTab(self):
        self.frmRailTop = tk.Frame(self.frmRail)
        self.frmRailTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5, pady=5)

        tk.Label(self.frmRailTop, text='Tips: 画像に従い面を選択後、[簡略化]ボタンを押してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmRailFig = tk.Frame(self.frmRailTop)
        self.frmRailFig.pack(side=tk.TOP, anchor=tk.CENTER)

        # Radial
        self.frmRailRad = tk.Frame(self.frmRailFig)
        self.frmRailRad.pack(side=tk.TOP, anchor=tk.CENTER)
        self.imageRailRad = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'linear_radial.png')), master=self.frmRailFig)
        tk.Label(self.frmRailRad, image=self.imageRailRad).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnRailRad = tk.Button(self.frmRailRad, text='ラジアル方向の両平面', command = lambda : self.SelectRailEntity('Face', self.railRadialFaces))
        self.btnRailRad.place(x=10, y=70)

        # Horizon
        self.frmRailHzn = tk.Frame(self.frmRailFig)
        self.imageRailHzn = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'linear_horizon.png')), master=self.frmRailFig)
        tk.Label(self.frmRailHzn, image=self.imageRailHzn).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnRailHzn = tk.Button(self.frmRailHzn, text='水平方向の両平面', command = lambda : self.SelectRailEntity('Face', self.railHorizontalFaces))
        self.btnRailHzn.place(x=10, y=70)

        # Drive
        self.frmRailDrv = tk.Frame(self.frmRailFig)
        self.imageRailDrv = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'linear_drive.png')), master=self.frmRailFig)
        tk.Label(self.frmRailDrv, image=self.imageRailDrv).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnRailDrv = tk.Button(self.frmRailDrv, text='駆動方向の両平面', command = lambda : self.SelectRailEntity('Face', self.railDriveFaces))
        self.btnRailDrv.place(x=10, y=75)

        tk.Frame(self.frmRailTop, height=5).pack(side=tk.TOP, anchor=tk.NW)

        # select ctrl
        self.frmRailSelCtrl = tk.Frame(self.frmRailTop)
        self.frmRailSelCtrl.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconRailPrev = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'prev.png')), master=self.frmRailSelCtrl)
        self.btnRailPrev = tk.Button(self.frmRailSelCtrl, image=self.iconRailPrev, command=self.JumpPrevRail)
        self.btnRailPrev.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)
        self.iconRailNext = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'next.png')), master=self.frmRailSelCtrl)
        self.btnRailNext = tk.Button(self.frmRailSelCtrl, image=self.iconRailNext, command=self.JumpNextRail)
        self.btnRailNext.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)
        self.UpdateRailPage()

        tk.Frame(self.frmRailTop, height=5).pack(side=tk.TOP)
        tk.Frame(self.frmRailTop, height=5).pack(side=tk.TOP)

        # Ctrl
        self.frmRailCtrl = tk.Frame(self.frmRailTop)
        self.frmRailCtrl.pack(side=tk.TOP, anchor=tk.NW)
        btnWidth = 10
        self.btnCreateRail = tk.Button(self.frmRailCtrl, text='簡略化', command=self.CreateRail, width=btnWidth)
        self.btnCreateRail.pack(side=tk.LEFT, anchor=tk.W)
        self.btnRailUndo = tk.Button(self.frmRailCtrl, text='戻す', command=self.Undo, width=btnWidth)
        self.btnRailUndo.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.backup.Append(self.btnRailUndo)

    def JumpPrevRail(self):
        self.ReilPageIndex -= 1
        self.UpdateRailPage()

    def JumpNextRail(self):
        self.ReilPageIndex += 1
        self.UpdateRailPage()

    def JumpIndexRail(self, idx):
        self.ReilPageIndex = idx
        self.UpdateRailPage()

    def UpdateRailPage(self):
        self.frmRailRad.forget()
        self.frmRailHzn.forget()
        self.frmRailDrv.forget()

        if self.ReilPageIndex == 0:
            self.frmRailRad.pack(side=tk.TOP, anchor=tk.CENTER)
            self.btnRailPrev.config(state='disabled')
            self.btnRailNext.config(state='normal')
        elif self.ReilPageIndex == 1:
            self.frmRailHzn.pack(side=tk.TOP, anchor=tk.CENTER)
            self.btnRailPrev.config(state='normal')
            self.btnRailNext.config(state='normal')
        else:
            self.frmRailDrv.pack(side=tk.TOP, anchor=tk.CENTER)
            self.btnRailPrev.config(state='normal')
            self.btnRailNext.config(state='disabled')

    def SelectRailEntity(self, entity, groupName):
        self.SelectEntity(entity, groupName)
        if self.ReilPageIndex != 2:
            self.JumpNextRail()

    def CreateRail(self):
        self.backup.Save('Rail')

        heighFaceGrp = self.railRadialFaces
        widthFaceGrp = self.railHorizontalFaces
        lengthFaceGrp = self.railDriveFaces
        importlib.reload(linearguideutil)
        linearguideutil.createRail(heighFaceGrp, widthFaceGrp, lengthFaceGrp)

        simlablib.DeleteGroups([self.railRadialFaces, self.railHorizontalFaces, self.railDriveFaces])
        self.JumpIndexRail(0)
        self.UpdateWidgets()

    def CreateEndCaplTab(self):
        self.frmEndCapTop = tk.Frame(self.frmEndCap)
        self.frmEndCapTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5, pady=5)

        tk.Label(self.frmEndCapTop, text='Tips: 分割する平面を選択して[削除]を押下してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmEndCapFig = tk.Frame(self.frmEndCapTop)
        self.frmEndCapFig.pack(side=tk.TOP, anchor=tk.CENTER)

        self.imageEndCap = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'linear_guide_endcap.png')), master=self.frmEndCapFig)
        tk.Label(self.frmEndCapFig, image=self.imageEndCap).pack(side=tk.TOP, anchor=tk.CENTER)

        tk.Frame(self.frmEndCapTop, height=5).pack(side=tk.TOP)

        self.frmEndCapCtrl = tk.Frame(self.frmEndCapTop)
        self.frmEndCapCtrl.pack(side=tk.TOP, anchor=tk.NW)

        btnWidth = 10
        self.btnEndCapDel = tk.Button(self.frmEndCapCtrl, text='削除', command=self.DeleteEndCap, width=btnWidth)
        self.btnEndCapDel.pack(side=tk.LEFT, anchor=tk.W)
        self.btnEndCapUndo = tk.Button(self.frmEndCapCtrl, text='戻す', command=self.Undo, width=btnWidth)
        self.btnEndCapUndo.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.backup.Append(self.btnEndCapUndo)

    def DeleteEndCap(self):
        modelName = simlab.getModelName('FEM')

        self.backup.Save('EndCap')

        faces = simlab.getSelectedEntities('Face')
        planeGrp = simlabutil.UniqueGroupName('_Plane')
        simlablib.CreateGroup(modelName, 'Face', faces, planeGrp)

        maxCount = 100
        iCount = 0
        proceededFaces = []
        while True:
            iCount += 1
            if iCount > maxCount:
                break

            planeFace = -1
            faces = simlab.getEntityFromGroup(planeGrp)
            for face in faces:
                result = simlab.definePlaneFromEntity(modelName, face)
                if len(result) == 0:
                    continue
                if face in proceededFaces:
                    continue
                planeFace = face
                break            
            else:
                break
            if planeFace < 0:
                break

            linearguideendcap.DeleteEndCap(planeFace)
            proceededFaces.append(planeFace)

        simlablib.DeleteGroups(planeGrp)
        self.UpdateWidgets()

    def CreateAlignTab(self):
        self.frmAlignTop = tk.Frame(self.frmAlign)
        self.frmAlignTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5, pady=5)

        tk.Label(self.frmAlignTop, text='Tips: 画像の面を選択して[投影]を押下してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmAlignFig = tk.Frame(self.frmAlignTop)
        self.frmAlignFig.pack(side=tk.TOP, anchor=tk.CENTER)

        self.imageAlign = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'linear_guide_align.png')), master=self.frmAlignFig)
        tk.Label(self.frmAlignFig, image=self.imageAlign).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnAlignBase = tk.Button(self.frmAlignFig, text='基準平面', command=lambda : self.SelectEntity('Face', self.alignBaseFaces))
        self.btnAlignBase.place(x=40, y=35)
        self.btnAlignTarget = tk.Button(self.frmAlignFig, text='投影したい面', command=lambda : self.SelectEntity('Face', self.alignTargetFaces))
        self.btnAlignTarget.place(x=160, y=200)

        tk.Frame(self.frmAlignTop, height=5).pack(side=tk.TOP)

        self.frmAlignCtrl = tk.Frame(self.frmAlignTop)
        self.frmAlignCtrl.pack(side=tk.TOP, anchor=tk.NW)

        btnWidth = 10
        self.btnAlign = tk.Button(self.frmAlignCtrl, text='投影', command=self.AlignFaces, width=btnWidth)
        self.btnAlign.pack(side=tk.LEFT, anchor=tk.W)
        self.btnAlignUndo = tk.Button(self.frmAlignCtrl, text='戻す', command=self.Undo, width=btnWidth)
        self.btnAlignUndo.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.backup.Append(self.btnAlignUndo)

    def AlignFaces(self):
        self.backup.Save('Align')

        importlib.reload(linearguideutil)
        refFaces = simlab.getEntityFromGroup(self.alignBaseFaces)
        if len(refFaces) > 1:
            messagebox.showinfo("情報","Select only 1 planar face for the reference")
            return
        
        linearguideutil.alignFaces(self.alignTargetFaces, self.alignBaseFaces)

        simlablib.DeleteGroups([self.alignBaseFaces, self.alignTargetFaces])
        self.UpdateWidgets()

    def CreateSpringTab(self):
        self.frmSpringTop = tk.Frame(self.frmSpring)
        self.frmSpringTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5, pady=5)

        tk.Label(self.frmSpringTop, text='Tips: 画像の節点と両ボディを選択後、パラメータを指定してボタンを押してください。').pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmSpringFig = tk.Frame(self.frmSpringTop)
        self.frmSpringFig.pack(side=tk.TOP, anchor=tk.CENTER)

        self.imageSpring = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'linear_guide_spring.png')), master=self.frmSpringFig)
        tk.Label(self.frmSpringFig, image=self.imageSpring).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnSpringNode1 = tk.Button(self.frmSpringFig, text='節点1', command=lambda : self.SelectEntity('Node', self.springNode1))
        self.btnSpringNode1.place(x=40, y=70)
        self.btnSpringNode2 = tk.Button(self.frmSpringFig, text='節点2', command=lambda : self.SelectEntity('Node', self.springNode2))
        self.btnSpringNode2.place(x=25, y=200)
        self.btnSpringNode3 = tk.Button(self.frmSpringFig, text='節点3', command=lambda : self.SelectEntity('Node', self.springNode3))
        self.btnSpringNode3.place(x=140, y=215)
        self.btnSpringNode4 = tk.Button(self.frmSpringFig, text='節点4', command=lambda : self.SelectEntity('Node', self.springNode4))
        self.btnSpringNode4.place(x=70, y=10)

        tk.Frame(self.frmSpringFig, height=5).pack(side=tk.TOP)

        btnWidth = 10
        self.frmSpringBody = tk.Frame(self.frmSpringTop)
        self.frmSpringBody.pack(side=tk.TOP, anchor=tk.W)
        tk.Label(self.frmSpringBody, text='ボディ:').pack(side=tk.LEFT, anchor=tk.W)
        self.btnSpringBlock = tk.Button(self.frmSpringBody, text='ブロック', width=btnWidth, command=lambda : self.SlectBody(self.springBlockBody))
        self.btnSpringBlock.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.btnSpringRail = tk.Button(self.frmSpringBody, text='レール', width=btnWidth, command=lambda : self.SlectBody(self.springRaidBody))
        self.btnSpringRail.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmSpringTop, height=5).pack(side=tk.TOP)

        self.frmSpringCoordinate = tk.Frame(self.frmSpringTop)
        self.frmSpringCoordinate.pack(side=tk.TOP, anchor=tk.W)
        tk.Label(self.frmSpringCoordinate, text='座標系:').pack(side=tk.LEFT, anchor=tk.W)
        coords = coordinate.GetAllCoordinates()
        self.springCoordinate = tk.StringVar()
        if len(coords) != 0:
            self.springCoordinate.set(coords[0])
        self.cmbSpringCoordinate = ttk.Combobox(self.frmSpringCoordinate, values=coords, textvariable=self.springCoordinate, width=20, state='readonly')
        self.cmbSpringCoordinate.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmSpringTop, height=5).pack(side=tk.TOP)

        self.frmSpringVals = tk.Frame(self.frmSpringTop)
        self.frmSpringVals.pack(side=tk.TOP, anchor=tk.W)
        self.frmSpringType = tk.Frame(self.frmSpringVals)
        self.frmSpringType.pack(side=tk.TOP, anchor=tk.W)
        tk.Label(self.frmSpringType, text='バネ:').pack(side=tk.LEFT, anchor=tk.W)
        self.springType = tk.StringVar()
        self.cmbSpringType = ttk.Combobox(self.frmSpringType, width=18, state='readonly', values=[], textvariable=self.springType)
        self.cmbSpringType.pack(side=tk.LEFT, anchor=tk.W, pady=2)
        self.cmbSpringType.bind('<<ComboboxSelected>>' , self.springs.Select)

        self.frmSpringStifs = tk.Frame(self.frmSpringVals)
        self.frmSpringStifs.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=2)
        tk.Label(self.frmSpringStifs, text='X:').grid(row=0, column=0, pady=2)
        tk.Label(self.frmSpringStifs, text='Y:').grid(row=1, column=0, pady=2)
        tk.Label(self.frmSpringStifs, text='Z:').grid(row=2, column=0, pady=2)
        self.entSpringX = tk.Entry(self.frmSpringStifs, width=15)
        self.entSpringY = tk.Entry(self.frmSpringStifs, width=15)
        self.entSpringZ = tk.Entry(self.frmSpringStifs, width=15)
        self.entSpringX.grid(row=0, column=1, padx=2)
        self.entSpringY.grid(row=1, column=1, padx=2)
        self.entSpringZ.grid(row=2, column=1, padx=2)
        self.entSpringX.insert(tk.END, 0)
        self.entSpringY.insert(tk.END, 0)
        self.entSpringZ.insert(tk.END, 0)
        self.springs.AppendWidget(self.cmbSpringType, self.springType, self.entSpringX, self.entSpringY, self.entSpringZ)

        tk.Frame(self.frmSpringTop, height=5).pack(side=tk.TOP)

        self.frmSpringCtrl = tk.Frame(self.frmSpringTop)
        self.frmSpringCtrl.pack(side=tk.TOP, anchor=tk.NW)
        self.btnCreateSpring = tk.Button(self.frmSpringCtrl, text='バネ作成', command=self.CreateSpring, width=btnWidth)
        self.btnCreateSpring.pack(side=tk.LEFT, anchor=tk.W)
        self.btnSpringUndo = tk.Button(self.frmSpringCtrl, text='戻す', command=self.Undo, width=btnWidth)
        self.btnSpringUndo.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.backup.Append(self.btnSpringUndo)

    def SlectBody(self, groupName):
        bodies = simlab.getSelectedBodies()
        if len(bodies) == 0:
            messagebox.showinfo('情報','ボディを選択してください。')
            return

        simlablib.DeleteGroups(groupName)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Body', bodies, groupName)

        simlabutil.ClearSelection()
        self.UpdateWidgets()

    def CreateSpring(self):
        try:
            sx = float(self.entSpringX.get())
            sy = float(self.entSpringY.get())
            sz = float(self.entSpringZ.get())
        except:
            messagebox.showinfo('情報','実数で指定してください。')
            return

        CID = coordinate.GetID(self.springCoordinate.get())
        if CID < 0:
            messagebox.showinfo('情報','座標系を指定してください。')
            return

        self.backup.Save('Spring')
        importlib.reload(linearguideutil)
        nodeGrps = (self.springNode1, self.springNode2, self.springNode3, self.springNode4)
        bodyGrps = (self.springBlockBody, self.springRaidBody)
        springstiff = (sx, sy, sz)
        linearguideutil.createSpring(nodeGrps, bodyGrps, springstiff, CID)

        simlablib.DeleteGroups([self.springNode1, self.springNode2, self.springNode3, self.springNode4,\
            self.springBlockBody, self.springRaidBody])
        self.UpdateWidgets()

    def UpdateWidgets(self):
        self.UpdateButtonState()
        self.UpdateButtonFG()
        self.UpdateRailPage()

    def UpdateButtonState(self):
        if (simlab.isGroupPresent(self.railRadialFaces) and
            simlab.isGroupPresent(self.railHorizontalFaces) and
            simlab.isGroupPresent(self.railDriveFaces)):
            self.btnCreateRail.config(state='normal')
        else:
            self.btnCreateRail.config(state='disabled')

        if (simlab.isGroupPresent(self.alignBaseFaces) and
            simlab.isGroupPresent(self.alignTargetFaces)):
            self.btnAlign.config(state='normal')
        else:
            self.btnAlign.config(state='disabled')

        if (simlab.isGroupPresent(self.springNode1) and
            simlab.isGroupPresent(self.springNode2) and
            simlab.isGroupPresent(self.springNode3) and
            simlab.isGroupPresent(self.springNode4) and
            simlab.isGroupPresent(self.springBlockBody) and
            simlab.isGroupPresent(self.springRaidBody)):
            self.btnCreateSpring.config(state='normal')
        else:
            self.btnCreateSpring.config(state='disabled')

    def UpdateButtonFG(self):
        for i in range(len(self.groups)):
            color = 'black'
            if simlab.isGroupPresent(self.groups[i]):
                color = 'blue'
            self.buttons[i].config(fg=color)

    def Undo(self):
        self.backup.Load()

        # Since the CAD model is displayed immediately after Undo, it is confusing
        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

    def CloseDialog(self):
        simlablib.DeleteGroups(self.groups)
        super().CloseDialog()