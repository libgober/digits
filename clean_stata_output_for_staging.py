"""
Takes as input a folder containing csvs. Transforms the output
"""

import sys
import os
import pandas as pd
import glob
import numpy as np

folderin = sys.argv[1]

x = None 
while x not in ['y','Y','n','N']:
    x = raw_input("Sure you want to transform " + folderin + "? Changes can't be undone.[Y/N]  ")
if x.lower() ==  'y':
    os.chdir(folderin)
    #list all the files
    fins = glob.glob("*.csv")
    for fin in fins:
        #read in the file
        data = pd.read_csv(fin,engine='python',sep=None)
        #save the fileout anme
        data = data.iloc[:,data.columns.str.startswith("p_")]
        #drop parties that are all NAN
        data.dropna(axis=1,how='all',inplace=True)
        #add some information about the size of the sheet
        data.to_csv(fin,index=False)
        
    
