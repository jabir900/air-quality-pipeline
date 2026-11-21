import json
from pathlib import Path

import pandas as pd

path = sorted(Path("data/raw").glob("abuja_*.json"))[-1]   # newest Abuja file

with open(path) as f:
    data = json.load(f)

df = pd.DataFrame(data["hourly"])

print(df.head())
print()
print(df.dtypes)
print()
print(df.isna().sum())
