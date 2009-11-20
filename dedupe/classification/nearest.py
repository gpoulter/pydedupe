"""
:mod:`classification.nearest` -- Nearest neighbour classification
=========================================================================

.. moduleauthor:: Graham Poulter
"""

def classify(comparisons, ex_matches, ex_nonmatches, distance):
    """Nearest-neighbour classification of comparisons vectors.

    :type comparisons: {(`R`, `R`):[:class:`float`,...],...}
    :param comparisons: similarity vectors of compared record pairs.
    :type ex_matches: [[:class:`float`,...],...]
    :param ex_matches: List of examples of matching similarity vectors.
    :type ex_matches: [[:class:`float`,...],...]
    :param ex_nonmatches: List examples of non-matching similarity vectors.
    :type distance: function([:class:`float`,...],[:class:`float`,...]) :class:`float`
    :param distance: calculates distance between similarity vectors.
    :rtype: {(`R`, `R`)::class:`float`}, {(`R`, `R`)::class:`float`}
    :return: classifier scores for match pairs and non-match pairs
    
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
    import logging, math
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

