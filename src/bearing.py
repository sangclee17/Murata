import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from hwx import simlab
import os, sys, importlib
from PIL import Image, ImageTk
import re

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = os.path.join(PROJECT_DIR,'log')
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

# local import
import basedialog
import simlabutil
import simlablib
import tooltip as tp
import backup
import springcsv
import messageboxWithCheckbox as mc
import bearingutil
import muratautil
import coordinate

class BearingDlg(basedialog.BaseDialog):
    def __init__(self, master, parent, backup, springs):
        super().__init__(master, parent)
        self.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.backup = backup
        self.springs = springs

        self.InnerEdge = '_Shell_Bearing_Inner'
        self.OuterEdge = '_Shell_Bearing_Outer'
        self.bearingBody = '_Shell_Bearing_Body'
        self.shlPageIndex = 0

        self.SolidOuterEdge = '_Bearing_Outer'
        self.SolidInnerEdge = '_Bearing_Inner'

        self.master.title('ベアリング作成')
        self.CreateWidgets()

        self.UpdateShlWidgets()
        simlabutil.ClearSelection()

    def CreateWidgets(self):
        self.frmTop = tk.Frame(self)
        self.frmTop.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=5, pady=5)

        self.nb = ttk.Notebook(self.frmTop)
        self.frmShell = tk.Frame(self.nb)
        self.frmSolid = tk.Frame(self.nb)
        self.nb.add(self.frmShell, text=' シェル ')
        self.nb.add(self.frmSolid, text=' ソリッド ')
        self.nb.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.CreateShellTab()
        self.CreateSolidTab()

        self.frmCtrl = tk.Frame(self.frmTop)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5)

        btnWidth = 10
        self.btnClose = tk.Button(self.frmCtrl, text=' 閉じる ', compound=tk.RIGHT, command=self.CloseDialog, width=btnWidth)
        self.btnClose.pack(side=tk.RIGHT, anchor=tk.NE)

    def CreateShellTab(self):
        self.frmShellSel = tk.Frame(self.frmShell)
        self.frmShellSel.pack(side=tk.TOP, anchor=tk.CENTER, expand=0, fill=tk.X, padx=5, pady=5)

        # for width
        self.frmShellWd = tk.Frame(self.frmShellSel)
        self.frmShellWd.pack(side=tk.TOP, anchor=tk.CENTER, expand=0, fill=tk.X)
        self.lblNote1 = tk.Label(self.frmShellWd, text='Tips: ベアリングの元ボディと幅を規定する円弧エッジを選択してください。')
        self.lblNote1.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconWd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bearing_shell1.png')), master=self.frmShellWd)
        tk.Label(self.frmShellWd, image=self.iconWd).pack(side=tk.TOP, anchor=tk.CENTER)
        self.btnShellInnerArc = tk.Button(self.frmShellWd, text='内径円筒エッジ', command=self.SelectInnterArcEdge)
        self.btnShellInnerArc.place(x=140, y=30)

        # for radius
        self.frmShellRd = tk.Frame(self.frmShellSel)
        self.lblNote2 = tk.Label(self.frmShellRd, text='Tips: 径を規定する円弧をそれぞれ選択して、ボタンを押してください。')
        self.lblNote2.pack(side=tk.TOP, anchor=tk.CENTER)

        self.frmShellSub = tk.Frame(self.frmShellRd)
        self.frmShellSub.pack(side=tk.TOP, anchor=tk.CENTER)

        self.iconRd = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'bearing_shell2.png')), master=self.frmShellRd)
        tk.Label(self.frmShellSub, image=self.iconRd).pack(side=tk.LEFT, anchor=tk.NW)
        self.btnShellOuterArc = tk.Button(self.frmShellSub, text='外径円筒エッジ', command=self.SelectOuterArcEdge)
        self.btnShellOuterArc.place(x=20, y=45)

        tk.Frame(self.frmShellSub, width=5).pack(side=tk.LEFT, anchor=tk.W)

        self.frmShellVal = tk.Frame(self.frmShellSub)
        self.frmShellVal.pack(side=tk.LEFT, anchor=tk.W, expand=1, fill=tk.BOTH, padx=5)

        self.frmShlBearingBody = tk.Frame(self.frmShellVal)
        self.frmShlBearingBody.pack(side=tk.TOP, anchor=tk.W)
        tk.Label(self.frmShlBearingBody, text='ベアリングのソリッドボディ:').pack(side=tk.LEFT, anchor=tk.W)
        self.btnShlBearingBody = tk.Button(self.frmShlBearingBody, text='ボディ', width=10, command=self.SelectBearingBody)
        self.btnShlBearingBody.pack(side=tk.LEFT, anchor=tk.W)

        tk.Frame(self.frmShellVal, height=5).pack(side=tk.TOP, anchor=tk.W)

        self.frmShlBearingNum = tk.LabelFrame(self.frmShellVal, text='要素分割数:')
        self.frmShlBearingNum.pack(side=tk.TOP, anchor=tk.W, expand=0, fill=tk.X)

        self.frmShlBearingValAxis = tk.Frame(self.frmShlBearingNum)
        self.frmShlBearingValAxis.pack(side=tk.TOP, anchor=tk.W, padx=5,pady=2)
        tk.Label(self.frmShlBearingValAxis, text='軸方向:').pack(side=tk.LEFT, anchor=tk.W)
        self.entShlBearingNumAxis = tk.Entry(self.frmShlBearingValAxis, width=5)
        self.entShlBearingNumAxis.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entShlBearingNumAxis.insert(tk.END, 4)

        self.frmShlBearingValAng = tk.Frame(self.frmShlBearingNum)
        self.frmShlBearingValAng.pack(side=tk.TOP, anchor=tk.W, padx=5,pady=2)
        tk.Label(self.frmShlBearingValAng, text='周方向:').pack(side=tk.LEFT, anchor=tk.W)
        self.shlBearingNumAngle = tk.IntVar()
        self.shlBearingNumAngle.set(32)
        self.cmbShlBearingNumAngle = ttk.Combobox(self.frmShlBearingValAng, width=3, state='readonly', values=[24,32,36], textvariable=self.shlBearingNumAngle)
        self.cmbShlBearingNumAngle.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        tk.Frame(self.frmShlBearingNum, height=5).pack(side=tk.TOP, anchor=tk.W)

        tk.Frame(self.frmShellVal, height=5).pack(side=tk.TOP, anchor=tk.W)

        self.frmShlBearingSp = tk.LabelFrame(self.frmShellVal, text='バネ要素:')
        self.frmShlBearingSp.pack(side=tk.TOP, anchor=tk.W, expand=0, fill=tk.X)

        self.frmShlBearingSpNum = tk.Frame(self.frmShlBearingSp)
        self.frmShlBearingSpNum.pack(side=tk.TOP, anchor=tk.W, padx=5,pady=2)
        tk.Label(self.frmShlBearingSpNum, text='バネの数:').pack(side=tk.LEFT, anchor=tk.W)
        self.entShlBearingNumSpring = tk.Entry(self.frmShlBearingSpNum, width=5)
        self.entShlBearingNumSpring.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entShlBearingNumSpring.insert(tk.END, 10)

        tk.Frame(self.frmShlBearingSp, height=5).pack(side=tk.TOP, anchor=tk.W)

        self.frmShlCoord = tk.Frame(self.frmShlBearingSp)
        self.frmShlCoord.pack(side=tk.TOP, anchor=tk.W, padx=5,pady=2)
        self.lblShlCoord = tk.Label(self.frmShlCoord, text='座標系 : ')
        self.lblShlCoord.pack(side=tk.LEFT, anchor=tk.W)

        coords = coordinate.GetAllCoordinates()
        self.shlCoord = tk.StringVar()
        if len(coords) != 0:
            self.shlCoord.set(coords[0])
        self.cmbShlCoords = ttk.Combobox(self.frmShlCoord, values=coords, textvariable=self.shlCoord, width=20, state='readonly')
        self.cmbShlCoords.pack(side=tk.LEFT, anchor=tk.W)

        self.frmShlBearingSpStiff = tk.LabelFrame(self.frmShlBearingSp, text='剛性:')
        self.frmShlBearingSpStiff.pack(side=tk.TOP, anchor=tk.W, padx=5)

        self.frmSprintType = tk.Frame(self.frmShlBearingSpStiff)
        self.frmSprintType.pack(side=tk.TOP, anchor=tk.NW)

        self.shlSpringType = tk.StringVar()
        self.cmbShlSpringType = ttk.Combobox(self.frmSprintType, width=18, state='readonly', values=[], textvariable=self.shlSpringType)
        self.cmbShlSpringType.pack(side=tk.LEFT, anchor=tk.W)
        self.cmbShlSpringType.bind('<<ComboboxSelected>>' , self.springs.Select)

        tk.Frame(self.frmShlBearingSpStiff, height=5).pack(side=tk.TOP, anchor=tk.W)

        self.frmShlBearingSpStiffR = tk.Frame(self.frmShlBearingSpStiff)
        self.frmShlBearingSpStiffR.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmShlBearingSpStiffR, text='R:').pack(side=tk.LEFT, anchor=tk.W)        
        self.entShlBearingSpStiffR = tk.Entry(self.frmShlBearingSpStiffR, width=10)
        self.entShlBearingSpStiffR.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entShlBearingSpStiffR.insert(tk.END, 0.0)

        self.frmShlBearingSpStiffT = tk.Frame(self.frmShlBearingSpStiff)
        self.frmShlBearingSpStiffT.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmShlBearingSpStiffT, text='θ:').pack(side=tk.LEFT, anchor=tk.W)        
        self.entShlBearingSpStiffT = tk.Entry(self.frmShlBearingSpStiffT, width=10)
        self.entShlBearingSpStiffT.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entShlBearingSpStiffT.insert(tk.END, 0.0)

        self.frmShlBearingSpStiffZ = tk.Frame(self.frmShlBearingSpStiff)
        self.frmShlBearingSpStiffZ.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmShlBearingSpStiffZ, text='Z:').pack(side=tk.LEFT, anchor=tk.W)        
        self.entShlBearingSpStiffZ = tk.Entry(self.frmShlBearingSpStiffZ, width=10)
        self.entShlBearingSpStiffZ.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entShlBearingSpStiffZ.insert(tk.END, 0.0)

        self.springs.AppendWidget(self.cmbShlSpringType, self.shlSpringType, self.entShlBearingSpStiffR, self.entShlBearingSpStiffT, self.entShlBearingSpStiffZ)

        tk.Frame(self.frmShlBearingSp, height=5).pack(side=tk.TOP, anchor=tk.W)

        # prev,next
        self.frmShlSelCtrl = tk.Frame(self.frmShell)
        self.frmShlSelCtrl.pack(side=tk.TOP, anchor=tk.CENTER, expand=0, fill=tk.X)
        self.frmShlSelBtn = tk.Frame(self.frmShlSelCtrl)
        self.frmShlSelBtn.pack(side=tk.TOP, anchor=tk.CENTER)
        self.iconShlPrev = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'prev.png')), master=self.frmShlSelBtn)
        self.btnShlPrev = tk.Button(self.frmShlSelBtn, image=self.iconShlPrev, command=self.JumpPrevShl)
        self.btnShlPrev.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)
        self.iconShlNext = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'next.png')), master=self.frmShlSelBtn)
        self.btnShlNext = tk.Button(self.frmShlSelBtn, image=self.iconShlNext, command=self.JumpNextShl)
        self.btnShlNext.pack(side=tk.LEFT, anchor=tk.CENTER, padx=10)

        # cntrl
        self.frmCtrlShl = tk.Frame(self.frmShell)
        self.frmCtrlShl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5, pady=5)

        btnWidth = 10
        self.btnCreateShl = tk.Button(self.frmCtrlShl, text=' 作成 ', compound=tk.LEFT, command=self.CreateShellBearing, width=btnWidth)
        self.btnCreateShl.pack(side=tk.LEFT, anchor=tk.NW)        
        self.btnUndoShl = tk.Button(self.frmCtrlShl, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndoShl.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndoShl)

    def SelectInnterArcEdge(self):
        edges = simlab.getSelectedEntities('EDGE')
        if len(edges) == 0:
            messagebox.showinfo('情報','2円弧を選択した後、ボタンを押下してください。')
            return
        for thisEdge in edges:
            arcAtt = muratautil.getArcAttribute(thisEdge)
            if not arcAtt:
                messagebox.showinfo('情報','円弧エッジを選択してください。')
                return

        self.DeleteSolidGroup(self.InnerEdge)

        for thisEdge in edges:
            arcAtt = muratautil.getArcAttribute(thisEdge)
            if not arcAtt:
                messagebox.showinfo('情報','Select cylindrical edges')
                return

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.InnerEdge)

        simlabutil.ClearSelection()
        if simlab.isGroupPresent(self.InnerEdge):
            self.JumpNextShl()
        else:
            self.UpdateShlWidgets()

    def SelectOuterArcEdge(self):
        importlib.reload(muratautil)
        edges = simlab.getSelectedEntities('EDGE')
        if len(edges) == 0:
            messagebox.showinfo('情報','2円弧を選択した後、ボタンを押下してください。')
            return
        for thisEdge in edges:
            arcAtt = muratautil.getArcAttribute(thisEdge)
            if not arcAtt:
                messagebox.showinfo('情報','円弧エッジを選択してください。')
                return

        self.DeleteSolidGroup(self.OuterEdge)

        for thisEdge in edges:
            arcAtt = muratautil.getArcAttribute(thisEdge)
            if not arcAtt:
                messagebox.showinfo('情報','Select cylindrical edges')
                return

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.OuterEdge)

        simlabutil.ClearSelection()
        self.UpdateShlWidgets()

    def SelectBearingBody(self):
        bodies = simlab.getSelectedBodies()
        if len(bodies) == 0:
            messagebox.showinfo('情報','対象ベアリングのボディを１つ選択してください。')
            return

        self.DeleteSolidGroup(self.bearingBody)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Body', bodies, self.bearingBody)

        simlabutil.ClearSelection()
        self.UpdateShlWidgets()
        
    def JumpPrevShl(self):
        self.shlPageIndex -= 1
        self.UpdateShlWidgets()

    def JumpNextShl(self):
        self.shlPageIndex += 1
        self.UpdateShlWidgets()
    
    def UpdateShlWidgets(self):
        self.UpdateShlFig()
        self.UpdateShlButtonState()
        self.UpdateButtonFG()

    def UpdateShlFig(self):
        self.frmShellWd.forget()
        self.frmShellRd.forget()
        if self.shlPageIndex == 0:
            self.frmShellWd.pack(side=tk.TOP, anchor=tk.CENTER, expand=0, fill=tk.X)
            selectionFilter = 'CircleEdge'
        elif self.shlPageIndex == 1:
            self.frmShellRd.pack(side=tk.TOP, anchor=tk.CENTER, expand=0, fill=tk.X)
            selectionFilter = 'CircleEdge'
        else:
            pass
        simlab.setSelectionFilter(selectionFilter)

    def UpdateShlButtonState(self):
        self.btnShlPrev.config(state='normal')
        self.btnShlNext.config(state='normal')
        if self.shlPageIndex == 0:
            self.btnShlPrev.config(state='disabled')
        elif self.shlPageIndex == 1:
            self.btnShlNext.config(state='disabled')
        else:
            pass

        self.btnCreateShl.config(state='normal')
        if not simlab.isGroupPresent(self.InnerEdge) or not simlab.isGroupPresent(self.OuterEdge) or not simlab.isGroupPresent(self.bearingBody):
            self.btnCreateShl.config(state='disabled')

    def CreateShellBearing(self):
        groups = [self.InnerEdge, self.OuterEdge, self.bearingBody]
        for i in range(len(groups)):
            if not simlab.isGroupPresent(groups[i]):
                messagebox.showinfo('情報', '全ての円弧とボディを選択した後、押下してください。')
                return
        try:
            numAxis = int(self.entShlBearingNumAxis.get())
            numCirc = int(self.cmbShlBearingNumAngle.get())
            numSpring = int(self.entShlBearingNumSpring.get())
            stiffSpringR = float(self.entShlBearingSpStiffR.get())
            stiffSpringT = float(self.entShlBearingSpStiffT.get())
            stiffSpringZ = float(self.entShlBearingSpStiffZ.get())
        except:
            messagebox.showinfo('情報', '実数を指定してください。')
            return
        
        if stiffSpringR == 0.0 and stiffSpringT == 0.0 and  stiffSpringZ == 0.0:
            messagebox.showinfo('情報', 'Set 剛性 for spring')
            return

        importlib.reload(bearingutil)
        self.backup.Save('ShellBearing')

        springName = self.shlSpringType.get()
        if len(springName) == 0:
            springName = 'Shell_Bearing'

        elementProp = (numAxis, numCirc)
        dof = (stiffSpringR, stiffSpringT, stiffSpringZ)
        springProp = (springName, numSpring, dof)
        CID = coordinate.GetID(self.shlCoord.get())
        
        if CID == -1:
            messagebox.showinfo('情報', "Select coordinate id")
            return

        bodyNm = simlab.getBodiesFromGroup(self.bearingBody)

        bearingutil.createShellBearing(bodyNm, self.InnerEdge, self.OuterEdge, CID, elementProp, springProp)

        simlablib.DeleteGroups(groups)
        self.JumpPrevShl()

        # message = '不要になったソリッドは手動で削除してください。'
        # msgbox = mc.MessageBoxWithCheckBox(self.master)
        # msgbox.ShowInfoIfNeeded('情報', message, 3)        

    def CreateSolidTab(self):
        self.lblNote2 = tk.Label(self.frmSolid, text='Tips: 画像の面を選択して、[ 作成 ]ボタンを押してください。')
        self.lblNote2.pack(side=tk.TOP, anchor=tk.NW, padx=5, pady=5)

        self.frmFig = tk.Frame(self.frmSolid)
        self.frmFig.pack(side=tk.TOP, anchor=tk.NW, padx=5)

        self.frmFigL = tk.Frame(self.frmFig)
        self.frmFigL.pack(side=tk.LEFT, anchor=tk.NW)

        self.iconRing = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'Bearing4.png')), master=self.frmFig)
        tk.Label(self.frmFigL, image=self.iconRing).pack(side=tk.LEFT, anchor=tk.CENTER, padx=5)
        self.btnOuter = tk.Button(self.frmFigL, text=' 外径円筒エッジ ', command=self.SelectOuter)
        self.btnOuter.place(x= 50, y=90)
        self.btnInner = tk.Button(self.frmFigL, text=' 内径円筒エッジ ', command=self.SelectInner)
        self.btnInner.place(x= 110, y=210)

        self.frmFigR = tk.Frame(self.frmFig)
        self.frmFigR.pack(side=tk.RIGHT, anchor=tk.NW)

        self.frmFigRNumE = tk.LabelFrame(self.frmFigR, text='要素分割数:')
        self.frmFigRNumE.pack(side=tk.TOP, anchor=tk.W, expand=0, fill=tk.X)

        self.frmAxis = tk.Frame(self.frmFigRNumE)
        self.frmAxis.pack(side=tk.TOP, anchor=tk.W, padx=5,pady=2)
        tk.Label(self.frmAxis, text='軸方向:').pack(side=tk.LEFT, anchor=tk.W)
        self.entNumAxis = tk.Entry(self.frmAxis, width=5)
        self.entNumAxis.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entNumAxis.insert(tk.END, 3)

        self.frmAng = tk.Frame(self.frmFigRNumE)
        self.frmAng.pack(side=tk.TOP, anchor=tk.W, padx=5,pady=2)
        tk.Label(self.frmAng, text='周方向:').pack(side=tk.LEFT, anchor=tk.W)
        self.bearingNumAngle = tk.IntVar()
        self.bearingNumAngle.set(20)
        self.cmbBearingNumAngle = ttk.Combobox(self.frmAng, width=3, state='readonly', values=[12, 16, 20, 24], textvariable=self.bearingNumAngle)
        self.cmbBearingNumAngle.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=2)
        tk.Frame(self.frmAng, height=5).pack(side=tk.TOP, anchor=tk.W)

        tk.Frame(self.frmFigR, height=5).pack(side=tk.TOP, anchor=tk.W)

        self.frmSp = tk.LabelFrame(self.frmFigR, text='バネ要素:')
        self.frmSp.pack(side=tk.TOP, anchor=tk.W, expand=0, fill=tk.X)

        self.frmNumSpring = tk.Frame(self.frmSp)
        self.frmNumSpring.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=2)
        tk.Label(self.frmNumSpring, text='バネの数:').pack(side=tk.LEFT, anchor=tk.W)
        self.entNumSpring = tk.Entry(self.frmNumSpring, width=5)
        self.entNumSpring.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entNumSpring.insert(tk.END, 4)

        tk.Frame(self.frmFigR, height=5).pack(side=tk.TOP, anchor=tk.W)

        self.frmSldCoord = tk.Frame(self.frmSp)
        self.frmSldCoord.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=2)
        self.lblSldCoord = tk.Label(self.frmSldCoord, text='座標系 : ')
        self.lblSldCoord.pack(side=tk.LEFT, anchor=tk.W)

        coords = coordinate.GetAllCoordinates()
        self.sldCoord = tk.StringVar()
        if len(coords) != 0:
            self.sldCoord.set(coords[0])
        self.cmbShlCoords = ttk.Combobox(self.frmSldCoord, values=coords, textvariable=self.sldCoord, width=20, state='readonly')
        self.cmbShlCoords.pack(side=tk.LEFT, anchor=tk.W)

        self.frmSpStiff = tk.LabelFrame(self.frmSp, text='剛性:')
        self.frmSpStiff.pack(side=tk.TOP, anchor=tk.W, padx=5)

        self.frmSldSprintType = tk.Frame(self.frmSpStiff)
        self.frmSldSprintType.pack(side=tk.TOP, anchor=tk.NW)

        self.sldSpringType = tk.StringVar()
        self.cmbSldSpringType = ttk.Combobox(self.frmSldSprintType, width=18, state='readonly', values=[], textvariable=self.sldSpringType)
        self.cmbSldSpringType.pack(side=tk.LEFT, anchor=tk.W)
        self.cmbSldSpringType.bind('<<ComboboxSelected>>' , self.springs.Select)

        tk.Frame(self.frmSpStiff, height=5).pack(side=tk.TOP, anchor=tk.W)

        self.frmSpStiffR = tk.Frame(self.frmSpStiff)
        self.frmSpStiffR.pack(side=tk.TOP, anchor=tk.W)
        tk.Label(self.frmSpStiffR, text='R:').pack(side=tk.LEFT, anchor=tk.W)        
        self.entSpStiffR = tk.Entry(self.frmSpStiffR, width=10)
        self.entSpStiffR.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entSpStiffR.insert(tk.END, 0.0)

        self.frmSpStiffT = tk.Frame(self.frmSpStiff)
        self.frmSpStiffT.pack(side=tk.TOP, anchor=tk.W)
        tk.Label(self.frmSpStiffT, text='θ:').pack(side=tk.LEFT, anchor=tk.W)        
        self.entSpStiffT = tk.Entry(self.frmSpStiffT, width=10)
        self.entSpStiffT.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entSpStiffT.insert(tk.END, 0.0)

        self.frmSpStiffZ = tk.Frame(self.frmSpStiff)
        self.frmSpStiffZ.pack(side=tk.TOP, anchor=tk.W)
        tk.Label(self.frmSpStiffZ, text='Z:').pack(side=tk.LEFT, anchor=tk.W)        
        self.entSpStiffZ = tk.Entry(self.frmSpStiffZ, width=10)
        self.entSpStiffZ.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.entSpStiffZ.insert(tk.END, 0.0)

        self.springs.AppendWidget(self.cmbSldSpringType, self.sldSpringType, self.entSpStiffR, self.entSpStiffT, self.entSpStiffZ)

        self.frmCtrlSolid = tk.Frame(self.frmSolid)
        self.frmCtrlSolid.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5, pady=5)

        btnWidth = 10
        self.btnCreate = tk.Button(self.frmCtrlSolid, text=' 作成 ', compound=tk.LEFT, command=self.CreateSolidBearing, width=btnWidth)
        self.btnCreate.pack(side=tk.LEFT, anchor=tk.NW)
        
        self.btnUndo = tk.Button(self.frmCtrlSolid, text=' 戻す ', compound=tk.LEFT, command=self.Undo, width=btnWidth)
        self.btnUndo.pack(side=tk.LEFT, anchor=tk.NW)
        self.backup.Append(self.btnUndo)

    def SelectOuter(self):
        edges = simlab.getSelectedEntities('EDGE')
        if len(edges) == 0:
            messagebox.showinfo('情報','エッジを選択した後、[外径面] ボタンを押下してください。')
            return
        for thisEdge in edges:
            arcAtt = muratautil.getArcAttribute(thisEdge)
            if not arcAtt:
                messagebox.showinfo('情報','Select cylindrical edges')
                return
        
        self.DeleteSolidGroup(self.SolidOuterEdge)
        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.SolidOuterEdge)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def SelectInner(self):
        edges = simlab.getSelectedEntities('EDGE')
        if len(edges) == 0:
            messagebox.showinfo('情報','エッジを選択した後、[内径面] ボタンを押下してください。')
            return
        for thisEdge in edges:
            arcAtt = muratautil.getArcAttribute(thisEdge)
            if not arcAtt:
                messagebox.showinfo('情報','Select cylindrical edges')
                return

        self.DeleteSolidGroup(self.SolidInnerEdge)

        modelName = simlab.getModelName('FEM')
        simlablib.CreateGroup(modelName, 'Edge', edges, self.SolidInnerEdge)

        simlabutil.ClearSelection()
        self.UpdateButtonFG()

    def CreateSolidBearing(self):
        groups = [self.SolidOuterEdge, self.SolidInnerEdge]
        for i in range(len(groups)):
            if not simlab.isGroupPresent(groups[i]):
                messagebox.showinfo('情報','全ての面を選択した後、[簡略化] ボタンを押下してください。')
                return

        try:
            numAxis = int(self.entNumAxis.get())
            numCirc = int(self.cmbBearingNumAngle.get())
            numSpring = int(self.entNumSpring.get())
            stiffSpringR = float(self.entSpStiffR.get())
            stiffSpringT = float(self.entSpStiffT.get())
            stiffSpringZ = float(self.entSpStiffZ.get())
        except:
            messagebox.showinfo('情報','パラメータは整数、実数を指定してください。')
            return
        
        if stiffSpringR == 0.0 and stiffSpringT == 0.0 and  stiffSpringZ == 0.0:
            messagebox.showinfo('情報', 'Set 剛性 for spring')
            return

        self.backup.Save('Bearing')
        importlib.reload(bearingutil)

        springName = self.sldSpringType.get()
        if len(springName) == 0:
            springName = 'Solid_Bearing'

        elementProp = (numAxis, numCirc)
        dof = (stiffSpringR, stiffSpringT, stiffSpringZ)
        springProp = (springName, numSpring, dof)
        CID = coordinate.GetID(self.sldCoord.get())
        
        if CID == -1:
            messagebox.showinfo('情報', "Select coordinate id")
            return

        bearingutil.createSolidBearing(self.SolidInnerEdge, self.SolidOuterEdge, CID, elementProp, springProp)
        
        self.DeleteSolidGroup(self.SolidOuterEdge)
        self.DeleteSolidGroup(self.SolidInnerEdge)
        self.UpdateButtonFG()

        message = 'ベアリング作成が終了しました。形状を確認してください。'
        message += '\n\n異常があった場合は[戻す] ボタンを押してください。'
        msgbox = mc.MessageBoxWithCheckBox(self.master)
        msgbox.ShowInfoIfNeeded('情報', message, 3)        

    def Undo(self):
        self.backup.Load()

        modelName = simlab.getModelName('CAD')
        bodies = simlab.getBodiesWithSubString(modelName, ['*'])
        simlab.showOrHideEntities(bodies, 'Hide', modelName, 'Body')

        self.UpdateButtonFG()

    def UpdateButtonFG(self):
        groups = [self.SolidOuterEdge, self.SolidInnerEdge, self.InnerEdge, self.OuterEdge, self.bearingBody]
        widgets = [self.btnOuter, self.btnInner, self.btnShellInnerArc, self.btnShellOuterArc, self.btnShlBearingBody]

        for i in range(len(groups)):
            color = 'black'
            if simlab.isGroupPresent(groups[i]):
                color = 'blue'
            widgets[i].config(fg=color)

    def CloseDialog(self):
        simlablib.DeleteGroups([self.InnerEdge, self.OuterEdge, self.bearingBody])
        self.DeleteSolidGroup(self.SolidOuterEdge)
        self.DeleteSolidGroup(self.SolidInnerEdge)
        super().CloseDialog()
    
    def DeleteSolidGroup(self, grpNm):
        groups = simlab.getGroupsWithSubString("EdgeGroup", [grpNm+"*"])
        for thisGroup in groups:
            simlablib.DeleteGroups(thisGroup)
