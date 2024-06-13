import sys, os, time
from hwx import simlab
from datetime import datetime
from operator import itemgetter

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
LOG_DIR = (os.path.join(PROJECT_DIR, 'log'))

class ModelBackup:
    def __init__(self, config):
        self.backup = ''
        self.buttons = []
        self.config = config

    def Save(self, keyName='Backup'):
        if not os.path.isdir(LOG_DIR):
            os.mkdir(LOG_DIR)

        limitNumberOfBackups = int(self.config.Get('Number_Of_Backups'))
        if limitNumberOfBackups == 0:
            self.backup = ''
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup = os.path.join(LOG_DIR, keyName + '_backup_' + timestamp + '.slb')
            ExportSlb=''' <ExportSlb UUID="a155cd6e-8ae6-4720-8ab4-1f50d4a34d1c">
            <tag Value="-1"/>
            <Name Value=""/>
            <Option Value="1"/>
            <FileName Value="''' + self.backup + '''"/>
            </ExportSlb>'''
            simlab.execute(ExportSlb)
                
        self.UpdateState()
        self.DeleteBackupsIfExceeds()

    def Load(self):
        if self.backup == '':
            return
        if not os.path.isfile(self.backup):
            return
        
        simlab.closeActiveDocument()
        simlab.newDocument()

        ImportSlb=''' <ImportSlb CheckBox="ON" UUID="C806F6DF-56FA-4134-9AD1-1010BF292183" gda="">
        <tag Value="1"/>
        <Name Value=""/>
        <FileName Value="''' + self.backup + '''"/>
        <ImportOrOpen Value="1"/>
        <Output/>
        </ImportSlb>'''
        simlab.execute(ImportSlb)
        self.backup = ''
        self.UpdateState()

    def Append(self, button):
        self.buttons.append(button)
        self.UpdateState()
    
    def UpdateState(self):
        state = 'normal'
        if self.backup == '':
            state = 'disabled'

        buttons = []
        for button in self.buttons:
            try:
                button.config(state=state)
                buttons.append(button)
            except:
                pass
        self.buttons = buttons

    def DeleteBackupsIfExceeds(self):
        date_files = []
        for root, _, files in os.walk(LOG_DIR):
            for f in files:
                _, ext = os.path.splitext(f)
                if ext.lower() != '.slb':
                    continue
                if f.find('_backup_') == -1:
                    continue

                path = os.path.join(root, f)
                date_files.append((os.path.getctime(path), path))

        date_files = sorted(date_files, key=itemgetter(0), reverse=True)
        limitNumberOfBackups = int(self.config.Get('Number_Of_Backups'))

        for i, (_, path) in enumerate(date_files):
            if i < limitNumberOfBackups:
                continue
            os.remove(path)
