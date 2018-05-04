import pandas as pd

df = pd.read_csv("data/data.csv")
df.columns = ["url","company", "min_income", "max_income", "dispatch_flg", "memo", "corpus"]

# 不完全なデータをドロップする。
df = df.dropna(subset=['company'])
df = df.dropna(subset=['memo'])
df = df.dropna(subset=['corpus'])
df.drop_duplicates(['corpus'])

print(len(df))

# 学習用データとして200件抽出。
df[:200].to_csv("data/sample.csv")
