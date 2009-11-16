"""
:mod:`nearest` -- Nearest neighbour classification of vectors.
==============================================================

Nearest Neighbour classification of similarity vectors into matches and
non-matches.

.. module:: nearest
.. moduleauthor:: Graham Poulter
"""

import logging, math

def classify(comparisons, ex_matches, ex_nonmatches, distance):
    """Nearest-neighbour classification of comparisons vectors.

    :param comparisons: Map (item1,item2):comparison    
    :param ex_matches: List of examples of matching similarity vectors.
    :param ex_nonmatches: List examples of non-matching similarity vectors.
    :param distance: Function to compute distance between comparison vectors.
    :return: Two sets, one with matches and one with non-matches. \
    Each set contains (rec1,rec2) pairs of compared records.
    
    >>> ## Test 1D vectors
    >>> from distance import L2
    >>> matches, nomatches = classify(
    ... comparisons= {(1,2):[0.5], (2,3):[0.8], (3,4):[0.9], (4,5):[0.0]},
    ... ex_matches = [[1.0]],
    ... ex_nonmatches = [[0.3]],
    ... distance = L2)
    >>> sorted(matches.keys())
    [(2, 3), (3, 4)]
    >>> sorted(nomatches.keys())
    [(1, 2), (4, 5)]
    
    >>> ## Test 2D vectors with some null components
    >>> matches, nomatches = classify(
    ...  comparisons= {(1,2):[0.5,None], (2,3):[0.8,0.7], (3,4):[0.9,0.5], (4,5):[0.0,0.5]},
    ...  ex_matches = [[1.0,0.8],[1.0,None]],
    ...  ex_nonmatches = [[0.3,0.3]],
    ...  distance = L2)
    >>> sorted(matches.keys())
    [(2, 3), (3, 4)]
    >>> sorted(nomatches.keys())
    [(1, 2), (4, 5)]
    """
    logging.info("Nearest neighbour: %s match examples and %d non-match examples.", 
                 len(ex_matches), len(ex_nonmatches))
    matches, nonmatches = {}, {}
    for pair, comparison in comparisons.iteritems():
        match_dist = min(distance(comparison, example) for example in ex_matches)
        nonmatch_dist = min(distance(comparison, example) for example in ex_nonmatches)
        # Calculate a smoothed score as the log of the ratio of distances
        # of the similarity vector to the nearest match and non-match.
        score = math.log10((nonmatch_dist+0.1) / (match_dist+0.1))
        if match_dist < nonmatch_dist:
            matches[pair] = score
        else:
            nonmatches[pair] = score
    logging.info("Nearest neighbour: %d matches and %d non-matches",
                 len(matches), len(nonmatches))
    return matches, nonmatches

