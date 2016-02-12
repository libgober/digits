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
import scipy as sp
from scipy.special import gammaln,psi
from scipy.optimize import minimize
from numpy.random import dirichlet, multinomial
import sys


def log_polya(Z,alpha):
    """
    Z is a vector of counts
    https://en.wikipedia.org/wiki/Dirichlet-multinomial_distribution
    http://mimno.infosci.cornell.edu/info6150/exercises/polya.pdf
    """
    if not isinstance(alpha,np.ndarray):
        alpha = np.array(alpha)
    if not isinstance(Z,np.ndarray):
        Z = np.array(Z)
    #Concentration Parameter
    A = sum(alpha)
    #Number of Datapoints
    N = sum(Z)
    return gammaln(A) - gammaln(N+A) + sum(gammaln(Z+alpha) - gammaln(alpha))

def log_polya_derivative(Z,alpha):
    if not isinstance(alpha,np.ndarray):
        alpha = np.array(alpha)
    if not isinstance(Z,np.ndarray):
        Z = np.array(Z)
    #Concentration Parameter
    A = sum(alpha)
    #Number of Datapoints
    N = sum(Z)
    K = len(Z)
    return [psi(A) - psi(N+A) + psi(Z[i]+alpha[i]) - psi(alpha[i]) for i in xrange(K)]

def llike(data,alpha):
    return sum(data.apply(log_polya,1,alpha=alpha))

def gradient_llike(data,alpha):
    return data.apply(log_polya_derivative,1,alpha=alpha).sum(0)
                        
def mle(data):
    """
    To test the accuracy use the following code
    from numpy.random import dirichlet, multinomial
    alpha = [10,0,30,0,50]
    p = pd.DataFrame(dirichlet(alpha,100))
    data = p.apply(lambda x: multinomial(100,x),1)
    a = np.array(data.mean(0))
    result = minimize(lambda a: -1*llike(data,exp(a)),x0=np.log(a),method="Nelder-Mead")
    exp(result.x) #should be close to alpha, i.e. [10,20,30,40]
    """
    #0 columns make it go insane, so let's drop those
    mle = pd.Series(np.shape(data)[1]*[np.nan],index=data.columns)
    nonzero_columns = (data != 0).any()
    data = data.ix[:,nonzero_columns]
    a = np.array(data.mean(0))
    #optimize the log likelihood using Nelder-Mead
    result = minimize(lambda a: -1*llike(data,np.exp(a)),x0=np.log(a),method="Nelder-Mead")
    #improve the optimization a little bit by using BFGS
    result = minimize(fun=lambda a: -1*llike(data,np.exp(a)),
                x0=result.x,
                jac=lambda a: -1*gradient_llike(data,np.exp(a)),
                method="BFGS"
                )
    mle[nonzero_columns] = np.exp(result.x)
    mle[~nonzero_columns] = 0 
    #return the exponentiated values
    return mle

def sim_polya(alpha):
    """Mainly for debugging the MLE code """
    p = pd.DataFrame(dirichlet(alpha,100))
    data = p.apply(lambda x: multinomial(300,x),1)
    return(data)


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
    If inflate_mode=mean, 1/# parties is added to every entry to prevent a 0 chance of any party.
    So if inflate_mode=mean, the proportion for AKP would be 117.25/252. 
    
    If inflate_mode = dirichelt, we draw from a posterior corresponding to a jeffry's dirichlet prior
    
    If inflate_mode is a pandas Series, for example an object returned by the MLE function in this script
    then we treat inflate_mode as a vector of prior counts.
    
    If inflate is turned off, the proportion for AKP would be 117/251.
    
    
    
    NOTE THAT WHATEVER IS FED TO THIS FUNCTION MUST ALREADY BE CLEAN.
    
    *** counts = to_simulate.iloc[1,:]

    """
    if debug_mode:
        print counts
    Total = float(sum(counts))
    if isinstance(inflate_mode,pd.Series):
        pseudo_counts = counts + inflate_mode
        p = np.random.dirichlet(pseudo_counts,1)[0]
    elif inflate_mode == 'mean':
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
    inflate_mode=inflate_mode,
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
    
column_to_group = "ilce" #sys.argv[4]
  
## BREAK APART DATA INTO A PART TO SIMULATE AND PART TO SAVE AS META DATA
""""
cd ~/Dropbox/Digit_stats/RawData/Turkey_national/csv_prov/
fin = 'y2007_Agri.csv'
data.columns = list(data.columns[:1]) + list("m_"+data.columns[1:3]) + list(data.columns[3:])

"""

data = pd.read_csv(fin)
is_data_column = data.columns.str.slice(0,2) == "p_"
meta = data.ix[:,~is_data_column]

sims = pd.Panel(items=["sim_" + str(i) for i in range(nsims)],
            major_axis=meta.index,minor_axis=data.columns)

if column_to_group is not "None":
    #first precompute the mles, this was necessary because merging was awkward for unclear reasons
    thetas = {}
    for unit in np.unique(meta[column_to_group]):
        rows_selected = meta[column_to_group] == unit
        to_simulate = data.ix[rows_selected,is_data_column].astype('float64').fillna(0)
        thetas[unit] = mle(to_simulate)
    #now do the sims
    sims = {}
    for i in range(nsims):
        results = []
        for unit in np.unique(meta[column_to_group]):
            rows_selected = meta[column_to_group] == unit
            to_simulate = data.ix[rows_selected,is_data_column].astype('float64').fillna(0)
            simulated = simulate_election(to_simulate,inflate_mode=thetas[unit],debug_mode=False)
            results.append(simulated)
        sim = meta.join(pd.concat(results))
        sims["sim_"+str(i)] = sim
    sims = pd.Panel(sims,minor_axis=data.columns)
    
else:
    to_simulate = data.ix[:,is_data_column].astype('float64').fillna(0)
    sims = {}
    for i in range(nsims):
        sims["sim_"+str(i)] = meta.join(simulate_election(to_simulate,inflate_mode='dirichlet',debug_mode=False))
    sims = pd.Panel(sims)


sims.to_pickle(fout + "_" + "nsims"+str(nsims) + ".pkl")





