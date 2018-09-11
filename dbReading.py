import requests
import  csv
import  itertools
import re
import datetime
import sqlite3
import random as r
import string
import os
import time
import threading
from urllib import parse
from pyquery import PyQuery as py
from lxml import etree
best_picked=10
worst_picked=5
class DB():
    def __init__(self):
        self.conn = sqlite3.connect('books2.sqlite3')
        self.cursor = self.conn.cursor()
    def __del__(self):
        print('调用析构函数')
        self.conn.close()
    def storeBook(self,book):
        sql=f"insert into books(id,name,rating,num_of_commenter,tag,price,pub) values('{book.id}','{book.title}','{book.rating}',{book.num_of_commenter},'{book.tag}',{book.price},'{book.pub}')"
        self.cursor.execute(sql)
        self.conn.commit()
    def isDuplicated(self,id):
        sql=f"select * from books where id='{id}'"
        self.cursor.execute(sql)
        book =self.cursor.fetchone()
        if book == None:return False
        else: return True


class Book():
    def __init__(self,title,rating,id,num_of_commenter,tag,price,pub):
        self.title=title
        self.price = price
        self.pub = pub
        self.tag = tag
        self.rating=rating
        self.id = id
        self.num_of_commenter=num_of_commenter
    def __str__(self):
        return f'{self.title} 在{self.tag}下》》{self.id}》》价格》{self.price}》》出版日期》{self.pub}》》 分数为 {self.rating} 分,有效评价共{self.num_of_commenter}条'
    def len(self):
        return len(self.title)
    def __lt__(self, other):
        return self.len()<other.len()
    def __gt__(self, other):
        return self.len()>other.len()
class Category():
    def __init__(self,tag):
        self.tag=tag
        length = 60
        self.sums = [0 for i in range(length)]
        self.counts = [0 for i in range(length)]
        self.avgs = [0 for i in range(length)]
        self.max_rating = [Book('0', 0,'0',i,'0',0,'') for i in range(best_picked)]
        self.min_rating = [Book('0', 10,'0',i,'0',0,'') for i in range(worst_picked)]
        self.longest_name = Book('0', 0,'0',0,'0',0,'')
        self.shortest_name = Book('0'*length, 0,'0',0,'0',0,'')
    def process_item(self,book):
        db.storeBook(book)
        self.sums[book.len()] += float(book.rating)
        self.counts[book.len()] += 1
        self.max_rating.append(book)
        self.min_rating.append(book)
        self.max_rating = sorted(self.max_rating, key=lambda b: b.rating, reverse=True)
        self.min_rating = sorted(self.min_rating, key=lambda b: b.rating)
        del self.max_rating[best_picked]
        del self.min_rating[worst_picked]
        self.longest_name = book if book > self.longest_name else self.longest_name
        self.shortest_name = book if book < self.shortest_name else self.shortest_name
    @property
    def average(self):
        return ['%.2f'%(self.sums[i]/self.counts[i]) if self.counts[i]!=0 else 0 for i in range(len(self.sums))]
    @property
    def totalRating(self):
        return sum(self.sums)
    @property
    def total(self):
        return sum(self.counts)
    def print(self):
        print(f'标签 『{self.tag}』 下图书的统计数据：')
        for i in range(3):
            print(f'第{i+1}高分：{self.max_rating[i]}')
        for i in range(3):
            print(f'第{i+1}低分：{self.min_rating[i]}')
        print('最长书：' + str(self.longest_name))
        print('最短书：' + str(self.shortest_name))  # 必须强制转换，不会自动调用__str__
        for i, j in enumerate(self.average): print(f'长度{i}：平均分是{j}，共{self.counts[i]}本')
        print(f'一共统计了{self.total}本书')
    def output(self):
        with  open('origins_sum.csv','a+',encoding='utf-8',newline ='') as cat: #看了官方文档也找不到解决办法，后来通过搜索看到一个解决方法。就是csv的writer在window下写文件时都是自动在每行末尾加上CF，自动换行。要把打开方式指定为二进制打开才可以。
            sum_row=[self.tag] + self.sums[1:]
            cat_writer=csv.writer(cat)
            cat_writer.writerow(sum_row)
        with  open('origins_count.csv','a+',newline ='') as cat:
            count_row=[self.tag] + self.counts[1:]
            cat_writer=csv.writer(cat)
            cat_writer.writerow(count_row)
        with  open('best.csv', 'a+',encoding='utf-8',newline ='') as b:
            best_row=[self.tag] + self.max_rating
            best_writer=csv.writer(b)
            best_writer.writerow(best_row)
        with  open('worst.csv', 'a+',encoding='utf-8',newline ='') as w:
            worst_row=[self.tag] + self.min_rating
            worst_writer = csv.writer(w)
            worst_writer.writerow(worst_row)
        with  open('avgs.csv', 'a+',encoding='utf-8',newline ='') as a:
            avgs_row = [self.tag] + ['%.2f'%(sum(self.sums)/(sum(self.counts) or 1))]
            avgs_writer = csv.writer(a)
            avgs_writer.writerow(avgs_row)


