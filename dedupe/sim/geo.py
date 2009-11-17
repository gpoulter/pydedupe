"""
:mod:`sim.geo` -- Geographic comparisons
===============================================

.. module:: sim.geo
   :synopsis: Calculate distance and similarity between geographic coordinates.
.. moduleauthor:: Graham Poulter
"""

from __future__ import division


def field(latfield, lonfield, record):
    """Return floating (latitude,longitude) from a record using field
    specifiers latfield and lonfield. Returns None if any TypeError or
    ValueError occure during retrieval and conversion to floating point.
    
    Use for example geo=partial(geofield, "Lat", "Lon") partial function
    application to configure which fields to retrieve using geo(record) ==
    (lat,lon)
    
    >>> from functools import partial
    >>> from collections import namedtuple
    >>> getter = partial(field, "Lat", "Lon")
    >>> Record = namedtuple("Record", ("FullName","Lon","Lat"))
    >>> getter(Record("Joe Bloggs", 10.0, 20.0))
    (20.0, 10.0)
    """
    from . import getvalue
    try:
        lat = float(getvalue(record, latfield))
        lon = float(getvalue(record, lonfield))
    except (TypeError, ValueError):
        return None
    return (lat,lon)


def valid(coords):
    """Check whether the argument constitutes valid geographic coordinates. 

    :type coords: (float, float)
    :param coords: Geographic (latitude, longitude) tuple of coordinates.
    
    :rtype: bool
    :return: True only if coords is a tuple pair of floats in -90.0 to 90.0\
    on the latitude and -180.0 to 180.0 on the longitude.
    
    >>> valid((0.0,0))
    False
    >>> valid((0.0,0.0))
    True
    >>> valid((0.0,90.0))
    True
    >>> valid((91.0,0.0))
    False
    >>> valid(None)
    False
    >>> valid((-1.0,-1.0))
    True
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
    
    :type loc1, loc2: float, float
    :param loc1, loc2: (latitude,longitude) of two locations
    :rtype: float
    :return: Kilometer distance between locations.

    
    >>> km_per_degree = 111.21
    >>> distance((0.0,0.0),(1.0,0.0))
    111.21237993706758
    >>> distance((0.0,0.0),(0.0,1.0))
    111.21237993706758
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
    
    Also returns :keyword:`None` (no comparison possible) if either of the
    geographic coordinates is invalid according to L{valid_coordinate}.
    
    :param max_distance: The maximum distance in kilometers beyond which\
    the similarity is considered to be 0.
    
    Set the maximum to be 1.5 degrees (for 0 similarity), Therefore 1 degree
    should have 33% similarity, to two decimal places

    >>> from functools import partial
    >>> km_per_deg = 111.21237993706758
    >>> geocompare = partial(compare, km_per_deg*1.5)
    >>> geocompare((0.0,0.0), (1.0,0.0))
    0.33333333333333337
    """
    if not (valid(point1) and valid(point2)):
        return None
    dist = distance(point1, point2)
    if dist >= max_distance:
        return 0.0
    else:
        return 1.0 - (dist / max_distance)

