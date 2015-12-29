""""
Assumes that all files are sims contained in csv
Returns a pickled "panel" object which is a 3d array
"""

import sys
import pandas as pd

flist = sys.argv[1:]
temp = {}
for f in flist:
    name = f.replace(".csv","")
    temp[name] = pd.read_csv(f)

AllSims = pd.Panel(temp)
AllSims.to_pickle(str(len(flist))+"sims.pkl")

