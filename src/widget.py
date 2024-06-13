# coding: utf_8
# SimLab Version 2019.2 (64-bit)
#***************************************************************
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import sys, os

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))

# local
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

class LabelEntry(tk.Frame):
    def __init__(self, master, text='label', width=30, value=''):
        super().__init__(master)
        self.CreateWidgets(text, width, value)

    def CreateWidgets(self, text, width, value):
        self.lbl = tk.Label(self, text=text)
        self.lbl.pack(side=tk.LEFT, anchor=tk.NW, padx=5)
        self.ent = tk.Entry(self, width=width)
        self.ent.pack(side=tk.LEFT, anchor=tk.NW, padx=5)
        self.Set(value)

    def Set(self, value):
        self.ent.delete(0, tk.END)
        self.ent.insert(tk.END, str(value))

    def Get(self):
        return self.ent.get()

    def Config(self, state='normal'):
        self.ent.config(state=state)

class MeshParameterEntry(tk.Frame):
    def __init__(self, master, params):
        super().__init__(master)
        self.CreateWidgets(params)

    def CreateWidgets(self, params):
        self.frmType = tk.Frame(self)
        self.frmType.pack(side=tk.TOP, anchor=tk.NW)
        tk.Label(self.frmType, text='タイプ : ').pack(side=tk.LEFT, anchor=tk.NW)

        needPreserveMeshCtrl = bool(params[0])

        self.type = tk.StringVar()
        self.type.set('Face')
        self.chkFace = tk.Radiobutton(self.frmType, text='Face', value='Face', variable=self.type, command=self.SelectType)
        self.chkFace.pack(side=tk.LEFT, anchor=tk.NW, padx=5)
        self.chkFillet = tk.Radiobutton(self.frmType, text='Fillet', value='Fillet', variable=self.type, command=self.SelectType)
        self.chkFillet.pack(side=tk.LEFT, anchor=tk.NW, padx=5)
        self.chkISO = tk.Radiobutton(self.frmType, text='ISO', value='ISO', variable=self.type, command=self.SelectType)
        self.chkISO.pack(side=tk.LEFT, anchor=tk.NW, padx=5)
        if needPreserveMeshCtrl:
            self.chkPreserve = tk.Radiobutton(self.frmType, text='Preserve', value='Preserve', variable=self.type, command=self.SelectType)
            self.chkPreserve.pack(side=tk.LEFT, anchor=tk.NW, padx=5)

        self.frmFace = tk.Frame(self)
        self.frmFace.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=5)
        self.entFaceSize = LabelEntry(self.frmFace, text='平均要素長 :', width=10, value=params[1])
        self.entFaceSize.grid(row=0, column=0)
        self.entFaceAngle = LabelEntry(self.frmFace, text='最大要素角 :', width=10, value=params[2])
        self.entFaceAngle.grid(row=0, column=1)
        self.entFaceAspect = LabelEntry(self.frmFace, text='アスペクト比 :', width=10, value=params[3])
        self.entFaceAspect.grid(row=1, column=0)

        self.frmFillet = tk.Frame(self)
        self.entFilletSize = LabelEntry(self.frmFillet, text='平均要素長 :', width=10, value=params[4])
        self.entFilletSize.grid(row=0, column=0)
        self.entFilletAngle = LabelEntry(self.frmFillet, text='形状近似角度 :', width=10, value=params[5])
        self.entFilletAngle.grid(row=0, column=1)
        self.entFilletAspect = LabelEntry(self.frmFillet, text='アスペクト比 :', width=10, value=params[6])
        self.entFilletAspect.grid(row=1, column=0)

        self.frmISO = tk.Frame(self)
        self.entISOSize = LabelEntry(self.frmISO, text='軸方向長さ :', width=10, value=params[7])
        self.entISOSize.grid(row=0, column=0)
        self.entISOAngle = LabelEntry(self.frmISO, text='周方向角度 :', width=10, value=params[8])
        self.entISOAngle.grid(row=0, column=1)
        self.entISOAspect = LabelEntry(self.frmISO, text='アスペクト比 :', width=10, value=params[9])
        self.entISOAspect.grid(row=1, column=0)

        self.chkvalue = tk.BooleanVar()
        self.chkvalue.set(False)
        self.chk = tk.Checkbutton(self, text='面を結合する', variable=self.chkvalue)
        self.chk.pack(side=tk.TOP, anchor=tk.NW)

        self.SelectType()
    
    def SelectType(self):
        self.frmFace.forget()
        self.frmFillet.forget()
        self.frmISO.forget()
        self.chk.forget()

        if self.type.get() == 'Face':
            self.frmFace.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=5)
            self.chk.pack(side=tk.TOP, anchor=tk.NW)
            self.chk.config(text='選択した面の結合')
        elif self.type.get() == 'Fillet':
            self.frmFillet.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=5)
            self.chk.pack(side=tk.TOP, anchor=tk.NW)
            self.chk.config(text='微小フィレットの結合')
        elif self.type.get() == 'ISO':
            self.frmISO.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=5)
            self.chk.pack(side=tk.TOP, anchor=tk.NW)
            self.chk.config(text='軸方向エッジを共有するフェイスを結合')
        else:
            pass

    def Get(self):
        if self.type.get() == 'Face':
            return [ self.type.get(), self.entFaceSize.Get(), self.entFaceAngle.Get(), self.entFaceAspect.Get(), self.chkvalue.get() ]
        elif self.type.get() == 'Fillet':
            return [ self.type.get(), self.entFilletSize.Get(), self.entFilletAngle.Get(), self.entFilletAspect.Get(), self.chkvalue.get() ]
        elif self.type.get() == 'ISO':
            return [ self.type.get(), self.entISOSize.Get(), self.entISOAngle.Get(), self.entISOAspect.Get(), self.chkvalue.get() ]
        else:
            return [ self.type.get() ]

    def GetAll(self):
        return [
            self.entFaceSize.Get(), self.entFaceAngle.Get(), self.entFaceAspect.Get(),
            self.entFilletSize.Get(), self.entFilletAngle.Get(), self.entFilletAspect.Get(),
            self.entISOSize.Get(), self.entISOAngle.Get(), self.entISOAspect.Get()
        ]
