#!/usr/bin/env python

"""Implementation of Damerau-Levenshtein distance by mwh.geek.nz:

http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/

The Damerau-Levenshtein distance between two strings is the number of
additions, deletions, substitutions, and transpositions needed to transform
one into the other. It's an extension of the Levenshtein distance, 
by incorporating transpositions into the set of operations.

I had a need to use it in a program recently, but I couldn't find any Python
implementation around that wasn't trivially buggy or horrendously
inefficient (strictly, you can implement it neatly by recursion, and it's
instructive for examining the algorithm, but it takes an age to run when you
do). I've put one together myself from the algorithmic definition that
I've tested to work correctly and reasonably efficiently.

The algorithm is inherently O(N*M) in time, and the naive version is in space
as well. This implementation is O(M) in space, as only the last two rows of th

The code is available under the MIT licence, in the hope that it will be
useful, but without warranty of any kind. I have also included a codesnippet
GUID in line with the linked post, as a sort of experiment. Please leave that
comment intact if you're posting a derivative somewhere, and add your own.
"""

from __future__ import division

__license__ = "MIT"

def distance(seq1, seq2):
    """Calculate the Damerau-Levenshtein distance between sequences.

    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Although generally used with strings, any sequences of
    comparable objects will work.

    Transpositions are exchanges of *consecutive* characters; all other
    operations are self-explanatory.

    This implementation is O(N*M) time and O(M) space, for N and M the
    lengths of the two sequences.
    """
    # codesnippet:D0DE4716-B6E6-4161-9219-2903BF8F547F
    # Conceptually, this is based on a len(seq1) + 1 * len(seq2) + 1 matrix.
    # However, only the current and two previous rows are needed at once,
    # so we only store those.
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y-1]
                and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y-2] + 1)
    return thisrow[len(seq2) - 1]


def compare(s1, s2, threshold=1.0, missing=None):
    """A Damerau-Levenshtein string comparator, returning a similarity
    value scaled between 0.0 and 1.0. 
    
    The threshold scales the maximum number of differences before the
    comparator returns 0, from the default maximum equal to the length of the
    shorter string. Thresholds less than 1.0 are more strict, and thresholds
    greater than 1.0 are more lenient about the maximum number of differences.
    
    If one of the strings is empty or None, the comparison returns None (no
    comparison possible).
    """
    if not s1 or not s2:
        return missing
    ndiffs = distance(s1,s2)
    maxdiffs = min(len(s1),len(s2)) * threshold
    if ndiffs >= maxdiffs:
        return 0.0
    else:
        return 1.0 - (ndiffs / maxdiffs)


if __name__=="__main__":
    from sys import argv
    print distance(argv[1],argv[2])
