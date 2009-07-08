"""Function to a apply a rule-based classifier that returns True, False or
None. Generally, using a strict rule-based classifier to create training
examples for a stronger classifiers."""

import logging

def classify(comparisons, rule):
    """Use provided rule to judge provided similarity vectors as being True
    (match), False (non-match), while discarding the None results from the rule.
    
    @param comparisons: Mapping from (rec1,rec2) to vector of similarity values.
    
    @param rule: Function of similarity vector that returns True, False or None.
   
    @return: List of (similarity vector, judgement) with judgement as
    True or False for distinct similarity vectors that could be classified.
    """
    matches, nonmatches, uncertain = set(), set(), set()
    for simvec in comparisons.itervalues():
        ismatch = rule(simvec)
        if ismatch is True:
            matches.add(simvec)
        elif ismatch is False:
            nonmatches.add(simvec)
        elif ismatch is None:
            uncertain.add(simvec)
        else:
            raise ValueError("rulebased classify: %s is not True/False/None" % repr(ismatch))
    logging.debug("rulebased classifier on %d vectors: %d matches, %d non-matches, %d uncertain", 
                  len(comparisons), len(matches), len(nonmatches), len(uncertain))
    return matches, nonmatches, uncertain
