"""
Takes as input a csv of election results from command line, which should be formatted as

    akp    mhp    chp    other
    128    101    25     2
    117    81     45     8
    :       :      :     :
    122    102    28     2
    

Returns a pickled election result distribution

Takes as input a file of csv results, an output file to simulate to, a number of simulations,
and whether compactification should be done.

"""

######## HEADERS

import csv
import os
import pandas as pd
import numpy as np
import sys

   
def clean(returns):
    if not isinstance(returns,pd.DataFrame):
        raise Exception('Returns is not a Pandas Dataframe')
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
    return(returns.apply(simulate_box,
    axis='columns',
    broadcast=False,
    inflate_mode='mean',
    debug_mode=debug_mode,
    raw=False)) #note axis is columns applies to each row


########### MAIN ################
## GET THE INPUT INFORMATION
fin = sys.argv[1]
fout = sys.argv[2]
try:
    nsims = int(sys.argv[3])
except:
    nsims = 1

    
    
## BREAK APART DATA INTO A PART TO SIMULATE AND PART TO SAVE AS META DATA
data = pd.read_csv(fin)
is_data_column = data.columns.str.slice(0,2) == "p_"
meta = data.ix[:,~is_data_column]
to_simulate = data.ix[:,is_data_column]
to_simulate = clean(to_simulate)

sims = {}
for i in range(nsims):
    sims["sim_"+str(i)] = meta.join(simulate_election(to_simulate,inflate_mode='dirichlet'))

sims = pd.Panel(sims)
sims.to_pickle(fout + "_" + "nsims"+str(nsims) + ".pkl")





