"""K-means clustering of similarity vectors into two groups (matches and
non-matches).

The default kmeans implementation has the advantage in that it is
able to handle missing (None) values in the similarity vectors.  It does
this by "not counting" whenever it comes across None, which should produce
better results than replacing None with 0 in instances where two field
values could not be compared.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

import logging

def kmeans_febrl(comparisons, distance, maxiter=50, sample=100.0):
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
                    max_iter_count = maxiter,
                    centroid_init = "min/max", 
                    sample = sample)
    kmeans.train(comparisons, None, None) # Identify the centroids
    [match, nomatch, probablematch] = kmeans.classify(comparisons)
    return match, nomatch

def kmeans(comparisons, distance, maxiter=10):
    """Classify each pair of comparisons as match or nonmatch, by clustering
    weight vectors around "match centroind" and "nonmatch centroid". 
    
    The match/nonmatch centroids are initialised using the largest/smallest
    occuring value for each component.
       
    @param comparisons: mapping (rec1,rec2):weights from record pair to
    field-by-field comparison vector.
    
    @param distance: Function distance(v1,v2) of two similarity vectors
    returninng the floating point distance between them, discarding components
    having a None value.
    
    @param maxiter: Maximum number of loops for adjusting the centroid.
    
    @return: set of matched pairs of records, set of non-matched pairs of
    records.
    """
    # Get length of the comparison vector
    k,v = comparisons.popitem()
    vlen = len(v)
    vidx = range(vlen)
    comparisons[k] = v
    logging.debug("KMeans: Dimension %d, maxiter %d",vlen,maxiter)
    str_vector = lambda vector: "[" + ", ".join("%.4f" % v for v in vector) + "]"
    
    # Get initial centroids
    high_centroid = [ max(x[i] for x in comparisons.itervalues() 
                          if x[i] is not None) for i in vidx ]
    low_centroid = [ min(x[i] for x in comparisons.itervalues() 
                         if x[i] is not None) for i in vidx ]
    logging.debug("  Initial match centroid: %s", str_vector(high_centroid))
    logging.debug("  Initial non-match centroid: %s", str_vector(high_centroid))
    
    # Mapping key to (value, class assignment).
    # All items initially assigned to the "False" class (non-match).
    assignments = dict( (k,[v,False]) for k,v in comparisons.iteritems() )
    # Number of items that changed class
    n_changed = 1
    # Number of classifier iterations
    iters = 0

    while n_changed > 0 and iters < maxiter:
        n_changed = 0
        iters += 1
        
        # Sums for the values in the high/low classes
        high_total = [0.0] * vlen
        low_total = [0.0] * vlen
        # Number of non-None values in each component for high/low class
        high_count = [0] * vlen
        low_count = [0] * vlen
    
        # Now assign the vectors to centroids
        for k, (v,match) in assignments.iteritems():
            dist_high = distance(v, high_centroid)
            dist_low = distance(v, low_centroid)
            if dist_high < dist_low:
                if not match: 
                    n_changed += 1	
                assignments[k][1] = True # Set match to True
                for i in vidx:
                    if v[i] is not None:
                        high_total[i] += v[i]
                        high_count[i] += 1 
            else:
                if match: 
                    n_changed += 1
                assignments[k][1] = False # Set match to False
                for i in vidx:
                    if v[i] is not None:
                        low_total[i] += v[i]
                        low_count[i] += 1
            
        high_centroid = [ high_total[i]/high_count[i] for i in vidx ]
        low_centroid = [ low_total[i]/low_count[i] for i in vidx ]
            
        logging.debug("  Iteration %d: %d vectors changed assignment.", iters, n_changed)
        logging.debug("    Match centroid: %s", str_vector(high_centroid))
        logging.debug("    Non-match centroid: %s", str_vector(low_centroid))
        
    matches = set(k for k, (v,match) in assignments.iteritems() if match)
    nomatches = set(k for k, (v,match) in assignments.iteritems() if not match)
    logging.debug("Classified %d similarity vectors, %d as matches and %d as non-matches.",
                  len(comparisons), len(matches), len(nomatches))
    return matches, nomatches
