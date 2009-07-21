"""Function to a apply a rule-based classifier that returns True, False or
None. Generally, using a strict rule-based classifier to create training
examples for a stronger classifiers."""

import logging

def classify(comparisons, rule):
    """Use provided rule to judge provided similarity vectors as being True
    (match), False (non-match), while discarding the None results from the rule.
    
    @param comparisons: Mapping from (rec1,rec2) to vector of similarity values.
    
    @param rule: Function of similarity vector that returns True, False or None.
   
    @return: Three sets for matches, non-matches and uncertain pairs. Each
    set contains (rec1,rec2) representing the compared pair.
    """
    matches, nonmatches, uncertain = set(), set(), set()
    for pair, simvec in comparisons.iteritems():
        ismatch = rule(simvec)
        if ismatch is True:
            matches.add(pair)
        elif ismatch is False:
            nonmatches.add(pair)
        elif ismatch is None:
            uncertain.add(pair)
        else:
            raise ValueError("rulebased classify: %s is not True/False/None" % repr(ismatch))
    logging.debug("rulebased classifier on %d vectors: %d matches, %d non-matches, %d uncertain", 
                  len(comparisons), len(matches), len(nonmatches), len(uncertain))
    return matches, nonmatches, uncertain
