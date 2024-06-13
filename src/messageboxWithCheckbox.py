from hwx import simlab
import tkinter as tk
import os, sys
from PIL import Image, ImageTk

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))
LOG_DIR = os.path.join(PROJECT_DIR,'log')
LOG_FILE = os.path.join(LOG_DIR, 'displayMessageBox.log')

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)
import simlablib

class MessageBoxWithCheckBox():
    def __init__(self, parentDialog):
        self.parentDialog = parentDialog
        self.dialog = None
        self.ID = 0
        self.parameterName = 'DisplayMessageBox'

    def ShowInfoIfNeeded(self, title, text, ID):
        self.ID = ID

        if self.dialog != None:
            self.dialog.destroy()

        if not self.Needs():
            return

        self.dialog = tk.Toplevel()
        self.dialog.title(title)
        self.dialog.resizable(width=False, height=False)
        self.dialog.attributes("-topmost", True)
        self.dialog.protocol("WM_DELETE_WINDOW", self.CloseDialog)
        self.Geometry()
        self.CreateWidget(text)

        self.dialog.transient(self.parentDialog)
        self.dialog.mainloop()

    def Geometry(self):        
        x = y = 0
        x, y, _, _ = self.parentDialog.bbox("insert")
        x += self.parentDialog.winfo_rootx()
        y += self.parentDialog.winfo_rooty()
        self.dialog.wm_geometry("+%d+%d" % (x, y))

    def CreateWidget(self, text):
        self.frmMsg = tk.Frame(self.dialog, bg='white')
        self.frmMsg.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.BOTH)

        self.iconInfo = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_DIR, 'info.png')), master=self.frmMsg)
        tk.Label(self.frmMsg, image=self.iconInfo, bg='white').pack(side=tk.LEFT, anchor=tk.NW, padx=10, pady=10)

        self.lblMessage = tk.Label(self.frmMsg, text=text, bg='white', justify='left')
        self.lblMessage.pack(side=tk.RIGHT, anchor=tk.NW, expand=1, fill=tk.BOTH, padx=10, pady=20)

        self.frmCtrl = tk.Frame(self.dialog)
        self.frmCtrl.pack(side=tk.TOP, anchor=tk.NW, expand=1, fill=tk.X, padx=5, pady=5)

        self.chVal = tk.BooleanVar()
        self.chVal.set(False)
        self.chk = tk.Checkbutton(self.frmCtrl, text='今後、このメッセージを表示しない', variable=self.chVal)
        self.chk.pack(side=tk.LEFT, anchor=tk.CENTER, pady=5)

        tk.Button(self.frmCtrl, text='OK', width=8, command=self.CloseDialog).pack(side=tk.RIGHT, anchor=tk.CENTER, padx=5)

    def SaveParameter(self):
        n = self.GetParaemter()
        if self.chVal.get():
            n = n | (1 << self.ID)
        self.SetParaemter(n)

    def GetParaemter(self):
        if not os.path.isfile(LOG_FILE):
            return 0        
        try:
            with open(LOG_FILE) as fin:
                return int(fin.read())
        except:
            return 0

    def SetParaemter(self, n):
        if not os.path.isdir(LOG_DIR):
            os.mkdir(LOG_DIR)

        with open(LOG_FILE, mode='w') as fout:
            fout.write(str(n))

    def Needs(self):
        n1 = self.GetParaemter()
        n2 = (1 << self.ID)
        if (n1 & n2):
            return False
        return True

    def ResetParameter(self):
        self.SetParaemter(0)

    def CloseDialog(self):
        self.SaveParameter()
        self.dialog.destroy()
