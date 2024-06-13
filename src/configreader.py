# coding: utf_8
# SimLab Version 2019.2 (64-bit)
#***************************************************************
import sys, os, csv
from collections import OrderedDict

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
CONFIG_FILE = 'config.csv'

if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

class ConfigReader():
    def __init__(self):
        # set system defaults (these parameters were used, if there is no configuration file on local and server)
        self._SetSystemDefaults()

        # read config.csv
        self._ReadCSV(os.path.join(PROJECT_DIR, CONFIG_FILE))

    def _SetSystemDefaults(self):
        self._values = OrderedDict()
        self._values['Number_Of_Backups'] = 10
        self._values['Boolean_FEM_Tolerance'] = 2.0

    def _ReadCSV(self, path):
        with open(path, 'r', encoding="utf_8") as f:
            reader = csv.reader(f)
            _ = next(reader)
            for line in reader:
                if len(line) != 2:
                    continue
                self._values[line[0]] = line[1]

    def Get(self, key):
        if not key in self._values.keys():
            return ''
        return self._values[key]
