import csv
import os
import glob


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
        S57Path.append('.'.join(_file.split('.')[:-1]))
    
    return S57Path

def OgrCommandLine(GeoJSONDestinationPath, DestinationFile, S57FilePath, ObjectClass):
    _cmd = os.system('ogr2ogr -progress -t_srs EPSG:4326 -f GeoJSON {0}/{1}.json {2} {3}'.format(GeoJSONDestinationPath, DestinationFile, S57FilePath, ObjectClass.lower()))
    if _cmd == 1:
        os.remove('{0}/{1}.json'.format(GeoJSONDestinationPath, DestinationFile))

def ExtractToGeoJSON(S57FilesPath, GeoJSONDestinationPath):
    os.mkdir(GeoJSONDestinationPath + os.sep + S57FilesPath)
    for _file in GetAllS57Repertory(S57FilesPath):
        os.mkdir(GeoJSONDestinationPath+os.sep+_file)
        for _object in GetObjectClass('s57objectclasses.csv'):
            OgrCommandLine(GeoJSONDestinationPath+os.sep+_file, str(_object), str(_file+'.000'), str(_object))





########################################
####### MAIN COMMAND FOR EXTRACT #######
########################################
ExtractToGeoJSON('ENC_ROOT', 'GeoJSON')

