from joblib import Parallel, delayed
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
    datalocation = "/nfs/projects/b/blibgober/digits/Results/TurkishSimStorage_prov.h5"
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
#
#
#Results_Province = pd.DataFrame(columns=[
#                    "Race",
#                    "Province",
#                    "Party",
#                    "N",
#                    "chisquare-uniform",
#                    "chisquare-benford-3d",
#                    "chisquare-mean-sim",
#                    "lilliefors-type-test",
#                    ]) 
#
#calls = []
#
#for Race in Races:
#    for Province in Provinces:
#        #select the row to get the key
#        print 'Looking up', Race, Province
#        key = get_key(election_directory,["Race","Province"])
#        print "Got Key", key
#        try:
#            panel = store[key]
#            calls.append([panel,Race,Province])
#        except KeyError:
#            continue
#
#def by_province_function(obj):
#    panel,Race,Province = obj
#    col =  candidate_columns(panel)
#    parties = panel.minor_axis[col]
#    rows = []
#    for party in parties:
#        ### load somee data
#        party_panel =  (panel.ix[:,:,party]).fillna(0)
#        real_raw = party_panel.real
#        digits_table = digit_aggregate(party_panel)
#        real_digits = digits_table.real
#        sim_digits = digits_table.drop("real",axis=1)
#        mean_sim_digit = sim_digits.mean(1)
#        ### calculate the statistics we want
#        statistics = {"Race":Race,"Province":Province,"Party":party,"N":len(real_raw)}
#        statistics.update(stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits,True))
#        rows.append(statistics)
#    return(rows)
#     
#d = Parallel(n_jobs=-1,verbose=10)(delayed(by_province_function)(obj) for obj in calls)
#
#Results_Province = pd.DataFrame([item for sublist in d for item in sublist])
#
#
#print "Finished Province Results"
#Results_Province.to_csv("Turkey_Province_Results.csv")
#for alpha in [0.01,0.05,0.1]:
#    print "Alpha=", alpha
#    print coverage(alpha=alpha,results= Results_Province)
#del Results_Province,d

        
#########################
#####  By Ilce ("County") ########
#########################
        

calls = []
for Race in Races:
    for Province in Provinces:
        #select the row to get the key
        print 'Looking up', Race, Province
        key = get_key(election_directory,["Race","Province"])
        print "Got Key", key
        try:
            panel = store[key]
            calls.append([panel,Race,Province])
        except KeyError:
            continue
    
def by_ilce_function(obj):
    panel,Race,Province = obj
    col = candidate_columns(panel)
    Parties = panel.minor_axis[col]
    Ilces = np.unique(panel.ix[0,:,"ilce"])
    outrows = []
    for Ilce in Ilces:
        ilcerows = panel.real.ilce == Ilce
        for Party in Parties:
            ### load somee dat
            party_panel =  (panel.ix[:,ilcerows,Party]).fillna(0)
            if np.shape(party_panel)[0] == 0:
                continue
            real_raw = party_panel.real.fillna(0)
            digits_table = digit_aggregate(party_panel)
            real_digits = digits_table.real
            sim_digits = digits_table.drop("real",axis=1)
            mean_sim_digit = sim_digits.mean(1)
            ### calculate the statistics we want
            statistics = {"Race":Race,"Province":Province,"Ilce":Ilce,"Party":Party,"N":len(real_raw)}
            statistics.update(stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits,True))
            outrows.append(statistics)
    return(outrows)
    
d = Parallel(n_jobs=-1,verbose=10)(delayed(by_ilce_function)(obj) for obj in calls)

Results_Ilce = pd.DataFrame([item for sublist in d for item in sublist])
                    
Results_Ilce.to_csv("Turkey_Ilce_Results.csv")

###############
#### OUTPUT ###
###############

