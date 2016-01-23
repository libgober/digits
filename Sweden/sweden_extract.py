import pandas as pd
from os.path import join
import os 
import numpy as np

swedendata = '/Users/brianlibgober/Dropbox/Digit_stats/RawData/Sweden/'
os.chdir(swedendata)

#### 2014

#2014_kommunval_per_valdistrikt
readin = '2014/2014_kommunval_per_valdistrikt.xlsx'
data = pd.read_excel(os.path.abspath(readin),header=2)
identifiers = data.ix[:,range(0,6)] #save the identifying information
colselect = data.columns.str.contains('tal') #get rid of all non column totals 
data = data.ix[:,colselect]
major_parties = (data.sum(0) >  0.05*data.sum(0).sum())
other = data.ix[:,~major_parties].sum(1)
data = data.ix[:,major_parties] #only keep columns that have greater than 5% nationally
data.columns = ["p_" + header.split(" ")[0] for header in data.columns]
data["p_other"] = other
data = pd.concat([identifiers,data],axis=1) #recombine
data.fillna(0,inplace=True)
#now we will treat each "lan" as its own election and create a special file
out = os.path.abspath("Cleaned/ByState/Kommunval_2014.csv")
data.to_csv(out,index=False,encoding="utf-8")

#2014_landstingsval_per_valdistrikt
readin = "2014/2014_landstingsval_per_valdistrikt.xls"
data = pd.read_excel(os.path.abspath(readin),header=2)
identifiers = data.ix[:,range(0,6)] #save the identifying information
colselect = data.columns.str.contains('tal') #get rid of all non column totals 
data = data.ix[:,colselect]
major_parties = (data.sum(0) >  0.05*data.sum(0).sum())
other = data.ix[:,~major_parties].sum(1)
data = data.ix[:,major_parties] #only keep columns that have greater than 5% nationally
data.columns = ["p_" + header.split(" ")[0] for header in data.columns]
data["p_other"] = other
data = pd.concat([identifiers,data],axis=1) #recombine
data.fillna(0,inplace=True)
out = os.path.abspath("Cleaned/ByState/landstingsval_2014.csv")
data.to_csv(out,index=False,encoding="utf-8")


#riksdagsval
readin = "2014/2014_riksdagsval_per_valdistrikt.xls"
data = pd.read_excel(os.path.abspath(readin),header=2)
identifiers = data.ix[:,range(0,8)] #save the identifying information
colselect = data.columns.str.contains('tal') #get rid of all non column totals 
data = data.ix[:,colselect]
major_parties = (data.sum(0) >  0.05*data.sum(0).sum())
other = data.ix[:,~major_parties].sum(1)
data = data.ix[:,major_parties] #only keep columns that have greater than 5% nationally
data.columns = ["p_" + header.split(" ")[0] for header in data.columns]
data["p_other"] = other
data = pd.concat([identifiers,data],axis=1) #recombine
data.fillna(0,inplace=True)
out = os.path.abspath("Cleaned/ByState/riksdagsval_2014.csv")
data.to_csv(out,index=False,encoding="utf-8")

######## 2010

#Kommunval
readin = "2010/slutligt_valresultat_valdistrikt_K_antal.xls"
datain = pd.read_excel(os.path.abspath(readin),header=0)
identifiers = datain.iloc[:,range(0,6)]
data = datain.ix[:,6:-6]
major_parties = (data.sum(0) >  0.05*data.sum(0).sum())
other = data.ix[:,~major_parties].sum(1)
data = data.ix[:,major_parties] #only keep columns that have greater than 5% nationally
data.columns = ["p_" + header for header in data.columns]
data["p_other"] = other
data = pd.concat([identifiers,data],axis=1) #recombine
out = os.path.abspath("Kommunval_2010.csv")
data.to_csv(out,index=False,encoding="utf-8")


#Landstingsval
readin = "2010/slutligt_valresultat_valdistrikt_L.xls"
datain = pd.read_excel(os.path.abspath(readin),header=0)
identifiers = datain.iloc[:,range(0,6)]
data = datain.ix[:,datain.columns.str.contains('tal')]
data = data.ix[:,:-3]
major_parties = (data.sum(0) >  0.05*data.sum(0).sum())
other = data.ix[:,~major_parties].sum(1)
data = data.ix[:,major_parties] #only keep columns that have greater than 5% nationally
data.columns = ["p_" + header.split(" ")[0] for header in data.columns]
data["p_other"] = other
data = pd.concat([identifiers,data],axis=1) #recombine
data = data.fillna(0)
out = os.path.abspath("2010_Landstingsval.csv")
data.to_csv(out,index=False,encoding="utf-8")

#Riksdagsval
readin = "2010/slutligt_valresultat_valdistrikt_R.xls"
datain = pd.read_excel(os.path.abspath(readin),header=0)
identifiers = datain.iloc[:,range(6)]
colselect = datain.columns.str.contains('tal') #get rid of all non column totals 
data = datain.ix[:,colselect]
major_parties = (data.sum(0) >  0.05*data.sum(0).sum())
other = data.ix[:,~major_parties].sum(1)
data = data.ix[:,major_parties] #only keep columns that have greater than 5% nationally
data.columns = ["p_" + header.split(" ")[0] for header in data.columns]
data["p_other"] = other
data = pd.concat([identifiers,data],axis=1) #recombine
data.fillna(0,inplace=True)
out = os.path.abspath("Cleaned/ByState/riksdagsval_2010.csv")
data.to_csv(out,index=False,encoding="utf-8")


###  2002

readin = "2002/Sweden_2002_Riksdagsval.csv"
datain = pd.read_csv(readin,encoding="ISO-8859-1")
identifiers = datain.iloc[:,range(5)]
data = datain.ix[:,6:-1]
major_parties = (data.sum(0) >  0.05*data.sum(0).sum())
other = data.ix[:,~major_parties].sum(1)
data = data.ix[:,major_parties] #only keep columns that have greater than 5% nationally
data.columns = ["p_" + header for header in data.columns]
data["p_other"] = other
data = pd.concat([identifiers,data],axis=1)
out = os.path.abspath("Cleaned/ByState/Riksdagsval_2002.csv")
data.to_csv(out,index=False,encoding="utf-8")
