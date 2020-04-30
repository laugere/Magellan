# Getting started with Magellan

### Introduction

Application for extract S57 map in PostGis Database. This application uses GDAL to run and extract files in the PostGIS database.

### Prerequisite


* <a href="http://www.gisinternals.com/release.php">GDAL for Windows</a>

### Installation

### GDAL API installation

After installing the GDAL API you have to set your Windows environment variables (GDAL_DATA, GDAL_DRIVER_PATH, GDAL_VERSION, GDAL and PATH)

To open the window for setting environment variables you have to search in windows "environment" and you have to see "Edit the system environment" after that in this window click on "Environment variables" and the variable parameter window environment is open.

**GDAL_DATA** &rarr; Path to gdal-data folder into Gdal installation (example: Program\GDAL\gdal-data)

**GDAL_DRIVER_PATH** &rarr; Path to gdalplugins folder into Gdal installation (example: Program\GDAL\gdalplugins)

**GDAL** &rarr; Path to GDAL installation folder (example: Program\GDAL)

**Path** &rarr; Add a new variable with the Gdal installation folder (example: Program\GDAL)

### How to use

Magellan allows s57 maps to be sent to a PostGis base only it needs to be initialized to work, that's why there is the --initDatabase argument.

> --initDatabase

Also Magellan uses csv files in which there are all the attributes of the basic s57 standard Magellan will use the ones that are in the GDALCSV folder but it is possible to change with the arguments :

> --csvAttribute

> --csvObjectClasses

Otherwise here is the basic command to send a folder ENC_ROOT to the postGIS database (for example the database will be named ENC_ES) by initializing it:

> magellan.py --initDatabase "path/to/tempPath" "path/to/ENC_ROOT/" "username" "password" "host" "port" "ENC_ES"

