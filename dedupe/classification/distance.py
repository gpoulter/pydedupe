"""
:mod:`distance` -- Distances between similarity vectors
=======================================================

.. note:: Vector distance functions should accommodate the presence of
   :keyword:`None` values in the vectors, interpreted as "no comparison possible
   on this component for this vector", and ignore that component for comparisons.
   Alternatively, the distance function may replace :keyword:`None` with a
   default value for missing vector components.

.. module:: distance
   :synopsis: Functions to calculate distance between two similarity vectors.
.. moduleauthor:: Graham Poulter
"""

import math

def L2(vec1, vec2):
    """Return L2 Euclidian distance between two vectors. Ignores dimensions
    that have value :keyword:`None` in one of the vectors.
    
    :param vec1, vec2: Equal-length sequences of floating-point values.
    :rtype: float
    
    >>> L2([2,None],[5,None])
    3.0
    >>> L2([2,None],[5,1])
    3.0
    >>> L2([None,None],[1,1])
    0.0
    >>> L2([2,2],[3,3]) == math.sqrt(2)
    True
    >>> L2([3,2],[3,2])
    0.0
    >>> L2([4,3.0,2,3],[4,1.0,3,3]) == math.sqrt(5)
    True
    """
    assert len(vec1) == len(vec2)
    return math.sqrt(sum((a-b)**2 
                         for a,b in zip(vec1, vec2) 
                         if a is not None and b is not None))


def normL2(vec1, vec2, stdevs):
    """Normalised L2 distance, being the Mahalanobis distance with a
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
    
    
    >>> normL2([2,None],[5,1],[1,1])
    3.0
    >>> normL2([2,2],[3,3],[1,1]) == math.sqrt(2)
    True
    >>> normL2([2,2],[3,3],[0.5,1]) == math.sqrt(5)
    True
    """
    assert len(vec1) == len(vec2) == len(stdevs)
    return math.sqrt(sum(((a-b)/s)**2 
                         for a,b,s in zip(vec1, vec2, stdevs) 
                         if a is not None and b is not None))
