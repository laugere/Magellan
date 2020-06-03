import os.path
import osgeo.ogr
import csv


## class
## ## objectClasses
class objectClasse:
    def __init__(self, code, objectClass, acronym, attribute_A, attribute_B, attribute_C, classe, primitives):
        self.code = code
        self.objectClass = objectClass
        self.acronym = acronym
        self.genericAttribute = "CELLID;FIDS;RCID;PRIM;GRUP;OBJL;RVER;AGEN;FIDN;FIDS;LNAM;LNAM_REFS;FFPT_RIND;"
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


s57srcFile = os.path.join("D:", "Charts", "finish", "ENC_BE", "ENC_ROOT", "BE", "BE3VLBNK", "31", "0", "BE3VLBNK.000")
csvObjectClassePath = os.path.join("D:", "GDALCSV", "magellanS57objectClasses.csv")
chartFile = osgeo.ogr.Open(s57srcFile)
s57ObjectClasses = getObjectFromCsv(csvObjectClassePath,"objectClasse")
CELLID = open(s57srcFile)

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
            listObject.append(["CELLID", ])
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
                    sqlRequest += '\'' + str(s57Object[1]) + '\''
                else:
                    sqlRequest += ', ' + '\'' + str(s57Object[1]) + '\''
                i += 1
            sqlRequest += ");"
            print(sqlRequest)

