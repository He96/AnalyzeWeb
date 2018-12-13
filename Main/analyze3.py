from urllib import request
from bs4 import BeautifulSoup
import chardet
import re
import pymysql
import requests
import time
import threading as thread
from decimal import Decimal
from pyecharts import Liquid
from pyecharts import Bar3D, Page, Style
from pyecharts import WordCloud,Style

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


# 添加数据
def sql_add(data):
    values = []
    sql = 'INSERT INTO `python`.`mebook`(`title`,`review`,`content`,`url`,`password`,`page_nums`) VALUES (%s,%s,%s,%s,%s,%s)'
    for i in data:
        item = (i['title'], i['review'], i['content'], i['url'], i['password'], i['page_nums'])
        values.append(item)
    cur.executemany(sql, values)
    conn.commit()
    print('添加成功！')

# 分页查询
def sql_select(pageIndex,pageSize):
    sql = 'SELECT * FROM mebook limit %s,%s' % (pageIndex, pageSize)
    cur.execute(sql)
    results = cur.fetchall()
    mebook_list = []
    for row in results:
        data = {}
        data['id'] = row[0]
        data['title'] = row[1]
        data['review'] = row[2]
        data['content'] = row[3]
        data['url'] = row[4]
        data['password'] = row[5]
        data['page_nums'] = row[6]
        data['db_score'] = row[7]
        mebook_list.append(data)
    return mebook_list

#获取总记录数
def sql_count():
    sql = 'SELECT count(*) FROM mebook'
    cur.execute(sql)
    requests = cur.fetchone()
    return requests[0]
# 删除数据
def sql_remove(id):
    sql = 'delete from mebook where id = %s'%(id)
    try:
        cur.execute(sql)
        conn.commit()
    except:
        conn.rollback()

# 关闭数据库链接
def sql_close():
    cur.close()
    conn.close()

proc = 0.00


page = Page()

# 爬取进度
liquid = Liquid('网页爬取进度')
nowpro = sql_count()/6977
proc = Decimal(nowpro).quantize(Decimal('0.00'))
liquid.add("爬取进度", [str(proc)])

# 3D 柱状图
bar3d = Bar3D("豆瓣评分", width=1620, height=720)
datalist = sql_select(0, 6977)
# 书名
x_axis = []
y_axis = []
data = []
y = 0
x = 0

# 词库云
book_name = []
reviews =[]
for book in datalist:
    try:
        if book['title'].find('》') != -1:
            name = re.search(r'《.*》', book['title'], flags=0).group(0)
            name = name[1:len(name) - 1]
    except :
        name = book['title']
    book_name.append(name)
    reviews.append(book['review'])
    if len(x_axis) < 24:
        x_axis.append(name)

    item = []
    item = [x, y, book['db_score']]
    data.append(item)
    y = y + 1
    # 24条换一行
    if y % 24 == 0:
        x = x+1
        y = 0
        y_axis.append('豆瓣评分')


# x_axis = [
#     "12a", "1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a",
#     "12p", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p"]
# 评分

range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
               '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
bar3d.add("", x_axis, y_axis, [[d[1], d[0], d[2]] for d in data],
          is_visualmap=True, visual_range=[0, 10],
          visual_range_color=range_color, grid3d_width=200, grid3d_depth=80,is_grid3d_rotate=True)

# 词库云
style = Style(
    width=1620, height=720
)
chart = WordCloud('图书评论最多', **style.init_style)
chart.add("", book_name, reviews, word_size_range=[30, 100], rotate_step=66)
page.add(chart)

page.add(bar3d)

page.add(liquid)
#
page.render()

