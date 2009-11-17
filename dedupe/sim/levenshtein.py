#!/usr/bin/env python

"""
:mod:`sim.levenshtein` -- Levenshtein string distance
============================================================

.. module:: sim.levenshtein
   :synopsis: Calculate Levenshtein distance between two strings.

.. note:: Implementation is from the `Tyriel search engine
   <http://sourceforge.net/projects/tyriel/>` by caelyx, source code found at:
   http://www.koders.com/python/fid508C865D6E926EC0C45A7C4872E4F57AB33381B0.aspx
 
"""

def distance(a,b):
    """Calculates the Levenshtein distance between a and b.
    
    >>> distance("abcd","ab")
    2
    >>> distance("abcd","abdc")
    2
    >>> distance("dbca","abcd")
    2
    """
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*m
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
    return current[n]

def _compare(maxdiff, s1, s2, missing, distance):
    if not (0.0 <= maxdiff <= 1.0):
        raise ValueError("Difference threshold must be between 0.0 and 1.0.")
    if not s1 or not s2:
        return missing
    ndiffs = distance(s1,s2)
    maxdiffs = max(len(s1),len(s2)) * maxdiff
    if ndiffs >= maxdiffs:
        return 0.0
    else:
        return 1.0 - (ndiffs / maxdiffs)

def compare(maxdiff, s1, s2, missing=None):
    """Return similarity of strings based on Levenshtein distance.
    
    :type maxdiff: float between 0.0 and 1.0.
    :param maxdiff: proportion of ``max(len(s1),len(s2))`` beyond which\
     the similarity is considered similarity of 0. Higher values are more lenient.
    :param missing: If one of the strings is empty or :keyword:`None`, return `missing`.
    :rtype: float
    :return: similarity between 0.0 and 1.0.
    
    >>> compare(1.0, "abcd","abcd")
    1.0
    >>> compare(1.0, "abcd","abdc")
    0.5
    >>> compare(1.0, "abcd","") is None
    True
    >>> compare(0.5, "abcd","abdc")
    0.0
    >>> compare(0.5, "abcd","badc")
    0.0
    """
    return _compare(maxdiff, s1, s2, missing, distance)

if __name__=="__main__":
    import sys
    print distance(sys.argv[1],sys.argv[2])