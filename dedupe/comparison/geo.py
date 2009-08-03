#!/usr/bin/env python

"""Compare the similarity of two geographic coordinates by distance.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from __future__ import division

from dedupe.indexer import getfield

def field(latfield, lonfield, record):
    """Return floating (latitude,longitude) from a record using field
    specifiers latfield and lonfield. Returns None if any TypeError or
    ValueError occure during retrieval and conversion to floating point.
    
    Use for example geo=partial(geofield, "Lat", "Lon") partial function
    application to configure which fields to retrieve using geo(record) ==
    (lat,lon)
    """
    try:
        lat = float(getfield(record, latfield))
        lon = float(getfield(record, lonfield))
    except (TypeError, ValueError):
        return None
    return (lat,lon)


def valid(coords):
    """Check whether the argument constitutes valid geographic coordinates. 
    
    @param coords: Geographic (latitude, longitude) tuple of coordinates.
    
    @return: True only if coords is a tuple pair of floats in -90.0 to 90.0 
    on the latitude and -180.0 to 180.0 on the longitude.
    """
    if not (isinstance(coords,tuple) and len(coords) == 2):
        return False
    lat, lon = coords
    if not isinstance(lat,float) or not isinstance(lon,float):
        return False
    if (-90 < lat < 90) and (-180 < lon < 180):
        return True
    return False


def distance(loc1, loc2):
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


def compare(max_distance, point1, point2):
    """Compare two (lat,lon) coordinates. Similarity is 1.0 for identical
    locations, reducing to zero at max_distance in kilometers.
    
    Also returns None (no comparison possible) if either of the
    geographic coordinates is invalid according to L{valid_coordinate}.
    
    @ivar max_distance: The maximum distance in kilometers beyond which
    the similarity is considered to be 0.
    """
    if not (valid(point1) and valid(point2)):
        return None
    dist = distance(point1, point2)
    if dist >= max_distance:
        return 0.0
    else:
        return 1.0 - (dist / max_distance)

if __name__=="__main__":
    from sys import argv as a
    print distance((float(a[1]), float(a[2])), (float(a[3]),float(a[4])))
