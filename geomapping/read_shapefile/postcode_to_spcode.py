#roman@dotmodus.com
#
#This script goes through all postcodes' lat longs and finds what shape it belongs to
#the lat longs from each post code must be extracted from the csv
#  and compared to all the shapes to find which subplace code it belongs to.
#  The subplace codes for each shape corresponds in order to its line in Level5
#The results are then saved to subplace_by_postcode
#
#data from  https://github.com/konektaz/shape-files/tree/master/South-Africa
#expl:      https://github.com/konektaz/shape-files/wiki/South-Africa---Census-2011-spatial-metadata

#shapefile library:
#pip install pyshp

import csv
sLatlngs = "latlngs_by_postcode.csv"

import shapefile
oShapeFile = shapefile.Reader("census_shapefiles/SP_SA_2011")
lShapes = oShapeFile.shapes()
llRecords = oShapeFile.records()

lSubPlaceNames = []
for lRecord in llRecords:
    lSubPlaceNames.append([lRecord[1], lRecord[2]])


sOut = "subplace_by_postcode.csv"
fOut = open(sOut, 'w')
oWriter = csv.writer(fOut, delimiter=',')


def point_in_poly(x,y,poly):
    "finds if x and y are in poly"
    n = len(poly)
    inside = False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside



sSubPlaceCode, sSubPlaceName = "", ""

with open(sLatlngs, 'r') as f:
    iTracker = 0
    iTotLen = 3906  
    iTotShapeLen = len(lShapes)
    next(f)        #depending on file header or not
    
    for sLine in f:
        sLine = sLine.strip()
        lLine = sLine.split(",")
        
        sPostCode = lLine[0]
        rLat = float(lLine[1])
        rLng = float(lLine[2])
        
        try:
            iSP = 0
            for oShape in lShapes:
                llCoords = oShape.points
                bInPoly = point_in_poly(rLat, rLng, llCoords)
                
                if bInPoly:
                    sSubPlaceCode, sSubPlaceName = lSubPlaceNames[iSP]
                    #lSubPlaceNames.pop(iSP)     # remove result to make process faster
                    break                       # sp found, and hence continuing to next coord
                
                iSP += 1
        except Exception as e:
            print "Error:  {0}".format(e)
            sSubPlaceCode, sSubPlaceName = "", ""
        
        iTracker += 1
        print "{0}/{1}".format(iTracker, iTotLen)
        lWrite = [sPostCode, rLat, rLng, sSubPlaceCode, sSubPlaceName]
        oWriter.writerow(lWrite)






