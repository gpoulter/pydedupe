"""Distance functions for similarity vectors.  

The functions should handle the presence of "None" values in a similarity vector
(meaning "no comparison possible" on that component), and neglect that
component in the calculation.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

import math

def distL2(vec1, vec2):
    """L2 distance , also known as Euclidean distance. 
    @note: Python implementation to avoid a numpy dependency for now.
    """
    #assert len(vec1) == len(vec2)
    return math.sqrt(sum((float(a)-float(b))**2 for a,b in zip(vec1, vec2)))


def dist_norm_L2(vec1, vec2, stdevs):
    """Normalised L2 distance, being the Mahalanobis distance with a
    diagonal covariance matrix.
    
    @param stdevs: Standard deviations for vector components 
    (higher variance gives less weight to that component).
    """
    #assert len(vec1) == len(vec2) == len(stdevs)
    return math.sqrt(sum(((a-b)/s)**2 for a,b,s in zip(vec1, vec2, stdevs)))