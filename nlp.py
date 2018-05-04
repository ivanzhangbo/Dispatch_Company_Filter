import os
import MeCab
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

path = os.environ.get("DIC_PATH")
print(path)
#
# def tokenization():
#
#     tagger = MeCab("Owakachi -d ")
#     df = pd.read_csv("data/test.csv")
