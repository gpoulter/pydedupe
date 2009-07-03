"""Nearest Neighbour classification of similarity vectors into matches and
non-matches.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

def classify(comparisons, examples, distance):
    """Nearest-neighbour classification of comparisons vectors.

    @param comparisons: Map (item1,item2):comparison    

    @param examples: List of (comparison, boolean) example pairs - True for
    match and False for non-match.

    @param distance: Function to compute distance between comparison vectors.

    @return: set of matched record pair, set of non-matched record pairs.
    """    
    match = set()
    nomatch = set()
    for pair, comparison in comparisons.iteritems():
        min_dist, ismatch = min((distance(comparison, example), ismatch) 
                                for example, ismatch in examples)
        if ismatch:
            match.add(pair)
        else:
            nomatch.add(pair)
    return match, nomatch

