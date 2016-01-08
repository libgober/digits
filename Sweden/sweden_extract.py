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
identifiers = data.ix[:,[0,3]] #save the identifying information
colselect = data.columns.str.contains('tal') #get rid of all non column totals 
data = data.ix[:,colselect]
data = data.ix[:,data.sum(0) >  0.05*data.sum(0).sum()] #only keep columns that have greater than 5% nationally
data = pd.concat([identifiers,data],axis=1) #recombine
#now we will treat each "lan" as its own election and create a special file
for lanNo in np.unique(data.ix[:,0]):
    lanName = [i.split(" ")[0] for i in np.unique(data.ix[data.ix[:,0] == lanNo,1])][0]
    temp = data.ix[data.ix[:,0] ==lanNo,2:]
    #select only those parties getting more than 5% of the total nationally
    temp = temp.fillna(0)
    out = os.path.abspath("Cleaned/ByState/_2014_"+lanName+"_LANNO-"+ str(lanNo) + "_" +"Kommunval.csv")
    temp.to_csv(out,index=False)

#2014_landstingsval_per_valdistrikt
readin = "2014/2014_landstingsval_per_valdistrikt.xls"
data = pd.read_excel(os.path.abspath(readin),header=2)
identifiers = data.ix[:,[0,3]] #save the identifying information
colselect = data.columns.str.contains('tal') #get rid of all non column totals 
data = data.ix[:,colselect]
data = data.ix[:,data.sum(0) >  0.05*data.sum(0).sum()] #only keep columns that have greater than 5% nationally
data = pd.concat([identifiers,data],axis=1) #recombine
data.fillna(0)
for lanNo in np.unique(data.ix[:,0]):
    lanName = [i.split(" ")[0] for i in np.unique(data.ix[data.ix[:,0] == lanNo,1])][0]
    temp = data.ix[data.ix[:,0] ==lanNo,2:]
    out = os.path.abspath("Cleaned/ByState/_2014_"+lanName+"_LANNO-"+ str(lanNo) + "_" +"landstingsval.csv")
    temp.to_csv(out,index=False)

#riksdagsval
readin = "2014/2014_riksdagsval_per_valdistrikt.xls"
data = pd.read_excel(os.path.abspath(readin),header=2)
identifiers = data.ix[:,[0,4]] #save the identifying information
data = data.ix[:,data.columns.str.contains('tal')]
data = data.ix[:,data.sum(0) > 0.05*data.sum(0).sum()]
data = data.fillna(0)
data = pd.concat([identifiers,data],axis=1) #recombine
for lanNo in np.unique(data.ix[:,0]):
    lanName = [i.split(" ")[0] for i in np.unique(data.ix[data.ix[:,0] == lanNo,1])][0]
    temp = data.ix[data.ix[:,0] ==lanNo,2:]
    out = os.path.abspath("Cleaned/ByState/_2014_"+lanName+"_LANNO-"+ str(lanNo) + "_" +"riksdagsval.csv")
    temp.to_csv(out,index=False)

######## 2010

#Kommunval
readin = "2010/slutligt_valresultat_valdistrikt_K_antal.xls"
datain = pd.read_excel(os.path.abspath(readin),header=0)
identifiers = datain.iloc[:,[0,4]]
data = datain.ix[:,6:-6]
data = data.ix[:,data.sum(0) > 0.05*data.sum(0).sum()]
data = data.fillna(0)
data = pd.concat([identifiers,data],axis=1) #recombine
for lanNo in np.unique(data.ix[:,0]):
    lanName = [i.split(" ")[0] for i in np.unique(data.ix[data.ix[:,0] == lanNo,1])][0]
    temp = data.ix[data.ix[:,0] ==lanNo,2:]
    out = os.path.abspath("Cleaned/ByState/_2010_"+lanName+"_LANNO-"+ str(lanNo) + "_" +"Kommunval.csv")
    temp.to_csv(out,index=False)
    
#Landstingsval
readin = "2010/slutligt_valresultat_valdistrikt_L.xls"
datain = pd.read_excel(os.path.abspath(readin),header=0)
identifiers = datain.iloc[:,[0,4]]
data = datain.ix[:,datain.columns.str.contains('tal')]
data = data.ix[:,:-3]
data = data.ix[:,data.sum(0) > 0.05*data.sum(0).sum()]
data = data.fillna(0)
data = pd.concat([identifiers,data],axis=1) #recombine
for lanNo in np.unique(data.ix[:,0]):
    lanName = [i.split(" ")[0] for i in np.unique(data.ix[data.ix[:,0] == lanNo,1])][0]
    temp = data.ix[data.ix[:,0] ==lanNo,2:]
    out = os.path.abspath("Cleaned/ByState/_2010_"+lanName+"_LANNO-"+ str(lanNo) + "_" +"Landstingsval.csv")
    temp.to_csv(out,index=False)

#Riksdagsval
readin = "2010/slutligt_valresultat_valdistrikt_R.xls"
datain = pd.read_excel(os.path.abspath(readin),header=0)
identifiers = datain.iloc[:,[0,4]]
data = datain.ix[:,datain.columns.str.contains('tal')]
data = data.ix[:,data.sum(0) > 0.05*data.sum(0).sum()]
data = data.fillna(0)
data = pd.concat([identifiers,data],axis=1) #recombine
for lanNo in np.unique(data.ix[:,0]):
    lanName = [i.split(" ")[0] for i in np.unique(data.ix[data.ix[:,0] == lanNo,1])][0]
    temp = data.ix[data.ix[:,0] ==lanNo,2:]
    out = os.path.abspath("Cleaned/ByState/_2010_"+lanName+"_LANNO-"+ str(lanNo) + "_" +"Riksdagsval.csv")
    temp.to_csv(out,index=False)


###  2002

readin = "2002/Sweden_2002_Riksdagsval.csv"
datain = pd.read_csv(readin)
identifiers = datain.iloc[:,0]
data = datain.ix[:,6:-1]
data = pd.concat([identifiers,data],axis=1)
for lanNo in np.unique(data.ix[:,0]):
    temp = data.ix[data.ix[:,0] ==lanNo,2:]
    out = os.path.abspath("Cleaned/ByState/_2002"+"_LANNO-"+ str(lanNo) + "_" +"Riksdagsval.csv")
    temp.to_csv(out,index=False)
