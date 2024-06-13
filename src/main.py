# coding: utf_8
# SimLab Version 2019.2 (64-bit)
#***************************************************************
from hwx import simlab, gui
import os, sys
import tkinter as tk
import importlib

## global variable
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
IMAGE_DIR = (os.path.join(PROJECT_DIR, 'images'))
ROOT = None

gui.addResourcePath(PROJECT_DIR)
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)
os.chdir(PROJECT_DIR)

## local import
import maintool

## menu functions
def LaunchMainTool():
    global ROOT
    if Exists(ROOT):
        ROOT.deiconify()
        return

    importlib.reload(maintool)

    ROOT = tk.Tk()
    app = maintool.MainTool(ROOT)
    app.mainloop()

def Exists(win):
    try:
        if ROOT == None:
            return False
        return ROOT.winfo_exists()
    except:
        return False

## adds menus to SimLab
page = gui.RibbonPage (text="Automation", name='demopage'+'99999', after='Project')
group1 = gui.SpriteActionGroup (page, text="Automation")
gui.SpriteAction(group1, tooltip="Automation", icon=(os.path.join(IMAGE_DIR, 'icon.png')), command=LaunchMainTool)