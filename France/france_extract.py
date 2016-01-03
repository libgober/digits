import pandas as pd
from os.path import join
import os 
import numpy as np
from numpy import unique

sourcefolder = '/Users/brianlibgober/Dropbox/Digit_stats/RawData/France/'
targetfolder = join(sourcefolder,"ByDepartment")
os.chdir(sourcefolder)
datain = pd.read_csv("france_president.csv")
for year in unique(datain.electionyear):
    for Round in unique(datain.ix[:,2]):
        for department in unique(datain.cdepartment):
            selected_rows = (datain.electionyear == year) & (datain.ix[:,2] == Round) & (datain.cdepartment == department)
            data = datain.loc[selected_rows,:]
            droplist = [u'type','electionyear', u'round', u'cdepartment',
            u'ccommune',u'ncommune', u'station','regvoters','voters','valid']
            data = data.drop(droplist,axis=1)
            data = data.dropna(axis=1,how='all')
            fout = join(targetfolder,"Year-" + str(year)+"_Round-" + str(Round) + "_Department" + str(department) + ".csv")
            data.to_csv(fout,index=False)

