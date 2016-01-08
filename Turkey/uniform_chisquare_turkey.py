"""

Takes in an HDFStore.  Produces graphs that show rejection regions for uniform.

"""
import os
import glob
import subprocess
import errno
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ColorConverter
from matplotlib import collections as mc
from scipy.stats import chisquare
import sys
sys.path.append("")
from helpers2 import digit_aggregate, read_many_csv
##### LOCAL INFO
#RCE
#all = pd.HDFStore("Real.h5")
#LAPTOP
Real_Results = "/Users/brianlibgober/Dropbox/Digit_stats/RawData/Turkey_national/Cleaned/"
os.chdir(Real_Results)
fins = glob.glob("*.csv")
Panel = read_many_csv(fins)
meta = Panel.items.str.split("_")
meta = pd.DataFrame([meta.str[0], meta.str[1], meta.str[2]]).T
meta.ix[meta.ix[:,2] == "ge5percent.csv",2] = "Nov"
meta.ix[meta.ix[:,2] == '1',2] = "JUN"
meta.ix[meta.ix[:,2] == '2',2] = "NOV"
meta.ix[:,"election"] = meta.ix[:,1].str.cat(meta.ix[:,2]).str.lower()
###########

pvalue = .95
print "Target Percentile " "Percent Accepted"

fig, axall = plt.subplots(1, 3, sharex=False, sharey=True) #each election year gets its own axis
ObservedPValues = []
j = 0 #subplot number
i = 0 #x-axis location
for el in np.unique(meta.election):
    items = meta.index[meta.election == el]
    ax = axall[j]
    b = 0.2
    ax.set_xlim(left=i-b)
    points = []
    text = []
    for party in Panel.minor_axis[1:]:
        for election in Panel.items[items]:
            #if there is any data in that parties' column for the particular election
            if any(~Panel.ix[election,:,party].isnull()):
                sheet =  Panel.ix[election,:,party] #load the sheet
                sheet = sheet.dropna(axis=0,how="all")
                sheet = sheet % 10
                lookup = {i : 0 for i in range(10)}
                for key in lookup.keys():
                    try:
                        lookup[key]  = sheet.value_counts(sort=False)[key]
                    except:
                        print 
                chi2, pObs = chisquare(f_obs=lookup.values())
                ObservedPValues.append(pObs)
                points.append((i,pObs,party))
                if pObs <= 0.05:
                    text.append((i,1.05,election.split("_")[0]+party))
                i = i+1
    ax.plot([x[0] for x in points],[y[1] for y in points],"r^",color="blue") #plot dems
    ax.axhline(y=0.05,c="black",linewidth=0.5,zorder=0) #horizontal line
    ax.axhline(y=0.10,c="black",linewidth=0.25,zorder=0) #horizontal line
    ax.axhline(y=0.011,c="black",linewidth=0.75) 
    ##### GENERIC PLOTTING AXIS STUFF
    ax.set_xlim(right=i+b) #now i has changed, it is at the most right of the x-axis
    ax.set_ylim(0,1.1)
    ax.yaxis.set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False) #turn off the bar to the right
    if j == 0:
        ax.yaxis.set_visible(True)
        ax.spines['left'].set_visible(True)
        ax.yaxis.set_label("P-Value")
    if j == 2:
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
    ax.set_title(el)
    ax.title.set_position((0.5,-0.05))
    #finish
    j = j+1
        ### Legend ###
ObservedPValues = np.array(ObservedPValues) 
values =  {
'0.90' : str(np.mean(ObservedPValues > 0.1))[0:5],
'0.95' : str(np.mean(ObservedPValues > 0.05))[0:5],
'0.99' : str(np.mean(ObservedPValues > 0.01))[0:5]
}
txt =     """P:Accepted |0.90:%(0.90)s | 0.95:%(0.95)s | 0.99:%(0.99)s """ % values
fig.subplots_adjust(wspace=0)
plt.text(0.1,-0.1,txt)
fig.suptitle(el + "PValues Using ChiSquare Test Against Uniform",fontsize=14, fontweight='bold')
plt.savefig("Turkey_chisq.pdf")


observation_sizes = []
for item in Panel.items:
    observation_sizes.append(np.shape(Panel.ix[item].dropna(axis=0,how="all"))[0])

            



