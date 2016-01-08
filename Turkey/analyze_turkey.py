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
from matplotlib.colors import ColorConverter, Colormap
import sys
import re
import os

os.chdir("/Users/brianlibgober/GitHub/digits/Turkey/Province Level/")
filein = 'province_level_turkey_jan_6.pkl'
datain = pd.read_pickle(filein)

#### GET SOME META DATA USEFUL FOR MANIPULATING THE PANEL
metain = datain.items.str.split("_")
meta = []
for tag in metain:
    if len(tag) == 2:
        meta.append([tag[0],tag[1]])
    else:
        meta.append([tag[0]+"-"+tag[1],tag[2]])
meta = pd.DataFrame(meta,columns=["election","province"])
######

numberofparties = len(datain.minor_axis)
cm = plt.get_cmap("viridis")
gradient = np.linspace(0, 1,numberofparties)
ColorScheme = {datain.minor_axis[i] : cm(gradient[i]) for i in range(numberofparties)}

pvalues = [90,95,99] #must be between 0 and 100
print "Pvalue, Actual"
DEBUGALL = []
results = []
for pvalue in pvalues:
    j=0 #index of subplot we are working on
    fig, ax_all = plt.subplots(1,len(np.unique(meta.election)))
    accept_election = []
    DEBUG = []
    for election in np.unique(meta.election):
        lines = [] #store information about segments
        points = [] #store information about points
        text = [] #store text
        COLOR = []
        i = 0 #iterator controlling placement on x
        parties =  datain.minor_axis #get name of parties in this election
        data = datain[datain.items[meta.election == election]]
        for party in parties:
            partydata  = (data.ix[:,:,party])  #extract that parties data, returns a 500 x #elections dataframe
            #some parties will not appear very often, so let's kill all their data
            partydata.dropna(axis=1,how="all",inplace=True)
            #note if party data has no columns then this part is skipped, 
            for province in partydata.columns: 
                statistics = partydata.ix[:,province]
                if all(~statistics.isnull()): #only produce a line if we didn't get NAs
                    c = np.percentile(statistics[1:],pvalue) #critical value for the sims.
                    MAX = np.max(statistics) #max value for sims and real
                    MIN = np.min(statistics) #min value for sims and real
                    lines.append([(i,MIN/MAX),(i,c/MAX)]) #add segment information, (x1,y1) to (x2,y2)
                    #we will place a point at the observed value
                    pObs = statistics[0]
                    points.append((i,pObs/MAX))
                    if pObs > c:
                        text.append((i,1.05,party))
                        #print "Rejecting", province, party, election
                    accept_election.append(pObs <= c)
                    DEBUG.append([province.split("_")[1], election,party,pvalue])
                    i = i + 1
                    COLOR.append(ColorScheme[party])
        lc = mc.LineCollection(lines,colors=COLOR)
        ax = ax_all[j]
        ax.set_ylim(0,110/100.)
        b = 5
        ax.set_xlim(0-b,b+len(points))
        ax.plot([x[0] for x in points],[y[1] for y in points],"r^")
        ax.add_collection(lc)
        for entry in text:
            x,y,txt = entry
            ax.text(x,y,txt,fontsize=6)
        """ AXIS STUFF """
        ax.set_xlim(right=i+b) #now i has changed, it is at the most right of the x-axis
        ax.set_ylim(0,110/100.)
        ax.yaxis.set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False) #turn off the bar to the right
        if j == 0:
            ax.yaxis.set_visible(True)
            ax.spines['left'].set_visible(True)
        LargestElectionIndex = max(range(len(np.unique(meta.election))))
        if j == LargestElectionIndex:
            ax.spines['right'].set_visible(True) 
        ax.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelbottom='off') # labels along the bottom edge are off
        ax.tick_params(
            axis = 'y',
            which = 'both',
            right = 'off'
            )
        ax.set_title(election)
        ax.title.set_position((0.5,0))
        #next iter setup
        j = j+1
    fig.suptitle("Turkish Parliament" + " \nTarget Acceptance Rate: " + str(pvalue) + "; Actual " + str(100*np.mean(accept_election))[0:5],fontsize=14, fontweight='bold')
    fig.subplots_adjust(wspace=0)
    fig.savefig("Turkish_Parliament" + str(pvalue)+"_percentile_test.pdf")
    print pvalue, np.mean(accept_election)
    results = results + accept_election
    DEBUGALL = DEBUGALL + DEBUG
    


#### SOME ANALYSIS NO OUTPUT PRODUCED
party_elections = pd.DataFrame(DEBUGALL)
party_elections.columns = ["province","election","party","pvalue"]
party_elections["accept"] = pd.Series(results)
party_elections = party_elections[party_elections.pvalue == 95]
rejects = party_elections[~party_elections.accept]
pd.crosstab(rejects.party,rejects.election).to_clipboard()
pd.crosstab(rejects.party,rejects.election)


