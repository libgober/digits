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

filein = 'SwedenJan4.pkl'
data = pd.read_pickle(filein)
election_types = {
    "Riksdagsval": data.items[data.items.str.lower().str.contains("riksdagsval")],
    "Landstingsval": data.items[data.items.str.lower().str.contains("Landstingsval")], 
    "Kommunval": data.items[data.items.str.lower().str.contains("Landstingsval")]}
election_years = {
    "Riksdagsval" : [2002,2010,2014],
    "Landstingsval" : [2010,2014],
    "Kommunval" : [2010,2014]
}

numberofparties = len(data.minor_axis)
cm = plt.get_cmap("viridis")
gradient = np.linspace(0, 1,numberofparties)
ColorScheme = {data.minor_axis[i] : cm(gradient[i]) for i in range(numberofparties)}

pvalues = [90,95,99] #must be between 0 and 100
print "Pvalue, Actual"
DEBUGALL = []
for pvalue in pvalues:
    overall = []
    for election_type in election_types.keys():
        j=0 #index of subplot we are working on
        fig, ax_all = plt.subplots(1,len(election_years[election_type]))
        accept_election = []
        DEBUG = []
        for year in election_years[election_type]:
            lines = [] #store information about segments
            points = [] #store information about points
            text = [] #store text
            COLOR = []
            i = 0 #iterator controlling placement on x
            elections_in_year_in_type = data.items[
                    data.items.str.contains(str(year),case=False) & 
                    data.items.str.contains(election_type,case=False)
                    ]
            parties =  data.minor_axis #get name of parties in this election
            for party in parties: 
                partydata  = (data.ix[:,:,party])  #extract parties data, returns a 500 x #elections dataframe
                for electionName in elections_in_year_in_type:
                    statistics = partydata.ix[:,electionName]
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
                            #print "Rejecting", electionName, party, year
                        accept_election.append(pObs <= c)
                        DEBUG.append([electionName, party, year,pvalue])
                        i = i + 1
                        COLOR.append(ColorScheme[party])
            lc = mc.LineCollection(lines,colors=COLOR)
            ax = ax_all[j]
            ax.set_ylim(0,110/100.)
            b = 5
            ax.set_xlim(0-b,b+len(points))
            ax.plot([x[0] for x in points],[y[1] for y in points],"r^")
            ax.add_collection(lc)
            ax.set_title(year)
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
            LargestElectionIndex = max(range(len(election_years[election_type])))
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
            ax.set_title(str(year))
            ax.title.set_position((0.5,0))
            #next iter setup
            j = j+1
        fig.suptitle(election_type + " \nTarget Acceptance Rate: " + str(pvalue) + "; Actual " + str(100*np.mean(accept_election))[0:5],fontsize=14, fontweight='bold')
        fig.subplots_adjust(wspace=0)
        fig.savefig(election_type+ str(pvalue)+"_percentile_test.pdf")
        overall = overall + accept_election
    print pvalue, np.mean(overall)
    DEBUGALL = DEBUGALL + DEBUG
    
    
 #### SOME ANALYSIS NO OUTPUT PRODUCED
party_elections = pd.DataFrame(DEBUGALL)
party_elections.columns = ["province","election","party","pvalue"]
party_elections["accept"] = pd.Series(results)
party_elections = party_elections[party_elections.pvalue == 95]

###
#group by election and place
grouped = party_elections.groupby(["province","election"])
grouped_accept = grouped['accept']
summary = grouped_accept.agg([np.sum,len,np.mean,lambda x:1-np.mean(x)])
summary.columns = ["#Accepted","#Districts","Fraction Accepted","Fraction Rejected"]
summary.to_clipboard()
rejects = party_elections[~party_elections.accept]
pd.crosstab(rejects.party,rejects.election).to_clipboard()
pd.crosstab(rejects.party,rejects.election).to_clipboard()

#chisquared test
o1 = sum(party_elections.accept)
o2 =len(party_elections.accept) - sum(party_elections.accept)
N= o1+o2
p=0.95
chisquare(f_obs=[o1,o2],f_exp=[0.95*N,0.05*N])

pd.pivot_table(party_elections,columns="election",index="party",aggfunc=len).fillna(0).sum(0)
pd.pivot_table(party_elections,columns="election",index="party",aggfunc=len)


###### GROUP BY ELECTIONS
""""

    T   F
EL
EL
"""|

piv = pd.pivot_table(party_elections.ix[:,["election","accept"]],columns="accept",index="election",aggfunc=len,margins=True).to_clipboard(sep="|")  


