import os
import sys
import time


def InitGDAL(GDALInstallPath, GDALDataPath):
        _cmd = os.system('setx PATH "{0}"'.format(GDALInstallPath))
        time.sleep( 1 )
        _cmd = os.system('setx GDAL_DATA "{0}"'.format(GDALDataPath))
        print('GDAL is initialized')

########################################
####### MAIN COMMAND FOR INIT ##########
########################################

try:
    InitGDAL(sys.argv[1], sys.argv[2])
except:
    print('ERROR : Not a valid path')
    print('COMMAND USAGE : py InitMagellan.py < GDAL installation folder path > < GDAL-data folder path >')
