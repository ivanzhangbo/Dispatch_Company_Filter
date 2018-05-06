import sys
import pickle
from crawling_type import get_detail
from exe_ml import owakati
"""
urlからその求人が派遣会社なのか否かを自動判別します。
"""

# コマンドの引数からurlを取得する。
argvs = sys.argv

# コマンドの引数が多過ぎるときはエラーメッセージを吐いて終了。
if len(argvs) >= 3:
    print("argument error")
    sys.exit()

# 保存したMLモデルを開く。
with open("models/logisticregression_model.pickle", "rb") as f:
    model = pickle.load(f)

# 保存したベクトル変換器を開く。
with open("models/vectorizer.pickle", "rb") as f:
    vectorizer = pickle.load(f)

# crawling_typeからget_detailを呼び出し、対象のURLをクローリング&スクレイピング
df = get_detail(argvs[1])

# exe_mlからowakatiを呼び出し、コーパスを作成。
df = owakati(df)

# ベクトル分類器を使ってコーパスをベクトル化。
vec = vectorizer.transform(df['owakati'])

# MLモデルを使って結果を予測。
flg = model.predict(vec)

# 操作しやすいようにdfをリスト化
li = df.loc[0].values

# 結果をprint
print("会社名:\t\t{}".format(li[1]))
print("年収:\t\t{}〜{}万円".format(li[2], li[3]))
print("年収捕捉:\t{}".format(li[5]))
print("派遣フラグ:\t{}".format(flg[0]))
