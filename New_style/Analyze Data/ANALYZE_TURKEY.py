import sys
import os
if sys.platform =="darwin":
    sys.path = ['/Users/brianlibgober/GitHub/digits/New_style/'] +sys.path
if sys.platform != "darwin":
    sys.path = [os.path.expanduser("~/digits/")] + sys.path
from helpers import *
import scipy as sp



#Load Data
if sys.platform == "darwin":
    datalocation = os.path.expanduser("~/TurkishSimStorage_prov.h5") 
if sys.platform != "darwin":
    datalocation = "/scratch/blibgober/TurkishSimStorage_prov.h5"
store = pd.HDFStore(datalocation)
election_directory = split_key_names(store)
#fix some misalignment
misaligned = election_directory.ix[:,2].isnull()
election_directory.ix[misaligned,2] = election_directory.ix[misaligned,1]
election_directory.ix[~misaligned,0] = election_directory.ix[~misaligned,0].map(str) + "_" + election_directory.ix[~misaligned,1].map(str)
election_directory = election_directory.drop(1,axis=1)
election_directory.columns = ["Race","Province","Keys"] #may need to change this given reorganized naming convetion
Races = np.unique(election_directory.Race)
Provinces = np.unique(election_directory.Province)

################################
##### DEFINE SOME FUNCTIONS ####
##################################
  
def get_key(election_directory,criteria):
    """
    Criteria must be formatted like ["Race","Province"].  The operation will
    select rows responding to election.Race == Race and election.Province == Province
    Check the Analyze Turkey File for Syntax
    """
    #fix naming issue with scope
    row = ~pd.Series(election_directory.index.values).isnull()
    for i in criteria:
        try:
            row = row & (eval("election_directory."+i) == eval(i))
        except:
            pass
    key = election_directory.Keys[row]
    if len(key) == 0:
        return(None)
    else:
        return(key.get_values()[0])




########################
#####  By Province ########
########################


Results_Province = pd.DataFrame(columns=[
                    "Race",
                    "Province",
                    "Party",
                    "N",
                    "chisquare-uniform",
                    "chisquare-benford-3d",
                    "chisquare-mean-sim",
                    "lilliefors-type-test",
                    ]) 
index=0            

for Race in Races:
    for Province in Provinces:
        #select the row to get the key
        print 'Looking up', Race, Province
        key = get_key(election_directory,["Race","Province"])
        print "Got Key", key
        try:
            panel = store[key]
        except KeyError:
            continue
        col =  candidate_columns(panel)
        parties = panel.minor_axis[col]
        for party in parties:
            ### load somee data
            party_panel =  (panel.ix[:,:,party])
            real_raw = party_panel.real
            digits_table = digit_aggregate(party_panel)
            real_digits = digits_table.real
            sim_digits = digits_table.drop("real",axis=1)
            mean_sim_digit = sim_digits.mean(1)
            ### calculate the statistics we want
            statistics = {"Race":Race,"Province":Province,"Party":party,"N":len(real_raw)}
            statistics.update(stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits))
            to_add = pd.DataFrame(statistics,index=[index])
            Results_Province = Results_Province.append(to_add)
            index += 1

print "Finished Province Results"
Results_Province.to_csv("Turkey_Province_Results.csv")
for alpha in [0.01,0.05,0.1]:
    print "Alpha=", alpha
    print coverage(alpha=alpha,results= Results_Province)
del Results_Province


        
#########################
#####  By Ilce ("County") ########
#########################
        

Results_Ilce = pd.DataFrame(columns=[
                    "Race",
                    "Province",
                    "Ilce",
                    "Party",
                    "N",
                    "chisquare-uniform",
                    "chisquare-benford-3d",
                    "chisquare-mean-sim",
                    "lilliefors-type-test",
                    ]) 
index=0            
for Race in Races:
    for Province in Provinces:
        #select the row to get the key
        print 'Looking up', Race, Province
        key = get_key(election_directory,["Race","Province"])
        print "Got Key", key
        try:
            panel = store[key]
        except KeyError:
            continue
        col =  candidate_columns(panel)
        Parties = panel.minor_axis[col]
        Ilces = np.unique(panel.ix[0,:,"ilce"])
        for Ilce in Ilces:
            ilcerows = panel.real.ilce == Ilce
            for Party in Parties:
                ### load somee dat
                party_panel =  (panel.ix[:,ilcerows,Party])
                if np.shape(party_panel)[0] == 0:
                    continue
                real_raw = party_panel.real
                digits_table = digit_aggregate(party_panel)
                real_digits = digits_table.real
                sim_digits = digits_table.drop("real",axis=1)
                mean_sim_digit = sim_digits.mean(1)
                ### calculate the statistics we want
                statistics = {"Race":Race,"Province":Province,"Ilce":Ilce,"Party":Party,"N":len(real_raw)}
                statistics.update(stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits))
                to_add = pd.DataFrame(statistics,index=[index])
                Results_Ilce = Results_Ilce.append(to_add)
                index += 1
                    
                    
Results_Ilce.to_csv("Turkey_Ilce_Results.csv")

###############
#### OUTPUT ###
###############

