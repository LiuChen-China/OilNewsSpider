import requests
from lxml import etree
import time
import re
from tqdm import tqdm
import pandas as pd
from Module.Common import *
from html import unescape
import traceback
pageTitle = "worldoil"
session = requests.session()
headers = {
    'Host': 'worldoil.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
url = "https://worldoil.com/"
html = session.get(url=url,headers=headers,timeout=60).text
time.sleep(1)
errors = {"url":[]}
#爬取新闻链接列表
if 0:
    tree = etree.HTML(html)
    aTags = tree.xpath("//div[@class='submenu-links mega-submenu']/a")
    topics = [{"topic":aTag.text,"url":"https://worldoil.com"+aTag.attrib['href']} for aTag in aTags]
    bar = tqdm(topics)
    newsList = []
    for topic in bar:
        bar.set_description("抽取新闻链接")
        pageCount = 0
        while True:
            pageCount += 1
            url = topic["url"] + "?page=%d"%pageCount
            html = session.get(url=url,headers=headers,timeout=60).text
            time.sleep(1)
            tree = etree.HTML(html)
            aTags = tree.xpath("//div[@class='topic-title']/a")
            if not aTags:
                break
            for aTag in aTags:
                newsUrl = "https://worldoil.com" + aTag.attrib['href']
                title = etree.HTML(etree.tostring(aTag)).xpath('//h2')[0].text
                newsList.append({"title":title,"topic":topic["topic"],"url":newsUrl})
    newsList = pd.DataFrame(newsList)
    newsList = newsList.drop_duplicates()
    newsList.to_excel(resultDir+"/worldoil/%s.xlsx"%pageTitle,index=None)

#爬取新闻内容
newsList = pd.read_excel(resultDir+"/worldoil/%s.xlsx"%pageTitle)
if os.path.exists(resultDir+"/worldoil/%s_articles.xlsx"%pageTitle):
    newsRecords = pd.read_excel(resultDir+"/worldoil/%s_articles.xlsx"%pageTitle)
    newsRecords = {
        "title":newsRecords["title"].values.tolist(),
        "author":newsRecords["author"].values.tolist(),
        "topic":newsRecords["topic"].values.tolist(),
        "date":newsRecords["date"].values.tolist(),
        "content":newsRecords["content"].values.tolist(),
        "url":newsRecords["url"].values.tolist(),
    }
else:
    newsRecords = {"title":[],"author":[],"topic":[],"date":[],"content":[],"url":[]}
bar = tqdm(newsList.index)
for i in bar:
    bar.set_description("爬取新闻内容")
    row = newsList.loc[i]
    if row["url"] in newsRecords["url"]:
        continue
    try:
        html = session.get(url=row["url"], headers=headers, timeout=60).text
        time.sleep(1)
        tree = etree.HTML(html)
        if tree.xpath("//span[@class='news-detail-author']"):
            author = tree.xpath("//span[@class='news-detail-author']")[0].text
        else:
            author = None
        if tree.xpath("//span[@class='news-detail-date']"):
            date = tree.xpath("//span[@class='news-detail-date']")[0].text
        elif tree.xpath("//div[@class='article-detail-issue']"):
            date = tree.xpath("//div[@class='article-detail-issue']")[0].text.strip()

        if tree.xpath("//div[@class='news-detail-content content-body']"):
            content = tree.xpath("//div[@class='news-detail-content content-body']")[0]
        elif tree.xpath("//div[@class='article-detail-content content-body']"):
            content = tree.xpath("//div[@class='article-detail-content content-body']")[0]

        content = clearTag(unescape(etree.tostring(content,encoding="utf-8").decode()))
        newsRecords["title"].append(row["title"])
        newsRecords["author"].append(author)
        newsRecords["topic"].append(row["topic"])
        newsRecords["date"].append(date)
        newsRecords["content"].append(content)
        newsRecords["url"].append(row["url"])
        pd.DataFrame(newsRecords).to_excel(resultDir+"/worldoil/%s_articles.xlsx"%pageTitle,index=None)
    except Exception as e:
        print(row["url"])
        errors["url"].append(row["url"])
        traceback.print_exc()
pd.DataFrame(errors).to_excel(resultDir+"/worldoil/%s_failed.xlsx"%pageTitle,index=None)