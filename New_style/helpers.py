###########################
######### Modules  ########
###########################
from scipy.spatial import distance
import scipy as sp
import scipy.stats
from scipy.stats import power_divergence,kstest
import pandas as pd
import numpy as np
from numpy import mean
import os 
import glob
import subprocess
import errno
import time
join = os.path.join

#### START R SESSION AND LOAD R FUNCTIONS
import rpy2.robjects as ro
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage,importr

string = """freq = function(x){
    x/sum(x)
  }
  cumulate <- function(x){
    sto = 0
    for (i in 1:length(x)){
      sto = c(sto,sum(x[1:i]))
    }
    sto
  }
  """
powerpack = SignatureTranslatedAnonymousPackage(string, "powerpack")
stats = importr("stats")
dgof =  importr("dgof")



#########################
##### CLEANING ##########
#########################
def clean(returns):
    if not isinstance(returns,pd.DataFrame):
        raise Exception('Returns is not a Pandas Dataframe')
    #make sure there are no NAN values, and make sure the returns are integers!
    returns = returns.fillna(0)
    #make sure that there are no negative vote totals
    #this would happen if the total column was not correctly entered
    #we choose to throw out such mistakes rather than throw out the whole election 
    #we do not make any attempt to impute
    returns = returns.loc[returns.apply(lambda x: all(x >= 0), axis=1),:]
    #get rid of all 0 rows
    returns = returns.loc[returns.apply(lambda x: any(x > 0),axis=1),:]
    #get rid of all 0 columns
    returns  = returns.loc[:,(returns != 0).any(axis=0)]
    return(returns)


###########################
######### Analysis  #######
###########################

def digit_aggregate(table):
    """
    Takes a table of returns and produces a table with frequency of digits
    """
    table = table % 10
    digits = table.apply(lambda x: x.value_counts(sort=False),axis='index')
    for i in np.arange(0,10):
        if i not in digits.index:
            digits = digits.set_value(i,digits.columns,0)
    digits.sort_index(inplace=True)
    digits.fillna(0,inplace=True)
    return(digits)

def custom_dist(a,b):
    """ Assumes NAN means 0 """
    a = a.fillna(0)
    b = b.fillna(0)
    return(distance.euclidean(a,b))

def read_many_csv(fins):
    """ Takes a list of csv file locations, reads them in ,returns a dataframe """
    temp = {}
    for fin in fins:
        temp[fin] = pd.read_csv(fin)
    return(pd.Panel(temp))
    
def mod_if_numeric(entry,num):
    """Takes the entry mod num if it is numeric"""
    if isinstance(entry,str):
        return(entry)
    else:
        return(entry % num)

def digit_aggregate_panel(panel):
     #take everything mod 10
     panel = panel % 10
     #function counts occurence of unique values for each column of a dataframe
     value_count_dataframe = lambda df: df.apply(lambda x: x.value_counts(sort=False),axis=0)
     #to each dataframe in panel, apply the value count function and return
     return(panel.apply(value_count_dataframe, axis=(1,2)))
     
def candidate_columns(panel):
    return(panel.minor_axis.str.slice(0,2) == "p_")

def split_key_names(store):
    """
    Takes an HDFStore and makes a dataframe out of the keys.
    The dataframe is useful for organizing operations
    """
    keys = store.keys()
    keys = [key.replace("/","") for key in keys]
    keys = [key.split("_") for key in keys]
    keys = pd.DataFrame(keys)
    keys["Keys"] = pd.Series(store.keys())
    return(keys)
#  
#def get_key(election_directory,values,criteria):
#    """
#    Criteria must be formatted like ["Race","Province"].  The operation will
#    select rows responding to election.Race == Race and election.Province == Province
#    Check the Analyze Turkey File for Syntax
#    """
#    print criteria
#    row = ~pd.Series(election_directory.index.values).isnull()
#    for i in criteria:
#        try:
#            row = row & (eval("election_directory."+i) == eval(i))
#        except:
#            pass
#    key = election_directory.Keys[row]
#    if len(key) == 0:
#        return(None)
#    else:
#        return(key.get_values()[0])

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


benford1 = lambda d: np.log10(1.+1./d)

def benford2(d): 
  sto = 0
  for k in range(1,10):
    sto= sto + benford1(10*k+d)
  return(sto)

def benford3(d):
  sto = 0
  for d1 in range(1,10):
    for d2 in range(0,10):
      sto = sto + benford1(100*d1 + 10*d2+d)
  return(sto)

def benford4(d):
    sto = 0
    for d1 in range(1,10):
        for d2 in range(0,10):
            for d3 in range(0,10):
                sto = sto + benford1(1000*d1+100*d2+10*d3+d)
    return(sto)
  
