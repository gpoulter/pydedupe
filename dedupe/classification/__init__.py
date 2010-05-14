"""
Classify record pairs as match or non-match
===========================================

Load example match and non-match record pairs, calculate distances between
similarity vectors, and classify similarity vectors as match/non-match using
K-Means, K-Nearest-Neighbours (enhanced with rule-based override), or a
hard-coded rule.
"""

import distance
import examples
import kmeans
import nearest
import rulebased
