import pandas as pd

df = pd.read_csv("data/data.csv")
df.columns = ["url","company", "min_income", "max_income", "dispatch_flg", "memo", "corpus"]
df = df.dropna(subset=['company'])
df = df.dropna(subset=['memo'])
df = df.dropna(subset=['corpus'])

df = df.reset_index(drop=True)

print(len(df))

# df.to_csv("data/data")
