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
    datalocation = os.path.expanduser("~/US_Sim_Storage.h5") 
if sys.platform != "darwin":
    datalocation = "/nfs/projects/b/blibgober/digits/Results/US_Sim_Storage.h5"
store = pd.HDFStore(datalocation)
election_directory = split_key_names(store)
election_directory.columns = ["Race","Year","State","Keys"] #may need to change this given reorganized naming convetion
Years = np.unique(election_directory.Year)
States = np.unique(election_directory.State)
Races = np.unique(election_directory.Race)

print "All setup to run"

########################
#####  By State ########
########################

print "Starting States"

Results_State = pd.DataFrame(columns=[
                    "Race",
                    "Year",
                    "State",
                    "Party",
                    "N",
                    "chisquare-uniform",
                    "chisquare-benford-3d",
                    "chisquare-mean-sim",
                    "lilliefors-type-test",
                    ]) 
index=0            



for Race in Races:
    for Year in Years:
        for State in States:
            #select the row to get the key
            key = get_key(election_directory,["Race","State","Year"])
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
                statistics = {"Race":Race,"Year":Year,"State":State,"Party":party,"N":len(real_raw)}
                statistics.update(stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits))
                to_add = pd.DataFrame(statistics,index=[index])
                Results_State = Results_State.append(to_add)
                index += 1

print "Finished States"

#################################
#####  USA USP WHOLE COUNTRY ########
#################################

USP = pd.DataFrame()
index=0            
Race = 'USP'

#################################################################
####### CREATE A BIG ASS DATAFRAME OF ALL RESULTS    ############
#################################################################

print "Collecting data for USP country wide"

for Year in Years:
    for State in States:
        #select the row to get the key
        key =  get_key(election_directory,["Race","State","Year"])
        try:
            panel = store[key]
        except KeyError:
            continue
        col =  candidate_columns(panel)
        parties = panel.minor_axis[col]
        for party in parties:
            print State
            ### load somee data
            party_panel =  (panel.ix[:,:,party])
            party_panel["State"] = State
            party_panel["Year"] = Year
            party_panel["State.Index"] = party_panel.index
            party_panel["Party"] = party
            if len(USP) == 0:
                USP = pd.concat([USP,party_panel],ignore_index=True)
            else:
                new_index = party_panel.index + USP.index[-1] + 1 
                party_panel.index = new_index
                USP = pd.concat([USP,party_panel])


Results_Pres = pd.DataFrame(columns=[
                    "Year",
                    "Party",
                    "N",
                    "chisquare-uniform",
                    "chisquare-benford-3d",
                    "chisquare-mean-sim",
                    "lilliefors-type-test",
                    ]) 

index = 0
for party in parties:
    for Year in Years:
        panel = USP.ix[(USP.ix[:,"Party"] == party) & (USP.ix[:,"Year"] == Year),:]
        panel.drop(["State","Year","State.Index","Party"],axis=1,inplace=True)
        real_raw = panel.real
        digits_table = digit_aggregate(panel)
        real_digits = digits_table.real
        sim_digits = digits_table.drop("real",axis=1)
        mean_sim_digit = sim_digits.mean(1)
        statistics = {"Year":Year,"Party":party,"N":len(real_raw)}
        statistics.update(stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits))
        to_add = pd.DataFrame(statistics,index=[index])
        Results_Pres = Results_Pres.append(to_add)
        index += 1

print "Finished USA-wide"
        
#########################
#####  By COUNTY ########
#########################
        
print "Starting county"

Results_County = pd.DataFrame(columns=[
                    "Race",
                    "Year",
                    "State",
                    "County",
                    "Party",
                    "N",
                    ]) 
index=0            
for Race in Races:
    for Year in Years:
        for State in States:
            #select the row to get the key
            key =  get_key(election_directory,["Race","State","Year"])
            try:
                panel = store[key]
            except KeyError:
                continue
            col =  candidate_columns(panel)
            Parties = panel.minor_axis[col]
            Counties = np.unique(panel.ix[0,:,"county"])
            for County in Counties:
                countyrows = panel.real.county == County
                for Party in Parties:
                    ### load somee dat
                    party_panel =  (panel.ix[:,countyrows,Party])
                    if np.shape(party_panel)[0] == 0:
                        continue
                    real_raw = party_panel.real
                    digits_table = digit_aggregate(party_panel)
                    real_digits = digits_table.real
                    sim_digits = digits_table.drop("real",axis=1)
                    mean_sim_digit = sim_digits.mean(1)
                    ### calculate the statistics we want
                    statistics = {"Race":Race,"Year":Year,"State":State,"County":County,"Party":Party,"N":len(real_raw)}
                    statistics.update(stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits))
                    to_add = pd.DataFrame(statistics,index=[index])
                    Results_County = Results_County.append(to_add)
                    index += 1
                    
###############
#### OUTPUT ###
###############

Results_State.to_csv("US_State_Results.csv")
Results_County.to_csv("US_County_Results.csv")
Results_Pres.to_csv("US_Pres_Results.csv")
