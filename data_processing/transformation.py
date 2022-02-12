#%%
import pandas as pd
import json
from collections import defaultdict

# %%
df = pd.read_csv('../data/situation_annotation.csv')
df = df.iloc[:266]
# %%
data = defaultdict(list)
for _, row in df.iterrows():
    situation = row['상황']
    descriptions = row[1:].dropna().tolist()
    data[situation].extend(descriptions)

# %%
with open('../data/situation_annotation.json', 'w+') as fp:
    json.dump(data, fp, indent=4, ensure_ascii=False)
# %%
