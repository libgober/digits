""" 
Database location, folderout
"""

import sys
import pandas as pd
import os
import numpy

def candidate_columns(panel):
    return(panel.minor_axis.str.slice(0,2) == "p_")


store = pd.HDFStore(sys.argv[1])
folderout = sys.argv[2]
os.chdir(folderout)
keys = store.keys()
for key in numpy.random.choice(a=keys,size=int(0.05*len(keys))):
    panel = store[key]
    parties = panel.minor_axis[candidate_columns(panel)]
    party = numpy.random.choice(a=parties,size=1)[0]
    data = panel.ix[:,:,party]
    fout = key.replace("/","") + "_" + party + ".csv"
    data.to_csv(os.path.abspath(fout),index=False)
    