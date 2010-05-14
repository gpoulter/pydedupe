"""
Geographic distance and similarity
==================================

.. moduleauthor:: Graham Poulter
"""

from __future__ import division

def field(latfield, lonfield, record):
    """A function to get (lat,lon) coordinates of a record.
    
    :type latfield, lonfield: :class:`str` or :class:`int` or :class:`function`
    :param latfield, lonfield: how to :func:`sim.getvalue` the fields
    :param record: Record from which to retrieve values.
    
    >>> from functools import partial
    >>> from collections import namedtuple
    >>> from dedupe.sim import geo
    >>> Record = namedtuple("Record", ("FullName","Lon","Lat","Phone"))
    >>> getter = partial(geo.field, "Lat", "Lon")
    >>> getter(Record("Joe Bloggs", "10.0", "20.0", "555 1234"))
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

    :type coords: (:class:`float`, :class:`float`)
    :param coords: Geographic (latitude, longitude) tuple of coordinates.
    :rtype: :class:`bool`
    :return: :keyword:`True` only if coords is a tuple pair of floats\
       in -90.0 to 90.0 on the latitude and -180.0 to 180.0 on the longitude.
    
    >>> from dedupe.sim import geo
    >>> geo.valid((0.0,0))
    False
    >>> geo.valid((0.0,0.0))
    True
    >>> geo.valid((0.0,90.0))
    True
    >>> geo.valid((91.0,0.0))
    False
    >>> geo.valid(None)
    False
    >>> geo.valid((-1.0,-1.0))
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
    
    :type loc1, loc2: :class:`float`, :class:`float`
    :param loc1, loc2: (latitude,longitude) of two locations
    :rtype: :class:`float`
    :return: Kilometer distance between locations.

    >>> from dedupe.sim import geo
    >>> # there are 111.21 kilometers per degree at the equator
    >>> geo.distance((0.0,0.0),(1.0,0.0))
    111.21237993706758
    >>> geo.distance((0.0,0.0),(0.0,1.0))
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
    
    :type max_distance: :class:`float`
    :param max_distance: Distance greater than this means similarity of 0.0
    :type point1,point2: (:class:`float`, :class:`float`)
    :param point1,point2: Coordinate pairs to be compared.    
    :rtype: :class:`float` or :keyword:`None`
    :return: scaled imilarity of the points, or :keyword:`None` if missing/invalid.
    
    >>> ## maximum distance is 1.5 degrees, so 1 degree = 1/3 similarity
    >>> from functools import partial
    >>> from dedupe.sim import geo
    >>> km_per_deg = 111.21237993706758
    >>> compare = partial(geo.compare, km_per_deg*1.5)
    >>> compare((0.0,0.0), (1.0,0.0))
    0.33333333333333337
    """
    if not (valid(point1) and valid(point2)):
        return None
    dist = distance(point1, point2)
    if dist >= max_distance:
        return 0.0
    else:
        return 1.0 - (dist / max_distance)

