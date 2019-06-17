# Magellan

### Introduction

Application for extract S57 map in PostGis Database.

### Getting Started
#### Basic Commmand
    py Magellan.py < S57 Folder Path > < Host Database > < User Name > < Password > < Database Name >
>Extract S57 file to PostGis Database.

#### InitMagellan Commmand
    py InitMagellan.py < GDAL installation folder path > < GDAL-data folder path >
>Initialize environment variables for GDAL.

#### InitDatabse Commmand
    py InitDatabase.py < Database Name > < Host Database > < User Name > < Password > < Port >
>Initialize S57 database with all objects and their attributes.

### Files

    GDALCSV\*
>CSV for InitDatabase.

    InitDatabase.py
>Initialize S57 database with all objects and their attributes.

    InitMagellan.py
>Initialize environment variables for GDAL.

    Magellan.py
>A main program for extract S57 file to PostGis Database.
