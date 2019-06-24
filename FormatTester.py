import csv
import os
import glob
import sys

def GetAllS57Repertory(FilesPath):
    S57Path = []
    for _file in glob.glob(('{0}{1}*.000').format(FilesPath, os.sep)):
        S57Path.append(_file)
    
    return S57Path

def ExtractToGeoJSON(FilesPath):
    _cmd = 1

    for _file in GetAllS57Repertory(FilesPath):
        _cmd = os.system('ogr2ogr -f GeoJSON {0} {1} m_covr'.format("_temp_{0}.json".format(GetAllS57Repertory(FilesPath).index(_file)), _file))
        try:
            os.remove("_temp_{0}.json".format(GetAllS57Repertory(FilesPath).index(_file)))
        except:
            print("I think is s63 file or whatever...")

    return _cmd
        
            

def Tester(FilesPath):
    if(ExtractToGeoJSON(FilesPath) == 0):
        return True
    else:
        return False

if(Tester(sys.argv[1]) == True):
    print("is s57")
else:
    print("is s63")
