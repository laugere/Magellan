import csv
import psycopg2
import argparse
import os.path
import subprocess
import json
import time
import osgeo.ogr


## class
## ## objectClasses
class objectClasse:
    def __init__(self, code, objectClass, acronym, attribute_A, attribute_B, attribute_C, classe, primitives):
        self.code = code
        self.objectClass = objectClass
        self.acronym = acronym
        self.genericAttribute = "CELLID;fid;RCID;PRIM;GRUP;OBJL;RVER;AGEN;FIDN;FIDS;LNAM;LNAM_REFS;FFPT_RIND;"
        self.attribute_A = attribute_A
        self.attribute_B = attribute_B
        self.attribute_C = attribute_C
        self.classe = classe
        self.primitives = primitives


## ## attribute
class attribute:
    def __init__(self, code, attribute, acronym, attributeType, classe):
        self.code = code
        self.attribute = attribute
        self.acronym = acronym
        self.attributeType = attributeType
        self.classe = classe


## main
## ## get csv to object
def getObjectFromCsv(csvPath, typeObject):
    if typeObject == "objectClasse":
        objects = []
        with open(csvPath, newline='') as csvFile:
            reader = csv.reader(csvFile, delimiter=',')
            next(reader)
            for row in reader:
                if row:
                    objects.append(objectClasse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        return objects

    if typeObject == "attribute":
        attributes = []
        with open(csvPath, newline='') as csvFile:
            reader = csv.reader(csvFile, delimiter=',')
            next(reader)
            for row in reader:
                if row:
                    attributes.append(attribute(row[0], row[1], row[2], row[3], row[4]))
        return attributes


## ## send object
def sendObjectToSql(attributes, objects, user, password, host, port, database):
    connection = psycopg2.connect(user = user, password = password, host = host, port = port, database = database)
    cursor = connection.cursor()
    for Object in objects:
        createQuery = "CREATE TABLE \"{0}\" (wkb_geometry geometry);".format(Object.acronym)
        if createQuery != "":
            try:
                cursor.execute(createQuery)
                connection.commit()
            except:
                print("la table {0} existe déjà".format(Object.acronym))
        tableQuery = ""
        tableQuery = getAttributeSql(Object.acronym, attributes, Object.genericAttribute)
        if Object.attribute_A:
            tableQuery = tableQuery + getAttributeSql(Object.acronym, attributes, Object.attribute_A)
        if Object.attribute_B:
            tableQuery = tableQuery + getAttributeSql(Object.acronym, attributes, Object.attribute_B)
        if Object.attribute_C:
            tableQuery = tableQuery + getAttributeSql(Object.acronym, attributes, Object.attribute_C)
        if tableQuery != "":
            try:
                cursor.execute(tableQuery)
                connection.commit()
            except:
                print("la table {0} existe déjà".format(Object.acronym))


## ## send s57
def sends57ToSql(tempDir, s57Dir, objects, user, password, host, port, database):
    connection = psycopg2.connect(user = user, password = password, host = host, port = port, database = database)
    cursor = connection.cursor()
    listCells = []
    envGDAL = os.environ["GDAL"]
    for _dir, _file, _filenames in os.walk(s57Dir):
        for _files in sorted(_filenames):
            _name = os.path.splitext(_files)[0]
            _ext = os.path.splitext(_files)[1]
            try:
                if(_ext == ".000"):
                    if (_ext in ['.TXT', '.TIF', '.JPG', '.XML'] or
                        _name[0] == '.' or
                        _name == 'CATALOG'):
                        pass
                    else:
                        listCells.append(_dir + os.sep + _files)
            except OSError as err:
                print(err)
                pass
    for cell in listCells:
        CELLID = os.path.basename(cell).split('.')[0]
        chartFile = osgeo.ogr.Open(cell)
        s57ObjectClasses = objects
        for i in range(chartFile.GetLayerCount()):
            layer = chartFile.GetLayer(i)
            isInList = False
            for s57ObjectClasse in s57ObjectClasses:
                if s57ObjectClasse.acronym == layer.GetName():
                    isInList = True
            if isInList:
                defn = layer.GetLayerDefn()
                for j in range(layer.GetFeatureCount()):
                    listObject = []
                    feature = layer.GetNextFeature()
                    #print("GEOM : {0}".format(feature.geometry()))
                    geom = feature.geometry()
                    listObject.append(["CELLID", CELLID])
                    if(geom != None):
                        listObject.append(["wkb_geometry", feature.geometry()])
                    for n in range(defn.GetFieldCount()):
                        layerDefn = defn.GetFieldDefn(n)
                        #print("{0} : {1}".format(layerDefn.GetName(), feature.GetField(layerDefn.GetName())))
                        listObject.append([layerDefn.GetName(), feature.GetField(layerDefn.GetName())])
                    sqlRequest = "INSERT INTO \"{0}\" (".format(layer.GetName(),)
                    i = 0
                    for s57Object in listObject:
                        if i == 0:
                            sqlRequest += '\"' + str(s57Object[0]) + '\"'
                        else:
                            sqlRequest += ', ' + '\"' + str(s57Object[0]) + '\"'
                        i += 1
                    sqlRequest += ") VALUES ("
                    i = 0
                    for s57Object in listObject:
                        if i == 0:
                            if str(s57Object[0]) ==  "LNAM_REFS" or str(s57Object[0]) ==  "FFPT_RIND":
                                sqlRequest += '\'' + "1:" + s57Object[1].replace('[', '').replace('\'', '').replace(']','') + '\''
                            elif str(s57Object[1]) != "None":
                                sqlRequest += '\'' + str(s57Object[1]).replace('[', '').replace('\'', '').replace(']','') + '\''
                            else:
                                sqlRequest += 'NULL'
                        else:
                            if str(s57Object[0]) ==  "LNAM_REFS" or str(s57Object[0]) ==  "FFPT_RIND":
                                sqlRequest += '\'' + "1:" + str(s57Object[1]).replace('[', '').replace('\'', '').replace(']','') + '\''
                            elif str(s57Object[1]) != "None":
                                sqlRequest += ', ' + '\'' + str(s57Object[1]).replace('[', '').replace('\'', '').replace(']','') + '\''
                            else:
                                sqlRequest += ', ' + 'NULL'
                        i += 1
                    sqlRequest += ");"
                    try:
                        cursor.execute(tableQuery)
                        connection.commit()
                    except:
                        print("Erreur dans l'insertion des données de la carte {0}".format(CELLID))
    print("FINI !!!!!")



## ## get attribute sql command
def getAttributeSql(objectAcronym, globalAttributes, objectAttributes):
    sqlQuery = ""
    for objectAttribute in objectAttributes.split(';'):
        if objectAttribute:
            for globalAttribute in globalAttributes:
                if objectAttribute == globalAttribute.acronym:
                    sqlQuery = sqlQuery + "ALTER TABLE \"{0}\" ADD COLUMN \"{1}\" {2};".format(objectAcronym, objectAttribute, GetAttributeType(globalAttribute.attributeType))
                    break
    return sqlQuery


## ## get attribute type
def GetAttributeType(charType):
    if charType == "E":
        return "INT"
    if charType == "L":
        return "VARCHAR"
    if charType == "S":
        return "TEXT"
    if charType == "F":
        return "FLOAT"
    if charType == "I":
        return "INT"
    if charType == "A":
        return "VARCHAR"
    ## default text
    return "TEXT"

argparser = argparse.ArgumentParser()

argparser.add_argument("--initDatabase", help="Initialize Database for Magellan", action="store_true")
argparser.add_argument("--csvAttribute", default="GDALCSV\\s57attributes.csv", help="Change s57attribute.csv path")
argparser.add_argument("--csvObjectClasses", default="GDALCSV\\s57objectclasses.csv", help="Change s57objectClasses path")
argparser.add_argument("--update", help="update overwrite temp and data into the database for updating cells", action="store_true")
argparser.add_argument("--resume", help="Resume installation of the cells", action="store_true")
argparser.add_argument("tempDir", help="temp path")
argparser.add_argument("s57Dir", help="s57 chart path")
argparser.add_argument("userName", help="Username of the database")
argparser.add_argument("password", help="Password of the database")
argparser.add_argument("host", help="Address of the database")
argparser.add_argument("port", help="Port of the database")
argparser.add_argument("nameDb", help="name of the database")

args = argparser.parse_args()


tempDir = args.tempDir
csvAttribute = args.csvAttribute
csvObjectClasses = args.csvObjectClasses
s57Dir = args.s57Dir
userName = args.userName
password = args.password
host = args.host
port = args.port
nameDb = args.nameDb

isUpdate = args.update
isResume = args.resume

attributeCsv = getObjectFromCsv(csvAttribute, "attribute")
objectClassCsv = getObjectFromCsv(csvObjectClasses, "objectClasse")

if args.initDatabase:
    sendObjectToSql(attributeCsv, objectClassCsv, userName, password, host, port, nameDb)

sends57ToSql(tempDir, s57Dir, objectClassCsv, userName, password, host, port, nameDb)