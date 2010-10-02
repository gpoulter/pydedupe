"""
Nearest neighbour classification of match/non-match
===================================================

Nearest-Neighbour classification works best with a small number of carefully
specified example pairs pre-labelled as matches and non-matches.  Each
comparison (a similarity vector) is then classified by whether the closest
example vector is a match or a non-match.

.. moduleauthor:: Graham Poulter
"""

import logging
import math


def classify(comparisons, ex_matches, ex_nonmatches, distance, rule=None):
    """Nearest-neighbour classification of comparisons vectors.

    :type comparisons: {(`R`, `R`):[:class:`float`, ...], ...}
    :param comparisons: similarity vectors of compared record pairs.
    :type ex_matches: [[:class:`float`, ...], ...]
    :param ex_matches: List of examples of matching similarity vectors.
    :type ex_matches: [[:class:`float`, ...], ...]
    :param ex_nonmatches: List examples of non-matching similarity vectors.
    :type distance: function([:class:`float`, ...], [:class:`float`, ...]) :class:`float`
    :param distance: calculates distance between similarity vectors.
    :type rule: function(`R`, `R`, [:class:`float`, ...]) -> :class:`bool` or :keyword:`None`
    :param rule: optional rule-based override that returns a boolean for\
    record pairs and similarities that definitely match/non-match, and :keyword:`None`\
    to fall back to nearest neighbour algorithm.
    :rtype: {(`R`, `R`)::class:`float`}, {(`R`, `R`)::class:`float`}
    :return: classifier scores for match pairs and non-match pairs

    >>> ## Test 1D vectors
    >>> from dedupe.classification.distance import L2
    >>> from dedupe.classification import nearest
    >>> matches, nomatches = nearest.classify(
    ... comparisons= {(1, 2):[0.5], (2, 3):[0.8], (3, 4):[0.9], (4, 5):[0.0]},
    ... ex_matches = [[1.0]],
    ... ex_nonmatches = [[0.4]], # to match when sim[0]>0.7
    ... distance = L2,
    ... rule = lambda a, b, s: True if (a, b)==(4, 5) else None)
    >>> # the rule makes (4, 5) a match, overriding the classifier
    >>> sorted(matches.keys())
    [(2, 3), (3, 4), (4, 5)]
    >>> sorted(nomatches.keys())
    [(1, 2)]

    >>> ## Test 2D vectors with some null components
    >>> matches, nomatches = nearest.classify(
    ...  comparisons= {(1, 2):[0.5, None], (2, 3):[0.8, 0.7],
    ...                (3, 4):[0.9, 0.5], (4, 5):[0.0, 0.5]},
    ...  ex_matches = [[1.0, 0.8], [1.0, None]],
    ...  ex_nonmatches = [[0.3, 0.3]],
    ...  distance = L2)
    >>> sorted(matches.keys())
    [(2, 3), (3, 4)]
    >>> sorted(nomatches.keys())
    [(1, 2), (4, 5)]
    """
    logging.debug("Nearest neighbour example: {0} match, {1} non-match."\
                  .format(len(ex_matches), len(ex_nonmatches)))
    matches, nonmatches = {}, {}
    for pair, comparison in comparisons.iteritems():
        judge = rule(pair[0], pair[1], comparison) if rule else None
        if judge is None:
            match_dist = min(distance(comparison, example)
                             for example in ex_matches)
            nonmatch_dist = min(distance(comparison, example)
                                for example in ex_nonmatches)
            # Calculate a smoothed score as the log of the ratio of distances
            # of the similarity vector to the nearest match and non-match.
            score = math.log10((nonmatch_dist + 0.1) / (match_dist + 0.1))
            if match_dist < nonmatch_dist:
                matches[pair] = score
            else:
                nonmatches[pair] = score
        elif judge is True:
            matches[pair] = 1.0
        elif judge is False:
            nonmatches[pair] = 0.0
        else:
            raise ValueError(
                "rule returned {0!s}: should be True/False/None".format(judge))
    logging.debug("Nearest neighbour: {0} matches and {1} non-matches".format(
                 len(matches), len(nonmatches)))
    return matches, nonmatches
