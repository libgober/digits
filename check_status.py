import os
import sys
import pandas as pd
import numpy as np
from scipy.spatial import distance
 
def simulate_box(counts,inflate=True,debug_mode=False):
    """
    Takes a vector of election counts like
    akp      117
    mhp       81
    chp       45
    other      8
    
    Which should sum to a total (here 251).  
    
    Returns a random draw from a multinomial. 
    
    The parameter of the multinomial is taken directly from the input vector.
    If inflate is on, 1/# parties is added to every entry to prevent a 0 chance of any party.
    
    If inflate is turned on, the proportion for AKP would be 117.25/252. 
    If inflate is turned off, the proportion for AKP would be 117/251.
    
    NOTE THAT WHATEVER IS FED TO THIS FUNCTION MUST ALREADY BE CLEAN.
    """
    if debug_mode:
        print counts
    if any(counts < 0):
      	print counts
      	for entry in range(len(counts)):
            counts[entry] = None
      	counts.fillna(np.nan)
      	return(None)
    if all(counts == 0):
        return(counts)
    if all(~counts.isnull()):
    #no NAs
        if inflate is True:
            counts = counts + 1./len(counts)
        Total = sum(counts)
        p = counts/Total
        if inflate is True:
            Total = Total - 1
        return(np.random.multinomial(Total,p))
    elif all(counts.isnull()):
		#ALL NAs
	return(counts)
    else:
        good_counts = counts[~counts.isnull()]
        if inflate is True:
            good_counts = good_counts + 1./len(good_counts)
        Total = sum(good_counts)
        p = good_counts/Total
        foo = np.random.multinomial(Total,p)
        counts[~counts.isnull()] = foo
        return(counts)
    
def clean(returns):
    #make sure there are no NAN values
    returns = returns.fillna(0)
    
    returns = returns.loc[returns.apply(lambda x: all(x >= 0), axis=1),:]
    
    return(returns)
    


def simulate_election(returns,inflate=True,debug_mode=False):
    """"
    Takes a pandas dataframe of election returns like
    akp    mhp    chp    other
    128    101    25     2
    117    81     45     8
    :       :      :     :
    122    102    28     2

    calls the simulate_box function on each row
    
    returns another matrix of election returns
    """
    returns = clean(returns)
    return(returns.apply(simulate_box,axis='columns',broadcast=False,inflate=inflate,debug_mode=debug_mode,raw=False)) #note axis is columns applies to each row


def digit_distro(returns):
    last = returns % 10
    return(last.apply(lambda x: x.value_counts(),axis='index'))

def simulate_digit_distro(reps,returns,inflate=True,multiprocess=False):
    """For Reps number of times
    
    Takes a pandas dataframe of election returns like
        akp    mhp    chp    other
        128    101    25     2
        117    81     45     8
        :       :      :     :
        122    102    28     2
    
    call the simulate_box function on each row to make simulated returns
    summarize  the digit distribution on simulated reutrns
    return a dictionary containing these digit summarize
    inflate will give a small boost to 0 totals, see simulate_box function."""
    func = (lambda x: digit_distro(simulate_election(x,inflate=True)))
    return(func(returns))
    
##### MAIN

"""
NY_2010_g2010_COM
NY_2010_g2010_COM
NY_2010_g2010_GOV
NY_2010_g2010_USS
NY_2010_s2010_USS
"""

datafolder = "/Users/brianlibgober/Dropbox/Digit_stats/Dataverse/Combined"
join = os.path.join
data = pd.read_csv(join(datafolder,"NY_2010.tab"),sep="\t")
senate = data.loc[:,["s2010_USS_dv","s2010_USS_rv","s2010_USS_tv"]]
senate['other'] = senate.s2010_USS_tv - (senate.s2010_USS_rv + senate.s2010_USS_dv)
run_senate = pd.read_csv("/Users/brianlibgober/Dropbox/Digit_stats/Dataverse/Extracts/NY_2010_s2010_USS.csv")

sim = simulate_election(run_senate)
(sim % 10).apply(lambda x: x.value_counts(),axis='index')
(run_senate % 10).apply(lambda x: x.value_counts(),axis='index')

"""
All kinds of badness from floating point errors
"""

#run_senate
fixed = run_senate.fillna(0).astype(int)
fixed.sum(0)

(fixed % 10).apply(lambda x: x.value_counts(),axis='index')

from tqdm import tqdm

temp = {}
for i in tqdm(range(10)):
    foo = simulate_election(run_senate,inflate=False,debug_mode=False)
    temp[i] = foo
panel = pd.Panel(temp)
sims = panel.apply(lambda x: digit_aggregate(x),axis=(1,2))
real = (clean(run_senate) % 10).apply(lambda x: x.value_counts(),axis='index') 
mean = sims.mean(0)
seriessto = []
for columnNumber in [0,1]:
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
####


""" Let's see which guys have this rpobelm """
import glob
import csv
fins = glob.glib("")
bad_guys = []
for fin in fins:
    with open(fin) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader[1:]:
            for entry in row:
                try:
                    if int(entry) < 0:
                        bad_guys.append(fin)
                except:
                    print fin, row
                    
                 
                
    
