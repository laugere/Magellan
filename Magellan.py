import csv
import os
import glob
import sys

def GetAllS57Repertory(S57FilesPath):
    S57Path = []
    for _file in glob.glob(('{0}{1}*.000').format(S57FilesPath, os.sep)):
        S57Path.append(_file)
    
    return S57Path

def ExtractToGeoJSON(S57FilesPath, HostDatabase, Port, UserName, Password, Database):
    for _file in GetAllS57Repertory(S57FilesPath):
        _cmd = os.system('ogr2ogr -lco ENCODING=UTF-8 -oo SPLIT_MULTIPOINT=ON -update -append -skipfailures -t_srs EPSG:4326 -f PostGreSQL PG:"host={0} user={1} password={2} dbname={3}" {4}'.format(HostDatabase, UserName, Password, Database, _file))



########################################
####### MAIN COMMAND FOR EXTRACT #######
########################################

try:
    ExtractToGeoJSON(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
except:
    print('COMMAND USAGE : py Magellan.py < S57 Folder Path > < Host Database > < Port > < User Name > < Password > < Database Name >')
    print('||   if GDAL is not initialized launch InitMagellan.py command')