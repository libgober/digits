###############
#### SETUP ####
###############

import os
join = os.path.join
import helpers

Home = os.path.abspath("/nfs/projects/b/blibgober/digits")
Storage = os.path.abspath("/scratch/blibgober/")
nsims = 100

##########################################
#########   LOW FRAUD COUNTRIES    #######
##########################################

############
### USA ####
############

source = join(Home,"US/Real_Returns")
target = join(Home,"US/Sim_Returns")
storelocation = join(Storage,"US_Sim_Storage.h5")
helpers.simulate(nsims,source,target)
helpers.collect_simulations(source,target,storelocation)

###############
### France ####
###############

source = join(Home,"France/Real_Returns")
target = join(Home,"France/Sim_Returns")
storelocation = join(Storage,"France_Sim_Storage.h5")
helpers.simulate(nsims,source,target)
helpers.collect_simulations(source,target,storelocation)


###############
### Sweden ####
###############

source = join(Home,"Sweden/Real_Returns")
target = join(Home,"Sweden/Sim_Returns")
storelocation = join(Storage,"Sweden_Sim_Storage.h5")
helpers.simulate(nsims,source,target)
helpers.collect_simulations(source,target,storelocation)


##########################################
#########   HIGH FRAUD COUNTRIES   #######
##########################################


###############
### Nigeria ####
###############


###############
### Russia ####
###############


################
### Iran ####
################



##########################################
#########   NEW APPLICATIONS       #######
##########################################




##### TURKISH PROVINCIAL ELECTIONS
#setup directory name space, Sim Returns is target
source = join(Home,"Turkey_prov/Real_Returns")
target = join(Home,"Turkey_prov/Sim_Returns")
storelocation = join(Storage,"TurkishSimStorage_prov.h5")
helpers.simulate(nsims,source,target)
helpers.collect_simulations(source,target,storelocation)


####### TURKISH DISTRICT ELECTIONS
source = join(Home,"Turkey_district/Real_Returns")
target = join(Home,"Turkey_district/Sim_Returns")
storelocation = join(Storage,"TurkishSimStorage_district.h5")
helpers.simulate(100,source,target)
helpers.collect_simulations(source,target,storelocation)

