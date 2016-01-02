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
import re

filein = 'SwedishDec29.pkl'
data = pd.read_pickle(filein)
election_types = {"Riksdagsval": [0,3,6], "Landstingsval": [2,5], "Kommunval": [1,4]}
pvalue = 99

## Riksdagsval
fig, (ax1, ax2, ax3) = plt.subplots(1,3) #create a 1x3 plot
j=1
for itemNumber in election_types["Riksdagsval"]:
    lines = [] #store information about segments
    points = [] #store information about points
    text = [] #store text
    i = 0 #iterator controlling placement on x
    for col in (data.ix[itemNumber]).columns: 
        p = np.percentile(data.ix[itemNumber,1:,col],pvalue) #critical value for the sims.
        m = np.max(data.ix[itemNumber,:,col]) #max value for sims and real
        lines.append([(i,np.min(data.ix[itemNumber,:,col])/m),(i,p/m)]) #add segment information, (x1,y1) to (x2,y2)
        #we will place a point at the observed value
        points.append((i,data.ix[itemNumber,0,col]/m))
        if data.ix[itemNumber,0,col] > p:
            text.append((i,1.05,col))
        i = i + 1
    lc = mc.LineCollection(lines)
    ax = eval("ax" + str(j))
    ax.set_ylim(0,110/100.)
    b = 5
    ax.set_xlim(0-b,b+len(points))
    ax.plot([x[0] for x in points],[y[1] for y in points],"r^")
    ax.add_collection(lc)
    year = re.search("\d+",data.items[itemNumber]).group(0) #get first sequence of digits in sheet name
    ax.set_title(year)
    for entry in text:
        x,y,txt = entry
        ax.text(x,y,txt,fontsize=6)
    j = j+1
    fig.suptitle("Riksdagsval, Target Acceptance Rate: " + str(pvalue),fontsize=14, fontweight='bold')
fig.savefig("Riksdagsval_"+ str(pvalue)+"_percentile_test.pdf")

#####  Other two elections
for t in ["Landstingsval","Kommunval"]:
    fig, (ax1, ax2) = plt.subplots(1,2) #create a 1x2 plot
    j=1
    for itemNumber in election_types[t]:
        lines = [] #store information about segments
        points = [] #store information about points
        text = [] #store text
        i = 0 #iterator controlling placement on x
        for col in (data.ix[itemNumber]).columns: 
            p = np.percentile(data.ix[itemNumber,1:,col],pvalue) #critical value for the sims.
            m = np.max(data.ix[itemNumber,:,col]) #max value for sims and real
            lines.append([(i,np.min(data.ix[itemNumber,:,col])/m),(i,p/m)]) #add segment information, (x1,y1) to (x2,y2)
            #we will place a point at the observed value
            points.append((i,data.ix[itemNumber,0,col]/m))
            if data.ix[itemNumber,0,col] > p:
                text.append((i,1.05,col))
            i = i + 1
        lc = mc.LineCollection(lines)
        ax = eval("ax" + str(j))
        ax.set_ylim(0,110/100.)
        b = 5
        ax.set_xlim(0-b,b+len(points))
        ax.plot([x[0] for x in points],[y[1] for y in points],"r^")
        ax.add_collection(lc)
        year = re.search("\d+",data.items[itemNumber]).group(0) #get first sequence of digits in sheet name
        ax.set_title(year)
        for entry in text:
            x,y,txt = entry
            ax.text(x,y,txt,fontsize=6)
        j = j+1
        fig.suptitle(t + ", Target Acceptance Rate: " + str(pvalue),fontsize=14, fontweight='bold')
    fig.savefig(t + str(pvalue)+"_percentile_test.pdf")




