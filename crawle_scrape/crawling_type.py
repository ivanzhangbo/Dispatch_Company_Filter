import re
import os
from sys import exit
import time
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def get_index():

    urls = set()
    pattern = re.compile(r"/job-./[0-9]*?_detail")
    base = ["https://type.jp/job-1/" + str(i) for i in range(1001, 1008)]
    df = pd.DataFrame(columns=["url"])

    for b in base:
        c = 1
        while True:

            time.sleep(1)

            index_url = b + "/p" + str(c) + "/?pathway=4"
            index_html = requests.get(index_url)

            if index_html.status_code != 200:
                print("break, c is " + str(c))
                break

            soup =  BeautifulSoup(index_html.content, "lxml")
            href = ["https://type.jp/job-1/" + a.get("href")[7:] + "?companyMessage=false" for a in soup.find_all("a") if re.search(pattern, a.get("href"))]
            href = set(href)
            urls = urls | href
            c += 1
            print(len(urls))

    print(len(urls))

    try:
        os.mkdir("index")
    except:
        pass

    with open("index/urls_" + datetime.now().strftime("%Y%m%d") + ".csv", "w") as f:
        for w in urls:
            f.writelines(w + "\n")

def get_detail():
    pass

try:
    f_name = (sorted(os.listdir("index"), reverse=True))[0]

except:
    print("There's no index file")
    exit()

datetime.now().strftime("%Y%m%d")
df = pd.read_csv(f_name)
