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
        self.attributes = attribute_A + attribute_B + attribute_C
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


def sendFunctionToSql(user, password, host, port, database):
    connection = psycopg2.connect(user = user, password = password, host = host, port = port, database = database)
    cursor = connection.cursor()
    for _dir, _file, _filenames in os.walk(os.path.join("SQL")):
        for _files in sorted(_filenames):
            _name = os.path.splitext(_files)[0]
            _ext = os.path.splitext(_files)[1]
            function = open(_dir + os.sep + _files)
            query = function.read()
            cursor.execute(query)
            connection.commit()
            function.close()

## ## send object
def sendObjectToSql(attributes, objects, user, password, host, port, database):
    connection = psycopg2.connect(user = user, password = password, host = host, port = port, database = database)
    cursor = connection.cursor()
    try:
        query = "CREATE EXTENSION postgis;"
        cursor.execute(query)
        connection.commit()
    except:
        print("Extension Postgis already exist in this database")
        connection.rollback()
    for Object in objects:
        createQuery = "CREATE TABLE IF NOT EXISTS \"{0}\" (wkb_geometry geometry);".format(Object.acronym.upper())
        if createQuery != "":
            try:
                cursor.execute(createQuery)
                connection.commit()
            except:
                print("Un problème avec la création de la table {0}".format(Object.acronym))
                connection.rollback()
    for Object in objects:
        query = "ALTER TABLE \"{0}\" ADD COLUMN id SERIAL PRIMARY KEY;".format(Object.acronym.upper())
        try:
            cursor.execute(query)
            connection.commit()
        except:
            print("La création de la clé primaire (id) n'a pas pu s'effectuer")
    for Object in objects:
        tableQuery = ""
        if Object.attributes:
            tableQuery = tableQuery + getAttributeSql(Object.acronym, attributes, Object.attributes)
        if tableQuery != "":
            try:
                cursor.execute(tableQuery)
                connection.commit()
            except:
                print("la table {0} est déjà initializé".format(Object.acronym))
                connection.rollback()


## ## send s57
def sends57ToSql(s57Dir, attributes, objects, user, password, host, port, database):
    connection = psycopg2.connect(user = user, password = password, host = host, port = port, database = database)
    cursor = connection.cursor()
    listCells = []
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
        s57Attributes = attributes
        for i in range(chartFile.GetLayerCount()):
            layer = chartFile.GetLayer(i)
            for s57ObjectClasse in s57ObjectClasses:
                if s57ObjectClasse.acronym == layer.GetName():
                    defn = layer.GetLayerDefn()
                    if verbose:
                        print(layer.GetName())
                        print(layer.GetFeatureCount())
                    for j in range(layer.GetFeatureCount()):
                        listObject = []
                        feature = layer.GetNextFeature()
                        geom = feature.geometry()
                        listObject.append(["CELLID", CELLID])
                        if geom != None:
                            if geom.GetGeometryName() == "MULTIPOINT" and layer.GetName() == "SOUNDG":
                                sqlRequest = ""
                                for n in range(defn.GetFieldCount()):
                                    layerDefn = defn.GetFieldDefn(n)
                                    for s57Attribute in s57Attributes:
                                        if s57Attribute.acronym == layerDefn.GetName():
                                            listObject.append([layerDefn.GetName(), feature.GetField(layerDefn.GetName())])
                                listObject.append(["DEPTH", None])
                                listObject.append(["wkb_geometry", None])
                                for i in range(geom.GetGeometryCount()):
                                    point = geom.GetGeometryRef(i)
                                    listObject[-2] = ["DEPTH", point.GetZ()]
                                    listObject[-1] = ["wkb_geometry", point]
                                    sqlRequest += createSQLQuery(listObject, layer.GetName())
                            else:
                                listObject.append(["wkb_geometry", geom])
                                for n in range(defn.GetFieldCount()):
                                    layerDefn = defn.GetFieldDefn(n)
                                    for s57Attribute in s57Attributes:
                                        if s57Attribute.acronym == layerDefn.GetName():
                                            listObject.append([layerDefn.GetName(), feature.GetField(layerDefn.GetName())])
                                sqlRequest = createSQLQuery(listObject, layer.GetName())
                        else:
                            for n in range(defn.GetFieldCount()):
                                layerDefn = defn.GetFieldDefn(n)
                                for s57Attribute in s57Attributes:
                                    if s57Attribute.acronym == layerDefn.GetName():
                                        listObject.append([layerDefn.GetName(), feature.GetField(layerDefn.GetName())])
                            sqlRequest = createSQLQuery(listObject, layer.GetName())
                        sqlRequest = sqlRequest.encode("utf-8", "replace").decode("utf-8", "replace")
                        cursor.execute(sqlRequest)
                        connection.commit()
    if verbose:
        print("Fin du process")



