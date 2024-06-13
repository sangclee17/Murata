import tkinter as tk
import tkinter.ttk as ttk
import sys, os, importlib
import csv
import simlab
import simlablib
import simlabutil

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
LOG_DIR = (os.path.join(PROJECT_DIR, 'log'))
SPRING_CSV = 'spring.csv'

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

class SpringCSV:
    def __init__(self):
        self.widgets = list()

    def AppendWidget(self, combobox, stringValue, entryX, entryY, entryZ):
        self.widgets.append([combobox, stringValue, entryX, entryY, entryZ])
        self.SetDefaultsForWidgets(self.widgets[-1])
        self.RefreshMissingWidgets()

    def Import(self, rPath):
        if not os.path.isdir(LOG_DIR):
            os.mkdir(LOG_DIR)
        wPath = os.path.join(LOG_DIR, SPRING_CSV)

        readingCSV = False
        with open(rPath, 'r') as fr:
            reader = csv.reader(fr)
            with open(wPath, 'w', newline='') as fw:
                writer = csv.writer(fw)

                for row in reader:
                    if len(row) == 0:
                        continue

                    key = row[0]
                    if readingCSV:
                        # ON -> OFF: end of reading
                        if key.startswith("##") and not 'spring csv' in key.lower():
                            readingCSV = False
                    else:
                        # OFF -> ON: start reading
                        if key.startswith("##") and 'spring csv' in key.lower():
                            readingCSV = True

                    if not readingCSV:
                        continue
                    if key.startswith("#"):
                        continue
                    if len(row) < 4:
                        continue

                    name = row[0]
                    x = row[1]
                    y = row[2]
                    z = row[3]

                    g = 9.80665
                    x = round(float(x) * g, 1)
                    y = round(float(y) * g, 1)
                    z = round(float(z) * g, 1)
                    writer.writerow([name,x,y,z])

        self.UpdateParameters()
        
    def Select(self, event):
        try:
            for items in self.widgets:
                combobox, stringValue, entryX, entryY, entryZ = items
                if event.widget != combobox:
                    continue

                entryX.delete(0, tk.END)
                entryY.delete(0, tk.END)
                entryZ.delete(0, tk.END)

                name = stringValue.get()
                x, y, z = self.GetStrengths(name)
                entryX.insert(tk.END, x)
                entryY.insert(tk.END, y)
                entryZ.insert(tk.END, z)
                break
        except:
            pass

    def SetDefaultsForWidgets(self, widgets):
        try:
            combobox, stringValue, entryX, entryY, entryZ = widgets
            names = self.GetSpringNames()

            combobox.config(values=names)
            entryX.delete(0, tk.END)
            entryY.delete(0, tk.END)
            entryZ.delete(0, tk.END)

            if len(names) == 0:
                stringValue.set('')
            else:
                name = names[0]
                x,y,z = self.GetStrengths(name)

                stringValue.set(name)
                entryX.insert(tk.END, x)
                entryY.insert(tk.END, y)
                entryZ.insert(tk.END, z)
        except:
            pass
        
    def RefreshMissingWidgets(self):
        widgets = []
        for items in self.widgets:
            combobox, stringValue, entryX, entryY, entryZ = items
            try:
                combobox.config(state='readonly')
                entryX.config(state='normal')
                entryY.config(state='normal')
                entryZ.config(state='normal')
                widgets.append([combobox, stringValue, entryX, entryY, entryZ])
            except:
                pass
        
        self.widgets = widgets

    def UpdateParameters(self):
        self.RefreshMissingWidgets()
        for items in self.widgets:
            self.SetDefaultsForWidgets(items)

    def GetSpringNames(self):
        names = []

        csvPath = os.path.join(LOG_DIR, SPRING_CSV)
        if not os.path.isfile(csvPath):
            return []

        with open(csvPath, 'r') as fr:
            reader = csv.reader(fr)
            for row in reader:
                names.append(row[0])

        return names
            
    def GetStrengths(self, name):
        xyz = [0,0,0]

        csvPath = os.path.join(LOG_DIR, SPRING_CSV)
        if not os.path.isfile(csvPath):
            return xyz

        with open(csvPath, 'r') as fr:
            reader = csv.reader(fr)
            for row in reader:
                chkName, x, y, z = row
                if chkName != name:
                    continue
                xyz = [float(x), float(y), float(z)]
                break
                
        return xyz

