"""
Distances between similarity vectors
====================================

These distance functions drop dimensions where one or both of the vectors have
None instead of a numeric value.  We feel that lowering dimensionality in
response to missing values is better than replacing the None with a default
similarity value (such as 0.2).

.. moduleauthor:: Graham Poulter
"""

import math

def L2(vec1, vec2):
    """Return L2 Euclidian distance between two vectors. 
    
    .. note:: components with :keyword:`None` in one or both of the vectors
       are ignored (reduced dimensionality of the comparison).
    
    :type vec1, vec2: [:class:`float` | :keyword:`None`,...]
    :param vec1, vec2: Nullable floating-point vectors of the same length.
    :rtype: :class:`float`
    :return: Euclidian (pythagorean) distance between `vec1` and `vec2`
    
    >>> from dedupe.classification.distance import L2, normL2
    >>> import math
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
    """Normalised L2 distance, also called the Mahalanobis distance with a
    diagonal covariance matrix. 
    
    .. note:: components with :keyword:`None` in one or both of the vectors
       are ignored (reduced dimensionality of the comparison).

    .. note:: the difference between any two components of the vector 
       is divided by the standard deviation, thus normalising the per-component
       distance measures.
    
    The principle is that a point can be considered "close" to a cluster of
    points if it is less than one standard deviation from the centroid of the
    cluster defined by items known to be members. Setting stdev[0]=0.5, for
    example, is equivalent to the first component range from 0.0 to 2.0
    instead of from 0.0 to 1.0, and defines "close" as being "less than 0.5
    away". If stdev has not been empirically estimated, the thumb-suck for
    each component should be the absolute difference below which the values
    should be considered "close".

    :type vec1, vec2: [:class:`float` | :keyword:`None`,...]
    :param vec1, vec2: Nullable floating-point vectors of the same length.
    :type stdevs: [:class:`float`,...]
    :param stdevs: standard deviations of vector components. 
    :rtype: :class:`float`
    :return: Euclidian (pythagorean) distance between `vec1` and `vec2`
    
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
