import os
import sys

def GDALArchIs64():
    _cmd = os.system(r'setx PATH “%PATH%;C:\OSGeo4W64\bin”')
    _cmd = os.system(r'setx GDAL_DATA “C:\OSGeo4W64\share\gdal”')

def GDALArchIs32():
    _cmd = os.system(r'setx PATH “%PATH%;C:\OSGeo4W\bin”')
    _cmd = os.system(r'setx GDAL_DATA “C:\OSGeo4W\share\gdal”')

def InitGDAL(GDALArch):
    try:
        if (int(GDALArch) == 64):
            GDALArchIs64()
            print('GDAL is initialized (64 architecture)')
        elif (int(GDALArch) == 32):
            GDALArchIs32()
            print('GDAL is initialized (32 architecture)')
        else:
            print('ERROR : py InitMagellan.py < Architecture (64 or 32) >')
    except:
        print('ERROR : Not a valid type for architecture')

########################################
####### MAIN COMMAND FOR INIT ##########
########################################
InitGDAL(sys.argv[1])