ben1 = np.append([0],np.vectorize(benford1)(np.arange(1,10)))
ben2 = np.vectorize(benford2)(np.arange(0,10))
ben3 = np.vectorize(benford3)(np.arange(0,10))
ben4 = np.vectorize(benford4)(np.arange(0,10))

first_benford_law = sp.stats.rv_discrete(name="first_benford_law",values=(np.arange(0,10),ben1))
second_benford_law = sp.stats.rv_discrete(name="second_benford_law",values=(np.arange(0,10),ben2))
third_benford_law = sp.stats.rv_discrete(name="third_benford_law",values=(np.arange(0,10),ben3))
fourth_benford_law = sp.stats.rv_discrete(name="fourt_benford_law",values=(np.arange(0,10),ben4))


def benford_mixture(series):
    """
    Calculates the percentage of 1,2,3, and more than 4 digit numbers 
    Uses these percentages to weight the benford probabilities
    This is useful for estimating what mixture of benfords the series came from
    """
    a = mean(series < 10)
    b = mean(series.apply(lambda x: 10 <= x < 100))
    c = mean(series.apply(lambda x: 100 <= x < 1000))
    d = mean(1000 <= series )
    mix = ben1 * a + ben2*b + ben3*c + ben4*d
    return(mix)

def column_to_cdf(series):
    x = series.value_counts(sort=False)
    x = x/sum(x)
    cdf = sp.stats.rv_discrete(values=(x.index,x.values))
    return(cdf)


def table_to_ecdfs(df):
    """
    Takes a dataframe of in pandas and returns an array of random variables from the empirical dstribution
    Assuems observations are rows and the variable we want is in columns.
    """
    cdfs = df.apply(column_to_cdf)
    return(cdfs)

def lilliefors_type(null_contingency,sim_contingency,empirical_contingency):
    """
    Takes in a number of counts of each number in a null distro, a bunch of simulations, and the empirical
    Returns the pvalue
    """
    null = null_contingency/sum(null_contingency)
    sim = sim_contingency/sim_contingency.sum(0)
    obs = empirical_contingency/sum(empirical_contingency)  
    calcT = lambda x: max(abs(x-null))
    simT = sim.apply(calcT)
    obsT = calcT(obs)
    pvalue = mean(simT > obsT)
    return(obsT,pvalue)

def ks_exact(null_distro,empirical_distro,n,method="two-sided"):
    ###INCOMPLETE
    """
    Calculate the exact KS p-value using the method in 
    Chapter 6.1, Conover, Practical Non-Parametric Statistics, 3rd Edition (1998)
    
    Assumes that both the empirical and null distro are in the discrete random variables class from scipy
    
    method of ks test can be "upper","lower", or "two-sided"
    
    Falls back on the usual KS-test for large n
    """
    if not (isinstance(null_distro,sp.stats._distn_infrastructure.rv_discrete)):
        raise Exception("Null Distro is not of rv_discrete class")
    if not (isinstance(empirical_distro,sp.stats._distn_infrastructure.rv_discrete)):
        raise Exception("Empirical Distro is not of rv_discrete class")     
    if empirical_distro.P.keys() != null_distro.P.keys():
        raise Exception("Distributions do not have the same support")
    if n > 200:
        pass
    t = 0
    ## calculate t+ so long as type is not lower
    if method in ["upper","two-sided"]:
        tplus = max([null_distro.P[x] - empirical_distro.P[x] for x in null_distro.P.keys()])
        f = []
        for j in np.arange(0,n*(1-tplus)):
            #solve by climbing up from 0
            ordinate = 1- tplus -float(j)/n
            for qval in np.append([0],null_distro.qvals):
                if qval > ordinate:
                    break
                level = qval
            f.append(level)
        e = [1]
        for k in range(1,len(f)):
            for j in range(0,k):
                sp.special.binom(k,j)
                
    #calculate t= so long as type is not upper
    if method in ["lower","two-sided"]:
        tminus = max([empirical_distro.P[x] - null_distro.P[x] for x in null_distro.P.keys()])
    return(t)
        

def r_kstest(raw,expected_count=None):
    obs = ro.vectors.IntVector([i % 10 for i in raw])
    if expected_count is None:
        expected_count = 10*[0.1*np.shape(raw)[0]]
    null_expected = ro.vectors.FloatVector(expected_count)
    p = powerpack.cumulate(powerpack.freq(null_expected))
    sim_ecdf = stats.stepfun(ro.vectors.IntVector(range(0,10)),p)
    test = dgof.ks_test(B=100,simulate_p_value=True,y=sim_ecdf,x=obs)
    pvalue = float(np.array(test.rx('p.value')))
    return(float(pvalue))
    

