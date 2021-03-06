from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

coordPoint = Point(lat, lng)
coordPolygon = Polygon(lBoundariesSorted[iB])

coordPolygon.contains(coordPoint)

#---OR---#


    def point_in_poly(x,y,poly):
        """
        function to check if a point is in a 2D polygon
        """
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



