"""Functions for encoding and comparing geographic coordinates.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from __future__ import division

__license__ = "GPL3"

from functools import wraps, partial
from indexer import getfield

def geofield(latfield, lonfield, record):
    """Retrive the (latitude,longitude) float pair from a record using
    field specifiers. Returns None if one or both of the 
    fields are empty strings."""
    if not (latfield.strip() and lonfield.strip()):
        return None
    lat = float(getfield(record, latfield))
    lon = float(getfield(record, lonfield))
    return (lat,lon)

def handle_missing(comparator, missing_weight=None, is_present=bool):
    """Wraps a comparator to handle missing values.
    @param comparator: Function taking two values and returning their similarity.
    @param missing_weight: What to return whene one/both of the values is not present.
    @param is_present: Predicate to determines whether the value is present.
    """
    @wraps(comparator)
    def wrapped_compare(x, y):
        """Compare the values only if both are valid."""
        if not (is_present(x) and is_present(y)):
            return missing_weight
        else:
            return comparator(x,y)
    return wrapped_compare

def transform_linear(value, inputrange, outputrange, none_value=None):
    """Scale a value from the input range to the output range, such that the
    left-end value of the input is matched to the left-end value in the
    output.  Values past the ends of the input range are mapped to the
    correspondind ends of the output range:
    
    For example scale_linear_clipped(4, (0,5), (1,0)) == 0.2, because
    [0,5] has been mapped onto [1,0]
    
    @param value: Floating point value to scale.
    @param inputrange: (leftend,rightend) for the input range.
    @param outputrange: (leftend,rightend) for the output range.
    @paran none_value: For "value is None", return this value.
    """
    from operator import __lt__, __gt__
    in_L, in_R = inputrange
    out_L, out_R = outputrange
    if value is None: return none_value
    outside = __lt__ if in_L < in_R else __gt__
    if outside(value, in_L): return out_L
    if outside(in_R, value): return out_R
    return out_L + (value-in_L) * (out_R-out_L) / (in_R-in_L)

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

def valid_coordinate(coords):
    """Validates geographic coordinates. Returns True for valid coords, False
    for a missing coordinates, and ValueError for invalid coords."""
    if not coords:
        return False
    if not (isinstance(coords,tuple) and len(coords) == 2
            and (isinstance(coords[0],float) and isinstance(coords[1],float))
            and (-90 < coords[0] < 90 and -180 < coords[1] < 180) ):
        raise ValueError("Invalid coordinate: %s" % str(coords))
    return True

def make_geo_comparator(max_distance):
    """Create comparator of geographical locations.
    @param max_distance: Maximum distance, at which similarity becomes 0.
    @return: Comparison function taking two (lat,lon) floating 
    point tuples that returns similarity in the range (0,1).
    """
    # Handle missing and invalid values
    geo_distance_safe = handle_missing(geodistance, None, valid_coordinate)
    # Scale the distances
    scale = partial(transform_linear, inputrange=(0,max_distance), outputrange=(1.0,0.0))
    # Create comparison function
    def geocompare(loc1, loc2):
        """Compare two (lat,lon) coordinates. Similarity is 1.0 for identical
        locations, reducing to zero at the maximum distance."""
        return scale(geo_distance_safe(loc1,loc2))
    return geocompare
