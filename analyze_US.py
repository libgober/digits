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
from matplotlib.colors import ColorConverter
from matplotlib import collections as mc
import sys
import os
### SOME SETTING THAT SHOULD BE CHANGED 
os.chdir("US")

filein = "dec31"
stylist = ColorConverter()
partycolors = {0 : stylist.to_rgba("blue"), 1: stylist.to_rgba("red")}

######


data = pd.read_pickle(filein)
meta = pd.DataFrame([i.split("_") for i in data.items])
#two elections are not named as the others, we throw them out
data = data[meta.ix[meta.ix[:,4].isnull(),:].index,:,:]
meta = pd.DataFrame([i.split("_") for i in data.items])
meta.columns = ["State","Year","ElectionYear","Type"]
election_types = ["GOV","USS","USP"]
election_years = ["2000","2004","2008","2012"]
pvalues = [90,95,99] #do not change, np.precentile requires to be between 0 and 100
print "Target Percentile " "Percent Accepted"

    
for pvalue in pvalues:
    accept_election = []
    for el in election_types:
        j = 1 #subplot number
        i = 0 #x-axis location
        fig, ((ax1, ax2, ax3, ax4)) = plt.subplots(1, 4, sharex=False, sharey=True)
        for year in election_years:
            """ POINTS AND LINE RELATED STUFF """
            ax = eval("ax" + str(j))
            b = 0.2
            ax.set_xlim(left=i-b) #set x-axis to start at wherever we are on the x-axis to begin with
            lines = []
            party = []
            points = []
            text = []
            temp = data[meta[(meta.Year == year) & (meta.Type == el)].index]
            for col in [0,1]:
                for item in temp.items:
                    p = np.percentile(temp.ix[item,1:,col],pvalue)
                    accept_election.append(data.ix[item,0,col] < p) #record whether we'd accept or reject
                    m = np.max(temp.ix[item,:,col])
                    lines.append([(i,np.min(temp.ix[item,:,col])/m),(i,p/m)])
                    #we will place a point at the observed value
                    points.append((i,temp.ix[item,0,col]/m))
                    if temp.ix[item,0,col] > p:
                        text.append((i,1.05,item[0:2]))
                    party.append(col) #add party information
                    i = i + 1
            lc = mc.LineCollection(lines,colors=[partycolors[foo] for foo in party]) 
            ax.plot([x[0] for x in points],[y[1] for y in points],"r^")  
            ax.add_collection(lc)         
            """ ANNOTATIONS ON FIGURE """
            for entry in text:
                x,y,txt = entry
                ax.text(x,y,txt,fontsize=6)
            """ AXIS STUFF """
            ax.set_xlim(right=i+b) #now i has changed, it is at the most right of the x-axis
            ax.set_ylim(0,110/100.)
            ax.yaxis.set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False) #turn off the bar to the right
            if j == 1:
                ax.yaxis.set_visible(True)
                ax.spines['left'].set_visible(True)
            if j == 4:
                ax.spines['right'].set_visible(True) 
            j = j+1
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
            ax.set_title(str(year))
            ax.title.set_position((0.5,0))
        fig.suptitle(el + " \nTarget Acceptance Rate: " + str(pvalue) + "; Actual " + str(100*np.mean(accept_election))[0:5],fontsize=14, fontweight='bold')
        fig.subplots_adjust(wspace=0)
        fig.savefig(el + str(pvalue)+"percentile_test.pdf")
    print pvalue, np.mean(accept_election)

os.chdir("..")






