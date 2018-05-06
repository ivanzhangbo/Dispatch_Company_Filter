import os
import MeCab
import pickle
import pandas as pd
from sys import exit
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV

"""
自然言語処理と機械学習を行うモジュールです。
"""

def owakati(df):
    """
    文章を形態素解析してコーパスを作ります。
    """

    # neologd付きMeCabを分かち書きで設置。
    tagger = MeCab.Tagger("-Owakati")

    # ipadic-neologdを使う場合は以下を参考に。
    # tagger = MeCab.Tagger("-Owakati -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    # tagger = MeCab.Tagger("-Owakati -d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")

    # Python3特有のバグを回避。
    tagger.parse(' ')

    # 新しいカラム「owakati」を作って「docs」を分かち書きにしたものを代入。
    df['owakati'] = [tagger.parse(d) for d in df['docs'].values]

    return df


def split_data(df):
    """
    機械学習に必要なデータだけを引き抜いて返却します。
    """

    X, y = df['owakati'].values, df['dispatch_flg'].values
    del df
    return X, y


def load_stop_word():
    """
    ストップワード("http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt")
    を読み込み、リストにして返します。
    """

    with open("stop_words.txt", "r") as f:
        stop_words = [w.strip("\n") for w in f]

    return stop_words


def nlp(df):
    """
    tf-idfモデルを用いてコーパスをベクトル化し、返却します。
    また学習済みのtf-idfモデルをpickle化して保存します。
    """

    # 必要なデータだけ取り出す。
    X, y = split_data(df)
    # ストップワードの読み込み。
    stop_words = load_stop_word()
    # パラメータを指定してモデル構築。
    vectorizer = TfidfVectorizer(min_df=3, use_idf=True, token_pattern=u'(?u)\\b\\w+\\b', stop_words=stop_words, ngram_range=(1, 7))
    # コーパスを学習 & ベクトル化。
    X_vecs = vectorizer.fit_transform(X)

    # モデル保存先ディレクトリ、ないなら作る。
    try:
        os.mkdir("models")
    except:
        pass

    # pickle化して保存。
    with open("models/vectorizer.pickle", "wb") as f:
        pickle.dump(vectorizer, f)

    return X_vecs


def ml_exe(df, pipe, param_grid, ml_name):
    """
    引数で渡されたモデルとパラメータを元にグリッドサーチ行い、
    最適のMLモデルを構築します。
    また構築されたMLモデルを保存します。
    """

    # 学習用データを取得。
    X_vecs = nlp(df)
    # よしなにデータ分割。
    X_train, X_test, y_train, y_test = train_test_split(X_vecs, y, random_state=0)

    # 引数を当てはめ、グリッドサーチの型を作る。
    grid = GridSearchCV(pipe, param_grid, cv=5)
    # 与えられたパラメータの全パターン学習を行い、最適なモデルを構築する。
    grid.fit(X_train, y_train)

    # 最適のモデルを保存。
    with open("models/" + ml_name +"_model.pickle", "wb") as f:
        pickle.dump(grid.best_estimator_.named_steps[ml_name], f)

    # テストデータの結果を算出。
    test_score = grid.best_estimator_.score(X_test, y_test)

    # ログの保存先ディレクトリ、ないなら作る。
    try:
        os.mkdir("log")
    except:
        pass

    # ログを保存。
    with open("log/result_" + ml_name + ".txt", "w") as file:
        print("Best Score: {:.3f}".format(grid.best_score_), file=file)
        print("Test Score: {:.3f}".format(test_score), file=file)
        print("Best Parameters:\n{}".format(grid.best_params_), file=file)


if __name__ == "__main__":

    # 一番新しい学習試験用ファイルを読み込む。ないならexit。
    try:
        f_name = (sorted(os.listdir("train_test_data"), reverse=True))[0]
        df = pd.read_csv("train_test_data/" + f_name)

    except:
        print("There's no train_test_data file")
        exit()

    df = owakati(df)

    # param_grid = {"xgbclassifier__max_depth": [3, 5, 7],
    #               "xgbclassifier__reg_alpha": [0.5, 0.7, 0.9],
    #               "xgbclassifier__n_estimators":[50, 75, 100, 125],
    #               "xgbclassifier__min_child_weight": [3, 5, 10],
    #               "xgbclassifier__colsample_bytree": [0.5, 0.6, 0.7, 0.8, 0.9],
    #               "xgbclassifier__colsample_bylevel": [0.5, 0.6, 0.7, 0.8, 0.9],
    #               "xgbclassifier__max_delta_step":[0.1]
    #               "random_state": [0]
    #               }

    # param_grid = {"xgbclassifier__max_depth": [3],
    #               "xgbclassifier__reg_alpha": [0.3],
    #               "xgbclassifier__n_estimators": [50],
    #               "xgbclassifier__min_child_weight": [5],
    #               "xgbclassifier__colsample_bytree": [0.7],
    #               "xgbclassifier__colsample_bylevel": [0.8],
    #               "xgbclassifier__max_delta_step":[0.1],
    #               "random_state": [0]
    #               }

    # pipe = make_pipeline(xgb.sklearn.XGBClassifier())

    param_grid = {'logisticregression__C': [10** x for x in range(-5, 5)],
                  'logisticregression__fit_intercept': [True, False],
                  'logisticregression__penalty': ['l2'],
                  'logisticregression__random_state': [0]
                  }

    pipe = make_pipeline(LogisticRegression())

    ml_exe(df, pipe, param_grid, "logisticregression")
