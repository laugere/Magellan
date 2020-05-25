import csv
import psycopg2
import argparse
import os
import subprocess
import json


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
        for Object in objects:
            command = "ogr2ogr -overwrite -f GeoJSON -oo SPLIT_MULTIPOINT=ON -oo ADD_SOUNDG_DEPTH=ON -oo RECODE_BY_DSSI=ON \"/vsistdout/\" \"{0}\" {1}".format(cell, Object.acronym)
            CELLID = os.path.basename(cell).split('.')[0]
            if not os.path.exists("{0}/{1}/{2}.json".format(tempDir, CELLID, Object.acronym)) or isUpdate:
                result = subprocess.Popen(command, cwd=envGDAL, stdout=subprocess.PIPE)
                resultJson = result.communicate()[0]
                result.wait()
                if resultJson != b'':
                    try:
                        objet = json.loads(resultJson)
                        for feature in objet['features']:
                            properties = feature['properties']
                            properties.update(CELLID = CELLID)
                        if not os.path.exists("{0}".format(tempDir)):
                            os.mkdir("{0}".format(tempDir))
                        if not os.path.exists("{0}/{1}".format(tempDir, CELLID)):
                            os.mkdir("{0}/{1}".format(tempDir, CELLID))
                        with open("{0}/{1}/{2}.json".format(tempDir, CELLID, Object.acronym), 'w') as file:
                            file.write(json.dumps(objet))
                            file.close()
                    except OSError as err:
                        print(err)
                        pass
                    except:
                        pass
            elif isResume:
                pass
    for cell in listCells:
        print("extract cell {0}".format(cell))
        i = 0
        for Object in objects:
            CELLID = os.path.basename(cell).split('.')[0]
            if os.path.exists("{0}/{1}/{2}.json".format(tempDir, CELLID, Object.acronym)):
                print("extract object {0}".format(Object.acronym))
                command = "ogr2ogr -update -append -skipfailures -f PostGreSQL PG:\"host={0} user={1} password={2} dbname={3}\" \"{4}\" {5}".format(host, user, password, database, "{0}/{1}/{2}.json".format(tempDir, CELLID, Object.acronym), Object.acronym)
                result = subprocess.Popen(command, cwd=envGDAL, stdout=subprocess.PIPE)
                i += 1
                if(i >= 30):
                    result.wait()
                    i = 0



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