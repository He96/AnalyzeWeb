from urllib import request
from bs4 import BeautifulSoup
import chardet
import re
import pymysql

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


# 关闭数据库链接
def sql_close():
    cur.close()
    conn.close()


def getHtml(url):
    response = request.urlopen(url)
    html = response.read()
    charset = chardet.detect(html)
    encoding = charset['encoding']
    if charset['encoding'] == 'Windows-1254':
        encoding = 'utf-8'
    html = html.decode(encoding)
    return str(html)


max_page = 0


def getData(url):
    html = getHtml(url)
    soup = BeautifulSoup(html, 'lxml')
    # 获取总页数
    # max_page = re.search(re.compile(r'page-numbers">.*?, 共 (\d+) 页'), html).group(1)
    max_page = soup.find_all('span', class_='page-numbers')[0].string
    # 获取最大页码
    max_p = max_page.split(',')[1]
    # 移除非数字内容
    size = re.sub(r'\D', "", max_p)
    # 获取当前页码
    current = soup.find_all('span', class_='current')[0].string
    print('第%s页，总共%s页' % (current, size))
    # 获取本页所有列表
    ul_page = soup.find_all('div', class_='content')
    list = []
    for i in ul_page:
        data = {}
        try:
            # 获取单个图书
            book_info = BeautifulSoup(str(i), 'lxml')
            book_a = book_info.h2.contents[1]
            # 跳转下一页地址
            to_book_url = book_a['href']
            # 书名
            title = book_a['title']
            if title.find('mobi') != -1 or title.find('azw3') != -1:
                # review_info = book_info.find('div',class_='info')
                # 获取评论数
                review_info = book_info.div.div.a.string
                review = re.sub('\D', "", review_info)
                if review < "1":
                    review = "0"
                # 获取简介
                content = book_info.p.string
                # 跳转下一页
                book_to1 = BeautifulSoup(getHtml(to_book_url), 'lxml')
                download_btn = book_to1.find_all('a', class_='downbtn')[0]['href']

                # print('下载地址:',download_btn)
                book_to2 = BeautifulSoup(getHtml(download_btn), 'lxml')
                # 获取百度网盘地址
                url = book_to2.find_all('div', class_='list')[0].contents[1]['href']

                # 获取百度网盘密码
                pws = book_to2.find_all('div', class_='desc')[0].contents[13].string
                password = (pws[(pws.find('百度网盘密码') + 7):(pws.find('百度网盘密码') + 14)]).strip()
                data['title'] = str(book_a.string)
                data['review'] = int(review)
                data['content'] = str(content)
                data['url'] = str(url)
                data['password'] = str(password)
                data['page_nums'] = str(current)
                list.append(data)
        except :
            print('此书不允许下载！')
            break

    return list


def main():
    for i in range(493, 500):
        url = "http://mebook.cc/page/" + str(i)
        list = getData(url)
        if list != None:
            sql_add(list)
    sql_close()
    print('数据爬取完毕！')


main()
