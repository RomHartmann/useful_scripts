def coords_to_ccg(lng, lat):
    """
    takes coordinates and returns ccg name and code
    """
    
    import json
    import operator
    
    import ast
    
    from shapely.geometry import Point
    from shapely.geometry.polygon import Polygon
    
    fd = open("ccg_kml_dicts")
    sd = fd.read()
    fd.close()
    
    ldData = ast.literal_eval(sd)
    
    
    lNames = [ldData[i]['CCG'] for i in range(len(ldData))]
    lCodes = [ldData[i]['CCG Code'] for i in range(len(ldData))]
    lBoundaries = [ldData[i]['boundary'] for i in range(len(ldData))]
    
    
    ldUnsorted = []
    
    
    #clean up boundaries
    for i in range(len(lBoundaries)):
        
        lBoundaries[i] = lBoundaries[i].split("\n")
        
        lx = []
        ly = []
        
        for j in range(len(lBoundaries[i])):
            lBoundaries[i][j] = lBoundaries[i][j].strip()
            
            lx.append(float(lBoundaries[i][j].split(",")[0]))
            lx.append(float(lBoundaries[i][j].split(",")[0]))
            ly.append(float(lBoundaries[i][j].split(",")[1]))
            ly.append(float(lBoundaries[i][j].split(",")[1]))
            
            lBoundaries[i][j] = (float(lBoundaries[i][j].split(",")[0]), float(lBoundaries[i][j].split(",")[1]))
        
        fXmid = ((min(lx))+(max(lx)))/2
        fYmid = ((min(ly))+(max(ly)))/2
        
        ldUnsorted.append({
            "ccg_name": lNames[i],
            "dist": ((fXmid - lat)**2 + (fYmid - lng)**2)**0.5,
            "boundary": lBoundaries[i],
            "ccg_code": lCodes[i]
            })
        
    
    #order all boundaries by how close they are to the lat lng
    ldSorted = sorted(ldUnsorted, key=lambda t:t['dist'])
    
    lNamesSorted = [ldSorted[i]["ccg_name"] for i in range(len(ldSorted))]
    lCodesSorted = [ldSorted[i]["ccg_code"] for i in range(len(ldSorted))]
    lBoundariesSorted = [ldSorted[i]["boundary"] for i in range(len(ldSorted))]
    
    
    for iB in range(len(lBoundariesSorted)):
        coordPoint = Point(lat, lng)
        coordPolygon = Polygon(lBoundariesSorted[iB])
        if coordPolygon.contains(coordPoint):
            sName = lNamesSorted[iB]
            sCode = lCodesSorted[iB]
            return sName,sCode
    
    return None,None
