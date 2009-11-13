"""
:mod:`classification.distance` -- Distances between similarity vectors
======================================================================

The functions should handle the presence of "None" values in a similarity
vector (meaning "no comparison possible" on that component), and neglect that
component in the calculation.

.. module:: classification.distance
   :synopsis: Functions to calculate distance between two similarity vectors.
.. moduleauthor:: Graham Poulter

"""

import math

def L2(vec1, vec2):
    """L2 or Euclidian distance between two vectors. Discards vector
    components having None values.
    
    :param vec1, vec2: Equal-length sequences of floating-point values.
    :rtype: float    
    """
    assert len(vec1) == len(vec2)
    return math.sqrt(sum((a-b)**2 
                         for a,b in zip(vec1, vec2) 
                         if a is not None and b is not None))


def normL2(vec1, vec2, stdevs):
    """The normalised L2 distance, being the Mahalanobis distance with a
    diagonal covariance matrix. Discards vector components having None values.
    
    A point can be considered "close" to a cluster of points if it is less
    than one standard deviation from the centroid of the cluster defined by
    items known to be members. Setting stdev[0]=0.5, for example, is
    equivalent to the first component range from 0.0 to 2.0 instead of from
    0.0 to 1.0, and defines "close" as being "less than 0.5 away". Guideline:
    if you are not estimating the stdev empirically, for each vector component
    set it to the absolute difference below which the component values should
    be considered close together.
    
    :param vec1, vec2: Equal-length sequences of floating-point values.
    :param stdevs: Standard deviations of vector components. The difference\
    between two components of a vector are divided by the standard deviation.
    :rtype: float
    """
    assert len(vec1) == len(vec2) == len(stdevs)
    return math.sqrt(sum(((a-b)/s)**2 
                         for a,b,s in zip(vec1, vec2, stdevs) 
                         if a is not None and b is not None))
