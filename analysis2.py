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
meta = pd.DataFrame([i.split("_") for i in data.items])
#two elections are not named as the others, we throw them out
data = data[meta.ix[meta.ix[:,4].isnull(),:].index,:,:]
meta = pd.DataFrame([i.split("_") for i in data.items])
meta.columns = ["State","Year","ElectionYear","Type"]
election_types = ["GOV","USS","USP"]
election_years = ["2000","2004","2008","2012"]
pvalue = 95
i = 0
j = 1
for el in election_types:
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex=True, sharey=True)
    for year in election_years:
        ax = eval("ax" + str(j))
        lines = []
        points = []
        temp = data[meta[(meta.Year == year) & (meta.Type == el)].index]
        for item in temp.items:
            for col in [0,1]:
                p = np.percentile(temp.ix[item,1:,col],pvalue)
                m = np.max(data.ix[item,:,col])
                lines.append([(i,np.min(data.ix[item,:,col])/m),(i,p/m)])
                #we will place a point at the observed value
                points.append((i,data.ix[item,0,col]/m))
                i = i + 1
        exec("lc"+str(j) + "= mc.LineCollection(lines)")
        ax.set_ylim(0,110/100.)
        b = 10
        ax.set_xlim(0-b,b+len(points))
        ax.plot([x[0] for x in points],[y[1] for y in points],"r^")
        ax.add_collection(eval("lc"+str(j)))
        ax.set_title(str(pvalue)+"th percentile test on US " + el + " elections")
    fig.savefig(el + str(pvalue)+"percentile_test.pdf")

pvalues = [90,95,99]
print "Target Percentile " "Percent Accepted"
for pvalue in pvalues:
    accept_election = []
    rejected_elections = []
    i = 1
    lines = []
    points = []
    #for item in data.items[0:1]:
    for item in data.items[:]:
        for col in [0,1]:
        #for col in range(sum(~data.ix[item,0].isnull())):
            #calculate whether we accept or reject at the p-value
            p = np.percentile(data.ix[item,1:,col],pvalue)
            valid = data.ix[item,0,col] < p
            accept_election.append(data.ix[item,0,col] < p)
            #Take all the sim results and the real results and place on a scale from 0 to 100
            m = np.max(data.ix[item,:,col])
            lines.append([(i,np.min(data.ix[item,:,col])/m),(i,p/m)])
            #we will place a point at the observed value
            points.append((i,data.ix[item,0,col]/m))
            i = i + 1
            if ~valid:
                rejected_elections.append(item)
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