userAgents = [
  'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)',
  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20',
  'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6',
  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
  'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0) ,Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
  'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
  'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
  'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
  'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre',
  'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52',
  'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
  'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)',
  'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6',
  'Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6',
  'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
  'Opera/9.25 (Windows NT 5.1; U; en), Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
  'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
]



def process_category(tag,type,cat):
    for i in itertools.count(0, 20):
        print(f'此时正在处理第{i//20+1}页')
        url = f'https://book.douban.com/tag/{tag}?start={i}&type={type}'
        if not process_page(url,cat): break

def process_page(url,cat):
    html = etree.HTML(getHtml(url))
    exmls = html.xpath('//*[@id="subject_list"]/ul/li[*]/div[2]/h2/a')
    if len(exmls) == 0:
        time.sleep(120)
        html = etree.HTML(getHtml(url))
        exmls = html.xpath('//*[@id="subject_list"]/ul/li[*]/div[2]/h2/a')
        if len(exmls) == 0:
            return False
    if len(exmls) != 0:
        for elm in exmls:
            rating = elm.xpath('../../div[contains(@class,"star")]/span[contains(@class,"rating_nums")]/text()')
            pub_info_el = elm.xpath('../../div[contains(@class,"pub")]/text()')
            if len(pub_info_el)!=0:
                pub_info=pub_info_el[0].replace(' ',"")

                pub_pattern=re.compile('/\d{4}-')
                pub_search=pub_pattern.search(pub_info)
                pub = pub_search.group()[1:-1] if pub_search != None else '0000'

                price_pattern=re.compile('\d+\.\d+')
                price_search=price_pattern.search(pub_info)
                price =price_search.group() if price_search!=None else 0
                price =int(float(price))
            else:price=0;pub='0000'
            t_commentedNum = elm.xpath('../../div[contains(@class,"star")]/span[contains(@class,"pl")]/text()')
            commentedNum = int(re.match(r'^\(\d+',t_commentedNum[0].strip()).group()[1:]) if t_commentedNum[0].strip() not in ['(少于10人评价)', '(目前无人评价)'] else 10
            href = elm.attrib.get('href')
            p = re.compile(r'/\d+/$')
            id = p.search(href).group()[1:-1];
            title = elm.attrib.get('title')
            title = title[0:(len(title) if title.find(':')==-1 else title.find(':'))]
            title=re.sub(r"[a-zA-Z0-9《》=']",'',title).strip()
            if len(rating)==0 or len(title)==0 or title == "=" or title.find("'")!=-1  or commentedNum < 50:
                pass# print(elm.attrib['title'] + '》》》无分数')
            else:
                global db
                book = Book(title,float(rating[0]),id,commentedNum,cat.tag,price,pub)
                if db.isDuplicated(id):pass
                else:
                    cat.process_item(book)
    return True

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

