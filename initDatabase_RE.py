import csv
import psycopg2
import argparse


## class
## ## objectClasses
class objectClasse:
    def __init__(self, code, objectClass, acronym, attribute_A, attribute_B, attribute_C, classe, primitives):
        self.code = code
        self.objectClass = objectClass
        self.acronym = acronym
        self.genericAttribute = "fid;RCID;PRIM;GRUP;OBJL;RVER;AGEN;FIDN;FIDS;LNAM;LNAM_REFS;FFPT_RIND"
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
            cursor.execute(createQuery)
            connection.commit()
        tableQuery = ""
        tableQuery = getAttributeSql(Object.acronym, attributes, Object.genericAttribute)
        if Object.attribute_A:
            tableQuery = tableQuery + getAttributeSql(Object.acronym, attributes, Object.attribute_A)
        if Object.attribute_B:
            tableQuery = tableQuery + getAttributeSql(Object.acronym, attributes, Object.attribute_B)
        if Object.attribute_C:
            tableQuery = tableQuery + getAttributeSql(Object.acronym, attributes, Object.attribute_C)
        if tableQuery != "":
            cursor.execute(tableQuery)
            connection.commit()


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

argparser.add_argument("--csvAttribute", default="GDALCSV\\s57attributes.csv", help="Change s57attribute.csv path")
argparser.add_argument("--csvObjectClasses", default="GDALCSV\\s57objectclasses.csv", help="Change s57objectClasses path")
argparser.add_argument("userName", help="Username of the database")
argparser.add_argument("password", help="Password of the database")
argparser.add_argument("host", help="Address of the database")
argparser.add_argument("port", help="Port of the database")
argparser.add_argument("nameDb", help="name of the database")

args = argparser.parse_args()

csvAttribute = args.csvAttribute
csvObjectClasses = args.csvObjectClasses
userName = args.userName
password = args.password
host = args.host
port = args.port
nameDb = args.nameDb

sendObjectToSql(getObjectFromCsv(csvAttribute, "attribute"), getObjectFromCsv(csvObjectClasses, "objectClasse"), userName, password, host, port, nameDb)