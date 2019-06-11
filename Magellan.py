import csv
import os
import glob
import sys


### Pas utile ###
def GetObjectClass(CsvPath):
    ObjectClass = []

    with open(CsvPath, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row != [] and row[2] == row[2].upper():
                ObjectClass.append(row[2])
    
    return ObjectClass

def GetAllS57Repertory(S57FilesPath):
    S57Path = []
    for _file in glob.glob(('{0}{1}*.000').format(S57FilesPath, os.sep)):
        S57Path.append(_file)
    
    return S57Path

def ExtractToGeoJSON(S57FilesPath, HostDatabase, UserName, Password, Database):
    for _file in GetAllS57Repertory(S57FilesPath):
        _cmd = os.system('ogr2ogr -oo SPLIT_MULTIPOINT=ON -skipfailures -t_srs EPSG:4326 -f PostGreSQL PG:"host={0} user={1} password={2} dbname={3}" {4}'.format(HostDatabase, UserName, Password, Database, _file))



########################################
####### MAIN COMMAND FOR EXTRACT #######
########################################
ExtractToGeoJSON(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
