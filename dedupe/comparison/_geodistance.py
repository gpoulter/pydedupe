"""Compare the similarity of two geographic coordinates by distance.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from __future__ import division

__license__ = "GPL"

from functools import wraps, partial

from dedupe.indexer import getfield

def geofield(latfield, lonfield, record):
    """Retrive the (latitude,longitude) float pair from a record using
    field specifiers. Returns None if one or both of the fields are empty.
    
    Use partial(geofield, "Lat", "Lon") partial function application to
    configure which fields to retrieve.
    """
    if not (latfield.strip() and lonfield.strip()):
        return None
    lat = float(getfield(record, latfield))
    lon = float(getfield(record, lonfield))
    return (lat,lon)


def is_geo_coordinates(coords):
    """Validates geographic coordinates. Returns True for valid coords, False
    for a missing coordinates, and ValueError for invalid coords.
    
    @param coords: Geographic (latitude, longitude) tuple of coordinates.
    
    @return: True only if coords is a tuple pair of floats in -90.0 to 90.0 
    on the latitude and -180.0 to 180.0 on the longitude.
    """
    if not (isinstance(coords,tuple) and len(coords) == 2
            and (isinstance(coords[0],float) and isinstance(coords[1],float))
            and (-90 < coords[0] < 90 and -180 < coords[1] < 180) ):
        return False
    return True


def geodistance(loc1, loc2):
    """Compare to geographical coordinates by distance. If the distance
    is greater than max_distance, the similarity is 0.  Assumes that
    the coordinates are valid!
    
    @param loc1: (latitude,longitude) of first location.
    @param loc2: (latitude,longitude) of second location.
    @return: Kilometer distance between locations.
    """
    import math
    earth_radius = 6372.0 
    deg2rad = math.pi/180.0
    long1, lat1 = loc1[0]*deg2rad, loc1[1]*deg2rad
    long2, lat2 = loc2[0]*deg2rad, loc2[1]*deg2rad
    cosine_distance = (math.cos(long1-long2) * math.cos(lat1)*math.cos(lat2) +
                       math.sin(lat1)*math.sin(lat2))
    #print loc1, loc2, cosine_distance
    if cosine_distance >= 1.0:
        distance = 0
    else:
        distance = earth_radius * math.acos(cosine_distance)
    if (distance <= 0.003): 
        distance = 0
    return distance


class GeoDistance:
    """Compare two (lat,lon) coordinates. Similarity is 1.0 for identical
    locations, reducing to zero at max_distance in kilometers.
    
    Also returns None (no comparison possible) if either of the
    geographic coordinates is invalid according to L{valid_coordinate}.
    
    @ivar max_distance: The maximum distance in kilometers beyond which
    the similarity is considered to be 0.
    """
    
    def __init__(self, max_distance):
        self.max_distance = max_distance
        
    def __call__(self, point1, point2):
        if not (is_geo_coordinates(point1) and is_geo_coordinates(point2)):
            return None
        distance = geodistance(point1, point2)
        if distance >= self.max_distance:
            return 0.0
        else:
            return 1.0 - (distance / self.max_distance)
