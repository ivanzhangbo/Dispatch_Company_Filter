import os
import MeCab
import pickle
import pandas as pd
import concurrent.futures
from sys import exit
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV


def owakati():
    """
    文章を形態素解析して分かち書きにします。
    """

    # 一番新しい学習試験用ファイルを読み込む。ないならexit。
    try:
        f_name = (sorted(os.listdir("train_test_data"), reverse=True))[0]
        df = pd.read_csv("train_test_data/" + f_name)

    except:
        print("There's no train_test_data file")
        exit()

    # neologd付きMeCabを分かち書きで設置。
    # tagger = MeCab.Tagger("-Owakati -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    tagger = MeCab.Tagger("-Owakati -d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")

    # Python3特有のバグを回避。
    tagger.parse(' ')

    # 新しいカラム「owakati」を作って「docs」を分かち書きにしたものを代入。
    df['owakati'] = [tagger.parse(d) for d in df['docs'].values]

    return df


def split_data(df):
    """
    機械学習に必要なデータだけを引き抜いて、よしなに分割して返します。
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


def grid_search(df):
    """
    tf-idfとXGBに最適のパラメータを探ります。
    """

    X, y = split_data(df)
    stop_words = load_stop_word()

    vectorizer = TfidfVectorizer(min_df=3, use_idf=True, token_pattern=u'(?u)\\b\\w+\\b', stop_words=stop_words, ngram_range=(1, 7))
    X_vecs = vectorizer.fit_transform(X)

    feature_names = vectorizer.get_feature_names()

    X_vecs = X_vecs.toarray()
    X_train, X_test, y_train, y_test = train_test_split(X_vecs, y, random_state=0)

    pipe = make_pipeline(xgb.sklearn.XGBClassifier(random_state=0))

    param_grid = {"xgbclassifier__max_delta_step":[0.1]}

    # param_grid = {"xgbclassifier__max_depth": [3, 5, 7],
    #               "xgbclassifier__reg_alpha": [0.5, 0.7, 0.9],
    #               "xgbclassifier__n_estimators":[50, 75, 100, 125],
    #               "xgbclassifier__min_child_weight": [3, 5, 10],
    #               "xgbclassifier__colsample_bytree": [0.5, 0.6, 0.7, 0.8, 0.9],
    #               "xgbclassifier__colsample_bylevel": [0.5, 0.6, 0.7, 0.8, 0.9],
    #               "xgbclassifier__max_delta_step":[0.1]
    #               }

    grid = GridSearchCV(pipe, param_grid, cv=5)
    grid.fit(X_train, y_train)

    try:
        os.mkdir("models")
    except:
        pass

    with open("models/xgb_model.pickle", "wb") as model:
        pickle.dump(grid.best_estimator_, model)

    with open("models/vectorizer.pickle", "wb") as vec:
        pickle.dump(vectorizer, vec)

    feature_importances = grid.best_estimator_.named_steps['xgbclassifier'].feature_importances_

    test_score = grid.best_estimator_.score(X_test, y_test)

    with open("result_xgb.txt", "w") as file:
        print("Best Parameters:\n{}".format(grid.best_params_), file=file)
        print("Best Score: {:.3f}".format(grid.best_score_), file=file)
        print("Test Score: {:.3f}".format(test_score), file=file)


def xgb_clf(df):
    """
    grid_searchの結果からテストデータのスコアを確認します。
    """

    X, y = split_data(df)
    stop_words = load_stop_word()

    vectorizer = TfidfVectorizer(min_df=3, use_idf=True, token_pattern=u'(?u)\\b\\w+\\b', stop_words=stop_words, ngram_range=(1, 7))
    X_vecs = vectorizer.fit_transform(X)
    X_vecs = X_vecs.toarray()

    X_train, X_test, y_train, y_test = train_test_split(X_vecs, y, random_state=0)

    model = xgb.sklearn.XGBClassifier(max_depth=3, random_state=0, reg_alpha=0.9, n_estimators=50)

    model.fit(X_train, y_train)

    with open("score_xgb.txt", "w") as file:
        print("Train Data Score:{}".format(model.score(X_train, y_train)),file=file)
        print("Test Data Score:{}".format(model.score(X_test, y_test)), file=file)


if __name__ == "__main__":

    df = owakati()
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as exe:
        grid_search(df)
    #     exe.submit(xgb_clf, df)
