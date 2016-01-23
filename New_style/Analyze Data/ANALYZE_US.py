import sys
sys.path.append("..")
from helpers import *
from scipy.stats import chisquare,kstest
import scipy as sp



#Load Data
datalocation = os.path.expanduser("~/US_Sim_Storage.h5")
store = pd.HDFStore(datalocation)
election_directory = split_key_names(store)
election_directory.columns = ["Year","State","Race","Keys"]
Years = np.unique(election_directory.Year)
States = np.unique(election_directory.State)
Races = np.unique(election_directory.Race)


########################
#####  By State ########
########################


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
            key = get_key(election_directory,Race,Races,State,States,Year,Years)
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
                stat_battery(real_digits,)
                #chisquares
                _ , statistics["chisquare-uniform"] = chisquare(real_digits)
                _ , statistics["chisquare-benford-3d"] = chisquare(real_digits,ben3*sum(real_digits)) #ben3 is the probability of each
                _ , statistics["chisquare-benford-mix"] = chisquare(real_digits,benford_mixture(real_raw)*sum(real_digits))
                _ , statistics["chisquare-mean-sim"] = chisquare(real_digits,mean_sim_digit)
                #Lilliefors-type test
                _ , statistics["lilliefors-type-test"] = lilliefors_type(mean_sim_digit,digits_table,real_digits)
                to_add = pd.DataFrame(statistics,index=[index])
                Results_State = Results_State.append(to_add)
                index += 1
    