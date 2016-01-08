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
RealReturns = os.path.join(Home,"Turkey_prov/Real_Returns")
SimReturns = os.path.join(Home,"Turkey_prov/Sim_Returns")

#load the files to work with
fins = os.listdir(RealReturns)
#place to store our sims
os.chdir(SimReturns)
storelocation = "/scratch/blibgober/Turkey/TurkishSimStorage_prov.h5"
store = pd.HDFStore(storelocation)
for fin in fins:
    print("Starting work on " + fin)
    ###create a folder for the file with storage and ensure write permissions
    ffolder = fin.replace(".csv","")
    ffolder = os.path.join(SimReturns,ffolder)
    spawnfolder = join(ffolder,"storage")
    make_sure_path_exists(spawnfolder)
    os.chdir(spawnfolder)
    subprocess.call(["chmod","-R","777","."])
    #### move to the subfolder where file will be created
    #create a condor submit script
    condor_script_text =  """
Universe        = vanilla
Executable	= /usr/local/bin/python27
Arguments	= /nfs/projects/b/blibgober/digits/simulate_election_2.py %(fin)s %(spawnfile)s %(nsims)s
request_memory  = 512
request_cpus    = 1
transfer_executable = false
should_transfer_files = NO
output  = %(spawnfolder)s/out.$(Process)
error   = %(spawnfolder)s/err.$(Process)
Log     = %(spawnfolder)s/l
Queue   1
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
    spawns = glob.glob("*.pkl")
    while len(spawns) < nsims:
        spawns = glob.glob("*.pkl")
        time.sleep(5)
        print fin.replace(".csv","") + ": Percent of cluster jobs done: " + str(float(len(spawns))/nsims)
    store[fin.replace(".csv","")] = pd.read_pickle(spawns[0])

store.close()
print "Sims are Stored in ", storelocation


