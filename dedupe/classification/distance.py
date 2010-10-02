"""
Distances between similarity vectors
====================================

These distance functions drops any dimensions valued as `None` in either
`vec1` or `vec2`.  The

An alternative to dropping `None`-valued dimensions is to replacing `None`
values in a similarity with a default value, such as 0.2, in cases where a
pair of records cannot be compared on a field due to missing data.  Replacing
a missing similarity with 0.2 puts the similarity vector closer to a
non-match example in nearest-neighbour classification.  Dropping a missing
similarity from the distance calculation excludes it from the decision.

.. moduleauthor:: Graham Poulter
"""

import math


def L2(vec1, vec2):
    """Return L2 Euclidian distance between two vectors.

    This distance function drops any dimensions valued as `None` in either
    `vec1` or `vec2`.

    :type vec1, vec2: tuple of `float`/`None`
    :param vec1, vec2: Floating point vectors
    :rtype: :class:`float`
    :return: Euclidian (Pythagorean) distance between `vec1` and `vec2`

    >>> from dedupe.classification.distance import L2
    >>> import math
    >>> L2([2, None], [5, None])
    3.0
    >>> L2([2, None], [5, 1])
    3.0
    >>> L2([None, None], [1, 1])
    0.0
    >>> L2([2, 2], [3, 3]) == math.sqrt(2)
    True
    >>> L2([3, 2], [3, 2])
    0.0
    >>> L2([4, 3.0, 2, 3], [4, 1.0, 3, 3]) == math.sqrt(5)
    True
    """
    assert len(vec1) == len(vec2)
    return math.sqrt(sum((a - b) ** 2
                         for a, b in zip(vec1, vec2)
                         if a is not None and b is not None))


def normL2(vec1, vec2, stdevs):
    """Normalised L2 distance, also called the Mahalanobis distance with a
    diagonal covariance matrix.

    This distance function drops any dimensions valued as `None` in either
    `vec1` or `vec2`.

    For dimension i, the value |vec1[i]-vec2[i]| is divided by the standard
    deviation stdevs[i].  Plain `L2` distance is `normL2` with 1.0 standard
    deviation in all dimensions.  Larger standard deviation in a dimension
    reduces that dimension's contribution to the total distance.  Setting
    stdev[i]=k is mathematically equivalent to scaling component i of the
    similarity to range over (0, 1/k) instead of (0, 1).

    :type vec1, vec2: [:class:`float` | :keyword:`None`, ...]
    :param vec1, vec2: Nullable floating-point vectors of the same length.
    :type stdevs: [:class:`float`, ...]
    :param stdevs: standard deviations of vector components.
    :rtype: :class:`float`
    :return: Euclidian (pythagorean) distance between `vec1` and `vec2`

    >>> from dedupe.classification.distance import normL2
    >>> import math
    >>> normL2([2, None], [5, 1], [1, 1])
    3.0
    >>> normL2([2, 2], [3, 3], [1, 1]) == math.sqrt(2)
    True
    >>> normL2([2, 2], [3, 3], [0.5, 1]) == math.sqrt(5)
    True
    """
    assert len(vec1) == len(vec2) == len(stdevs)
    return math.sqrt(sum(((a - b) / s) ** 2
                         for a, b, s in zip(vec1, vec2, stdevs)
                         if a is not None and b is not None))
