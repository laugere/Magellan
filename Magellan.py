import csv
import subprocess
import os


def GetObjectClass(CsvPath):
    ObjectClass = []

    with open(CsvPath, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row != [] and row[2] == row[2].upper():
                ObjectClass.append(row[2])
    
    return ObjectClass

def OgrCommandLine(GeoJSONDestinationPath, DestinationFile, S57FilePath, ObjectClass):
    subprocess.Popen('ogr2ogr -t_srs EPSG:4326 -f GeoJSON {0}/{1}.json {2} {3}'.format(GeoJSONDestinationPath, DestinationFile, S57FilePath, ObjectClass.lower()))

def ExtractToGeoJSON(S57FilePath, GeoJSONDestinationPath):
    for _object in GetObjectClass('s57objectclasses.csv'):
        OgrCommandLine(GeoJSONDestinationPath, str(_object), str(S57FilePath), str(_object))

ExtractToGeoJSON('GeoJSON', 'ENC_ROOT/2W7D1870.000')