"""
Syntax is like python27 digitize_storage.py filein fileout
File in is an HDFStore
FILE
"""

import pandas as pd
import os
import glob
import numpy as np
from scipy.spatial import distance
import sys

_, filein, fileout = sys.argv

def digit_aggregate(table):
    """
    Takes a table of returns and produces a table with frequency of digits
    """
    table = table % 10
    digits = table.apply(lambda x: x.value_counts(),axis='index')
    return(digits)

def custom_dist(a,b):
    """ Assumes NAN means 0 """
    a = a.fillna(0)
    b = b.fillna(0)
    return(distance.euclidean(a,b))
    
store = pd.HDFStore(filein)
digits_distances = {}
for key in store.keys():
    #first load the key key = store.keys()[0]
    panel = store[key]
    #to each datafame or "sheet" in the panel, transform to digit counts
    digit_panel = panel.apply(lambda x: digit_aggregate(x),axis=(1,2))
    #separate the real digit totals from the simulated ones
    real = digit_panel.iloc[0,:,:]
    sims = digit_panel.iloc[1:,:,:]
    mean = sims.mean(0)
    #iterate over each candidate and get the distance to mean sim digit count
    seriessto = []
    for columnNumber in range(np.shape(digit_panel)[2]):
        rDist = custom_dist(real.iloc[:,columnNumber],
                                   mean.iloc[:,columnNumber])
        simDist = []
        for item in range(np.shape(sims)[0]):
            simDist.append(
                custom_dist(
                    mean.iloc[:,columnNumber],
                    sims.iloc[item,:,columnNumber])
            )
        seriessto.append(pd.Series([rDist] + simDist))

    Distances = pd.DataFrame(seriessto).T
    #add the series produced to a dictionary we will turn into a panel
    digits_distances[key.replace("/","")] = Distances

out = pd.Panel(digits_distances)
out.to_pickle(fileout)