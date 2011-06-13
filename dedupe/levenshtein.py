"""
Levenshtein edit distance for strings
=====================================

The algorithm is from the Tyriel_ search engine by caelyx, source
code found here_.

.. _Tyriel: http://sourceforge.net/projects/tyriel
.. _here: http://www.koders.com/python/fid508C865D6E926EC0C45A7C4872E4F57AB33381B0.aspx

.. moduleauthor:: Graham Poulter
"""


def distance(a, b):
    """Calculates the Levenshtein distance between a and b.

    >>> from dedupe import levenshtein
    >>> levenshtein.distance("abcd","ab")
    2
    >>> levenshtein.distance("abcd","abdc")
    2
    >>> levenshtein.distance("dbca","abcd")
    2
    """
    if a is None or b is None:
        return None
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n, m)) space
        a, b = b, a
        n, m = m, n
    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * m
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)
    return current[n]


def similarity(a, b):
    """Levenshtein distance as similarity in the range 0.0 to 1.0.  Empty
    or missing values return a similarity of None.

    >>> from dedupe import levenshtein
    >>> levenshtein.similarity("abcd", "abcd")
    1.0
    >>> levenshtein.similarity("abcd", "abdc")
    0.5
    >>> print levenshtein.similarity("abcd", "")
    None
    """
    if a is None or b is None:
        return None
    else:
        return 1.0 - float(distance(a, b)) / max(len(a), len(b))

if __name__ == "__main__":
    import sys
    print distance(sys.argv[1], sys.argv[2])
