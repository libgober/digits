"""
Takes as input a csv of election results from command line, which should be formatted as

    akp    mhp    chp    other
    128    101    25     2
    117    81     45     8
    :       :      :     :
    122    102    28     2
    

Returns a pickled election result distribution

Takes as input a file of csv results, an output file to simulate to, and a number of simulations.

"""

######## HEADERS

import csv
import os
import pandas as pd
import numpy as np
import sys

def simulate_box(counts,inflate_mode='mean',debug_mode=False):
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
    Total = float(sum(counts))
    if inflate_mode == 'mean':
        #inflate to give some small chance of 0 entries to be non-zero
        counts = counts + 1./len(counts)
        p = counts/(Total+1.)
    elif inflate_mode == 'dirichlet':
        pseudo_counts = counts + 1./len(counts)
        p = np.random.dirichlet(pseudo_counts,1)[0]
    else:
        p = counts/Total
    out = np.random.multinomial(Total,p)
    if sum(out) < 0:
        print "Input", counts 
        print out
        Exception("Something went wrong")
    return(out)
    
def clean(returns):
    #make sure there are no NAN values, and make sure the returns are integers!
    returns = returns.fillna(0)
    #make sure that there are no negative vote totals
    #this would happen if the total column was not correctly entered
    #we choose to throw out such mistakes rather than throw out the whole election 
    #we do not make any attempt to impute
    returns = returns.loc[returns.apply(lambda x: all(x >= 0), axis=1),:]
    #get rid of all 0 rows
    returns = returns.loc[returns.apply(lambda x: any(x > 0),axis=1),:]
    #get rid of all 0 columns
    returns  = returns.loc[:,(returns != 0).any(axis=0)]
    return(returns)
    
def simulate_election(returns,inflate_mode='mean',debug_mode=False):
    """
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
    return(returns.apply(simulate_box,axis='columns',broadcast=False,inflate_mode='mean',debug_mode=debug_mode,raw=False)) #note axis is columns applies to each row


def digit_distro(returns):
    last = returns % 10
    return(last.apply(lambda x: x.value_counts(),axis='index'))

def simulate_digit_distro(reps,returns,inflate_mode='mean',multiprocess=False):
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
    func = (lambda x: digit_distro(simulate_election(x,inflate_mode='mean')))
    return(func(returns))

########### MAIN ################
fin = sys.argv[1]
data = pd.read_csv(fin,dtype=np.float64)
fout = sys.argv[2]
try:
    nsims = int(sys.argv[3])
except:
    nsims = 1

#sims = simulate_digit_distro(1,data,inflate=True)#sims = simulate_digit_distro(1,data,inflate=True)
if nsims==1 :
    sims = simulate_election(data,inflate_mode='mean')
    sims.to_csv(fout + ".csv",index=False)

if nsims > 1:
    sims={}
    for i in range(nsims):
        sims["sim_"+str(i)] = simulate_election(data,inflate_mode='dirichlet')
    sims = pd.Panel(sims)
    sims.to_pickle(fout + "_" + "nsims"+str(nsims) + ".pkl")





