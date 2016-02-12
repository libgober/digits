# -*- coding: utf-8 -*-
import os
import sys
if sys.platform =="darwin":
    sys.path = ['/Users/brianlibgober/GitHub/digits/New_style/'] +sys.path
if sys.platform != "darwin":
    sys.path = [os.path.expanduser("~/digits/")] + sys.path
from helpers import *
import scipy as sp


print "Modules Loaded"

#Load Data
if sys.platform == "darwin":
    datalocation = os.path.expanduser("~/Sweden_Sim_Storage.h5") 
if sys.platform != "darwin":
    datalocation = "/nfs/home/B/blibgober/digits/Results/Sweden_Sim_Storage.h5"
store = pd.HDFStore(datalocation)

print "Data Store Loaded"

Races = ["riksdagsval","kommunval","landstingsval"]
Years = ["2002","2010","2014"]


### make the lans and Kommuns 
print "Gathering Lans and Kommuns"
Kommuns = []
Lans = []
for key in store.keys():
    Lans = np.concatenate((Lans, np.unique(store[key].real.ix[:,0])))
    Kommuns = np.concatenate((Kommuns,np.unique(store[key].real.ix[:,1])))

Kommuns = np.unique(Kommuns)
Lans = np.unique(Lans)

print "Gathered Lans and Kommuns"

##########################
#####  By Country ########
##########################


def analyze_parallel(panel):
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
        statistics = {"Race":Race,"Year":Year,"Party":party,"N":len(real_raw)}
        statistics.update(stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits))
        to_add = pd.DataFrame(statistics,index=[index])
        return(to_add)

print "Starting results by country"

Results_Country = pd.DataFrame(columns=[
                    "Race",
                    "Year",
                    "Party",
                    "N",
                    ]) 
index=0      

calls = []      
for Race in Races:
    for Year in Years:
        #select the row to get the key
        key = [key for key in store.keys()
            if (Race in key.lower()) & (Year in key.lower())]
        try:
            key = key[0]
        except IndexError:
            continue
        try:
            panel = store[key]
        except KeyError:
            continue
        calls.append(panel)
to_add = analyze_parallel(key,panel)
Results_Country = Results_Country.append(to_add)
print index
        
             
print "Finished Country Results"

Results_Country.to_csv("Sweden_Results.csv")
del Results_Country

##########################
#####  By Lan ###########
##########################


Results_Lan = pd.DataFrame(columns=[
                    "Race",
                    "Year",
                    "Lan",
                    "Party",
                    "N",
                    ]) 
                    
index = 0
for Race in Races:
    for Year in Years:
        #select the row to get the key
        key = [key for key in store.keys()
            if (Race in key.lower()) & (Year in key.lower())]
        try:
            key = key[0]
        except IndexError:
            continue
        try:
            panel = store[key]
        except KeyError:
            continue
        col =  candidate_columns(panel)
        parties = panel.minor_axis[col]
        for Lan in Lans: 
            col =  candidate_columns(panel)
            parties = panel.minor_axis[col]
            Lan_rows = (panel.real.ix[:,0] == Lan)
            if sum(Lan_rows) == 0: #i.e. if nothing in Lan Rows
                continue
            for party in parties:
                ### load some data
                sub_panel =  (panel.ix[:,Lan_rows,party])
                real_raw = sub_panel.real
                digits_table = digit_aggregate(sub_panel)
                real_digits = digits_table.real
                sim_digits = digits_table.drop("real",axis=1)
                mean_sim_digit = sim_digits.mean(1)
                ### calculate the statistics we want
                statistics = {"Race":Race,"Year":Year,"Lan":Lan,"Party":party,"N":len(real_raw)}
                statistics.update(stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits))
                to_add = pd.DataFrame(statistics,index=[index])
                Results_Lan = Results_Lan.append(to_add)
                index += 1
                print index
                
print "Finished Province Results"
Results_Lan.to_csv("Sweden_Lan_Results.csv")
del Results_Lan

############################
#####  By Kommun ###########
############################               


Results_Kommun = pd.DataFrame(columns=[
                    "Race",
                    "Year",
                    "Lan",
                    "Kommun"
                    "Party",
                    "N",
                    ]) 
                    
index = 0
for Race in Races:
    for Year in Years:
        #select the row to get the key
        key = [key for key in store.keys()
            if (Race in key.lower()) & (Year in key.lower())]
        try:
            key = key[0]
        except IndexError:
            continue
        try:
            panel = store[key]
        except KeyError:
            continue
        col =  candidate_columns(panel)
        parties = panel.minor_axis[col]
        for Lan in Lans: 
            for Kommun in Kommuns:     
                Lan_rows = panel.real.ix[:,0].apply(int) == int(Lan)
                Kommun_rows = (panel.real.ix[:,1].apply(int) == int(Kommun)) & Lan_rows
                ##true whenever the kommun has at least one observation 
                if any(Kommun_rows):
                    for party in parties:
                        ### load somee data
                        sub_panel =  (panel.ix[:,Kommun_rows,party])
                        real_raw = sub_panel.real
                        digits_table = digit_aggregate(sub_panel)
                        real_digits = digits_table.real
                        sim_digits = digits_table.drop("real",axis=1)
                        mean_sim_digit = sim_digits.mean(1)
                        ### calculate the statistics we want
                        statistics = {"Race":Race,"Year":Year,"Lan":Lan,"Kommun":Kommun,"Party":party,"N":len(real_raw)}
                        statistics.update(stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits))
                        to_add = pd.DataFrame(statistics,index=[index])
                        Results_Kommun = Results_Kommun.append(to_add)
                        index += 1
                        print index
                
print "Finished District Results"

Results_Kommun.to_csv("Sweden_Kommun_Results.csv")

                  

