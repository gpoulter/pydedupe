#!/usr/bin/env python

"""
Calculates the Levenshtein distance between a and b.

Implementation from the Tyriel search engine by caelyx, 
http://sourceforge.net/projects/tyriel/

Source code from:
 http://www.koders.com/python/fid508C865D6E926EC0C45A7C4872E4F57AB33381B0.aspx
 
"""

def distance(a,b):
    """Calculates the Levenshtein distance between a and b."""
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

def compare(s1, s2, threshold=1.0, missing=None):
    """A Levenshtein (edit distance) string comparator, returning a similarity
    value scaled between 0.0 and 1.0.
    
    The threshold scales the maximum number of differences before the
    comparator returns 0, from the default maximum equal to the length of the
    shorter string. Thresholds less than 1.0 are more strict, and thresholds
    greater than 1.0 are more lenient about the maximum number of differences.
    
    @param threshold: 
    
    @param missing: If one of the strings is empty or None, returns this value.
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
