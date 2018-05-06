import sys
import pickle
from crawling_type import get_detail

argvs = sys.argv

if len(argvs) >= 3:
    print("argument error")
    sys.exit()

with open("models/logisticregression_model.pickle", "rb") as f:
    model = pickle.load(f)

with open("models/vectorizer.pickle", "rb") as f:
    vectorizer = pickle.load(f)

df = get_detail(argvs[1])
vec = vectorizer.transform(df['docs'])
flg = model.predict(vec)

df = df.loc[0].values

print("会社名:\t\t{}".format(df[1]))
print("年収:\t\t{}〜{}万円".format(df[2], df[3]))
print("年収捕捉:\t{}".format(df[5]))
print("派遣フラグ:\t{}".format(flg[0]))
