import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
"""
学習の結果からどのような単語が効果的なのかを調べます。
"""

# 保存したMLモデルを開く。
with open("models/logisticregression_model.pickle", "rb") as f:
    model = pickle.load(f)

# 保存したベクトル変換器を開く。
with open("models/vectorizer.pickle", "rb") as f:
    vectorizer = pickle.load(f)

# 使用するDFオブジェクトを作成。
df = pd.DataFrame(columns=["term", "weight"])

# それぞれのモデルからtermに単語を、weightに重みを取得する。
df["term"] = [term for term in vectorizer.get_feature_names()]
df["weight"] = [y for x in model.coef_ for y in x]

# 重みが0の単語はドロップ。
df = df[df.weight != 0.0000]

# 重み順に並べ替え。
df = df.sort_values(by="weight", ascending=False)

# 保存先ディレクトリ、ないなら作る。
try:
    os.mkdir("coefficients")
except:
    pass

# 保存。
df.to_csv("coefficients/coefficients.csv", index=False)
