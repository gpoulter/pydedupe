"""Distance functions for similarity vectors.  

The functions should handle the presence of "None" values in a similarity vector
(meaning "no comparison possible" on that component), and neglect that
component in the calculation.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

import math

def L2(vec1, vec2):
    """L2 or Euclidian distance between two vectors. Discards vector
    components having None values.
    
    @param vec1, vec2: Equal-length sequences of floating-point values.
    """
    assert len(vec1) == len(vec2)
    return math.sqrt(sum((a-b)**2 
                         for a,b in zip(vec1, vec2) 
                         if a is not None and b is not None))


def normL2(vec1, vec2, stdevs):
    """The normalised L2 distance, being the Mahalanobis distance with a
    diagonal covariance matrix. Discards vector components having None values.
    
    @param vec1, vec2: Equal-length sequences of floating-point values.
    
    @param stdevs: Standard deviations for vector components 
    (higher variance gives less weight to that component).
    """
    assert len(vec1) == len(vec2) == len(stdevs)
    return math.sqrt(sum(((a-b)/s)**2 
                         for a,b,s in zip(vec1, vec2, stdevs) 
                         if a is not None and b is not None))
