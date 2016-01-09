from scipy.spatial import distance
import pandas as pd

def digit_aggregate(table):
    """
    Takes a table of returns and produces a table with frequency of digits
    """
    table = table % 10
    digits = table.apply(lambda x: x.value_counts(),axis='index')
    return(digits)

def custom_dist(a,b):
    """ Assumes NAN means 0 """
    a = a.fillna(0)
    b = b.fillna(0)
    return(distance.euclidean(a,b))

def read_many_csv(fins):
    """ Takes a list of csv file locations, reads them in ,returns a dataframe """
    temp = {}
    for fin in fins:
        temp[fin] = pd.read_csv(fin)
    return(pd.Panel(temp))
    
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
