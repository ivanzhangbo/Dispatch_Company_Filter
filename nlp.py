import os
import MeCab
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

tagger = MeCab.Tagger("-Owakati")
tagger.parse(' ')

str = tagger.parse("私は鳥になりたい")
str
# path = os.environ.get("DIC_PATH")
# print(path)

# def tokenization():


    # df = pd.read_csv("data/test.csv")
