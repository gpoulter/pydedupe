"""
Rule-based classification into match/non-match
==============================================

Uses a function of the similarity vector to determine match or non-match.  Note
that Nearest-Neighbour classifier allows an override rule to assist
classification.

.. moduleauthor:: Graham Poulter
"""


def classify_bool(rule, comparisons):
    """Use provided rule to classify similarity vectors as
    matches (True), non-matches (False) and uncertain (None).

    :type rule: function(record, record, [`float`, ...]) `bool` | `None`
    :param rule: Takes (rec1, rec2, similarity) and returns True/False/None\
    as to whether the pair is a match. `None` is unknown.
    :type comparisons: {(`R`, `R`):[:class:`float`, ...], ...}
    :param comparisons: similarity vectors of compared record pairs.
    :rtype: {(`R`, `R`) ...}, {(`R`, `R`) ...}, {(`R`, `R`) ...}
    :return: sets of matching, non-matching and uncertain record pairs
    """
    matches, nonmatches, uncertain = set(), set(), set()
    for pair, simvec in comparisons.iteritems():
        ismatch = rule(pair[0], pair[1], simvec)
        if ismatch is True:
            matches.add(pair)
        elif ismatch is False:
            nonmatches.add(pair)
        elif ismatch is None:
            uncertain.add(pair)
        else:
            raise ValueError(
                "rule classify: {0!r} is not True/False/None".format(ismatch))
    import logging
    logging.debug(
        "rule on {0} vectors: {1} match, {2} non-match, {3} uncertain"\
        .format(len(comparisons), len(matches),
                len(nonmatches), len(uncertain)))
    return matches, nonmatches, uncertain


def classify(rule, comparisons):
    """Uses a rule to classify matches/non-matches using scores of 0.0 and
    1.0, which is the format produced by :mod:`~classification.kmeans` and
    :mod:`~classification.nearest`.

    :type rule: function([:keyword:`float`, ...]) `bool`|`None`
    :param rule: "is this similarity vector a match" - returns :keyword:`True`\
      :keyword:`False` or :keyword:`None`
    :rtype: {(`R`, `R`)::class:`float`}, {(`R`, `R`)::class:`float`}
    :return: classifier scores for match pairs (1.0) and non-match pairs (0.0)
    """
    match, nomatch, uncertain = classify_bool(rule, comparisons)
    return dict((x, 1.0) for x in match), dict((x, 0.0) for x in nomatch)
