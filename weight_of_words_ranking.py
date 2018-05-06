import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt

with open("models/logisticregression_model.pickle", "rb") as f:
    model = pickle.load(f)

with open("models/vectorizer.pickle", "rb") as f:
    vectorizer = pickle.load(f)

df = pd.DataFrame(columns=["term", "weight"])

df["term"] = [term for term in vectorizer.get_feature_names()]
df["weight"] = [y for x in model.coef_ for y in x]

df = df[df.weight != 0.0000]
df = df.sort_values(by="weight", ascending=False)
df = df.reset_index(drop=True)

try:
    os.mkdir("coefficients")
except:
    pass

df.to_csv("coefficients/coefficients.csv", index=False)
