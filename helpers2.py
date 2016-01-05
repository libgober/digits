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