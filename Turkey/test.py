
import pandas as pd
import sys

out = sys.argv + ['something']
print(out)
pd.DataFrame(out).to_csv("yo.csv")

