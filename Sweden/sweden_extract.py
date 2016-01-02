import pandas as pd
from os.path import join
import os 

swedendata = '/Users/brianlibgober/Dropbox/Digit_stats/RawData/Sweden/'
os.chdir(swedendata)

#### 2014

#2014_kommunval_per_valdistrikt
readin = '2014/2014_kommunval_per_valdistrikt.xlsx'
data = pd.read_excel(os.path.abspath(readin),header=2)
data = data.ix[:,data.columns.str.contains('tal')]
#select only those parties getting more than 5% of the total
important_data = data.ix[:,data.sum(0) > 0.05*data.sum(0).sum()]
#assume nas are 0
important_data = important_data.fillna(0)
out = os.path.abspath("Cleaned/2014_kommunval_per_valdistrikt_above5percent.csv")
important_data.to_csv(out,index=False)

#2014_landstingsval_per_valdistrikt
readin = "2014/2014_landstingsval_per_valdistrikt.xls"
data = pd.read_excel(os.path.abspath(readin),header=2)
data = data.ix[:,data.columns.str.contains('tal')]
important_data = data.ix[:,data.sum(0) > 0.05*data.sum(0).sum()]
important_data = important_data.fillna(0)
out = os.path.abspath("Cleaned/2014_landstingsval_per_valdistrikt_above5percent.csv")
important_data.to_csv(out,index=False)

#riksdagsval
readin = "2014/2014_riksdagsval_per_valdistrikt.xls"
data = pd.read_excel(os.path.abspath(readin),header=2)
data = data.ix[:,data.columns.str.contains('tal')]
important_data = data.ix[:,data.sum(0) > 0.05*data.sum(0).sum()]
important_data = important_data.fillna(0)
out = os.path.abspath("Cleaned/2014_riksdagsval_per_valdistrikt_above5percent.csv")
important_data.to_csv(out,index=False)

######## 2010

#slutligt
readin = "2010/slutligt_valresultat_valdistrikt_K_antal.xls"
datain = pd.read_excel(os.path.abspath(readin),header=0)
data = datain.ix[:,6:-6]
important_data = data.ix[:,data.sum(0) > 0.05*data.sum(0).sum()]
important_data = important_data.fillna(0)
out = os.path.abspath("Cleaned/2010_slutligt_valresultat_valdistrikt_K_antal_above5percent.csv")
important_data.to_csv(out,index=False)

#L
readin = "2010/slutligt_valresultat_valdistrikt_L.xls"
datain = pd.read_excel(os.path.abspath(readin),header=0)
data = datain.ix[:,datain.columns.str.contains('tal')]
data = data.ix[:,:-3]
important_data = data.ix[:,data.sum(0) > 0.05*data.sum(0).sum()]
important_data = important_data.fillna(0)
out = os.path.abspath("Cleaned/2010_slutligt_valresultat_valdistrikt_L_above5percent.csv")
important_data.to_csv(out,index=False)

#R
readin = "2010/slutligt_valresultat_valdistrikt_R.xls"
datain = pd.read_excel(os.path.abspath(readin),header=0)
data = datain.ix[:,datain.columns.str.contains('tal')]
important_data = data.ix[:,data.sum(0) > 0.05*data.sum(0).sum()]
important_data = important_data.fillna(0)
out = os.path.abspath("Cleaned/2010_slutligt_valresultat_valdistrikt_R_above5percent.csv")
important_data.to_csv(out,index=False)


###  2002

readin = "2002/Sweden_2002_Riksdagsval.csv"
datain = pd.read_csv(readin)
data = datain.ix[:,6:-1]
out = os.path.abspath("Cleaned/2002_Riksdagsval.csv")
data.fillna(0).to_csv(out)

