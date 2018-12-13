from urllib import request
from bs4 import BeautifulSoup
import chardet
import re
import pymysql
import math
import requests
import time
from decimal import Decimal
import threading as thread

# 数据库连接
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='he123123',
    db='python',
    charset='utf8'
)
cur = conn.cursor()


def sql_update(data):
    sql = 'UPDATE mebook SET review = %s,db_score = %s where id = %s'
    cur.execute(sql, data)
    conn.commit()


def deal(pageIndex, pageSize):
    sql = 'SELECT * FROM mebook order by id ASC limit %s,%s' % (pageIndex, pageSize)
    cur.execute(sql)
    results = cur.fetchall()
    for row in results:
        id = row[0]
        content = row[3]
        if content.find('豆瓣评分') != -1:
            scores = re.search(r'\d+(\.)\d+', content, flags=0).group(0)
            score = scores.strip()
            reviews = re.search(r'(\()\d+人评价', content, flags=0).group(0)
            review = re.compile(r'\d+').findall(reviews)[0]
            data = (int(review), str(score).strip(), id)
            sql_update(data)
            print('修改成功! %s' % row[1])


def main():
    index = 0
    pageSize = 20
    pageIndex = 0
    count = 6977
    maxIndex = int(math.ceil(count / 20))
    while pageIndex <= count:
        pageIndex = index * pageSize
        deal(pageIndex, pageSize)
        index = index + 1


main()
