import os
import sys
import csv
import psycopg2
import time


## MAIN COMMAND FOR INITIALIZE DATABASE
def InitDatabase(DatabaseName, Host, Port, User, Password):
    Connection = psycopg2.connect(user = User, password = Password, host = Host, port = Port, database = DatabaseName)
    Cursor = Connection.cursor()

    ListAttribute = GetAttributesTypeList()

    for Object in GetObjectClass("GDALCSV/s57objectclasses.csv", 2):
        print("______________________________________________________________________")
        print("Création de la table {0}".format(Object))
        print("______________________________________________________________________")
        Query = 'CREATE TABLE "{0}" (wkb_geometry geometry);'.format(Object.lower())
        Cursor.execute(Query)
        Connection.commit()
        for Attribute in GetAttributes()[GetObjectClass("GDALCSV/s57objectclasses.csv", 2).index(Object)]:
            if Attribute != "":
                print("Insertion de la colonne {0}".format(Attribute))
                _Type = GetAttributeType(ListAttribute, Attribute.lower())
                Query = 'ALTER TABLE "{0}" ADD COLUMN "{1}" {2}'.format(Object.lower(), Attribute.lower(), _Type)
                Cursor.execute(Query)
                Connection.commit()

    return 0 

## READ CSV 
def GetObjectClass(CSVFile, Row):
    ObjectClass = []

    with open(CSVFile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row != []:
                ObjectClass.append(row[Row])
        
    return ObjectClass

## RETURN ATTRIBUTE LIST FROM CSV
def GetAttributesTypeList():
    Liste = []

    ListAttribute = []
    ListType = []

    for Attribute in GetObjectClass("GDALCSV/s57attributes.csv", 2):
        ListAttribute.append(Attribute)
    for Type in GetObjectClass("GDALCSV/s57attributes.csv", 3):
        ListType.append(Type)
    for Object in GetObjectClass("GDALCSV/s57attributes.csv", 2):
        Liste.append([ListAttribute[GetObjectClass("GDALCSV/s57attributes.csv", 2).index(Object)], ListType[GetObjectClass("GDALCSV/s57attributes.csv", 2).index(Object)]])

    return Liste

## RETURN TYPE OF ATTRIBUTE (USE GETATTRIBUTETYPELIST)
def GetAttributeType(ListAttribute, Attribute):
    AttributeType = "TEXT"

    for Type in ListAttribute:
        if Type[0].lower() == Attribute:
            if Type[1] == "E":
                AttributeType = "INT"
            elif Type[1] == "L":
                AttributeType = "VARCHAR"
            elif Type[1] == "S":
                AttributeType = "TEXT"
            elif Type[1] == "F":
                AttributeType = "FLOAT"
            elif Type[1] == "I":
                AttributeType = "INT"
            elif Type[1] == "A":
                AttributeType = "VARCHAR"
    
    return AttributeType

## RETURN LISTE OF ATTRIBUTES BY OBJECT
def GetAttributes():
    Liste = []
    _Counter = 0

    for Object in GetObjectClass("GDALCSV/s57objectclasses.csv", 2):
        _Part1 = GetObjectClass("GDALCSV/s57objectclasses.csv", 3)[_Counter].split(';')
        _Part2 = GetObjectClass("GDALCSV/s57objectclasses.csv", 4)[_Counter].split(';')
        _Part3 = GetObjectClass("GDALCSV/s57objectclasses.csv", 5)[_Counter].split(';')

        Liste.append(_Part1 + _Part2 + _Part3)
        _Counter = _Counter + 1

    for Object in Liste:
        for Attribute in Object:
            if Attribute == '':
                del Object[Object.index(Attribute)]

    return Liste


########################################
####### MAIN COMMAND FOR INIT ##########
########################################
try:
    InitDatabase(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
except:
    print('COMMAND USAGE : py InitDatabase.py < Database Name > < Host Database > < Port > < User Name > < Password >')
    