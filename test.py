import subprocess
import os
import json

envGDAL = os.environ["GDAL"]
command = "ogr2ogr -f GeoJSON -oo SPLIT_MULTIPOINT=ON -oo ADD_SOUNDG_DEPTH=ON -oo RECODE_BY_DSSI=ON \"/vsistdout/\" \"C:/Users/marti/Documents/ENC_Barcelona_Sample/ES200303/6/0/ES200303.000\" M_COVR"
CELLID = os.path.basename("C:/Users/marti/Documents/ENC_Barcelona_Sample/ES200303/6/0/ES200303.000").split('.')[0]
result = subprocess.Popen(command, cwd=envGDAL, stdout=subprocess.PIPE)
#result.wait()
objet = json.loads(result.communicate()[0])
for feature in objet['features']:
    properties = feature['properties']
    properties.update(cellid = CELLID)

print(json.dumps(objet))