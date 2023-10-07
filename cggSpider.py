import requests
from lxml import etree
import time
import re
from tqdm import tqdm
import pandas as pd
from Module.Common import *
from html import unescape
import traceback
import hashlib

pageTitle = "cgg"
session = requests.session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept': 'image/avif,image/webp,*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Referer': 'https://www.cgg.com/resources/technical-content?page=1',
}
if os.path.exists(resultDir+"/cgg/cgg_articles.xlsx"):
    records = pd.read_excel(resultDir+"/cgg/cgg_articles.xlsx")
    records = {
        "title":records["title"].values.tolist(),
        "url":records["url"].values.tolist(),
        "pdf":records["pdf"].values.tolist(),
    }
else:
    records = {"title":[],"url":[],"pdf":[]}
errors = {"url":[]}
bar = tqdm(range(1,63))
for i in bar:
    bar.set_description("cgg")
    url = 'https://www.cgg.com/resources/technical-content?page=%d'%i
    html = session.get(url=url, headers=headers, timeout=60).text
    time.sleep(1)
    tree = etree.HTML(html)
    aTags = tree.xpath("//a[@class='coh-link coh-ce-e0fc68fa']")
    for aTag in aTags:
        try:
            url = aTag.attrib["href"]
            if url in records['url']:
                continue
            aTag = etree.HTML(etree.tostring(aTag))
            h2 = aTag.xpath("//h2")[0]
            title = h2.text.strip()
            content = session.get(url=url,timeout=360).content
            time.sleep(1)
            md5Value = hashlib.md5(content).hexdigest()
            with open(resultDir+"/cgg/pdf/%s.pdf"%md5Value,"wb") as f:
                f.write(content)
            pd.DataFrame(records).to_excel(resultDir+"/cgg/cgg_articles.xlsx",index=None)
        except Exception as e:
            print(url)
            errors["url"].append(url)
            traceback.print_exc()
pd.DataFrame(errors).to_excel(resultDir+"/cgg/cgg_failed.xlsx",index=None)