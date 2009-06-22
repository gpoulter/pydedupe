"""Classification algorithms.  The K-Means depends on FEBRL and the
classifiers work on the comparisons object produced by L{indexer.Indeces}
class.

Each comparison is a vector of similarity values, each in the 0.0 to 1.0 range,
being the field-by-field similarity of a pair of records. 

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from febrl.classification import KMeans
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


def classify_kmeans(comparisons, distance=distL2):
    """Classify each pair of comparisons as match or nonmatch, by clustering
    weight vectors around "match centroind" and "nonmatch centroid"
       
    @param comparisons: mapping (rec1,rec2):weights from record pair to
    field-by-field comparison vector.
    
    @param distance: Vector distance function.
    
    @return: set of matched pairs of records, set of non-matched pairs of records.
    """
    if not comparisons: # Nothing to classify
        return {}, []
    kmeans = KMeans(dist_measure = distance,  
                    max_iter_count = 50,
                    centroid_init = "min/max", 
                    sample = 100.0)
    kmeans.train(comparisons, None, None) # Identify the centroids
    [match, nomatch, probablematch] = kmeans.classify(comparisons)
    return match, nomatch


def classify_nearest(comparisons, examples, distance):
    """Nearest-neighbour classification of comparisons vectors.

    @param comparisons: Map (item1,item2):comparison    

    @param examples: List of (comparison, boolean) example pairs - True for
    match and False for non-match.

    @param distance: Function to compute distance between comparison vectors.

    @return: set of matched record pair, set of non-matched record pairs.
    """    
    match = set()
    nomatch = set()
    for pair, comparison in comparisons.iteritems():
        min_dist, ismatch = min((distance(comparison, example), ismatch) 
                                for example, ismatch in examples)
        if ismatch:
            match.add(pair)
        else:
            nomatch.add(pair)
    return match, nomatch

