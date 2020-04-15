import subprocess
import os

_envGDAL = os.environ["GDAL"]
command = "ogr2ogr -oo SPLIT_MULTIPOINT=ON -skipfailures -f GPKG \"C:\\Users\\marti\\Documents\\Just Magic\\Magellan\\testmcovr.gpkg\" \"C:\\Users\\marti\\Documents\\ENC_Barcelona_Sample\\ES30048C\\6\\0\\ES30048C.000\" M_COVR"
#command = "ogr2ogr -lco ENCODING=UTF-8 -oo SPLIT_MULTIPOINT=ON -update -append -skipfailures -f PostGreSQL PG:\"host=labs.geogarage.com user=martin password=d1frukobRo3a dbname=ENC_ES\" \"C:\\Users\\marti\\Documents\\ENC_Barcelona_Sample\\ES30048C\\6\\0\\ES30048C.000\" SOUNDG"
result = subprocess.Popen(command, cwd=_envGDAL, stdout=subprocess.PIPE)
returnedCode = result.wait()
print(returnedCode)