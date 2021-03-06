import re
import os
import requests
import pandas as pd
from sys import exit
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime

"""
クローリングとスクレイピングを行うモジュールです。
"""

# ユーザエージェントの指定。
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
           'referer': 'https://console.cloud.google.com'}

def get_index():
    """
    IT系求人のインデックスページに対してクローリング & スクレイピングを行い、調査対象となるURLを取得します。
    「./index/」以下にcsvファイルを吐き出します。
    """

    # スクレイピングのパターンを正規表現で指定してコンパイル。
    pattern = re.compile(r"/job-./[0-9]*?_detail")
    # インデックスページのURLパターンを配列に格納。
    base = ["https://type.jp/job-1/" + str(i) for i in range(1001, 1008)]
    # データを蓄積させるDFオブジェクトを作成。
    urls = pd.DataFrame(columns=["url"])

    for b in base:
        c = 1

        while True:

            # クローリングのマナー。
            sleep(1)

            # URLをセットしてリクエスト。
            index_url = b + "/p" + str(c) + "/?pathway=4"
            index_html = requests.get(index_url, headers=headers)

            # ステータスコードが200でないならブレイク。
            if index_html.status_code != 200:
                break

            # スクレイピングをして必要な情報(個別URL)だけを抜き出す。
            soup =  BeautifulSoup(index_html.content, "lxml")
            list = ["https://type.jp/job-1/" + a.get("href")[7:] + "?companyMessage=false" for a in soup.find_all("a") if re.search(pattern, a.get("href"))]

            # DFにリストの内容を追加。
            urls = urls.append(pd.DataFrame({"url":list}))

            c += 1

    # ないならディレクトリを作る。
    try:
        os.mkdir("index")

    except:
        pass

    # ユニーク抽出をして保存。
    urls = urls.drop_duplicates()
    urls.to_csv("index/urls_" + datetime.now().strftime("%Y%m%d") + ".csv", index=False)


def get_detail(url):
    """
    urlを引数に詳細ページをクローリング & スクレイピングして、
    結果をDFオブジェクトで返却します。
    """

    # クローリングのマナー。
    sleep(1)

    # 保存に使うDFをリセット。
    df = pd.DataFrame(columns=['url','company', 'min_income', 'max_income', 'dispatch_flg', 'memo', 'docs'])

    # URLをセットしてリクエスト。
    detail_html = requests.get(url, headers=headers)

    # ステータスコードが200以外なら処理を終了。
    if detail_html.status_code != 200:
        print("request error")
        return df

    # スクレイピング開始。
    soup =  BeautifulSoup(detail_html.content, "lxml")

    # 会社名を取得。
    company = ""
    try:
        company = soup.find("a", class_="corp-link base_gray size-14px weight-bold")
        company = re.sub(r'<.*?>', '', company.text)
    except:
        pass

    # 年収を取得。
    baseSalary = soup.find("p", itemprop="baseSalary")

    money_str = ""

    try:
        money_str = re.search(r'(年|月).*?[0-9,]*?万円.*?[0-9,]万円', baseSalary.text).group()
    except:
        try:
            money_str = re.search(r'(年|月).*?[0-9,]*?万円', baseSalary.text).group()

        except:
            pass

    max_income, min_income = 0, 0
    try:
        money_int = re.findall(r'[0-9,]+', money_str)

        if "月" in money_str:
            money_int = [int(n) * 12 for n in money_int]
        else:
            money_int = [int(n) for n in money_int]

        money_int.reverse()

        if len(money_int) >= 2:
            max_income, min_income = money_int[0], money_int[1]
        elif len(money_int) == 1:
            max_income, min_income = money_int[0], money_int[0]

    except:
        pass

    docs = ""
    # コーパスを取得し、正規化する。
    try:
        docs = [re.sub(r'<.*?>', '', i.text) for i in soup.find_all("p")]
        docs = ",".join(docs)
        docs = re.sub(r",", '', docs)
        docs = re.sub(r"\n", '', docs)
        docs = re.sub(r"\s", '', docs)
        docs = re.sub(r"\s", '', docs)
        docs = re.sub(r"転職サイト＠type.*?ALLRIGHTSRESERVED", '', docs)
        docs = re.sub(r"掲載終了予定日.*?掲載終了日前に募集を終了する可能性があります》", '', docs)

    except:
        pass

    # ファイル形式をDFオブジェクトに変換。
    se = pd.Series([url, company, min_income, max_income, "", money_str, docs], index=df.columns)
    df = df.append(se, ignore_index=True)
    return df


def saving(df):
    """
    スクレイピングの結果を1保存します。
    """

    # 保存先ディレクトリがないなら作る。
    try:
        os.mkdir("data")

    except:
        pass

    df.to_csv("data/data_" + datetime.now().strftime("%Y%m%d") + ".csv",  index=False, header=False, mode='a')


def get_all():
    """
    urlsファイルにある分だけget_detailとsavingを呼び出します。
    """

    # urlsオブジェクトが作られていないなら、一番新しいurls_YYYYmmdd.csvを読み込む。ないならexit。
    try:
        urls

    except:
        try:
            f_name = (sorted(os.listdir("index"), reverse=True))[0]
            urls = pd.read_csv("index/" + f_name)

        except:
            print("There's no index file")
            exit()

    # URLの数だけget_detail関数をぶん回す。
    for i in urls["url"].values:
        df = get_detail(i)
        saving(df)


if __name__ == "__main__":

    get_index()
    get_all()
