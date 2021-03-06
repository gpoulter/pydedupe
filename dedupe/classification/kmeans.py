"""K-Means clustering of vectors into match/non-match

Please note that K-Means training results in two centroid vectors, one for
matches and one for non-matches.  Each similarity vector (for a pair of input
records) is classified by whether the match or non-match centroid is closer.

This results in a linear classification threshold, and the accuracy
is low when there are lots of dimensions or missing values.
"""
from __future__ import division
import logging
import math

LOG = logging.getLogger('dedupe.kmeans')


def classify(comparisons, distance, maxiter=10):
    """Classify record pair similarity vectors as matches and non-matches
    using K-Means (K=2) clustering around match and non-match centroids.

    .. note:: match and nonmatch centroids are initialised using the
       largest and smallest occuring values for each component respectively.

    .. note: :keyword:`None` values in vectors are handled by removing the
       null'ed component for vector distance calculation and totals for
       averaging.

    :type comparisons: {(`R`, `R`):[:class:`float`, ...], ...}
    :param comparisons: similarity vectors of compared record pairs.
    :type distance: function([`float`, ...], [`float`, ...]) `float`
    :param distance: calculates distance between similarity vectors.
    :type maxiter: :class:`int`
    :param maxiter: maximum number of loops to adjust the centroid
    :rtype: {(`R`, `R`): `float`}, {(`R`, `R`): `float`}
    :return: classifier scores for match pairs and non-match pairs

    >>> ## simple test of clustering 1D vectors
    >>> from dedupe.classification.distance import L2
    >>> from dedupe.classification import kmeans
    >>> matches, nomatches = kmeans.classify(
    ...   comparisons={(1, 2):[0.5], (2, 3):[0.8], (3, 4):[0.9], (4, 5):[0.0]},
    ...   distance = L2)
    >>> sorted(matches.keys())
    [(1, 2), (2, 3), (3, 4)]
    >>> sorted(nomatches.keys())
    [(4, 5)]

    >>> ## cluster 2D vectors with some nulled components
    >>> matches, nomatches = kmeans.classify(
    ...  comparisons= {(1, 2):[0.5, None], (2, 3):[0.8, 0.7],
    ...                (3, 4):[0.9, 0.5], (4, 5):[0.0, 0.5]},
    ...  distance = L2)
    >>> sorted(matches.keys())
    [(1, 2), (2, 3), (3, 4)]
    >>> sorted(nomatches.keys())
    [(4, 5)]
    """
    # pylint:disable=C0103
    # Get length of the comparison vector
    if len(comparisons) == 0:
        return set(), set()
    k, v = comparisons.popitem()
    vlen = len(v)
    vidx = range(vlen)
    comparisons[k] = v
    LOG.debug("name=KMeansInit dimension=%s maxiter=%s", vlen, maxiter)
    str_vector = lambda vector: "[" + ", ".join(
        "%.4f" % v if v is not None else "None" for v in vector) + "]"
    safe_div = lambda n, d: n / d if d > 0 else None

    # Get initial centroids
    high_centroid = [max(x[i] for x in comparisons.itervalues()
                          if x[i] is not None) for i in vidx]
    low_centroid = [min(x[i] for x in comparisons.itervalues()
                         if x[i] is not None) for i in vidx]
    LOG.debug("name=KMeansMatch centroid=%s", str_vector(high_centroid))
    LOG.debug("name=KMeansNonMatch centroid=%s", str_vector(low_centroid))

    # Mapping key to (value, class assignment).
    # All items initially assigned to the "False" class (non-match).
    assignments = dict((k, [v, False]) for k, v in comparisons.iteritems())
    # Number of items that changed class
    n_changed = 1
    # Number of classifier iterations
    iters = 0

    while n_changed > 0 and iters < maxiter:
        n_changed = 0
        iters += 1

        # Sums for the values in the high/low classes
        high_total = [0.0] * vlen
        low_total = [0.0] * vlen
        # Number of non-None values in each component for high/low class
        high_count = [0] * vlen
        low_count = [0] * vlen

        # Now assign the vectors to centroids
        for k, (v, match) in assignments.iteritems():
            dist_high = distance(v, high_centroid)
            dist_low = distance(v, low_centroid)
            if dist_high < dist_low:
                if not match:
                    n_changed += 1
                assignments[k][1] = True  # Set match to True
                for i in vidx:
                    if v[i] is not None:
                        high_total[i] += v[i]
                        high_count[i] += 1
            else:
                if match:
                    n_changed += 1
                assignments[k][1] = False  # Set match to False
                for i in vidx:
                    if v[i] is not None:
                        low_total[i] += v[i]
                        low_count[i] += 1

        high_centroid = [safe_div(high_total[i], high_count[i]) for i in vidx]
        low_centroid = [safe_div(low_total[i], low_count[i]) for i in vidx]

        LOG.debug("name=Iteration iters=%s changed=%s match=%s nonmatch=%s",
                  iters, n_changed, str_vector(high_centroid),
                  str_vector(low_centroid))

    # Calculate a smoothed score as the log of the ratio of distances
    # of the similarity vector to each of the centroids.
    score = lambda v: math.log10((distance(v, low_centroid) + 0.1)
                                  / (distance(v, high_centroid) + 0.1))
    matches = dict((k, score(v))  for k, (v, match)
                   in assignments.iteritems() if match)
    nomatches = dict((k, score(v)) for k, (v, match)
                     in assignments.iteritems() if not match)
    LOG.debug("name=KMeansFinished comparisons=%s, matches=%s, nonmatches=%s",
              len(comparisons), len(matches), len(nomatches))
    return matches, nomatches
