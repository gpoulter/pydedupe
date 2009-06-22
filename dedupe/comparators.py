"""Configured text comparison functions from FEBRL

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from febrl.comparison import (
    FieldComparatorDaLeDist, 
    FieldComparatorSWDist, 
    FieldComparatorKeyDiff)
                              
dale5 = FieldComparatorDaLeDist(
    agree_weight = 1.0,
    disagree_weight = 0.0,
    missing_values = [None,''],
    missing_weight = 0.2,
    threshold = 0.5).compare

dale7 = FieldComparatorDaLeDist(
    agree_weight = 1.0,
    disagree_weight = 0.0,
    missing_values = [None,''],
    missing_weight = 0.2,
    threshold = 0.7).compare

dale5nomissing = FieldComparatorDaLeDist(
    agree_weight = 1.0,
    disagree_weight = 0.0,
    missing_values = [None,''],
    missing_weight = 0.0,
    threshold = 0.5).compare

sw5 = FieldComparatorSWDist(
    common_divisor = 'average',
    agree_weight = 1.0,
    disagree_weight = 0.0,
    missing_values = [None,''],
    missing_weight = 0.2,
    threshold = 0.5).compare

keydiff = FieldComparatorKeyDiff(
    max_key_diff = 3,
    agree_weight = 1.0,
    disagree_weight = 0.0,
    missing_values = [None,''],
    missing_weight = 0.2).compare
