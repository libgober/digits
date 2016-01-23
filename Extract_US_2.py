import os
import pandas as pd
import sys
import glob
import numpy as np
from numpy import unique, concatenate
import re 

def get_county(data):
    """
    TAKES IN A DATA TABLE 
    RETURNS THE NAME OF THE COLUMN CONTAINING COUNTIES IF IT EXIST, OTHERWISE RETURNS EMPTY ARRAY
    """
    if "county_name" in data.columns:
        return(["county_name"])
    elif "county" in data.columns:
        return(["county"])
    elif "parish" in data.columns:
        return(["parish"])
    else:
        return([])

def get_election(code,data):
    """ Takes a code corresponding to office such as GOV,TRE,USS,USP,LTG and a datatable.
    Returns the columns containing dem and republican vote totals.
    If multiple matches, returns an array of 0 length as a fail safe.
    """
    columns = [colname for colname in data.columns if code in colname]
    dem_columns = [colname for colname in columns if "dv" in colname]
    rep_columns = [colname for colname in columns if "rv" in colname]
    if len(dem_columns) == 1 and len(rep_columns) == 1:
        return(dem_columns+rep_columns)
    else:
        return([])


def test_size(data,name):
    """" REPORTS SOME SIZE TESTS ON THE MATRIX"""
    #basic size tests
    s = np.shape(data)
    if s[1] != 3:
        print name, "Wrong number of columns"
        return(False)
    if s[0] < 100:
        print name, "Less than 100 precincts!"
        return(False)
    # more advanced size tests about precincts in counties
    min_number_precinct_per_county = 25
    county_below_min = data.groupby("county").count()["p_democrat"].values < min_number_precinct_per_county
    fraction_below_min = float(sum(county_below_min))/len(county_below_min)
    if fraction_below_min > 0.50:
        print name, "More than 50% of counties have fewer than 25 precincts"
        return(False)
    good_number_precincts_per_county = 100
    county_good = data.groupby("county").count()["p_democrat"].values < good_number_precincts_per_county
    fraction_good = float(sum(county_good))/len(county_good)
    if fraction_good < 0.2:
        print name, "Fewer than 20% of counties have at least 100 precincts"
        return(False)
    ### PASSED ALL TESTS
    return(True)

folder_in = '/Users/brianlibgober/Dropbox/Digit_stats/Dataverse/Combined'
os.chdir(folder_in)

states = []
codes = []
years = []
for filein in glob.glob("*.tab"):
    data = pd.read_csv(filein,sep="\t")
    county = get_county(data)
    for code in ["USP"]:
        election = get_election(code,data)
        if (len(county) == 1) & (len(election) == 2):
            out = data[county+election]
            out = out.dropna(axis=0,how=u'any')
            out[election] = out[election].astype(int)
            out.columns = ["county","p_democrat","p_republican"]
            if test_size(out,code + " " + filein):
                year = re.search("\d+",election[0]).group(0)
                state = filein[0:2]
                office = code
                fout = "_".join([year,state,office]) + ".csv"
                outfolder = '/Users/brianlibgober/Dropbox/Digit_stats/RawData/US/'
                fout = os.path.join(outfolder,fout)
                out.to_csv(fout,index=False)
                states.append(state);years.append(year);codes.append(code)
    
""""

all_columns = np.array([])
for filein in glob.glob("*.tab"):
    data = pd.read_csv(filein,sep="\t")
    all_columns = concatenate((all_columns,data.columns),axis=0)
for entry in unique(all_columns):
    print entry
"""                     

