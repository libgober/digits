import os
import glob
import subprocess
import errno
import time
import pandas as pd
join = os.path.join


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
            
            
############# MAIN ##################

#number of sims
nsims = 100

#setup directory name space, Sim Returns is target
Home = os.path.abspath("/nfs/projects/b/blibgober/digits")
RealReturns = os.path.join(Home,"Turkey/Real_Returns")
SimReturns = os.path.join(Home,"Turkey/Sim_Returns")

os.chdir(RealReturns)
#load the files to work with
fins = glob.glob("*.csv")
#place to store our sims
os.chdir(SimReturns)
storelocation = "/scratch/blibgober/Turkey/TurkishSimStorage.h5"
store = pd.HDFStore(storelocation)
#now that all the processes have been submitted, wait for completion and then combine
for fin in fins: 
    ffolder = fin.replace(".csv","")
    ffolder = os.path.join(SimReturns,ffolder)
    spawnfolder = join(ffolder,"storage")
    os.chdir(spawnfolder)
    spawns = glob.glob("*.csv")
    while len(spawns) < nsims:
        spawns = glob.glob("*.csv")
        time.sleep(5)
        print fin.replace(".csv","") + ": Percent of cluster jobs done: " + str(float(len(spawns))/nsims)
    #now that all the sims have finished we will combine them into a single pandas
    temp = {}
    temp["real_election"] = pd.read_csv(join(RealReturns,fin))
    for spawned in spawns:
        temp[spawned.replace(".csv","")] = pd.read_csv(spawned) 
    all_sims = pd.Panel(temp)
    store[fin.replace(".csv","")] = all_sims

store.close()
print "Sims are Stored in ", storelocation


