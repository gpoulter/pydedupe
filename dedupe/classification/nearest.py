"""Nearest Neighbour classification of similarity vectors into matches and
non-matches.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

import logging, math

def classify(comparisons, examples, distance):
    """Nearest-neighbour classification of comparisons vectors.

    @param comparisons: Map (item1,item2):comparison    

    @param examples: List of (comparison, boolean) example pairs - True for
    match and False for non-match.

    @param distance: Function to compute distance between comparison vectors.

    @return: set of matched record pair, set of non-matched record pairs.
    """    
    match_examples = [ vec for vec, ismatch in examples if ismatch ]
    nomatch_examples = [ vec for vec, ismatch in examples if not ismatch ]
    match, nomatch = {}, {}
    for pair, comparison in comparisons.iteritems():
        match_dist = min(distance(comparison, example) for example in match_examples)
        nomatch_dist = min(distance(comparison, example) for example in nomatch_examples)
        # Calculate a smoothed score as the log of the ratio of distances
        # of the similarity vector to the nearest match and non-match.
        score = math.log10((nomatch_dist+0.1) / (match_dist+0.1))
        if score >= 0:
            match[pair] = score
        else:
            nomatch[pair] = score
    return match, nomatch