# your spider code

def getHtml(url):
    # ....
    retry_count = 5
    while True:
        proxy = get_proxy()
        while retry_count > 0:
            try:
                html = requests.get(url, proxies={"http": "http://{}".format(proxy)},headers={'User-Agent':userAgents[r.randrange(len(userAgents))],"Cookie": "bid=%s" % "".join(r.sample(string.ascii_letters + string.digits, 11))})
                # 使用代理访问
                return html.text
            except Exception:
                retry_count -= 1
        # 出错5次, 删除代理池中代理
        delete_proxy(proxy)

    return None

starttime = datetime.datetime.now()#开始计时
with open('start_time.txt','a+',encoding='utf-8',newline ='\n') as f:
    f.write(str(starttime))
    print('开始时间： '+str(starttime))

length=60
if not os.path.exists('worst.csv'):
    with  open('origins_sum.csv', 'a+',encoding='utf-8') as cat:
        title_row = ['标签'] + [i for i in range(1, length)]
        cat_writer = csv.writer(cat)
    with  open('origins_count.csv', 'a+',encoding='utf-8') as cat:
        title_row = ['标签'] + [i for i in range(1, length)]
        cat_writer = csv.writer(cat)
        cat_writer.writerow(title_row)
    with  open('best.csv', 'a+',encoding='utf-8') as b:
        title_row = ['标签'] + [i for i in range(1, best_picked + 1)]
        best_writer = csv.writer(b)
        best_writer.writerow(title_row)
    with  open('worst.csv', 'a+',encoding='utf-8') as w:
        title_row = ['标签'] + [i for i in range(1, worst_picked + 1)]
        worst_writer = csv.writer(w)
        worst_writer.writerow(title_row)
    with  open('avgs.csv', 'a+',encoding='utf-8') as a:
        title_row = ['标签'] + ['均分']
        avgs_writer = csv.writer(a)
        avgs_writer.writerow(title_row)
db=DB()

summary=[]
url = 'https://book.douban.com/tag/?icn=index-nav'
req=requests.get(url,headers={'User-Agent':userAgents[r.randrange(len(userAgents))]})
index=etree.HTML(req.text)
tags=index.xpath('//*[@id="content"]/div/div[1]/div[2]/div/table/tbody/tr/td/a/text()')
t=open('tag.txt','r+',encoding='utf-8')
start=t.read()
index=tags.index(start) if start!='' else 0
tags=tags[index:]
print(f'总标签数{len(tags)}')
for tag in tags:
    print(f'此时正在处理标签  >>>>>>>>>>>>>>>    {tag}')
    cat = Category(tag)
    summary.append(cat)
    for type in ['T','R','S']:
        print(f'此时正在处理排序类型  >>>>>>>>>>>>>>>    {type}')
        process_category(tag.strip(),type,cat)
    cat.output()


s_seperated=[0 for i in range(length)]
c_seperated=[0 for i in range(length)]
a_seperated=[0 for i in range(length)]
for c in summary:
    for i in range(length):
        s_seperated[i]+=c.sums[i]
        c_seperated[i]+=c.counts[i]
    c.print()
for c in summary:
    print(f'在标签 『{c.tag}』 下共有{c.total}本书，平均分为{c.average}')

a_seperated=['%.2f'%(s_seperated[i]/c_seperated[i]) if c_seperated[i]!=0 else 0 for i in range(length)]
for i, j in enumerate(a_seperated): print(f'长度{i}：平均分是{j}，共{c_seperated[i]}本')
avg='%.2f'%(sum(s_seperated)/sum(c_seperated))
print(f'共统计了{sum(c_seperated)}本书,平均得分为{avg}')
endtime = datetime.datetime.now()

print('开始时间'+str(starttime))
print('结束时间'+str(endtime))
print('共计用时'+str((endtime - starttime).seconds//3600)+'小时'+str((endtime - starttime).seconds%3600//60)+'分钟')


