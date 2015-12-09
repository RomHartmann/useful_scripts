def address_to_coords(sAddress):
    #sAddress is a string
    import urllib2
    import StringIO
    import json
    
    sAddress = sAddress.strip()
    
    sURL_Address = ""
    for s in sAddress:
        if s != " ":
            sURL_Address += s
        elif s == " ":
            sURL_Address += "+"
    
    sURL = "http://maps.google.com/maps/api/geocode/json?address="+sURL_Address+"&sensor=false"
    
    try:
        response = urllib2.urlopen(sURL)
        responseBody = response.read()
        body = StringIO.StringIO(responseBody)
        result = json.load(body)
        
        if result['status'] == "OK":
            lat = result['results'][0]['geometry']['location']['lat']
            lng = result['results'][0]['geometry']['location']['lng']
        else:
            lat = None
            lng = None
    except:
        lat = "Connection_error"
        lng = "Connection_error"
    
    
    return (lat, lng)



def coords_to_address(lat, lng):
    #lat and lng are either float or integer
    import urllib2
    import StringIO
    import json
    
    lat = str(lat)
    lng = str(lng)
    
    sURL = "http://maps.google.com/maps/api/geocode/json?latlng="+lat+","+lng+"&sensor=false"
    
    try:
        response = urllib2.urlopen(sURL)
        responseBody = response.read()
        body = StringIO.StringIO(responseBody)
        result = json.load(body)
        
        if result['status'] == "OK":
            sAddress = result['results'][0]['formatted_address']
        else:
            sAddress = "Sorry, the address to these coordninates could not be found"
        
    except:
        sAddress = "Could not connect to google geocode api"
    
    
    return sAddress

