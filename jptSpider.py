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

pageTitle = "jpt"
session = requests.session()
headers = {
    'Host': 'jpt.spe.org',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
url = "https://jpt.spe.org/"
html = session.get(url=url,headers=headers,timeout=60).text
time.sleep(1)
errors = {"url":[]}
time.sleep(1)
tree = etree.HTML(html)
topics = []
aTags = tree.xpath('//ul[@class="NavigationList-items"]/li[@class="NavigationList-items-item"]/a')
for aTag in aTags:
    topic = {"topic":aTag.text,"url":aTag.attrib["href"]}
    if topic in topics:
        continue
    topics.append(topic)

if os.path.exists(resultDir+"/jpt/%s_articles.xlsx"%pageTitle):
    newsRecords = pd.read_excel(resultDir+"/jpt/%s_articles.xlsx"%pageTitle)
    newsRecords = {
        "title":newsRecords["title"].values.tolist(),
        "author":newsRecords["author"].values.tolist(),
        "topic":newsRecords["topic"].values.tolist(),
        "date":newsRecords["date"].values.tolist(),
        "summary":newsRecords["summary"].values.tolist(),
        "content":newsRecords["content"].values.tolist(),
        "url":newsRecords["url"].values.tolist(),
    }
else:
    newsRecords = {"title":[],"author":[],"topic":[],"date":[],"summary":[],"content":[],"url":[]}

bar = tqdm(topics)
for topic in bar:
    html = session.get(url=topic["url"], headers=headers, timeout=60).text
    time.sleep(1)
    pageTotalNum = int(re.findall(r'>Page 1 of (\d+)</div>',html)[0])
    for pageNum in range(1,pageTotalNum+1):
        bar.set_description("%s-%d/%d"%(topic["topic"],pageNum,pageTotalNum))
        url = topic["url"]+"?00000176-732a-d76b-af77-7f2fb0270000-page=%d"%pageNum
        html = session.get(url=url, headers=headers, timeout=60).text
        tree = etree.HTML(html)
        time.sleep(1)
        aTags = tree.xpath("//div[@class='PromoB-title']/a[@class='Link']")
        for aTag in aTags:
            try:
                title = aTag.text.strip()
                newsUrl = aTag.attrib['href']
                if newsUrl in newsRecords["url"]:
                    continue
                html = session.get(url=newsUrl, headers=headers, timeout=60).text
                tree = etree.HTML(html)
                time.sleep(1)
                if tree.xpath("//h2[@class='ArticlePage-subHeadline']"):
                    summary = tree.xpath("//h2[@class='ArticlePage-subHeadline']")[0].text.strip()
                else:
                    summary = ""
                if len(tree.xpath("//div[@class='ArticlePage-authorName']//span"))>1:
                    author = tree.xpath("//div[@class='ArticlePage-authorName']//span")[1].text
                else:
                    author = ""
                date = tree.xpath("//div[@class='ArticlePage-datePublished']")[0].text.strip()
                content = tree.xpath("//div[@class='RichTextArticleBody-body RichTextBody']")[0]
                content = clearTag(unescape(etree.tostring(content,encoding="utf-8").decode())).strip()
                newsRecords["title"].append(title)
                newsRecords["author"].append(author)
                newsRecords["topic"].append(topic["topic"])
                newsRecords["date"].append(date)
                newsRecords["content"].append(content)
                newsRecords["url"].append(newsUrl)
                newsRecords["summary"].append(summary)
                pd.DataFrame(newsRecords).to_excel(resultDir + "/jpt/%s_articles.xlsx" % pageTitle, index=None)
            except Exception as e:
                print(newsUrl)
                errors["url"].append(newsUrl)
                traceback.print_exc()
pd.DataFrame(errors).to_excel(resultDir+"/jpt/%s_failed.xlsx"%pageTitle,index=None)