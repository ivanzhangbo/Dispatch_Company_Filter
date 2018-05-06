import pandas as pd
from sys import os
from datetime import datetime

"""
前処理を行うモジュールです。
"""

# 一番新しいデータファイルを読み込む。ないならexit。
try:
    f_name = (sorted(os.listdir("data"), reverse=True))[0]
    df = pd.read_csv("data/" + f_name)

except:
    print("There's no data file")
    exit()

df.columns = ['url','company', 'min_income', 'max_income', 'dispatch_flg', 'memo', 'docs']

# 不完全なデータをドロップする。
df = df.dropna(subset=['company'])
df = df.dropna(subset=['memo'])
df = df.dropna(subset=['docs'])

# 会社名が重複しているデータをドロップする。
df = df.drop_duplicates(['company'])

print(len(df))

# 保存先ディレクトリがないなら作る。
try:
    os.mkdir("cleansing_data")
    os.mkdir("train_test_data")

except:
    pass

# 学習用データとして200件抽出。
df[:200].to_csv("cleansing_data/cleansing_data_" + datetime.now().strftime("%Y%m%d") + ".csv")