def stat_battery(real_digits,real_raw,mean_sim_digit,sim_digits):
    statistics = {}
    lookup_test = {"chi2" : "pearson" ,
    "Gtest" :"log-likelihood",
    "freeman-tukey" : "freeman-tukey",
    "mod-log-likelihood" :"mod-log-likelihood",
    "neyman" : "neyman",
    "cressie-read" : "cressie-read"}
    
    lookup_null = {
    "uniform" : None,
    "benford3d" : ben3*sum(real_digits), 
    "benford-mix" : benford_mixture(real_raw)*sum(real_digits),
    "mean-sim" : mean_sim_digit,
    }
        
    ##### POWER DIVERGENCE TESTS
    for testname in lookup_test.keys():
        for null in lookup_null.keys():
            colname  = "-".join([testname,null])
            _, statistics[colname] = power_divergence(real_digits,
                                    lookup_null[null],
                                    lambda_=lookup_test[testname])

    ######## KS-tests
    for null in lookup_null.keys(): 
        statistics["KS-"+null] = r_kstest(real_raw,lookup_null[null])
        
    _ , statistics["lilliefors-type-test"] = lilliefors_type(mean_sim_digit,sim_digits,real_digits)
    return(statistics)
  
def coverage(alpha,results):
    stats = ["chisquare-uniform",
    "chisquare-benford-3d",
    "chisquare-benford-mix",
    "chisquare-mean-sim",
    "lilliefors-type-test",
    ]
    results = results.ix[:,stats]
    results = results.fillna(0)
    coverage = (results < alpha).mean(0)
    return(coverage)

#####################
####  Simulation ####
#####################


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
            
def generate_condor_text(fin,spawnfolder,nsims):
    condor_script_text =  """
    Universe        = vanilla
    Executable	= /usr/local/bin/python27
    Arguments	= /nfs/projects/b/blibgober/digits/simulate_election.py %(fin)s %(spawnfile)s %(nsims)s %(threshhold)s
    request_memory  = 4GB
    request_cpus    = 1
    transfer_executable = false
    should_transfer_files = NO
    output  = %(spawnfolder)s/out.$(Process)
    error   = %(spawnfolder)s/err.$(Process)
    Log     = %(spawnfolder)s/l
    Queue   1
    """ % {"fin": fin,
    "spawnfolder":spawnfolder,
    "nsims" : str(nsims),
    "spawnfile":join(spawnfolder,
    "sims_$(Process)"),
    "outfile":join(spawnfolder,"out.$(Process)"),
    "threshhold": "0.05",
    }
    
    return(condor_script_text)

def simulate(nsims, source, target):
    """
    Calls the condor batch processor on every file in source folder.  Assumes all are csvs 
    Within target, it creates the following directory structure and files
    -Target
    |--fileIn_1
        |- storage
            |- out.1
            |- log.1
            |- error.1 
            |- sims_1_nsims.pkl
    
    """
    
    fins = os.listdir(source)
    for fin in fins:
        print("Starting work on " + fin)
        os.chdir(target)
        fins = os.listdir(source)
        ###create a folder for the file with storage and ensure write permissions
        ffolder = fin.replace(".csv","")
        ffolder = os.path.join(target,ffolder)
        spawnfolder = join(ffolder,"storage")
        make_sure_path_exists(spawnfolder)
        os.chdir(spawnfolder)
        subprocess.call(["chmod","-R","777","."])
        #create a condor submit script
        condor_script_text = generate_condor_text(join(source,fin),spawnfolder,nsims)
        #save the condor submit script
        condor_script_location = join(spawnfolder,"condor_script.submit")
        with open(condor_script_location,"w+") as foo:
            foo.write(condor_script_text)
            #submit it
        subprocess.call(["condor_submit",condor_script_location])

def collect_simulations(source,target,storelocation):
    fins = os.listdir(source)
    store = pd.HDFStore(storelocation)
    for fin in fins: 
        ffolder = fin.replace(".csv","")
        ffolder = os.path.join(target,ffolder)
        spawnfolder = join(ffolder,"storage")
        os.chdir(spawnfolder)
        spawns = glob.glob("*.pkl")
        while len(spawns) < 1:
            spawns = glob.glob("*.pkl")
            time.sleep(5)
            print fin.replace(".csv",""), " stuck"
        sims = pd.read_pickle(spawns[0])
        real = pd.read_csv(join(source,fin))
        real = pd.Panel({"real":real})
        items = sims.items.insert(0,"real")
        panel = real.join(sims)
        panel.items = items
        store[fin.replace(".csv","")] = panel
    print "Sims are Stored in ", storelocation
    store.close()

    
    
