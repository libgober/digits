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

filein = "dec31"

data = pd.read_pickle(filein)
meta = pd.DataFrame([i.split("_") for i in data.items])
#two elections are not named as the others, we throw them out
data = data[meta.ix[meta.ix[:,4].isnull(),:].index,:,:]
meta = pd.DataFrame([i.split("_") for i in data.items])
meta.columns = ["State","Year","ElectionYear","Type"]
election_types = ["GOV","USS","USP"]
election_years = ["2000","2004","2008","2012"]
pvalues = [90,95,99]
print "Target Percentile " "Percent Accepted"
for pvalue in pvalues:
    accept_election = []
    for el in election_types:
        j = 1 #subplot number
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex=False, sharey=False)
        for year in election_years:
            i = 0 #x-axis location
            ax = eval("ax" + str(j))
            lines = []
            points = []
            text = []
            temp = data[meta[(meta.Year == year) & (meta.Type == el)].index]
            for item in temp.items:
                for col in [0,1]:
                    p = np.percentile(temp.ix[item,1:,col],pvalue)
                    accept_election.append(data.ix[item,0,col] < p) #record whether we'd accept or reject
                    m = np.max(temp.ix[item,:,col])
                    lines.append([(i,np.min(temp.ix[item,:,col])/m),(i,p/m)])
                    #we will place a point at the observed value
                    points.append((i,temp.ix[item,0,col]/m))
                    if temp.ix[item,0,col] > p:
                        text.append((i,1.05,item[0:2]))
                    i = i + 1
            lc = mc.LineCollection(lines)
            ax.set_ylim(0,110/100.)
            b = 10
            ax.set_xlim(0-b,b+len(points))
            ax.plot([x[0] for x in points],[y[1] for y in points],"r^")
            ax.add_collection(lc)
            ax.set_title(str(year)+ " US " + el)
            for entry in text:
                x,y,txt = entry
                ax.text(x,y,txt,fontsize=6)
            j = j+1
        fig.suptitle("Target Acceptance Rate: " + str(pvalue),fontsize=14, fontweight='bold')
        #fig.savefig(el + str(pvalue)+"percentile_test.pdf")
    print pvalue, np.mean(accept_election)






