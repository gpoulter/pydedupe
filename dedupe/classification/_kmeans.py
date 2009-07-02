"""K-means clustering of similarity vectors into two groups (matches and non-matches).

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

def kmeans_febrl(comparisons, distance):
    """Classify each pair of comparisons as match or nonmatch, by clustering
    weight vectors around "match centroind" and "nonmatch centroid"
       
    @param comparisons: mapping (rec1,rec2):weights from record pair to
    field-by-field comparison vector.
    
    @param distance: Function distance(v1,v2) of two similarity vectors
    returninng the floating point distance between them, discarding components
    having a None value.
    
    @return: set of matched pairs of records, set of non-matched pairs of records.
    """
    from dedupe.febrl.classification import KMeans
    # Return empty sets if there is nothing to classify
    if not comparisons: return set(), set()
    # Configure the FEBRL classifier
    kmeans = KMeans(dist_measure = distance,  
                    max_iter_count = 50,
                    centroid_init = "min/max", 
                    sample = 100.0)
    kmeans.train(comparisons, None, None) # Identify the centroids
    [match, nomatch, probablematch] = kmeans.classify(comparisons)
    return match, nomatch

def kmeans(comparisons, distance, sample=None):
    """Classify each pair of comparisons as match or nonmatch, by clustering
    weight vectors around "match centroind" and "nonmatch centroid"
       
    @param comparisons: mapping (rec1,rec2):weights from record pair to
    field-by-field comparison vector.
    
    @param distance: Function distance(v1,v2) of two similarity vectors
    returninng the floating point distance between them, discarding components
    having a None value.
    
    @return: set of matched pairs of records, set of non-matched pairs of
    records.
    """
    pass