"""
Takes as input a csv of election results from command line, which should be formatted as

    akp    mhp    chp    other
    128    101    25     2
    117    81     45     8
    :       :      :     :
    122    102    28     2
    

Returns a pickled election result distribution

"""

######## HEADERS

import csv
import os
print(os.system("hostname"))
import sys
print(sys.path)
import imp
print(imp.find_module("pandas"))
import pandas as pd
import numpy as np


def simulate_box(counts,inflate=True):
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
    """
    if inflate is True:
        counts = counts + 1./len(counts)
    Total = sum(counts)
    p = counts/Total
    return(np.random.multinomial(Total,p)) 
    
def simulate_election(returns,inflate=True):
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
    return(returns.apply(simulate_box,axis='columns',broadcast=True,inflate=inflate,raw=True)) #note axis is columns applies to each row


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

########### MAIN ################
print(sys.argv)
fin = sys.argv[1]
data = pd.read_csv(fin)
fout = sys.argv[2]

sims = simulate_digit_distro(1,data,inflate=True)
sims.to_csv(fout + ".csv",index=False)



