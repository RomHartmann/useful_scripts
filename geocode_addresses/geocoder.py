#Roman Hartmann
#roman@dotmodus.com
#---------
#This script takes full street addresses from input csv, runs them through the google maps
#geocoding api, and writes results to output csv
#---------
#--external libraries used:
#pip install geolocation-python


from geolocation.google_maps import GoogleMaps
oGoogleMaps = GoogleMaps(api_key='AIzaSyDBkYIaHDM2ixsPpjyKAiSozYuIAx7rQTc') 

import csv
sCsvIn = "addresses_by_subnum.csv"
sCsvOut = "latlngs_by_subnum.csv"

i=0     #line counter

with open(sCsvOut, 'w') as fOut:
    oWriter = csv.writer(fOut)
    oWriter.writerow(["subnum", "address_lat_i", "address_lng_i"])
    
    with open(sCsvIn, 'r') as fIn:
        oReader = csv.reader(fIn)
        next(fIn)       #skip heading
        for lRow in oReader:
            i+= 1
            sSubnum = lRow[0]
            sAddress = lRow[1]
            print "{0}:\t{1} \t{2}".format(i, sSubnum, sAddress)
            
            if sAddress != "":
                oLocation = oGoogleMaps.search(location=sAddress) # sends search to Google Maps.
                
                try:
                    oFirstLocation = oLocation.first() # returns only first location.
                    sLat = oFirstLocation.lat
                    sLng = oFirstLocation.lng
                except AttributeError:
                    #if no hits
                    sLat = ""
                    sLng = ""
                
            else:
                sLat = ""
                sLng = ""
            
            oWriter.writerow([sSubnum, sLat, sLng])





