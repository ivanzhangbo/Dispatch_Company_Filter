import os
import MeCab
import pickle
import pandas as pd
from sys import exit
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
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
    tf-idfとLogisticRegressionに最適のパラメータを探ります。
    """

    X, y = split_data(df)
    stop_words = load_stop_word()

    pipe = make_pipeline(
        TfidfVectorizer(min_df=3, use_idf=True, token_pattern=u'(?u)\\b\\w+\\b', stop_words=stop_words),
        LogisticRegression()
        )

    param_grid = {"logisticregression__C": [1**x for x in range(-1, 1)],
                  "tfidfvectorizer__ngram_range": [(1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8)]}

    grid = GridSearchCV(pipe, param_grid, cv=5)
    grid.fit(X, y)

    with open("result_logi.txt", "w") as file:
        print("Best Score: {:.3f}".format(grid.best_score_), file=file)
        print("Best Parameters:\n{}".format(grid.best_params_), file=file)


def logreg(df):
    """
    grid_searchの結果からテストデータのスコアを確認します。
    """

    X, y = split_data(df)
    stop_words = load_stop_word()

    vectorizer = TfidfVectorizer(min_df=3, use_idf=True, token_pattern=u'(?u)\\b\\w+\\b', stop_words=stop_words, ngram_range=(1, 7))
    X_vecs = vectorizer.fit_transform(X)
    X_vecs = X_vecs.toarray()

    X_train, X_test, y_train, y_test = train_test_split(X_vecs, y)

    model = LogisticRegression(C=1.0)
    model.fit(X_train, y_train)

    print("Train Data Score:{}".format(model.score(X_train, y_train)))
    print("Test Data Score:{}".format(model.score(X_test, y_test)))

if __name__ == "__main__":

    df = owakati()
    grid_search(df)
    # logreg(df)
