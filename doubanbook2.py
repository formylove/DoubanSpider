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
import  requestpool
import threading
from urllib import parse
from pyquery import PyQuery as py
from lxml import etree
class DB():
    def __init__(self):
        self.conn = sqlite3.connect('books3.sqlite3')
        self.cursor = self.conn.cursor()
    def __del__(self):
        self.conn.close()
    def storeBook(self,book):
        sql=f"insert into books(id,name,rating,num_of_commenter,tag,author,publisher,price,pub) values('{book.id}','{book.title}','{book.rating}',{book.num_of_commenter},'|{book.tag}|','{book.author}','{book.publisher}',{book.price},'{book.pub}')"
        self.cursor.execute(sql)
        self.conn.commit()
    def isDuplicated(self,id):
        sql=f"select * from books where id='{id}'"
        self.cursor.execute(sql)
        book =self.cursor.fetchone()
        if book == None:return False
        else: return True
    def updateBook(self,book):
        sql=f"update books set tag=tag ||'{book.tag}|' where id='{book.id}'"
        self.cursor.execute(sql)
        self.conn.commit()
class Book():
    def __init__(self,title,rating,id,num_of_commenter,tag,author,publisher,price,pub):
        self.title=title
        self.price = price
        self.pub = pub
        self.tag = tag
        self.author = author
        self.publisher = publisher
        self.rating=rating
        self.id = id
        self.num_of_commenter=num_of_commenter
    def __str__(self):
        return f'{self.title} 在{self.tag}下》作者》{self.author}》{self.id}》》价格》{self.price}》》出版日期》{self.pub}》出版社》{self.publisher}》 分数为 {self.rating} 分,有效评价共{self.num_of_commenter}条'
    def len(self):
        return len(self.title)
    def __lt__(self, other):
        return self.len()<other.len()
    def __gt__(self, other):
        return self.len()>other.len()
    def process_item(self,book):
        if db.isDuplicated(book.id):
            db.updateBook(book)
        else:
            db.storeBook(book)



def process_page(url,tag):
    html = etree.HTML(requestpool.getHtml(url))
    exmls = html.xpath('//*[@id="subject_list"]/ul/li[*]/div[2]/h2/a')
    if len(exmls) == 0:
        time.sleep(120)
        html = etree.HTML(requestpool.getHtml(url))
        exmls = html.xpath('//*[@id="subject_list"]/ul/li[*]/div[2]/h2/a')
        if len(exmls) == 0:
            return False
    if len(exmls) != 0:
        for elm in exmls:
            rating = elm.xpath('../../div[contains(@class,"star")]/span[contains(@class,"rating_nums")]/text()')
            pub_info_el = elm.xpath('../../div[contains(@class,"pub")]/text()')
            if len(pub_info_el)!=0:
                pub_info=pub_info_el[0].replace(' ',"").replace('\n','')

                publisher_pattern=re.compile(r'/[^\d/]+/\d{4}-')
                publishers=publisher_pattern.findall(pub_info)
                publisher=publishers[0][1:-6].strip().replace("'",'') if len(publishers)!=0 and len(publishers[0])>6 else ''

                author_pattern=re.compile(r'^[^/]+/')
                authors=author_pattern.findall(pub_info)
                author=authors[0][:-1].strip().replace("'",'') if len(authors)!=0 else ''

                year_pattern=re.compile('/\d{4}-')
                year = year_pattern.search(pub_info).group()[1:-1] if year_pattern.search(pub_info) != None else '0000'

                price_pattern=re.compile('\d+\.\d+')
                price =price_pattern.search(pub_info).group() if price_pattern.search(pub_info)!=None else 0
                price =int(float(price))
            else:price=0;pub_year='0000';publisher=''
            t_commentedNum = elm.xpath('../../div[contains(@class,"star")]/span[contains(@class,"pl")]/text()')
            commentedNum = int(re.match(r'^\(\d+',t_commentedNum[0].strip()).group()[1:]) if t_commentedNum[0].strip() not in ['(少于10人评价)', '(目前无人评价)'] else 0
            href = elm.attrib.get('href')
            p = re.compile(r'/\d+/$')
            id = p.search(href).group()[1:-1];
            title = elm.attrib.get('title')
            title=re.sub(r"'",'',title).strip()
            if len(rating)==0 or len(title)==0 or title.find("'")!=-1:
                pass
            else:
                global db
                book = Book(title,float(rating[0]),id,commentedNum,tag,author,publisher,price,year)
                book.process_item(book)
    return True





starttime = datetime.datetime.now()#开始计时
db=DB()

url = 'https://book.douban.com/tag/?icn=index-nav'
index=etree.HTML(requestpool.getHtml(url))
tags=index.xpath('//*[@id="content"]/div/div[1]/div[2]/div/table/tbody/tr/td/a/text()')
t=open('tag.txt','r+',encoding='utf-8')
start=t.read()
index=tags.index(start) if start!='' else 0
tags=tags[index:]
print(f'总标签数{len(tags)}')

for tag in tags:
    for type in ['T','R','S']:
            for i in itertools.count(0, 20):
                print(f'此时正在处理《{tag}》类型{type}第{i//20+1}页')
                url = f'https://book.douban.com/tag/{tag}?start={i}&type={type}'
                if not process_page(url,tag): break



endtime = datetime.datetime.now()

print('开始时间'+str(starttime))
print('结束时间'+str(endtime))
print('共计用时'+str((endtime - starttime).seconds//3600)+'小时'+str((endtime - starttime).seconds%3600//60)+'分钟')