def createSQLQuery(listObject, layerName):
    if verbose:
        print("Extraction de la couche {0} en cours ...".format(layerName))
        print("Création de la requete SQL en cours ...")
    sqlRequest = "INSERT INTO \"{0}\" (".format(layerName.upper())
    i = 0
    for s57Object in listObject:
        if i == 0:
            sqlRequest += '\"' + str(s57Object[0]) + '\"'
            i += 1
        else:
            sqlRequest += ', ' + '\"' + str(s57Object[0]) + '\"'
    sqlRequest += ") VALUES ("
    i = 0
    for s57Object in listObject:
        if i == 0:
            if str(s57Object[1]) != "None":
                sqlRequest += '\'' + str(s57Object[1]).replace('[', '').replace('\'', '').replace(']','') + '\''
            else:
                sqlRequest += 'NULL'
            i += 1
        else:
            if str(s57Object[1]) != "None":
                sqlRequest += ', ' + '\'' + str(s57Object[1]).replace('[', '').replace('\'', '').replace(']','') + '\''
            else:
                sqlRequest += ', ' + 'NULL'
    sqlRequest += ");"
    if verbose:
        print("Fin de la création de la requête SQL")
    return sqlRequest



## ## get attribute sql command
def getAttributeSql(objectAcronym, globalAttributes, objectAttributes):
    sqlQuery = ""
    for objectAttribute in objectAttributes.split(';'):
        if objectAttribute:
            for globalAttribute in globalAttributes:
                if objectAttribute == globalAttribute.acronym:
                    sqlQuery = sqlQuery + "ALTER TABLE \"{0}\" ADD COLUMN \"{1}\" {2};".format(objectAcronym.upper(), objectAttribute, GetAttributeType(globalAttribute.attributeType))
                    break
    if objectAcronym != "DSID":
        sqlQuery = sqlQuery + "CREATE INDEX index_{0} ON \"{1}\" (\"CELLID\", \"LNAM\");".format(objectAcronym.upper(), objectAcronym)
    else:
        sqlQuery = sqlQuery + "CREATE INDEX index_{0} ON \"{1}\" (\"CELLID\");".format(objectAcronym.upper(), objectAcronym)
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


## ## prepare for update
def prepareForUpdate(s57Dir, userName, password, host, port, nameDb):
    connection = psycopg2.connect(user = userName, password = password, host = host, port = port, database = nameDb)
    cursor = connection.cursor()
    if verbose:
        print("preparing for update ...")
        print("delete all cell from country ...")
    listCells = []
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
        query = "SELECT * FROM s57_drop_cell(\'{0}\')".format(CELLID)
        try:
            cursor.execute(query)
            connection.commit()
        except:
            print("La requête n'a pas fonctionné peut être que la function n'est pas initialisé")


argparser = argparse.ArgumentParser()

argparser.add_argument("--initDatabase", help="Initialize Database for Magellan", action="store_true")
argparser.add_argument("--csvAttribute", default="GDALCSV\\s57attributes.csv", help="Change s57attribute.csv path")
argparser.add_argument("--csvObjectClasses", default="GDALCSV\\s57objectclasses.csv", help="Change s57objectClasses path")
argparser.add_argument("--update", help="update overwrite temp and data into the database for updating cells", action="store_true")
argparser.add_argument("--verbose", help="Verbose for talk about the process", action="store_true")
argparser.add_argument("s57Dir", help="s57 chart path")
argparser.add_argument("userName", help="Username of the database")
argparser.add_argument("password", help="Password of the database")
argparser.add_argument("host", help="Address of the database")
argparser.add_argument("port", help="Port of the database")
argparser.add_argument("nameDb", help="name of the database")

args = argparser.parse_args()

verbose = args.verbose
csvAttribute = args.csvAttribute
csvObjectClasses = args.csvObjectClasses
s57Dir = args.s57Dir
userName = args.userName
password = args.password
host = args.host
port = args.port
nameDb = args.nameDb

isUpdate = args.update

attributeCsv = getObjectFromCsv(csvAttribute, "attribute")
objectClassCsv = getObjectFromCsv(csvObjectClasses, "objectClasse")

if args.initDatabase:
    sendObjectToSql(attributeCsv, objectClassCsv, userName, password, host, port, nameDb)
    sendFunctionToSql(userName, password, host, port, nameDb)

if isUpdate:
    prepareForUpdate(s57Dir, userName, password, host, port, nameDb)

sends57ToSql(s57Dir, attributeCsv, objectClassCsv, userName, password, host, port, nameDb)