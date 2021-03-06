""""
Calculate the fraction of elections declared fraudulent
Produces a graph of all the election results and where the observed value occurs
Requires as input the file of a pickled output from digitize storage.
Also requires an array (passed as a string) of which parties to select. If none is provided then all will be used
Graphs will be produced int the directory from which the file is called
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections as mc
import sys

_, filein = sys.argv


data = pd.read_pickle(filein)
cols = range(np.shape(data)[2]) #cols = [0,1] for US
pvalues = [90,95,99]
print "Target Percentile " "Percent Accepted"
for pvalue in pvalues:
    accept_election = []
    i = 1
    lines = []
    points = []
    #for item in data.items[0:1]:
    for item in data.items[:]:
        for col in range(sum(~data.ix[item,0].isnull())):
            #calculate whether we accept or reject at the p-value
            p = np.percentile(data.ix[item,1:,col],pvalue)
            accept_election.append(data.ix[item,0,col] < p)
            #Take all the sim results and the real results and place on a scale from 0 to 100
            m = np.max(data.ix[item,:,col])
            lines.append([(i,np.min(data.ix[item,:,col])/m),(i,p/m)])
            #we will place a point at the observed value
            points.append((i,data.ix[item,0,col]/m))
            i = i + 1
    print pvalue, np.mean(accept_election)
    lc = mc.LineCollection(lines)
    fig, ax = plt.subplots()
    ax.set_ylim(0,110/100.)
    b = 10
    ax.set_xlim(0-b,b+len(points))
    ax.plot([x[0] for x in points],[y[1] for y in points],"r^")
    ax.add_collection(lc)
    ax.set_title(str(pvalue)+"th percentile test on Swedish elections")
    fig.savefig(str(pvalue)+"perentile_test.pdf")



