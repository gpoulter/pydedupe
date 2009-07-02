"""Classification of comparison similarity vectors like (0.0,0.8.0.5,...) 
into matches and non-matches."""

from _distance import distL2, dist_norm_L2

from _kmeans import kmeans

from _nearest_neighbour import nearest_neighbour
