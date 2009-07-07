"""Functions for rule-based classification, to create some
known training examples for stronger classifiers."""

def classify_uncertain(comparisons, rule):
    """Run through comparisons as (rec1,rec2):simvec and return judgements
    as simvec:result where result is True (match), False (non-match),
    or None (cannot say)
    
    @param rule: Function of similarity vector that returns True, False or None.
   
    @return: List of (similarity vector, judgement) with judgement as
    True, False or None for all similarity vectors.
    """
    return [ (simvec, rule(simvec)) for simvec in comparisons.itervaules() ]

def classify_strict(comparisons, rule):
    """Run through comparisons as (rec1,rec2):simvec and return judgements
    as simvec:result where result is True (match) or False (non-match). 
    Uncertain judgements are not included.
   
    @param rule: Function of similarity vector that returns True, False or None.
   
    @return: List of (simvec, judgement) with judgement as True or False, for
    similarity vectors that could be classified.
    """
    results = []
    for simvec in comparisons.itervalues():
        ismatch = rule(simvec)
        if ismatch is not None:
            results.append((simvec,ismatch))
    return results

def split_judgements(judgements):
    """Split simvec judgements into disjoint sets.
    
    @param judgements: Iteration of (simvec, judgement) as True, False, or None.
    
    @return: Sets of match, nonmatch, uncertain similarity vectors.
    """
    match, nomatch, uncertain = set(), set(), set()
    for simvec, result in judgements:
        if result is True:
            match.add(simvec)
        elif result is None:
            uncertain.add(simvec)
        elif result is False:
            nomatch.add(simvec)
        else:
            raise ValueError("Classifier judgement %s is not True/False/None" % str(result))
    return match, nomatch, uncertain
