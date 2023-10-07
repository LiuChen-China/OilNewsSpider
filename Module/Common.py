# -*- coding: utf-8 -*-sts
import pandas as pd
import numpy as np
import os
import re

#当前目录
curDir = os.path.dirname(os.path.abspath(__file__))
#根目录
baseDir = os.path.dirname(curDir)
#静态文件目录
staticDir = os.path.join(baseDir,'Static')
#结果文件目录
resultDir = os.path.join(baseDir,'Result')

def clearTag(html):
    '''清理HTML标签和空格'''
    tags = re.findall(r"<.*?>",html)
    for tag in tags:
        html = html.replace(tag,"")
    html = html.replace("\n","").replace("\r","").replace("\t","")
    html = html.strip()
    return html