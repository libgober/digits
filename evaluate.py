import pandas as pd
from pandas import HDFStore
import numpy as np
from scipy.spatial import distance
import matplotlib.pyplot as plt


store = HDFStore("/Users/brianlibgober/Desktop/Sim Data/SimStorage.h5")
data = store['NV_2010_g2010_GOV']
store.close()

#real = data.iloc[0,:,0:2]
#sims = data.iloc[1:,:,0:2] % 10
#real_digits = (real % 10)
#real_digits.apply(value_counts).plot(kind="bar")
#sims.iloc[1,].apply(value_counts).plot(kind="bar")
#sims.iloc[2,].apply(value_counts).plot(kind="bar")

def digit_aggregate(table,degree=0):
    """
    Takes a table of returns and produces a table with frequency of digits
    """
    table = table.fillna(0).astype("int")
    for i in range(degree):
        table = (table/10).astype("int")
    table = table % 10
    digits = table.apply(lambda x: x.value_counts(),axis='index')
    return(digits)

def custom_dist(a,b):
    """ Assumes NAN means 0 """
    a = a.fillna(0)
    b = b.fillna(0)
    return(distance.euclidean(a,b))

plt.close(f)
digit_panel = data.apply(lambda x: digit_aggregate(x,1),axis=(1,2))
real = digit_panel.iloc[0,:,:2]
sims = digit_panel.iloc[1:,:,:2]
mean = sims.mean(0)
f, (ax1, ax2) = plt.subplots(1, 2)
real.plot(kind="bar",title="Real",ax=ax1)
mean.plot(kind="bar",title="Mean",ax=ax2)

seriessto = []
for columnNumber in range(np.shape(digit_panel)[2]):
    rDist = custom_dist(real.iloc[:,columnNumber],
                            mean.iloc[:,columnNumber])
    simDist = []
    for item in range(np.shape(sims)[0]):
        simDist.append(
            custom_dist(
                mean.iloc[:,columnNumber],
                sims.iloc[item,:,columnNumber])
        )
    seriessto.append(pd.Series([rDist] + simDist))

real.plot(kind="bar")
