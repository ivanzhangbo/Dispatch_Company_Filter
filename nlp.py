import os
import MeCab
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

DIC = os.environ['DIC']
print(DIC)
#
# def tokenization():
#
#     tagger = MeCab("Owakachi -d ")
#     df = pd.read_csv("data/test.csv")
