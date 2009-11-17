"""
:mod:`rulebased` -- Rule-based classifier of vector
===================================================

Function to a apply a rule-based classifier that returns True, False or
None. Generally, using a strict rule-based classifier to create training
examples for a stronger classifiers.

.. module:: rulebased
   :synopsis: Classify match/non-match vectors using rules.
.. moduleauthor:: Graham Poulter
"""

import logging

def classify_bool(rule, comparisons):
    """Use provided rule function to judge comparison 
    similarity vectors as matches (if True), non-matches (if False)
    and uncertain (if None).  
    
    :type rule: function([float,...]) bool or None
    :param rule: "is this similarity vector a match" - returns True, False or None
    :type comparisons: {(R,R):[float,...],...}
    :param comparisons: similarity vectors of compared record pairs.
    :rtype: {(R,R)...}, {(R,R)...}, {(R,R)...}
    :return: match, non-match and uncertain record pairs
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

def classify(rule, comparisons):
    """Uses :func:`classify_bool` but returns the boolean results as scores in
    the same format as results from :mod:`kmeans` and :mod:`nearest`.
    
    :type rule: function([float,...]) bool or None
    :param rule: "is this similarity vector a match" - returns True, False or None
    :rtype: {(R,R):float}, {(R,R):float}
    :return: classifier scores for match pairs (1.0) and non-match pairs (0.0)
    """
    match,nomatch,unknown = classify_bool(rule, comparisons)
    return dict((x,1.0) for x in match), dict((x,0.0) for x in nomatch)
