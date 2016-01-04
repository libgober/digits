import os
import glob
import subprocess
import errno
import time
import pandas as pd
import sys.argv
join = os.path.join
from helpers2 import clean


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
RealReturns = os.path.join(Home,"US/Real_Returns")
SimReturns = os.path.join(Home,"US/Sim_Returns")
StorageLocation = "/scratch/blibgober/US/SimStorage.h5"

#load the files to work with
fins = os.listdir(RealReturns)
#place to store our sims
fins = [fin for fin in fins if ("GOV" in fin) | ("USS" in fin) | ("USP" in fin)]
os.chdir(SimReturns)
store = pd.HDFStore(StorageLocation)
filelist = []
if
for fin in fins:
    print("Starting work on " + fin)
    ###create a folder for the file with storage and ensure write permissions
    ffolder = fin.replace(".csv","")
    ffolder = os.path.join(SimReturns,ffolder)
    spawnfolder = join(ffolder,"storage")
    make_sure_path_exists(spawnfolder)
    os.chdir(Home)
    subprocess.call(["chmod","-R","777","."])
    #### move to the subfolder where file will be created
    os.chdir(spawnfolder)
    #create a condor submit script
    condor_script_text =  """
Universe        = vanilla
Executable	= /usr/local/bin/python27
Arguments	= /nfs/projects/b/blibgober/digits/simulate_election.py %(fin)s %(spawnfile)s
request_memory  = 512
request_cpus    = 1
transfer_executable = false
should_transfer_files = NO
output  = %(spawnfolder)s/out.$(Process)
error   = %(spawnfolder)s/err.$(Process)
Log     = %(spawnfolder)s/l
Queue   %(nsims)s
""" % {"fin": join(RealReturns,fin),"spawnfolder":spawnfolder,"nsims" : str(nsims),"spawnfile":join(spawnfolder,"sims_$(Process)"),"outfile":join(spawnfolder,"out.$(Process)")}
    #save the condor submit script
    condor_script = join(spawnfolder,"condor_script.submit")
    with open(condor_script,"w+") as foo:
        foo.write(condor_script_text)
        #submit it
    subprocess.call(["condor_submit",condor_script])
	
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
    temp["real_election"] = clean(pd.read_csv(join(RealReturns,fin)))
    for spawned in spawns:
        temp[spawned.replace(".csv","")] = pd.read_csv(spawned) 
    all_sims = pd.Panel(temp)
    os.chdir(ffolder)
    fall_sims = join(ffolder,str(nsims) + "_simulated_from_" + fin.replace(".csv",""))  + ".pkl"
    #save all the sims
#   all_sims.to_pickle(fall_sims)
    store[fin.replace(".csv","")] = all_sims
    #filelist.append(fall_sims)
    
store.close()
os.chdir(SimReturns)
pd.Series(filelist).to_csv("sim_files_done.csv")


