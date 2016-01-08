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
from helpers2 import digit_aggregate
from scipy.stats import chisquare

##### LOCAL INFO
#RCE
#all = pd.HDFStore("Real.h5")
#LAPTOP
all = pd.HDFStore('/Users/brianlibgober/Dropbox/Digit_stats/RawData/US/sourcedata_GOVUSSUSP')
###########
election_types = ["GOV","USS","USP"]
election_years = ["2000","2004","2008","2012"]
pvalue = .95
print "Target Percentile " "Percent Accepted"

overall = []
for el in election_types:
    ObservedPValues = []
    j = 1 #subplot number
    i = 0 #x-axis location
    fig, ((ax1, ax2, ax3, ax4)) = plt.subplots(1, 4, sharex=False, sharey=True) #each election year gets its own axis
    for year in election_years:
        ### SETUP AXES AND POINT STORAGE
        ax = eval("ax" + str(j))
        b = 0.2
        ax.set_xlim(left=i-b)
        points = []
        text = []
        #prepare to iterate over all elections in that year
        keys = [key for key in all.keys() if (year in key) & (el in key)]
        for key in keys:    #e.g. key = all.keys()[0]
            sheet =  all[key] #load the sheet
            sheet = digit_aggregate(sheet)
            parties = [party for party in sheet.columns if 'other' not in party]
            for party in parties:
                chi2, pObs = chisquare(sheet[party])
                ObservedPValues.append(pObs)
                points.append((i,pObs,party))
                if pObs < 1-pvalue:
                    text.append((i,1.05,key[0:2]))
                i = i+1
        ax.plot([x[0] for x in points if "d" in x[2]],[y[1] for y in points if "d" in y[2]],"r^",color="blue") #plot dems
        ax.plot([x[0] for x in points if "r" in x[2]],[y[1] for y in points if "r" in y[2]],"r^",color="red") #plot republicans
        ax.axhline(y=1-0.95,c="black",linewidth=0.5,zorder=0) #horizontal line
        ax.axhline(y=1-0.90,c="black",linewidth=0.25,zorder=0) #horizontal line
        ax.axhline(y=1-0.99,c="black",linewidth=0.75) 
        ##### GENERIC PLOTTING AXIS STUFF
        ax.set_xlim(right=i+b) #now i has changed, it is at the most right of the x-axis
        ax.set_ylim(0,1.1)
        ax.yaxis.set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False) #turn off the bar to the right
        if j == 1:
            ax.yaxis.set_visible(True)
            ax.spines['left'].set_visible(True)
            ax.yaxis.set_label("P-Value")
        if j == 4:
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
        ax.set_title(str(year))
        ax.title.set_position((0.5,-0.05))
        #finish
        j = j+1
            ### Legend ###
    overall = overall + ObservedPValues 
    ObservedPValues = np.array(ObservedPValues) 
    values =  {
    '0.90' : str(np.mean(ObservedPValues < 1-0.90))[0:5],
    '0.95' : str(np.mean(ObservedPValues < 1-0.95))[0:5],
    '0.99' : str(np.mean(ObservedPValues < 1-0.99))[0:5]
    }
    txt =     """P:PRejected |0.90:%(0.90)s | 0.95:%(0.95)s | 0.9:%(0.99)s """ % values
    fig.subplots_adjust(wspace=0)
    plt.text(0.1,-0.1,txt)
    fig.suptitle(el + "PValues Using ChiSquare Test Against Uniform",fontsize=14, fontweight='bold')
    plt.savefig(el + "chisq.pdf")





overall = np.array(overall) 
values =  {
'0.90' : str(np.mean(overall > 0.90))[0:5],
'0.95' : str(np.mean(overall > 0.95))[0:5],
'0.99' : str(np.mean(overall > 0.99))[0:5]
}
txt =     """P:PRejected |0.90:%(0.90)s | 0.95:%(0.95)s | 0.99:%(0.99)s """ % values

print txt.replace(":","    ").replace("|","\n")

