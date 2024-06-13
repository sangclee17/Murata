# coding: utf_8
# SimLab Version 2019.2 (64-bit)
#***************************************************************
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import sys, os, importlib
from hwx import simlab, gui

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

## Group name
BEARING_SHELL_EDGE_FACE = 'Bearing_Shell_Edge_Face_'
BEARING_SHELL_AXIS_BODY = 'Bearing_Shell_Body_'
BEARING_SHELL_OUTER_FACE = 'Bearing_Shell_Outer_Face_'
WASHER_EDGE = 'Washer_Edge_'
LOGO_FACE = 'Logo_Face_'
BOLT_FACE = 'Bolt_Face_'
TRIM_FACE = 'Trim_Face_'
TRIM_BODY = 'Trim_Body_'
TRIM_MID_FACE = 'Trim_Mid_Face_'
TRIM_MID_BODY = 'Trim_Mid_Body_'
# TRIM_MID_EDGE = 'Trim_Mid_Edge_'
BODY_SPLIT_FACE = 'Body_Split_Face_'
MERGE_FACE = 'Merge_Face_'
PRESERVE_FACE = 'Preserve_Face_'

# local
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)
import simlablib
import simlabutil
import importlib
import basedialog
import widget as wt
import tooltip as tp
import grouputil

class GroupInfo(basedialog.BaseDialog):
    def __init__(self, master, parent):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        
        # static const
        self.bearingEdgeFace = '_BearingEdgeFace'
        self.bearingAxisBody = '_BearingAxisBody'
        self.bearingOuter = '_BearingOuter'
        self.washerEdge = '_WasherEdge'
        self.logoGuide = '_LogoGuide'
        self.logoLimit = '_LogoLimit'
        self.bolt = '_Bolt'
        self.trimFace = '_TrimFace'
        self.trimBody = '_TrimBody'
        self.trimMidFace= '_TrimMidFace'
        # self.trimMidEdge = '_TrimMidEdge'
        self.trimMidBody = '_TrimMidBody'
        self.bodyDivFace = '_BodyDivFace'

        # set dialog attributes
        self.master.title('グループ作成')
        self.CreateWidgets()
        
    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmBearing = tk.Frame(self.nb)
        self.frmWasher = tk.Frame(self.nb)
        self.frmLogo = tk.Frame(self.nb)
        self.frmBolt = tk.Frame(self.nb)
        self.frmTrim = tk.Frame(self.nb)
        self.frmTrimMid = tk.Frame(self.nb)
        self.frmBodyDiv = tk.Frame(self.nb)
        self.frmMergeFace = tk.Frame(self.nb)
        self.frmPreserveFace = tk.Frame(self.nb)
        #self.nb.add(self.frmBearing, text=' ベアリング（シェル）')
        self.nb.add(self.frmWasher, text=' ワッシャー ')
        self.nb.add(self.frmLogo, text=' ロゴ ')
        self.nb.add(self.frmBolt, text=' ボルト ')
        self.nb.add(self.frmTrim, text=' トリム ')
        self.nb.add(self.frmTrimMid, text=' トリム Mid ')
        self.nb.add(self.frmBodyDiv, text=' Body 分割 ')
        self.nb.add(self.frmMergeFace, text=' 面結合 ')
        self.nb.add(self.frmPreserveFace, text=' 保持面 ')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)
        self.nb.bind('<<NotebookTabChanged>>', self.ChangeTab)
        
        self.CreateShellBearingTab()
        self.CreateWasherTab()
        self.CreateLogoTab()
        self.CreateBolt()
        self.CreateTrim()
        self.CreateTrimMid()
        self.CreateBodyDiv()
        self.CreateMergeFace()
        self.CreatePreserveFace()

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.BOTTOM, anchor=tk.NE)

        btnWidth = 10
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.LEFT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)
        simlab.setSelectionFilter('Face')

    ##
    # Bearing
    def CreateShellBearingTab(self):
        self.frmBearing.rowconfigure((2,4), weight=1)
        self.frmBearing.columnconfigure(0, weight=1)

        self.lblBNote = tk.Label(self.frmBearing, text='Tips:  ベアリング（シェル）を自動作成します。画像の該当部を選択してください。')
        self.lblBNote.grid(row=0, column=0, sticky='we')

        tk.Frame(self.frmBearing, height=5).grid(row=1, column=0)

        self.frmFig = tk.Frame(self.frmBearing)
        self.frmFig.grid(row=2, column=0, sticky='we', padx=5) 

        self.iconBearing1 = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bearing1.png')), master=self.frmBearing)
        tk.Label(self.frmFig, image=self.iconBearing1).pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmFig, width=5).pack(side=tk.LEFT, anchor=tk.W)

        self.iconBearing2 = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bearing3.png')), master=self.frmBearing)
        tk.Label(self.frmFig, image=self.iconBearing2).pack(side=tk.LEFT, anchor=tk.W)

        self.btnEdgeFace = tk.Button(self.frmFig, text=' 両端面 ', command=self.SelectEdgeFace)
        self.btnEdgeFace.place(x=130, y=15)
        self.btnBody = tk.Button(self.frmFig, text=' 軸ボディ ', command=self.SelectAxisBody)
        self.btnBody.place(x=20, y=160)
        self.btnOuter = tk.Button(self.frmFig, text=' 外輪面 ', command=self.SelectOuter)
        self.btnOuter.place(x=280, y=60)

        tk.Frame(self.frmFig, width=5).pack(side=tk.LEFT, anchor=tk.W)

        self.frmBearingVal = tk.Frame(self.frmFig)
        self.frmBearingVal.pack(side=tk.LEFT, anchor=tk.W, expand=1, fill=tk.BOTH)

        self.frmfrmBearingNum = tk.LabelFrame(self.frmBearingVal, text='要素分割数:')
        self.frmfrmBearingNum.pack(side=tk.TOP, anchor=tk.W, expand=0, fill=tk.X)

        self.frmBearingValAxis = tk.Frame(self.frmfrmBearingNum)
        self.frmBearingValAxis.pack(side=tk.TOP, anchor=tk.W, padx=5,pady=2)
        tk.Label(self.frmBearingValAxis, text='軸方向:').pack(side=tk.LEFT, anchor=tk.W)
        self.entBearingNumAxis = tk.Entry(self.frmBearingValAxis, width=5)
        self.entBearingNumAxis.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entBearingNumAxis.insert(tk.END, 4)

        self.frmBearingValAng = tk.Frame(self.frmfrmBearingNum)
        self.frmBearingValAng.pack(side=tk.TOP, anchor=tk.W, padx=5,pady=2)
        tk.Label(self.frmBearingValAng, text='周方向:').pack(side=tk.LEFT, anchor=tk.W)
        self.bearingNumAngle = tk.IntVar()
        self.bearingNumAngle.set(20)
        self.cmbBearingNumAngle = ttk.Combobox(self.frmBearingValAng, width=3, state='readonly', values=[12, 16, 20, 24], textvariable=self.bearingNumAngle)
        self.cmbBearingNumAngle.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        tk.Frame(self.frmfrmBearingNum, height=5).pack(side=tk.TOP, anchor=tk.W)

        tk.Frame(self.frmBearingVal, height=5).pack(side=tk.TOP, anchor=tk.W)

        self.frmfrmBearingSp = tk.LabelFrame(self.frmBearingVal, text='バネ要素:')
        self.frmfrmBearingSp.pack(side=tk.TOP, anchor=tk.W, expand=0, fill=tk.X)

        self.frmBearingSpNum = tk.Frame(self.frmfrmBearingSp)
        self.frmBearingSpNum.pack(side=tk.TOP, anchor=tk.W, padx=5,pady=2)
        tk.Label(self.frmBearingSpNum, text='バネの数:').pack(side=tk.LEFT, anchor=tk.W)
        self.entBearingNumSpring = tk.Entry(self.frmBearingSpNum, width=5)
        self.entBearingNumSpring.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entBearingNumSpring.insert(tk.END, 6)

        self.frmBearingSpStiff = tk.Frame(self.frmfrmBearingSp)
        self.frmBearingSpStiff.pack(side=tk.TOP, anchor=tk.W, padx=5,pady=2)
        tk.Label(self.frmBearingSpStiff, text='剛性:').pack(side=tk.LEFT, anchor=tk.W)
        self.entBearingSpringStiff = tk.Entry(self.frmBearingSpStiff, width=10)
        self.entBearingSpringStiff.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entBearingSpringStiff.insert(tk.END, 10000.0)
        tk.Frame(self.frmfrmBearingSp, height=5).pack(side=tk.TOP, anchor=tk.W)

        tk.Frame(self.frmBearing, height=5).grid(row=3, column=0)

        self.frmBListTop =  tk.Frame(self.frmBearing, height=5)
        self.frmBListTop.grid(row=4, column=0, sticky='nwse')

        self.frmBListTop.rowconfigure(0, weight=1)
        self.frmBListTop.columnconfigure(0, weight=1)

        self.frmBList = tk.Frame( self.frmBListTop)
        self.frmBList.grid(row=0, column=0, sticky='nwse')
        self.frmBLCtrl = tk.Frame( self.frmBListTop)
        self.frmBLCtrl.grid(row=0, column=1, sticky='ns')
        self.frmBList.rowconfigure(0, weight=1)
        self.frmBList.columnconfigure(0, weight=1)

        self.treeBE = ttk.Treeview(self.frmBList, height=5)
        self.treeBE['column'] = (1)
        self.treeBE['show'] = 'headings'
        self.sorttreeBE = True
        self.treeBE.heading(1, text='登録名', anchor=tk.W, command=lambda : self.SortColumn(self.treeBE, 1, self.sorttreeBE))
        self.treeBE.grid(row=0, column=0, sticky='nwse')
        self.sbYB = ttk.Scrollbar(self.frmBList, orient=tk.VERTICAL, command=self.treeBE.yview)
        self.sbYB.grid(row=0, column=1, sticky='ns')
        self.treeBE.config(yscroll=self.sbYB.set)
        self.RestoretreeBE()
        self.treeBE.bind('<<TreeviewSelect>>', self.UpdateBearingButtonState) 

        self.iconBReview = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'review-24.png')), master=self.frmBLCtrl)
        self.bntReviewBE = tk.Button(self.frmBLCtrl, image=self.iconBReview, command=lambda: self.ReviewGroup(self.treeBE))
        self.bntReviewBE.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconBDelete = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmBLCtrl)
        self.bntDeleteBE = tk.Button(self.frmBLCtrl, image=self.iconBDelete, command=self.DeleteBearingGroup)
        self.bntDeleteBE.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconBAdd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'add-24.png')), master=self.frmBLCtrl)
        self.bntAddBE = tk.Button(self.frmBLCtrl, image=self.iconBAdd, command=self.AddBearingGroup)
        self.bntAddBE.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.UpdateBearingButtonState(None)

        self.tpAddLE = tp.ToolTip(self.bntAddBE, text='選択した情報を追加します。', parent=self.master)
        self.tpDelLE = tp.ToolTip(self.bntDeleteBE, text='選択した行を削除します。', parent=self.master)
        self.tpRevLE = tp.ToolTip(self.bntReviewBE, text='選択した行を強調表示します。', parent=self.master)

    def UpdateBearingButtonState(self, event):
        selectedRows = self.treeBE.selection()
        state = 'normal'
        if len(selectedRows) == 0:
            state = 'disabled'
        
        for btn in [ self.bntDeleteBE, self.bntReviewBE ]:
            btn.config(state=state)

    def SortColumn(self, tree, col, reverse):
        l = [(tree.item(k)["values"], k) for k in tree.get_children()]
        l.sort(key=lambda t: t[0][col-1], reverse=reverse)

        for index, (_, k) in enumerate(l):
            tree.move(k, '', index)
        tree.heading(col, command=lambda: self.SortColumn(tree, col, not reverse))

    def ChangeTab(self, event):
        simlabutil.ClearSelection()

        cid = self.nb.index('current')
        if cid == 0:
            simlab.setSelectionFilter('CircleEdge')
        elif cid == 1:
            simlab.setSelectionFilter('Face')
        elif cid == 2:
            simlab.setSelectionFilter('CylinderFace')
        elif cid == 3:
            self.SelectTrimSelType()
        elif cid == 4:
            self.SelectTrimMidSelType()
        elif cid == 5:
            simlab.setSelectionFilter('Face')
        elif cid == 6:
            simlab.setSelectionFilter('Face')
        elif cid == 7:
            simlab.setSelectionFilter('Face')
        elif cid == 8:
            pass

    def SelectEdgeFace(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) < 2:
            messagebox.showinfo('情報','両側の面を選択した後、[両端面] ボタンを押下してください。')
            return
      
        simlablib.DeleteGroups(self.bearingEdgeFace)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Face', faces, self.bearingEdgeFace)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectAxisBody(self):
        bodies = simlab.getSelectedBodies()
        if len(bodies) == 0:
            messagebox.showinfo('情報','ボディを選択した後、[軸ボディ] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.bearingAxisBody)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Body', bodies, self.bearingAxisBody)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectOuter(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','外輪面を選択した後、[外輪面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.bearingOuter)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Face', faces, self.bearingOuter)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def AddBearingGroup(self):
        groups = [self.bearingEdgeFace, self.bearingAxisBody, self.bearingOuter]
        for i in range(len(groups)):
            if not simlab.isGroupPresent(groups[i]):
                messagebox.showinfo('情報', '全ての面とボディを選択後、押下してください。')
                return
        try:
            numAxis = int(self.entBearingNumAxis.get())
            numCirc = int(self.cmbBearingNumAngle.get())
            numSpring = int(self.entBearingNumSpring.get())
            stiffSpring = float(self.entBearingSpringStiff.get())
        except:
            messagebox.showinfo('情報', '全ての面とボディを選択後、押下してください。')
            return
        
        count = self.GetMaxCountOfBearing()
        count += 1
        count = str(count)

        simlablib.RenameGroup(self.bearingEdgeFace, BEARING_SHELL_EDGE_FACE + count)
        simlablib.RenameGroup(self.bearingAxisBody, BEARING_SHELL_AXIS_BODY + count)
        simlablib.RenameGroup(self.bearingOuter, BEARING_SHELL_OUTER_FACE + count)
        
        self.treeBE.insert('', 'end', values=('Bearing_' + count))

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

        simlablib.AddIntParameters("SHELLRING_COUNT", count)
        simlablib.AddIntParameters("Bearing_Shell_Axis_{}".format(count), numAxis)
        simlablib.AddIntParameters("Bearing_Shell_Circle_{}".format(count), numCirc)
        simlablib.AddIntParameters("Bearing_Shell_Spring_{}".format(count), numSpring)
        simlablib.AddRealParameters("Bearing_Shell_SpringStiff_{}".format(count), stiffSpring)

        # create region MC
        importlib.reload(grouputil)
        face1_Ent, face2_Ent = simlab.getEntityFromGroup(BEARING_SHELL_EDGE_FACE + count)
        bearingShell_axis = simlab.getBodiesFromGroup(BEARING_SHELL_AXIS_BODY + count)[0]
        regionMc_prop = "Bearing_Shell_MC_{}".format(count), bearingShell_axis, face1_Ent, face2_Ent
        grouputil.createRegionMeshControl(regionMc_prop)
    
    def GetMaxCountOfBearing(self):
        icount = 1
        while simlab.isGroupPresent(BEARING_SHELL_EDGE_FACE + str(icount)):
            icount += 1
        return icount - 1

    def DeleteBearingGroup(self):
        selectedRows = self.treeBE.selection()
        if len(selectedRows) == 0:
            messagebox.showinfo('情報','削除したい行を選択した後、ボタンを押下してください。')
            return

        for row in selectedRows:
            name = self.treeBE.item(row)['values'][0]
            items = name.split('_')
            count = items[-1]
            simlablib.DeleteGroups([BEARING_SHELL_EDGE_FACE+count, BEARING_SHELL_AXIS_BODY+count, BEARING_SHELL_OUTER_FACE+count])
            simlablib.DeleteMeshControl("Bearing_Shell_MC_{}".format(count))
            simlablib.DeleteParameters("Bearing_Shell_Axis_{}".format(count))
            simlablib.DeleteParameters("Bearing_Shell_Circle_{}".format(count))
            simlablib.DeleteParameters("Bearing_Shell_Spring_{}".format(count))
            simlablib.DeleteParameters("Bearing_Shell_SpringStiff_{}".format(count))

            self.treeBE.delete(row)
        self.UpdateBearingButtonState(None)

    def RestoretreeBE(self):
        for child in self.treeBE.get_children():
            self.treeBE.delete(child)

        groupNames = simlab.getGroupsWithSubString('FaceGroup', [BEARING_SHELL_EDGE_FACE + '*'])
        for groupName in groupNames:
            count = groupName.split('_')[-1]
            self.treeBE.insert('', 'end', values=('Bearing_' + count))

    def ReviewGroup(self, tree):
        selectedRows = tree.selection()
        if len(selectedRows) == 0:
            return
        
        simlabutil.ClearSelection()

        groups = []
        for row in selectedRows:
            name = tree.item(row)['values'][0]
            items = name.split('_')
            count = items[-1]
            groups.append(BEARING_SHELL_EDGE_FACE+count)        
            groups.append(BEARING_SHELL_OUTER_FACE+count)        
        simlab.showOrHideEntities(groups, 'Show')

    ##
    # Washer
    def CreateWasherTab(self):
        self.frmWasher.rowconfigure((2,4), weight=1)
        self.frmWasher.columnconfigure(0, weight=1)

        self.lblWNote = tk.Label(self.frmWasher, text='Tips:  ワッシャーメッシュコントロールを作成する円弧を選択してください。')
        self.lblWNote.grid(row=0, column=0, sticky='we')

        tk.Frame(self.frmWasher, height=5).grid(row=1, column=0)

        self.frmWSel = tk.Frame(self.frmWasher)
        self.frmWSel.grid(row=2, column=0, sticky='we') 

        self.frmWFig = tk.Frame(self.frmWSel)
        self.frmWFig.pack(side=tk.LEFT, anchor=tk.NW, padx=5)
        self.iconWasher = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'washer.png')), master=self.frmWFig)
        tk.Label(self.frmWFig, image=self.iconWasher).pack(side=tk.TOP, anchor=tk.W)
        self.btnWasherEdge = tk.Button(self.frmWFig, text=' 円弧 ', command=self.SelectWasherEdge)
        self.btnWasherEdge.place(x=70, y=30)

        self.frmWSct = tk.Frame(self.frmWSel)
        self.frmWSct.pack(side=tk.LEFT, anchor=tk.NW)
        tk.Label(self.frmWSct, text='外直径:').pack(side=tk.TOP, anchor=tk.W)

        self.frmWType = tk.Frame(self.frmWSct)
        self.frmWType.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=5)
        tk.Label(self.frmWType, text='タイプ:').pack(side=tk.LEFT, anchor=tk.W)

        self.WType = tk.StringVar()
        self.WType.set('Nut')
        self.chkWNut = tk.Radiobutton(self.frmWType, text='ナット対角寸法', value='Nut', variable=self.WType, command=self.SelectWType)
        self.chkWNut.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.chkWWat = tk.Radiobutton(self.frmWType, text='ワッシャー径', value='Washer', variable=self.WType, command=self.SelectWType)
        self.chkWWat.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        self.frmWVal = tk.Frame(self.frmWSct)
        self.frmWVal.pack(side=tk.TOP, anchor=tk.W, padx=10)
        tk.Label(self.frmWVal, text='直径:').pack(side=tk.LEFT, anchor=tk.W)
        self.entWDim = tk.Entry(self.frmWVal, width=10)
        self.entWDim.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.entWDim.insert(tk.END, 0)

        tk.Frame(self.frmWasher, height=5).grid(row=3, column=0)

        self.frmWListTop =  tk.Frame(self.frmWasher, height=5)
        self.frmWListTop.grid(row=4, column=0, sticky='nwse')

        self.frmWListTop.rowconfigure(0, weight=1)
        self.frmWListTop.columnconfigure(0, weight=1)

        self.frmWList = tk.Frame( self.frmWListTop)
        self.frmWList.grid(row=0, column=0, sticky='nwse')
        self.frmWLCtrl = tk.Frame( self.frmWListTop)
        self.frmWLCtrl.grid(row=0, column=1, sticky='ns')
        self.frmWList.rowconfigure(0, weight=1)
        self.frmWList.columnconfigure(0, weight=1)

        self.treeWE = ttk.Treeview(self.frmWList, height=5)
        self.treeWE['column'] = (1)
        self.treeWE['show'] = 'headings'
        self.sortTreeWE = True
        self.treeWE.heading(1, text='登録名', anchor=tk.W, command=lambda : self.SortColumn(self.treeWE, 1, self.sortTreeWE))
        self.treeWE.grid(row=0, column=0, sticky='nwse')
        self.sbYWO = ttk.Scrollbar(self.frmWList, orient=tk.VERTICAL, command=self.treeWE.yview)
        self.sbYWO.grid(row=0, column=1, sticky='ns')
        self.treeWE.config(yscroll=self.sbYWO.set)
        self.RestoreTreeWE()
        self.treeWE.bind('<<TreeviewSelect>>', self.UpdateWasherButtonState) 

        self.iconWReview = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'review-24.png')), master=self.frmWLCtrl)
        self.bntReviewWE = tk.Button(self.frmWLCtrl, image=self.iconWReview, command=lambda: self.ReviewWGroup(self.treeWE))
        self.bntReviewWE.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconWDelete = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmWLCtrl)
        self.bntDeleteWE = tk.Button(self.frmWLCtrl, image=self.iconWDelete, command=self.DeleteWasherGroup)
        self.bntDeleteWE.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconWAdd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'add-24.png')), master=self.frmWLCtrl)
        self.bntAddWE = tk.Button(self.frmWLCtrl, image=self.iconWAdd, command=self.AddWasherGroup)
        self.bntAddWE.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.UpdateWasherButtonState(None)

        self.tpAddWE = tp.ToolTip(self.bntReviewWE, text='選択した情報を追加します。', parent=self.master)
        self.tpDelWE = tp.ToolTip(self.bntDeleteWE, text='選択した行を削除します。', parent=self.master)
        self.tpRevWE = tp.ToolTip(self.bntAddWE, text='選択した行を強調表示します。', parent=self.master)

    def SelectWType(self):
        if not simlab.isGroupPresent(self.washerEdge):
            return

        edges = simlab.getEntityFromGroup(self.washerEdge)
        if len(edges) == 0:
            return

        modelName = simlab.getModelName('CAD')
        result = simlab.getArcEdgeAttributes(modelName, edges[0])
        if len(result) == 0:
            return

        radius = result[1][0]
        outerDiameter = self.GetOuterDiameter(radius)

        self.entWDim.delete(0, tk.END)
        self.entWDim.insert(tk.END, str(outerDiameter))

    def DeleteWasherGroup(self):
        selectedRows = self.treeWE.selection()
        if len(selectedRows) == 0:
            messagebox.showinfo('情報','削除したい行を選択した後、ボタンを押下してください。')
            return

        for row in selectedRows:
            name = self.treeWE.item(row)['values'][0]
            simlablib.DeleteGroups([name])
            simlablib.DeleteMeshControl(name+'_MC')
            self.treeWE.delete(row)
        self.UpdateWasherButtonState(None)

    def AddWasherGroup(self):
        if not simlab.isGroupPresent(self.washerEdge):
            messagebox.showinfo('情報', '円弧を選択後、押下してください。')
            return

        try:
            outerRadius = 0.5 * float(self.entWDim.get())
        except:
            outerRadius = -1
        if outerRadius < 0:
            messagebox.showinfo('情報', '外直径を指定してください。')
            return
        
        grplist = []
        for row in self.treeWE.get_children():
            grplist.append(self.treeWE.item(row)["values"][0])

        importlib.reload(grouputil)
        groupName = "{}{}".format(WASHER_EDGE,outerRadius)
        grouputil.addToWasherGrp(groupName, self.washerEdge)
        grouputil.createWasherMesh()

        for thisGrp in simlab.getGroupsWithSubString("EdgeGroup",[WASHER_EDGE + "*"]):
            if not thisGrp in grplist:self.treeWE.insert('', 'end', values=(thisGrp))

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def RestoreTreeWE(self):
        for child in self.treeWE.get_children():
            self.treeWE.delete(child)

        groupNames = simlab.getGroupsWithSubString('EdgeGroup', [WASHER_EDGE + '*'])
        for groupName in groupNames:
            self.treeWE.insert('', 'end', values=(groupName))

    def UpdateWasherButtonState(self, event):
        selectedRows = self.treeWE.selection()
        state = 'normal'
        if len(selectedRows) == 0:
            state = 'disabled'
        
        for btn in [ self.bntDeleteWE, self.bntReviewWE ]:
            btn.config(state=state)

    def SelectWasherEdge(self):
        edges = simlab.getSelectedEntities('EDGE')
        if len(edges) == 0:
            messagebox.showinfo('情報','円弧を選択した後、[円弧] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.washerEdge)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.washerEdge)

        values = set()
        edges = simlab.getEntityFromGroup(self.washerEdge)
        for edge in edges:
            result = simlab.getArcEdgeAttributes(modelName, edge)
            if len(result) == 0:
                continue
            radius = result[1][0]
            values.add(round(radius))

        if len(values) == 0 or len(values) > 1:
            simlablib.DeleteGroups(self.washerEdge)
            messagebox.showinfo('情報','円弧情報がないか、異なる円弧を選択しています。同じ円弧を選択してください。')
            return

        radius = values.pop()
        outerDiameter = self.GetOuterDiameter(radius)
        
        self.entWDim.delete(0, tk.END)
        self.entWDim.insert(tk.END, str(outerDiameter))

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def GetOuterDiameter(self, radius):
        diameter = radius * 2.0

        # Hole, Nut, Washer
        table = [
            [10.2, 21.9, 24],
            [14,   27.7, 30],
            [17.5, 34.6, 37],
            [18.5, 34.6, 37],
            [21,   41.6, 44],
            [22,   41.6, 44],
        ]

        # find coloset hole
        minDiff = 1e10
        minRow = ""
        for row in table:
            diff = abs(diameter - row[0])
            if diff < minDiff:
                minDiff = diff
                minRow = row
        
        if minRow == "":
            return 0                
        if self.WType.get() == 'Nut':
            return minRow[1]
        else:
            return minRow[2]

    def ReviewWGroup(self, tree):
        selectedRows = tree.selection()
        if len(selectedRows) == 0:
            return
        
        simlabutil.ClearSelection()

        groups = []
        for row in selectedRows:
            name = tree.item(row)['values'][0]
            groups.append(name)        
        simlab.showOrHideEntities(groups, 'Show')

    ##
    # Logo
    def CreateLogoTab(self):
        self.frmLogo.rowconfigure((2,4), weight=1)
        self.frmLogo.columnconfigure(0, weight=1)

        self.lblLNote = tk.Label(self.frmLogo, text='Tips:  削除したいロゴ形状を選択してください。')
        self.lblLNote.grid(row=0, column=0, sticky='we')

        tk.Frame(self.frmLogo, height=5).grid(row=1, column=0)

        self.frmLFig = tk.Frame(self.frmLogo)
        self.frmLFig.grid(row=2, column=0, sticky='we') 

        self.iconLogo1 = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'logo_guide.png')), master=self.frmLogo)
        tk.Label(self.frmLFig, image=self.iconLogo1).pack(side=tk.TOP, anchor=tk.CENTER, padx=5)

        tk.Frame(self.frmLFig, height=5).pack()

        self.iconLogo2 = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'logo_limit.png')), master=self.frmLogo)
        tk.Label(self.frmLFig, image=self.iconLogo2).pack(side=tk.TOP, anchor=tk.CENTER, padx=5)

        self.btnGuide = tk.Button(self.frmLFig, text=' 除外したい面群のガイド面 ', command=self.SelectLogoGuide)
        self.btnGuide.place(x=60, y=10)
        self.btnLimit = tk.Button(self.frmLFig, text=' 境界面 ', command=self.SelectLogoLimit)
        self.btnLimit.place(x=120, y=140)

        tk.Frame(self.frmLogo, height=5).grid(row=3, column=0)

        self.frmLListTop =  tk.Frame(self.frmLogo, height=5)
        self.frmLListTop.grid(row=4, column=0, sticky='nwse')

        self.frmLListTop.rowconfigure(0, weight=1)
        self.frmLListTop.columnconfigure(0, weight=1)

        self.frmLList = tk.Frame( self.frmLListTop)
        self.frmLList.grid(row=0, column=0, sticky='nwse')
        self.frmLLCtrl = tk.Frame( self.frmLListTop)
        self.frmLLCtrl.grid(row=0, column=1, sticky='ns')
        self.frmLList.rowconfigure(0, weight=1)
        self.frmLList.columnconfigure(0, weight=1)

        self.treeLE = ttk.Treeview(self.frmLList, height=5)
        self.treeLE['column'] = (1)
        self.treeLE['show'] = 'headings'
        self.sorttreeLE = True
        self.treeLE.heading(1, text='登録名', anchor=tk.W, command=lambda : self.SortColumn(self.treeLE, 1, self.sorttreeLE))
        self.treeLE.grid(row=0, column=0, sticky='nwse')
        self.sbYL = ttk.Scrollbar(self.frmLList, orient=tk.VERTICAL, command=self.treeLE.yview)
        self.sbYL.grid(row=0, column=1, sticky='ns')
        self.treeLE.config(yscroll=self.sbYL.set)
        self.RestoretreeLE()
        self.treeLE.bind('<<TreeviewSelect>>', self.UpdateLogoButtonState) 

        self.iconLReview = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'review-24.png')), master=self.frmLLCtrl)
        self.bntReviewLE = tk.Button(self.frmLLCtrl, image=self.iconLReview, command=lambda: self.ReviewLGroup(self.treeLE))
        self.bntReviewLE.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconLDelete = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmLLCtrl)
        self.bntDeleteLE = tk.Button(self.frmLLCtrl, image=self.iconLDelete, command=self.DeleteLogoGroup)
        self.bntDeleteLE.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconLAdd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'add-24.png')), master=self.frmLLCtrl)
        self.bntAddLE = tk.Button(self.frmLLCtrl, image=self.iconLAdd, command=self.AddLogoGroup)
        self.bntAddLE.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.UpdateLogoButtonState(None)

        self.tpAddLE = tp.ToolTip(self.bntAddLE, text='選択した情報を追加します。', parent=self.master)
        self.tpDelLE = tp.ToolTip(self.bntDeleteLE, text='選択した行を削除します。', parent=self.master)
        self.tpRevLE = tp.ToolTip(self.bntReviewLE, text='選択した行を強調表示します。', parent=self.master)

    def AddLogoGroup(self):
        if not simlab.isGroupPresent(self.logoGuide):
            messagebox.showinfo('情報', '少なくともガイド面は選択してください。')
            return

        guides = simlab.getEntityFromGroup(self.logoGuide)
        limits = []
        if simlab.isGroupPresent(self.logoLimit):
            limits = simlab.getEntityFromGroup(self.logoLimit)

        importlib.reload(grouputil)
        logoGroup = grouputil.uniqueGroupName(LOGO_FACE)

        modelName = simlab.getModelName('CAD')

        if len(limits) == 0:
            # If there is no limit face, make guide face logo face.
            print('NO limits')
            simlablib.RenameGroup(self.logoGuide, logoGroup)
        else:
            tmpName = simlabutil.UniqueGroupName('_TEMP')
            simlablib.GetAdjacentFacesToLimitFaces(modelName, guides, limits, tmpName)
            if simlab.isGroupPresent(tmpName):
                # If adjacent face is found, make adjacent face logo face.
                print('Found Logo')
                simlablib.RenameGroup(tmpName, logoGroup)
            else:
                # If adjacent face is not found, make guide face logo face.
                print('Not Found Logo')
                simlablib.RenameGroup(self.logoGuide, logoGroup)

        simlablib.DeleteGroups([self.logoGuide, self.logoLimit])

        grouputil.createLogoMc()
        self.treeLE.insert('', 'end', values=(logoGroup))

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def DeleteLogoGroup(self):
        selectedRows = self.treeLE.selection()
        if len(selectedRows) == 0:
            messagebox.showinfo('情報','削除したい行を選択した後、ボタンを押下してください。')
            return

        for row in selectedRows:
            name = self.treeLE.item(row)['values'][0]
            simlablib.DeleteGroups([name])
            self.treeLE.delete(row)
        grouputil.createLogoMc()

    def UpdateLogoButtonState(self, event):
        selectedRows = self.treeLE.selection()
        state = 'normal'
        if len(selectedRows) == 0:
            state = 'disabled'
        
        for btn in [ self.bntDeleteLE, self.bntReviewLE ]:
            btn.config(state=state)

    def SelectLogoGuide(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','ガイド面を選択した後、[除去したい面のガイド面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.logoGuide)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Face', faces, self.logoGuide)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectLogoLimit(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','境界面を選択した後、[境界面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.logoLimit)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Face', faces, self.logoLimit)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def RestoretreeLE(self):
        for child in self.treeLE.get_children():
            self.treeLE.delete(child)

        groupNames = simlab.getGroupsWithSubString('FaceGroup', [LOGO_FACE + '*'])
        for groupName in groupNames:
            self.treeLE.insert('', 'end', values=(groupName))

    def ReviewLGroup(self, tree):
        selectedRows = tree.selection()
        if len(selectedRows) == 0:
            return
        
        simlabutil.ClearSelection()

        groups = []
        for row in selectedRows:
            name = tree.item(row)['values'][0]
            groups.append(name)        
        simlab.showOrHideEntities(groups, 'Show')

    ##
    # Bolt
    def CreateBolt(self):
        self.frmBolt.rowconfigure((2,4), weight=1)
        self.frmBolt.columnconfigure(0, weight=1)

        self.lblBoltNote = tk.Label(self.frmBolt, text='''Tips:  サーフェイスメッシュ作成で閾値以下の穴を簡略化します。
            閾値以下でも残したいボルト穴を、あらかじめ登録してください。''')
        self.lblBoltNote.grid(row=0, column=0, sticky='we')

        tk.Frame(self.frmBolt, height=5).grid(row=1, column=0)

        self.frmBoltFig = tk.Frame(self.frmBolt)
        self.frmBoltFig.grid(row=2, column=0, sticky='we') 

        self.iconBolt = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bolt_group.png')), master=self.frmBoltFig)
        tk.Label(self.frmBoltFig, image=self.iconBolt).pack(side=tk.TOP, anchor=tk.CENTER, padx=5)
        self.btnBolt = tk.Button(self.frmBoltFig, text=' ボルト穴面 ', command=self.SelectBolt)
        self.btnBolt.place(x=170, y=40)

        tk.Frame(self.frmBolt, height=5).grid(row=3, column=0)

        self.frmBoltListTop =  tk.Frame(self.frmBolt, height=5)
        self.frmBoltListTop.grid(row=4, column=0, sticky='nwse')

        self.frmBoltListTop.rowconfigure(0, weight=1)
        self.frmBoltListTop.columnconfigure(0, weight=1)

        self.frmBoltList = tk.Frame( self.frmBoltListTop)
        self.frmBoltList.grid(row=0, column=0, sticky='nwse')
        self.frmBoltLCtrl = tk.Frame( self.frmBoltListTop)
        self.frmBoltLCtrl.grid(row=0, column=1, sticky='ns')
        self.frmBoltList.rowconfigure(0, weight=1)
        self.frmBoltList.columnconfigure(0, weight=1)

        self.treeBolt = ttk.Treeview(self.frmBoltList, height=5)
        self.treeBolt['column'] = (1)
        self.treeBolt['show'] = 'headings'
        self.sorttreeBolt = True
        self.treeBolt.heading(1, text='登録名', anchor=tk.W, command=lambda : self.SortColumn(self.treeBolt, 1, self.sorttreeBolt))
        self.treeBolt.grid(row=0, column=0, sticky='nwse')
        self.sbYL = ttk.Scrollbar(self.frmBoltList, orient=tk.VERTICAL, command=self.treeBolt.yview)
        self.sbYL.grid(row=0, column=1, sticky='ns')
        self.treeBolt.config(yscroll=self.sbYL.set)
        self.RestoretreeBolt()
        self.treeBolt.bind('<<TreeviewSelect>>', self.UpdateBoltButtonState) 

        self.iconBoltReview = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'review-24.png')), master=self.frmBoltLCtrl)
        self.bntReviewBolt = tk.Button(self.frmBoltLCtrl, image=self.iconBoltReview, command=lambda: self.ReviewBoltGroup(self.treeBolt))
        self.bntReviewBolt.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconBoltDelete = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmBoltLCtrl)
        self.bntDeleteBolt = tk.Button(self.frmBoltLCtrl, image=self.iconBoltDelete, command=self.DeleteBoltGroup)
        self.bntDeleteBolt.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconBoltAdd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'add-24.png')), master=self.frmBoltLCtrl)
        self.bntAddBolt = tk.Button(self.frmBoltLCtrl, image=self.iconBoltAdd, command=self.AddBoltGroup)
        self.bntAddBolt.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.UpdateBoltButtonState(None)

        self.tpAddBolt = tp.ToolTip(self.bntAddBolt, text='選択した情報を追加します。', parent=self.master)
        self.tpDelBolt = tp.ToolTip(self.bntDeleteBolt, text='選択した行を削除します。', parent=self.master)
        self.tpRevBolt = tp.ToolTip(self.bntReviewBolt, text='選択した行を強調表示します。', parent=self.master)

    def AddBoltGroup(self):
        if not simlab.isGroupPresent(self.bolt):
            messagebox.showinfo('情報', 'ボルト穴面を選択後、押下してください。')
            return

        count = 1
        while simlab.isGroupPresent(BOLT_FACE + str(count)):
            count += 1
        boltGrpNm = BOLT_FACE + str(count)

        importlib.reload(grouputil)
        simlablib.RenameGroup(self.bolt, boltGrpNm)
        grouputil.persistentMeshCtrl(boltGrpNm, simlab.getEntityFromGroup(boltGrpNm))
        self.treeBolt.insert('', 'end', values=(boltGrpNm))

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def DeleteBoltGroup(self):
        selectedRows = self.treeBolt.selection()
        if len(selectedRows) == 0:
            messagebox.showinfo('情報','削除したい行を選択した後、ボタンを押下してください。')
            return

        for row in selectedRows:
            name = self.treeBolt.item(row)['values'][0]
            simlablib.DeleteGroups([name])
            self.treeBolt.delete(row)
        self.UpdateBoltButtonState(None)

    def UpdateBoltButtonState(self, event):
        selectedRows = self.treeBolt.selection()
        state = 'normal'
        if len(selectedRows) == 0:
            state = 'disabled'
        
        for btn in [ self.bntDeleteBolt, self.bntReviewBolt ]:
            btn.config(state=state)

    def RestoretreeBolt(self):
        for child in self.treeBolt.get_children():
            self.treeBolt.delete(child)

        groupNames = simlab.getGroupsWithSubString('FaceGroup', [BOLT_FACE + '*'])
        for groupName in groupNames:
            self.treeBolt.insert('', 'end', values=(groupName))

    def ReviewBoltGroup(self, tree):
        selectedRows = tree.selection()
        if len(selectedRows) == 0:
            return
        
        simlabutil.ClearSelection()

        groups = []
        for row in selectedRows:
            name = tree.item(row)['values'][0]
            groups.append(name)        
        simlab.showOrHideEntities(groups, 'Show')

    def SelectBolt(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','ボルト穴面を選択した後、[ボルト穴面] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.bolt)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Face', faces, self.bolt)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    ##
    # Trim
    def CreateTrim(self):
        self.frmTrim.rowconfigure((2,4), weight=1)
        self.frmTrim.columnconfigure(0, weight=1)

        self.lblTrimNote = tk.Label(self.frmTrim, text='Tips:  ボディの面を平面で分割します。分割されるボディと平面を規定する面を選択してください。')
        self.lblTrimNote.grid(row=0, column=0, sticky='we')

        tk.Frame(self.frmTrim, height=5).grid(row=1, column=0)

        self.frmTrimFig = tk.Frame(self.frmTrim)
        self.frmTrimFig.grid(row=2, column=0, sticky='we') 

        self.frmTrimFigCen = tk.Frame(self.frmTrimFig)
        self.frmTrimFigCen.pack(side=tk.TOP, anchor=tk.CENTER, padx=5)

        self.frmTrimFigLeft = tk.Frame(self.frmTrimFigCen)
        self.frmTrimFigLeft.pack(side=tk.LEFT, anchor=tk.W)

        self.iconTrim = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'trim.png')), master=self.frmTrimFig)
        tk.Label(self.frmTrimFigLeft, image=self.iconTrim).pack(side=tk.TOP, anchor=tk.CENTER, padx=5)
        self.btnTrimFace = tk.Button(self.frmTrimFigLeft, text=' 平面 ', command=self.SelectTrimFace)
        self.btnTrimFace.place(x=40, y=20)
        self.btnTrimBody = tk.Button(self.frmTrimFigLeft, text=' ボディ ', command=self.SelectTrimBody)
        self.btnTrimBody.place(x=40, y=160)

        self.frmTrimFigRight = tk.Frame(self.frmTrimFigCen)
        self.frmTrimFigRight.pack(side=tk.LEFT, anchor=tk.NW)
        tk.Label(self.frmTrimFigRight, text='選択タイプ:').pack(side=tk.TOP, anchor=tk.W)
        self.frmTrimFigRightType = tk.Frame(self.frmTrimFigRight)
        self.frmTrimFigRightType.pack(side=tk.TOP, anchor=tk.W, padx=5)        

        self.TrimSelType = tk.StringVar()
        self.TrimSelType.set('Plane')
        self.chkTrimSelPlane = tk.Radiobutton(self.frmTrimFigRightType, text='平面', value='Plane', variable=self.TrimSelType, command=self.SelectTrimSelType)
        self.chkTrimSelPlane.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.chkTrimSelArc = tk.Radiobutton(self.frmTrimFigRightType, text='円弧エッジ', value='Arc', variable=self.TrimSelType, command=self.SelectTrimSelType)
        self.chkTrimSelArc.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        tk.Frame(self.frmTrim, height=5).grid(row=3, column=0)

        self.frmTrimListTop =  tk.Frame(self.frmTrim, height=5)
        self.frmTrimListTop.grid(row=4, column=0, sticky='nwse')

        self.frmTrimListTop.rowconfigure(0, weight=1)
        self.frmTrimListTop.columnconfigure(0, weight=1)

        self.frmTrimList = tk.Frame( self.frmTrimListTop)
        self.frmTrimList.grid(row=0, column=0, sticky='nwse')
        self.frmTrimLCtrl = tk.Frame( self.frmTrimListTop)
        self.frmTrimLCtrl.grid(row=0, column=1, sticky='ns')
        self.frmTrimList.rowconfigure(0, weight=1)
        self.frmTrimList.columnconfigure(0, weight=1)

        self.treeTrim = ttk.Treeview(self.frmTrimList, height=5)
        self.treeTrim['column'] = (1)
        self.treeTrim['show'] = 'headings'
        self.sorttreeTrim = True
        self.treeTrim.heading(1, text='登録名', anchor=tk.W, command=lambda : self.SortColumn(self.treeTrim, 1, self.sorttreeTrim))
        self.treeTrim.grid(row=0, column=0, sticky='nwse')
        self.sbYL = ttk.Scrollbar(self.frmTrimList, orient=tk.VERTICAL, command=self.treeTrim.yview)
        self.sbYL.grid(row=0, column=1, sticky='ns')
        self.treeTrim.config(yscroll=self.sbYL.set)
        self.RestoretreeTrim()
        self.treeTrim.bind('<<TreeviewSelect>>', self.UpdateTrimButtonState) 

        self.iconTrimReview = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'review-24.png')), master=self.frmTrimLCtrl)
        self.bntReviewTrim = tk.Button(self.frmTrimLCtrl, image=self.iconTrimReview, command=lambda: self.ReviewTrimGroup(self.treeTrim))
        self.bntReviewTrim.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconTrimDelete = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmTrimLCtrl)
        self.bntDeleteTrim = tk.Button(self.frmTrimLCtrl, image=self.iconTrimDelete, command=self.DeleteTrimGroup)
        self.bntDeleteTrim.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconTrimAdd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'add-24.png')), master=self.frmTrimLCtrl)
        self.bntAddTrim = tk.Button(self.frmTrimLCtrl, image=self.iconTrimAdd, command=self.AddTrimGroup)
        self.bntAddTrim.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.UpdateTrimButtonState(None)

        self.tpAddTrim = tp.ToolTip(self.bntAddTrim, text='選択した情報を追加します。', parent=self.master)
        self.tpDelTrim = tp.ToolTip(self.bntDeleteTrim, text='選択した行を削除します。', parent=self.master)
        self.tpRevTrim = tp.ToolTip(self.bntReviewTrim, text='選択した行を強調表示します。', parent=self.master)

    def SelectTrimSelType(self):
        if self.TrimSelType.get() == 'Plane':
            self.btnTrimFace.config(text=' 平面 ', command=self.SelectTrimFace)
            simlab.setSelectionFilter('Face')
        else:
            self.btnTrimFace.config(text=' 円弧エッジ ', command=self.SelectTrimEdge)
            simlab.setSelectionFilter('Edge')

    def UpdateTrimButtonState(self, event):
        selectedRows = self.treeTrim.selection()
        state = 'normal'
        if len(selectedRows) == 0:
            state = 'disabled'
        
        for btn in [ self.bntDeleteTrim, self.bntReviewTrim ]:
            btn.config(state=state)

    def AddTrimGroup(self):
        groups = [self.trimBody, self.trimFace]
        for i in range(len(groups)):
            if not simlab.isGroupPresent(groups[i]):
                messagebox.showinfo('情報', '全ての面とボディを選択後、押下してください。')
                return
        
        count = self.GetMaxCountOfTrim()
        count += 1
        count = str(count)

        simlablib.RenameGroup(self.trimFace, TRIM_FACE + count)
        simlablib.RenameGroup(self.trimBody, TRIM_BODY + count)

        importlib.reload(grouputil)
        mcNm = "Trim_{}_MC".format(count)
        faceId1, faceId2 = simlab.getEntityFromGroup(TRIM_FACE + count)
        bodyNm = simlab.getBodiesFromGroup(TRIM_BODY + count)[0]
        meshProp = mcNm, bodyNm, faceId1, faceId2
        grouputil.createRegionMeshControl(meshProp)

        self.treeTrim.insert('', 'end', values=('Trimming_' + count))

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def GetMaxCountOfTrim(self):
        icount = 1
        while simlab.isGroupPresent(TRIM_FACE + str(icount)):
            icount += 1
        return icount - 1

    def DeleteTrimGroup(self):
        selectedRows = self.treeTrim.selection()
        if len(selectedRows) == 0:
            messagebox.showinfo('情報','削除したい行を選択した後、ボタンを押下してください。')
            return

        for row in selectedRows:
            name = self.treeTrim.item(row)['values'][0]
            items = name.split('_')
            count = items[-1]
            simlablib.DeleteGroups([TRIM_FACE+count, TRIM_BODY+count])
            simlablib.DeleteMeshControl("Trim_{}_MC".format(count))
            self.treeTrim.delete(row)

        self.UpdateTrimButtonState(None)

    def RestoretreeTrim(self):
        for child in self.treeTrim.get_children():
            self.treeTrim.delete(child)
        groupNames = []
        for groupType in ["FaceGroup", "EdgeGroup"]:
            trimGrp = list(simlab.getGroupsWithSubString(groupType, [TRIM_FACE + "*"]))
            groupNames.extend(trimGrp)
        for groupName in groupNames:
            count = groupName.split('_')[-1]
            self.treeTrim.insert('', 'end', values=('Trimming_' + count))

    def ReviewTrimGroup(self, tree):
        selectedRows = tree.selection()
        if len(selectedRows) == 0:
            return
        
        simlabutil.ClearSelection()

        groups = []
        for row in selectedRows:
            name = tree.item(row)['values'][0]
            items = name.split('_')
            count = items[-1]
            groups.append(TRIM_FACE+count)
        simlab.showOrHideEntities(groups, 'Show')

    def SelectTrimFace(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','平面を選択した後、[平面] ボタンを押下してください。')
            return
        
        if len(faces) != 2:
            messagebox.showinfo('情報','二つ平面を選択してください')
            return

        simlablib.DeleteGroups(self.trimFace)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Face', faces, self.trimFace)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectTrimEdge(self):
        edges = simlab.getSelectedEntities('EDGE')
        if len(edges) == 0:
            messagebox.showinfo('情報','円弧エッジを選択した後、[円弧エッジ] ボタンを押下してください。')
            return
        
        if len(edges) != 2:
            messagebox.showinfo('情報','二つ平面を選択してください')
            return

        simlablib.DeleteGroups(self.trimFace)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.trimFace)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectTrimBody(self):
        bodies = simlab.getSelectedBodies()
        if len(bodies) == 0:
            messagebox.showinfo('情報','ボディを選択した後、[ボディ] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.trimBody)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Body', bodies, self.trimBody)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    ##
    # Trim Mid
    def CreateTrimMid(self):
        self.frmTrimMid.rowconfigure((2,4), weight=1)
        self.frmTrimMid.columnconfigure(0, weight=1)

        self.lblTrimNote = tk.Label(self.frmTrimMid, text='Tips:  ボディの面を選択した両平面の中間で分割します。')
        self.lblTrimNote.grid(row=0, column=0, sticky='we')

        tk.Frame(self.frmTrimMid, height=5).grid(row=1, column=0)

        self.frmTrimMidFig = tk.Frame(self.frmTrimMid)
        self.frmTrimMidFig.grid(row=2, column=0, sticky='we') 

        self.frmTrimMidFigCen = tk.Frame(self.frmTrimMidFig)
        self.frmTrimMidFigCen.pack(side=tk.TOP, anchor=tk.CENTER, padx=5)

        self.frmTrimMidFigLeft = tk.Frame(self.frmTrimMidFigCen)
        self.frmTrimMidFigLeft.pack(side=tk.LEFT, anchor=tk.NW)

        self.iconTrimMid = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'trim2.png')), master=self.frmTrimMidFig)
        tk.Label(self.frmTrimMidFigLeft, image=self.iconTrimMid).pack(side=tk.TOP, anchor=tk.CENTER, padx=5)
        self.btnTrimMidFace = tk.Button(self.frmTrimMidFigLeft, text=' 平面 ', command=self.SelectTrimMidFace)
        self.btnTrimMidFace.place(x=135, y=30)
        self.btnTrimMidBody = tk.Button(self.frmTrimMidFigLeft, text=' ボディ ', command=self.SelectTrimMidBody)
        self.btnTrimMidBody.place(x=270, y=155)

        self.frmTrimMidFigRight = tk.Frame(self.frmTrimMidFigCen)
        self.frmTrimMidFigRight.pack(side=tk.LEFT, anchor=tk.NW)
        tk.Label(self.frmTrimMidFigRight, text='選択タイプ:').pack(side=tk.TOP, anchor=tk.W)
        self.frmTrimMidFigRightType = tk.Frame(self.frmTrimMidFigRight)
        self.frmTrimMidFigRightType.pack(side=tk.TOP, anchor=tk.W, padx=5)        

        self.TrimMidSelType = tk.StringVar()
        self.TrimMidSelType.set('Plane')
        self.chkTrimMidSelPlane = tk.Radiobutton(self.frmTrimMidFigRightType, text='平面', value='Plane', variable=self.TrimMidSelType, command=self.SelectTrimMidSelType)
        self.chkTrimMidSelPlane.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.chkTrimMidSelArc = tk.Radiobutton(self.frmTrimMidFigRightType, text='円弧エッジ', value='Arc', variable=self.TrimMidSelType, command=self.SelectTrimMidSelType)
        self.chkTrimMidSelArc.pack(side=tk.LEFT, anchor=tk.W, padx=5)

        tk.Frame(self.frmTrimMid, height=5).grid(row=3, column=0)

        self.frmTrimMidListTop =  tk.Frame(self.frmTrimMid, height=5)
        self.frmTrimMidListTop.grid(row=4, column=0, sticky='nwse')

        self.frmTrimMidListTop.rowconfigure(0, weight=1)
        self.frmTrimMidListTop.columnconfigure(0, weight=1)

        self.frmTrimMidList = tk.Frame( self.frmTrimMidListTop)
        self.frmTrimMidList.grid(row=0, column=0, sticky='nwse')
        self.frmTrimMidLCtrl = tk.Frame( self.frmTrimMidListTop)
        self.frmTrimMidLCtrl.grid(row=0, column=1, sticky='ns')
        self.frmTrimMidList.rowconfigure(0, weight=1)
        self.frmTrimMidList.columnconfigure(0, weight=1)

        self.treeTrimMid = ttk.Treeview(self.frmTrimMidList, height=5)
        self.treeTrimMid['column'] = (1)
        self.treeTrimMid['show'] = 'headings'
        self.sorttreeTrimMid = True
        self.treeTrimMid.heading(1, text='登録名', anchor=tk.W, command=lambda : self.SortColumn(self.treeTrimMid, 1, self.sorttreeTrimMid))
        self.treeTrimMid.grid(row=0, column=0, sticky='nwse')
        self.sbYLTrimMid = ttk.Scrollbar(self.frmTrimMidList, orient=tk.VERTICAL, command=self.treeTrimMid.yview)
        self.sbYLTrimMid.grid(row=0, column=1, sticky='ns')
        self.treeTrimMid.config(yscroll=self.sbYLTrimMid.set)
        self.RestoretreeTrimMid()
        self.treeTrimMid.bind('<<TreeviewSelect>>', self.UpdateTrimMidButtonState) 

        self.iconTrimMidReview = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'review-24.png')), master=self.frmTrimMidLCtrl)
        self.bntReviewTrimMid = tk.Button(self.frmTrimMidLCtrl, image=self.iconTrimMidReview, command=lambda: self.ReviewTrimMidGroup(self.treeTrimMid))
        self.bntReviewTrimMid.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconTrimMidDelete = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmTrimMidLCtrl)
        self.bntDeleteTrimMid = tk.Button(self.frmTrimMidLCtrl, image=self.iconTrimMidDelete, command=self.DeleteTrimMidGroup)
        self.bntDeleteTrimMid.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconTrimMidAdd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'add-24.png')), master=self.frmTrimMidLCtrl)
        self.bntAddTrimMid = tk.Button(self.frmTrimMidLCtrl, image=self.iconTrimMidAdd, command=self.AddTrimMidGroup)
        self.bntAddTrimMid.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.UpdateTrimMidButtonState(None)

        self.tpAddTrimMid = tp.ToolTip(self.bntAddTrimMid, text='選択した情報を追加します。', parent=self.master)
        self.tpDelTrimMid = tp.ToolTip(self.bntDeleteTrimMid, text='選択した行を削除します。', parent=self.master)
        self.tpRevTrimMid = tp.ToolTip(self.bntReviewTrimMid, text='選択した行を強調表示します。', parent=self.master)

    def SelectTrimMidSelType(self):
        if self.TrimMidSelType.get() == 'Plane':
            self.btnTrimMidFace.config(text=' 平面 ', command=self.SelectTrimMidFace)
            self.btnTrimMidFace.place(x=135, y=30)
            simlab.setSelectionFilter('Face')
        else:
            self.btnTrimMidFace.config(text=' 円弧エッジ ', command=self.SelectTrimMidEdge)
            self.btnTrimMidFace.place(x=125, y=30)
            simlab.setSelectionFilter('Edge')

    def UpdateTrimMidButtonState(self, event):
        selectedRows = self.treeTrimMid.selection()
        state = 'normal'
        if len(selectedRows) == 0:
            state = 'disabled'
        
        for btn in [ self.bntDeleteTrimMid, self.bntReviewTrimMid ]:
            btn.config(state=state)

    def AddTrimMidGroup(self):
        groups = [self.trimMidBody, self.trimMidFace]
        existGrpCount = 0
        for i in range(len(groups)):
            if simlab.isGroupPresent(groups[i]):
                existGrpCount += 1
        if not existGrpCount == 2:
            messagebox.showinfo('情報', '全ての面とボディを選択後、押下してください。')
            return
        
        count = self.GetMaxCountOfTrimMid()
        count += 1
        count = str(count)

        simlablib.RenameGroup(self.trimMidFace, TRIM_MID_FACE + count) 
        simlablib.RenameGroup(self.trimMidBody, TRIM_MID_BODY + count) 

        importlib.reload(grouputil)
  
        entity1, entity2 = simlab.getEntityFromGroup(TRIM_MID_FACE + count)
        
        bodyNm = simlab.getBodiesFromGroup(TRIM_MID_BODY + count)[0]
        mcNm = "TrimMid_{}_MC".format(count)
        meshProp = mcNm, bodyNm, entity1, entity2

        grouputil.createRegionMeshControl(meshProp, trimMid = True)
        self.treeTrimMid.insert('', 'end', values=('Trimming_mid_' + count))

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def GetMaxCountOfTrimMid(self):
        icount = 1
        while simlab.isGroupPresent(TRIM_MID_FACE + str(icount)) or simlab.isGroupPresent(TRIM_MID_EDGE + str(icount)):
            icount += 1
        return icount - 1

    def DeleteTrimMidGroup(self):
        selectedRows = self.treeTrimMid.selection()
        if len(selectedRows) == 0:
            messagebox.showinfo('情報','削除したい行を選択した後、ボタンを押下してください。')
            return

        for row in selectedRows:
            name = self.treeTrimMid.item(row)['values'][0]
            items = name.split('_')
            count = items[-1]
            simlablib.DeleteGroups([TRIM_MID_FACE+count, TRIM_MID_BODY+count])
            simlablib.DeleteMeshControl("TrimMid_{}_MC".format(count))
            self.treeTrimMid.delete(row)

        self.UpdateTrimMidButtonState(None)

    def RestoretreeTrimMid(self):
        for child in self.treeTrimMid.get_children():
            self.treeTrimMid.delete(child)

        groupNames = list(simlab.getGroupsWithSubString('FaceGroup', [TRIM_MID_FACE + '*']))
        for groupName in groupNames:
            count = groupName.split('_')[-1]
            self.treeTrimMid.insert('', 'end', values=('Trimming_mid_' + count))

    def ReviewTrimMidGroup(self, tree):
        selectedRows = tree.selection()
        if len(selectedRows) == 0:
            return
        
        simlabutil.ClearSelection()

        groups = []
        for row in selectedRows:
            name = tree.item(row)['values'][0]
            items = name.split('_')
            count = items[-1]
            groups.append(TRIM_MID_FACE+count)
        simlab.showOrHideEntities(groups, 'Show')

    def SelectTrimMidFace(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報','平面を選択した後、[平面] ボタンを押下してください。')
            return
        
        if len(faces) != 2:
            messagebox.showinfo("情報","二つ面を選択してください。")
            return
   
        importlib.reload(simlablib)
        simlablib.DeleteGroups(self.trimMidFace)
        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, "Face", faces, self.trimMidFace)
    
        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectTrimMidEdge(self):
        edges = simlab.getSelectedEntities('EDGE')
        if len(edges) == 0:
            messagebox.showinfo('情報','円弧エッジを選択した後、[円弧エッジ] ボタンを押下してください。')
            return
        
        if len(edges) != 2:
                messagebox.showinfo("情報","二つ円弧エッジを選択してください。")
                return

        simlablib.DeleteGroups(self.trimMidFace)
        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.trimMidFace)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectTrimMidBody(self):
        bodies = simlab.getSelectedBodies()
        if len(bodies) == 0:
            messagebox.showinfo('情報','ボディを選択した後、[ボディ] ボタンを押下してください。')
            return

        simlablib.DeleteGroups(self.trimMidBody)

        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Body', bodies, self.trimMidBody)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    ##
    # Body split
    def CreateBodyDiv(self):
        self.frmBodyDiv.rowconfigure((2,4), weight=1)
        self.frmBodyDiv.columnconfigure(0, weight=1)

        self.lblBodyDivNote = tk.Label(self.frmBodyDiv, text='Tips:  ボディを基準平面から指定した位置で分割します。')
        self.lblBodyDivNote.grid(row=0, column=0, sticky='we')

        tk.Frame(self.frmBodyDiv, height=5).grid(row=1, column=0)

        self.frmBodyDivFig = tk.Frame(self.frmBodyDiv)
        self.frmBodyDivFig.grid(row=2, column=0, sticky='we') 

        self.frmBodyDivFigCen = tk.Frame(self.frmBodyDivFig)
        self.frmBodyDivFigCen.pack(side=tk.TOP, anchor=tk.CENTER, padx=5)

        self.frmBodyDivFigLeft = tk.Frame(self.frmBodyDivFigCen)
        self.frmBodyDivFigLeft.pack(side=tk.LEFT, anchor=tk.NW)

        self.iconBodyDiv1 = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'body_div1.png')), master=self.frmBodyDivFig)
        tk.Label(self.frmBodyDivFigLeft, image=self.iconBodyDiv1).pack(side=tk.LEFT, anchor=tk.W)
        self.btnBodyDivFace = tk.Button(self.frmBodyDivFigLeft, text=' 基準平面 ', command=self.SelectBodyDivFace)
        self.btnBodyDivFace.place(x=160, y=50)

        self.iconBodyDiv2 = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'body_div2.png')), master=self.frmBodyDivFig)
        tk.Label(self.frmBodyDivFigLeft, image=self.iconBodyDiv2).pack(side=tk.LEFT, anchor=tk.W)

        self.entBodyDivLength = tk.Entry(self.frmBodyDivFigLeft, width=7)
        self.entBodyDivLength.place(x=360, y=35)
        self.entBodyDivLength.insert(tk.END, 100)

        tk.Frame(self.frmBodyDiv, height=5).grid(row=3, column=0)

        self.frmBodyDivListTop =  tk.Frame(self.frmBodyDiv, height=5)
        self.frmBodyDivListTop.grid(row=4, column=0, sticky='nwse')

        self.frmBodyDivListTop.rowconfigure(0, weight=1)
        self.frmBodyDivListTop.columnconfigure(0, weight=1)

        self.frmBodyDivList = tk.Frame( self.frmBodyDivListTop)
        self.frmBodyDivList.grid(row=0, column=0, sticky='nwse')
        self.frmBodyDivLCtrl = tk.Frame( self.frmBodyDivListTop)
        self.frmBodyDivLCtrl.grid(row=0, column=1, sticky='ns')
        self.frmBodyDivList.rowconfigure(0, weight=1)
        self.frmBodyDivList.columnconfigure(0, weight=1)

        self.treeBodyDiv = ttk.Treeview(self.frmBodyDivList, height=5)
        self.treeBodyDiv['column'] = (1)
        self.treeBodyDiv['show'] = 'headings'
        self.sorttreeBodyDiv = True
        self.treeBodyDiv.heading(1, text='登録名', anchor=tk.W, command=lambda : self.SortColumn(self.treeBodyDiv, 1, self.sorttreeBodyDiv))
        self.treeBodyDiv.grid(row=0, column=0, sticky='nwse')
        self.sbYLBodyDiv = ttk.Scrollbar(self.frmBodyDivList, orient=tk.VERTICAL, command=self.treeBodyDiv.yview)
        self.sbYLBodyDiv.grid(row=0, column=1, sticky='ns')
        self.treeBodyDiv.config(yscroll=self.sbYLBodyDiv.set)
        self.RestoretreeBodyDiv()
        self.treeBodyDiv.bind('<<TreeviewSelect>>', self.UpdateBodyDivButtonState) 

        self.iconBodyDivReview = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'review-24.png')), master=self.frmBodyDivLCtrl)
        self.bntReviewBodyDiv = tk.Button(self.frmBodyDivLCtrl, image=self.iconBodyDivReview, command=lambda: self.ReviewBodyDivGroup(self.treeBodyDiv))
        self.bntReviewBodyDiv.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconBodyDivDelete = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmBodyDivLCtrl)
        self.bntDeleteBodyDiv = tk.Button(self.frmBodyDivLCtrl, image=self.iconBodyDivDelete, command=self.DeleteBodyDivGroup)
        self.bntDeleteBodyDiv.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconBodyDivAdd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'add-24.png')), master=self.frmBodyDivLCtrl)
        self.bntAddBodyDiv = tk.Button(self.frmBodyDivLCtrl, image=self.iconBodyDivAdd, command=self.AddBodyDivGroup)
        self.bntAddBodyDiv.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.UpdateBodyDivButtonState(None)

        self.tpAddBodyDiv = tp.ToolTip(self.bntAddBodyDiv, text='選択した情報を追加します。', parent=self.master)
        self.tpDelBodyDiv = tp.ToolTip(self.bntDeleteBodyDiv, text='選択した行を削除します。', parent=self.master)
        self.tpRevBodyDiv = tp.ToolTip(self.bntReviewBodyDiv, text='選択した行を強調表示します。', parent=self.master)

    def UpdateBodyDivButtonState(self, event):
        selectedRows = self.treeBodyDiv.selection()
        state = 'normal'
        if len(selectedRows) == 0:
            state = 'disabled'
        
        for btn in [ self.bntDeleteBodyDiv, self.bntReviewBodyDiv ]:
            btn.config(state=state)

    def AddBodyDivGroup(self):
        if not simlab.isGroupPresent(self.bodyDivFace):
            messagebox.showinfo('情報', '平面を選択してください。')
            return

        try:
            length = float(self.entBodyDivLength.get())
        except:
            messagebox.showinfo('情報', '実数で指定してください。')
            return

        modelName = simlab.getModelName('CAD')
        planeFace = simlab.getEntityFromGroup(self.bodyDivFace)[0]
        bodyGrpName = simlabutil.UniqueGroupName('_TempBodyGrp')
        simlablib.SelectAssociatedEntities(modelName, 'Face', [planeFace], 'Body', bodyGrpName)
        body = simlab.getBodiesFromGroup(bodyGrpName)[0]
        simlablib.DeleteGroups(bodyGrpName)
        bodies = simlab.getBodiesWithSubString(modelName, [body])
        if len(bodies) > 1:
            answer = messagebox.askokcancel('情報', '同名のボディが複数存在します。\n全ての同名ボディが指定の平面で分割されます。\n\n同名ボディを1ボディずつ分割したい場合は、SimLab の Mesh Controls から Region を使って分割してください。\n\n処理を続けますか？')
            if not answer:
                return
        
        count = self.GetMaxCountOfBodyDiv()
        count += 1
        count = str(count)

        if simlab.isGroupPresent(self.bodyDivFace):
             simlablib.RenameGroup(self.bodyDivFace, BODY_SPLIT_FACE + count)
        planeFace = simlab.getEntityFromGroup(BODY_SPLIT_FACE + count)[0]

        importlib.reload(grouputil)
        mcNm = "Body_Split_{}_MC".format(count)
        grouputil.createBodySplitMeshControl(mcNm, planeFace, length)

        self.treeBodyDiv.insert('', 'end', values=('Body_split_' + count))

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def GetMaxCountOfBodyDiv(self):
        icount = 1
        while simlab.isGroupPresent(BODY_SPLIT_FACE + str(icount)):
            icount += 1
        return icount - 1

    def DeleteBodyDivGroup(self):
        selectedRows = self.treeBodyDiv.selection()
        if len(selectedRows) == 0:
            messagebox.showinfo('情報','削除したい行を選択した後、ボタンを押下してください。')
            return

        for row in selectedRows:
            name = self.treeBodyDiv.item(row)['values'][0]
            items = name.split('_')
            count = items[-1]
            simlablib.DeleteGroups([BODY_SPLIT_FACE + count])
            simlablib.DeleteMeshControl("Body_Split_{}_MC".format(count))
            self.treeBodyDiv.delete(row)

        self.UpdateBodyDivButtonState(None)

    def RestoretreeBodyDiv(self):
        for child in self.treeBodyDiv.get_children():
            self.treeBodyDiv.delete(child)

        groupNames = list(simlab.getGroupsWithSubString('FaceGroup', [BODY_SPLIT_FACE + '*']))
        for groupName in groupNames:
            count = groupName.split('_')[-1]
            self.treeBodyDiv.insert('', 'end', values=('Body_split_' + count))

    def ReviewBodyDivGroup(self, tree):
        selectedRows = tree.selection()
        if len(selectedRows) == 0:
            return
        
        simlabutil.ClearSelection()

        groups = []
        for row in selectedRows:
            name = tree.item(row)['values'][0]
            items = name.split('_')
            count = items[-1]
            groups.append(BODY_SPLIT_FACE + count)
        simlab.showOrHideEntities(groups, 'Show')

    def SelectBodyDivFace(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) != 1:
            messagebox.showinfo('情報','１面の平面を選択した後、ボタンを押下してください。')
            return
        
        face = faces[0]
        simlablib.DeleteGroups(self.bodyDivFace)

        modelName = simlab.getModelName('CAD')
        result = simlab.definePlaneFromEntity(modelName, face)
        if len(result) == 0:
            messagebox.showinfo('情報','平面情報が取れません。平面を選択してください。')
            return

        simlablib.CreateGroup(modelName, 'Face', [face], self.bodyDivFace)
    
        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    ##
    # Merge face
    def CreateMergeFace(self):
        self.frmMergeFace.rowconfigure((2), weight=1)
        self.frmMergeFace.columnconfigure(0, weight=1)

        self.lblMergeFaceNote = tk.Label(self.frmMergeFace, text='Tips:  結合したい面群を選択して[+]を押してください。')
        self.lblMergeFaceNote.grid(row=0, column=0, sticky='we')

        tk.Frame(self.frmMergeFace, height=5).grid(row=1, column=0)

        self.frmMergeFaceListTop =  tk.Frame(self.frmMergeFace, height=5)
        self.frmMergeFaceListTop.grid(row=2, column=0, sticky='nwse')

        self.frmMergeFaceListTop.rowconfigure(0, weight=1)
        self.frmMergeFaceListTop.columnconfigure(0, weight=1)

        self.frmMergeFaceList = tk.Frame( self.frmMergeFaceListTop)
        self.frmMergeFaceList.grid(row=0, column=0, sticky='nwse')
        self.frmMergeFaceLCtrl = tk.Frame( self.frmMergeFaceListTop)
        self.frmMergeFaceLCtrl.grid(row=0, column=1, sticky='ns')
        self.frmMergeFaceList.rowconfigure(0, weight=1)
        self.frmMergeFaceList.columnconfigure(0, weight=1)

        self.treeMergeFace = ttk.Treeview(self.frmMergeFaceList, height=5)
        self.treeMergeFace['column'] = (1)
        self.treeMergeFace['show'] = 'headings'
        self.sorttreeMergeFace = True
        self.treeMergeFace.heading(1, text='登録名', anchor=tk.W, command=lambda : self.SortColumn(self.treeMergeFace, 1, self.sorttreeMergeFace))
        self.treeMergeFace.grid(row=0, column=0, sticky='nwse')
        self.sbYLMergeFace = ttk.Scrollbar(self.frmMergeFaceList, orient=tk.VERTICAL, command=self.treeMergeFace.yview)
        self.sbYLMergeFace.grid(row=0, column=1, sticky='ns')
        self.treeMergeFace.config(yscroll=self.sbYLMergeFace.set)
        self.RestoretreeMergeFace()
        self.treeMergeFace.bind('<<TreeviewSelect>>', self.UpdateMergeFaceButtonState) 

        self.iconMergeFaceReview = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'review-24.png')), master=self.frmMergeFaceLCtrl)
        self.bntReviewMergeFace = tk.Button(self.frmMergeFaceLCtrl, image=self.iconMergeFaceReview, command=lambda: self.ReviewMergeFaceGroup(self.treeMergeFace))
        self.bntReviewMergeFace.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconMergeFaceDelete = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmMergeFaceLCtrl)
        self.bntDeleteMergeFace = tk.Button(self.frmMergeFaceLCtrl, image=self.iconMergeFaceDelete, command=self.DeleteMergeFaceGroup)
        self.bntDeleteMergeFace.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconMergeFaceAdd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'add-24.png')), master=self.frmMergeFaceLCtrl)
        self.bntAddMergeFace = tk.Button(self.frmMergeFaceLCtrl, image=self.iconMergeFaceAdd, command=self.AddMergeFaceGroup)
        self.bntAddMergeFace.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.UpdateMergeFaceButtonState(None)

        self.tpAddMergeFace = tp.ToolTip(self.bntAddMergeFace, text='選択した情報を追加します。', parent=self.master)
        self.tpDelMergeFace = tp.ToolTip(self.bntDeleteMergeFace, text='選択した行を削除します。', parent=self.master)
        self.tpRevMergeFace = tp.ToolTip(self.bntReviewMergeFace, text='選択した行を強調表示します。', parent=self.master)

    def UpdateMergeFaceButtonState(self, event):
        selectedRows = self.treeMergeFace.selection()
        state = 'normal'
        if len(selectedRows) == 0:
            state = 'disabled'
        
        for btn in [ self.bntDeleteMergeFace, self.bntReviewMergeFace ]:
            btn.config(state=state)

    def AddMergeFaceGroup(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報', '面を選択してください。')
            return
        
        count = self.GetMaxCountOfMergeFace()
        count += 1
        count = str(count)

        groupName = MERGE_FACE + str(count)
        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Face', faces, groupName)

        self.treeMergeFace.insert('', 'end', values=(MERGE_FACE + count))

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def GetMaxCountOfMergeFace(self):
        icount = 1
        while simlab.isGroupPresent(MERGE_FACE + str(icount)):
            icount += 1
        return icount - 1

    def DeleteMergeFaceGroup(self):
        selectedRows = self.treeMergeFace.selection()
        if len(selectedRows) == 0:
            messagebox.showinfo('情報','削除したい行を選択した後、ボタンを押下してください。')
            return

        for row in selectedRows:
            name = self.treeMergeFace.item(row)['values'][0]
            simlablib.DeleteGroups(name)
            self.treeMergeFace.delete(row)

        self.UpdateMergeFaceButtonState(None)

    def RestoretreeMergeFace(self):
        for child in self.treeMergeFace.get_children():
            self.treeMergeFace.delete(child)

        groupNames = list(simlab.getGroupsWithSubString('FaceGroup', [MERGE_FACE + '*']))
        for groupName in groupNames:
            self.treeMergeFace.insert('', 'end', values=(groupName))

    def ReviewMergeFaceGroup(self, tree):
        selectedRows = tree.selection()
        if len(selectedRows) == 0:
            return
        
        simlabutil.ClearSelection()

        groups = []
        for row in selectedRows:
            name = tree.item(row)['values'][0]
            groups.append(name)
        simlab.showOrHideEntities(groups, 'Show')

    ##
    # Preserve face
    def CreatePreserveFace(self):
        self.frmPreserveFace.rowconfigure((2), weight=1)
        self.frmPreserveFace.columnconfigure(0, weight=1)

        self.lblPreserveFaceNote = tk.Label(self.frmPreserveFace, text='Tips:  面の形状を保持したい面群を選択して[+]を押してください。')
        self.lblPreserveFaceNote.grid(row=0, column=0, sticky='we')

        tk.Frame(self.frmPreserveFace, height=5).grid(row=1, column=0)

        self.frmPreserveFaceListTop =  tk.Frame(self.frmPreserveFace, height=5)
        self.frmPreserveFaceListTop.grid(row=2, column=0, sticky='nwse')

        self.frmPreserveFaceListTop.rowconfigure(0, weight=1)
        self.frmPreserveFaceListTop.columnconfigure(0, weight=1)

        self.frmPreserveFaceList = tk.Frame( self.frmPreserveFaceListTop)
        self.frmPreserveFaceList.grid(row=0, column=0, sticky='nwse')
        self.frmPreserveFaceLCtrl = tk.Frame( self.frmPreserveFaceListTop)
        self.frmPreserveFaceLCtrl.grid(row=0, column=1, sticky='ns')
        self.frmPreserveFaceList.rowconfigure(0, weight=1)
        self.frmPreserveFaceList.columnconfigure(0, weight=1)

        self.treePreserveFace = ttk.Treeview(self.frmPreserveFaceList, height=5)
        self.treePreserveFace['column'] = (1)
        self.treePreserveFace['show'] = 'headings'
        self.sorttreePreserveFace = True
        self.treePreserveFace.heading(1, text='登録名', anchor=tk.W, command=lambda : self.SortColumn(self.treePreserveFace, 1, self.sorttreePreserveFace))
        self.treePreserveFace.grid(row=0, column=0, sticky='nwse')
        self.sbYLPreserveFace = ttk.Scrollbar(self.frmPreserveFaceList, orient=tk.VERTICAL, command=self.treePreserveFace.yview)
        self.sbYLPreserveFace.grid(row=0, column=1, sticky='ns')
        self.treePreserveFace.config(yscroll=self.sbYLPreserveFace.set)
        self.RestoretreePreserveFace()
        self.treePreserveFace.bind('<<TreeviewSelect>>', self.UpdatePreserveFaceButtonState) 

        self.iconPreserveFaceReview = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'review-24.png')), master=self.frmPreserveFaceLCtrl)
        self.bntReviewPreserveFace = tk.Button(self.frmPreserveFaceLCtrl, image=self.iconPreserveFaceReview, command=lambda: self.ReviewPreserveFaceGroup(self.treePreserveFace))
        self.bntReviewPreserveFace.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconPreserveFaceDelete = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'delete-24.png')), master=self.frmPreserveFaceLCtrl)
        self.bntDeletePreserveFace = tk.Button(self.frmPreserveFaceLCtrl, image=self.iconPreserveFaceDelete, command=self.DeletePreserveFaceGroup)
        self.bntDeletePreserveFace.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.iconPreserveFaceAdd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'add-24.png')), master=self.frmPreserveFaceLCtrl)
        self.bntAddPreserveFace = tk.Button(self.frmPreserveFaceLCtrl, image=self.iconPreserveFaceAdd, command=self.AddPreserveFaceGroup)
        self.bntAddPreserveFace.pack(side=tk.BOTTOM, anchor=tk.NW, expand=0)
        self.UpdatePreserveFaceButtonState(None)

        self.tpAddPreserveFace = tp.ToolTip(self.bntAddPreserveFace, text='選択した情報を追加します。', parent=self.master)
        self.tpDelPreserveFace = tp.ToolTip(self.bntDeletePreserveFace, text='選択した行を削除します。', parent=self.master)
        self.tpRevPreserveFace = tp.ToolTip(self.bntReviewPreserveFace, text='選択した行を強調表示します。', parent=self.master)

    def UpdatePreserveFaceButtonState(self, event):
        selectedRows = self.treePreserveFace.selection()
        state = 'normal'
        if len(selectedRows) == 0:
            state = 'disabled'
        
        for btn in [ self.bntDeletePreserveFace, self.bntReviewPreserveFace ]:
            btn.config(state=state)

    def AddPreserveFaceGroup(self):
        faces = simlab.getSelectedEntities('FACE')
        if len(faces) == 0:
            messagebox.showinfo('情報', '面を選択してください。')
            return
        
        count = self.GetMaxCountOfPreserveFace()
        count += 1
        count = str(count)

        groupName = PRESERVE_FACE + str(count)
        modelName = simlab.getModelName('CAD')
        simlablib.CreateGroup(modelName, 'Face', faces, groupName)

        self.treePreserveFace.insert('', 'end', values=(groupName))

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def GetMaxCountOfPreserveFace(self):
        icount = 1
        while simlab.isGroupPresent(PRESERVE_FACE + str(icount)):
            icount += 1
        return icount - 1

    def DeletePreserveFaceGroup(self):
        selectedRows = self.treePreserveFace.selection()
        if len(selectedRows) == 0:
            messagebox.showinfo('情報','削除したい行を選択した後、ボタンを押下してください。')
            return

        for row in selectedRows:
            name = self.treePreserveFace.item(row)['values'][0]
            simlablib.DeleteGroups(name)
            self.treePreserveFace.delete(row)

        self.UpdatePreserveFaceButtonState(None)

    def RestoretreePreserveFace(self):
        for child in self.treePreserveFace.get_children():
            self.treePreserveFace.delete(child)

        groupNames = list(simlab.getGroupsWithSubString('FaceGroup', [PRESERVE_FACE + '*']))
        for groupName in groupNames:
            self.treePreserveFace.insert('', 'end', values=(groupName))

    def ReviewPreserveFaceGroup(self, tree):
        selectedRows = tree.selection()
        if len(selectedRows) == 0:
            return
        
        simlabutil.ClearSelection()

        groups = []
        for row in selectedRows:
            name = tree.item(row)['values'][0]
            groups.append(name)
        simlab.showOrHideEntities(groups, 'Show')

    def UpdateButtonFG(self):
        groups = [self.bearingEdgeFace, self.bearingAxisBody, self.bearingOuter, self.washerEdge, self.logoGuide, self.logoLimit, self.bolt, self.trimFace, self.trimBody, self.trimMidFace, self.trimMidBody, self.bodyDivFace]
        widgets = [self.btnEdgeFace, self.btnBody, self.btnOuter, self.btnWasherEdge, self.btnGuide, self.btnLimit, self.btnBolt, self.btnTrimFace, self.btnTrimBody, self.btnTrimMidFace, self.btnTrimMidBody, self.btnBodyDivFace]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)       

    def CloseDialog(self):
        simlablib.DeleteGroups([self.bearingEdgeFace, self.bearingAxisBody, self.bearingOuter, self.washerEdge, self.logoGuide, self.logoLimit, self.bolt, self.trimFace, self.trimBody, self.trimMidFace, self.trimMidBody, self.bodyDivFace])
        simlabutil.ClearSelection()
        super().CloseDialog()