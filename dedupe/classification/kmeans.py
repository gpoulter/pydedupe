"""
:mod:`kmeans` -- K-Means vector clustering
==========================================

K-means clustering of similarity vectors into two groups (matches and
non-matches), that is K=2.

This is a special K-Means implementation which handles "None" values
for similarity, which occur when two field values could not be compared,
due to missing or invalid values in one or both of the compared records.

FEBRL assigns arbitrary weights to non-comparisons, such as "0.2" or "0", to
treat "unable to compare" in the same manner as "total mismatch".

In this module, we instead model occurrences of None as reduced-dimensionality
vectors. That is, (0.95,0.2,None,0.5) is treated like a
3-dimensional vector in distance calculations.

In centroid calculation, a None does contributes to the mean by reducing the
denominator of the averaging step for that component.

.. todo:: Revise kmeans docs

.. module:: kmeans
   :synopsis: Cluster match and non-match vectors using K=2 K-means.
.. moduleauthor:: Graham Poulter
"""

from __future__ import division

import logging, math

def classify(comparisons, distance, maxiter=10):
    """Classify each pair of comparisons as match or nonmatch, by clustering
    weight vectors around "match centroind" and "nonmatch centroid". 
    
    The match/nonmatch centroids are initialised using the largest/smallest
    occuring value for each component.
       
    :param comparisons: mapping (rec1,rec2):weights from record pair to\
    field-by-field comparison vector.
    
    :param distance: Function distance(v1,v2) of two similarity vectors\
    returninng the floating point distance between them, discarding components\
    having a None value.
    
    :param maxiter: Maximum number of loops for adjusting the centroid.
    
    :return: two mappings, one for matched pairs and one for non-matched pairs,\
    mapping (record1,record2) to classifier score.
    
    >>> ## simple test of clustering 1D vectors
    >>> from distance import L2
    >>> matches, nomatches = classify(
    ...   comparisons = {(1,2):[0.5], (2,3):[0.8], (3,4):[0.9], (4,5):[0.0]},
    ...   distance = L2)
    >>> sorted(matches.keys())
    [(1, 2), (2, 3), (3, 4)]
    >>> sorted(nomatches.keys())
    [(4, 5)]

    >>> ## cluster 2D vectors with some nulled components
    >>> matches, nomatches = classify(
    ...  comparisons= {(1,2):[0.5,None], (2,3):[0.8,0.7], (3,4):[0.9,0.5], (4,5):[0.0,0.5]},
    ...  distance = L2)
    >>> sorted(matches.keys())
    [(1, 2), (2, 3), (3, 4)]
    >>> sorted(nomatches.keys())
    [(4, 5)]
    """
    # Get length of the comparison vector
    if len(comparisons) == 0:
        return set(), set()
    k,v = comparisons.popitem()
    vlen = len(v)
    vidx = range(vlen)
    comparisons[k] = v
    logging.debug("KMeans: Dimension %d, maxiter %d",vlen,maxiter)
    str_vector = lambda vector: "[" + ", ".join("%.4f" % v if v is not None else "None" for v in vector) + "]"
    safe_div = lambda n,d: n/d if d > 0 else None
    
    # Get initial centroids
    high_centroid = [ max(x[i] for x in comparisons.itervalues() 
                          if x[i] is not None) for i in vidx ]
    low_centroid = [ min(x[i] for x in comparisons.itervalues() 
                         if x[i] is not None) for i in vidx ]
    logging.debug("  Initial match centroid: %s", str_vector(high_centroid))
    logging.debug("  Initial non-match centroid: %s", str_vector(low_centroid))
    
    # Mapping key to (value, class assignment).
    # All items initially assigned to the "False" class (non-match).
    assignments = dict( (k,[v,False]) for k,v in comparisons.iteritems() )
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
        for k, (v,match) in assignments.iteritems():
            dist_high = distance(v, high_centroid)
            dist_low = distance(v, low_centroid)
            if dist_high < dist_low:
                if not match: 
                    n_changed += 1	
                assignments[k][1] = True # Set match to True
                for i in vidx:
                    if v[i] is not None:
                        high_total[i] += v[i]
                        high_count[i] += 1 
            else:
                if match: 
                    n_changed += 1
                assignments[k][1] = False # Set match to False
                for i in vidx:
                    if v[i] is not None:
                        low_total[i] += v[i]
                        low_count[i] += 1

        high_centroid = [ safe_div(high_total[i], high_count[i]) for i in vidx ]
        low_centroid = [ safe_div(low_total[i], low_count[i]) for i in vidx ]
            
        logging.debug("  Iteration %d: %d vectors changed assignment.", iters, n_changed)
        logging.debug("    Match centroid: %s", str_vector(high_centroid))
        logging.debug("    Non-match centroid: %s", str_vector(low_centroid))
    
    # Calculate a smoothed score as the log of the ratio of distances
    # of the similarity vector to each of the centroids.
    score = lambda v: math.log10( (distance(v,low_centroid)+0.1) / (distance(v,high_centroid)+0.1) )
    matches = dict( (k, score(v))  for k, (v,match) in assignments.iteritems() if match)
    nomatches = dict( (k, score(v)) for k, (v,match) in assignments.iteritems() if not match)
    logging.debug("Classified %d similarity vectors, %d as matches and %d as non-matches.",
                  len(comparisons), len(matches), len(nomatches))
    return matches, nomatches
