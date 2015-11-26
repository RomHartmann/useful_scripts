import csv
sLatlngs = "latlngs_by_postcode.csv"

import shapefile
oShapeFile = shapefile.Reader("census_shapefiles/SP_SA_2011")
lShapes = oShapeFile.shapes()


import matplotlib.pyplot as plt
fig, ax1 = plt.subplots()

lPostCoords = []
with open(sLatlngs, 'r') as f:
    next(f)
    for sLine in f:
        sLine = sLine.strip()
        lLine = sLine.split(",")
        sPostCode = lLine[0]
        rLat = float(lLine[1])
        rLng = float(lLine[2])
        lPostCoords.append([rLat, rLng])

for i in range(len(lShapes)):
    llCoords = lShapes[i].points
    lLats = [l[0] for l in llCoords]
    lLngs = [l[1] for l in llCoords]
    ax1.plot(lLats, lLngs)

for i in range(len(lPostCoords)):
    [rPostLat, rPostLng] = lPostCoords[i]
    ax1.plot(rPostLat, rPostLng, 'rx')
    
plt.show()
