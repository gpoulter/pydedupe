"""Nearest Neighbour classification of similarity vectors into matches and
non-matches.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

import logging, math

def classify(comparisons, ex_matches, ex_nonmatches, distance):
    """Nearest-neighbour classification of comparisons vectors.

    @param comparisons: Map (item1,item2):comparison    

    @param ex_matches: List of examples of matching similarity vectors.
    
    @param ex_nonmatches: List examples of non-matching similarity vectors.

    @param distance: Function to compute distance between comparison vectors.

    @return: set of matched record pair, set of non-matched record pairs.
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

