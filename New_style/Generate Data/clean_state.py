import pandas as pd
import glob
import os
source = "/Users/brianlibgober/Dropbox/Digit_stats/RawData/Turkey_national/csv_prov"
os.chdir(source)
for fin in glob.glob("*.csv"):
    data = pd.read_csv(fin)
    allnull = data.isnull().all()
    data = data.ix[:,~allnull]
    data.to_csv(fin,index=False,encoding="utf-8")