#!/usr/bin/env python
#coding=gbk
# -*- coding: gbk -*-
#
# Copyright 2012 Channing Wong
#
# @mail: channing.wong@yahoo.com
# @home: http://blog.3363.me/
# @date: Mar 3, 2012
#
 
import json
import sys
import time
import types
import urllib
import urllib2
import re

import os
import codecs
import commonlang
import math
import FilterTag
import sqlite3
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding( "utf-8" )

__author__="kmlxk@163.com"
__date__ ="$2014-7-18 13:48:13$"

class NewsRepository:
    def __init__(self, filename):
        self.open(filename)
        pass

    def open(self, filename):
        self.db = sqlite3.connect(filename)

    def execute(self, sql, params = None):
        cursor = self.db.cursor()
        cursor.execute(sql, params)
        self.db.commit()
        cursor.close()

    def query(self, sql):
        cursor = self.db.cursor()
        cursor.execute(sql)
        rows = cu.fetchall()
        cursor.close()
        return rows

    def close(self):
        self.db.close()

    def add(self, title, content):
        sql = 'INSERT INTO pn_content (title, content) VALUES(?, ?)'
        self.execute(sql, (title, content));


class HtmlContentParser:
    
    def __init__(self):
        pass
    
    #将HTML拆分为若干份，找出p数量最多的段
    def getContent(self, html, blockCount = 40, neighbour = 0.15):
        total = len(html)
        each = int(math.ceil(total / blockCount))
        stat = self.statistic(html, blockCount)
        neighbourStep = int(math.ceil(neighbour * blockCount))
        # 计算斜率
        slope = [0 for i in range(0, len(stat))]
        for i in range(0, len(stat)):
            if i == 0:
                slope[i] = 0
            else:
                slope[i] = stat[i] - stat[i-1]
        # 寻找最密集的p标签所在段落
        maxUpPos, maxDownPos = self.findMax(slope)
        # 最密集的p段位于 [maxUpPos, maxDownPos] 之间
        # 扩展前后搜寻
        maxDownPos = self.findNeighbour(stat, neighbourStep, 1, maxDownPos)
        maxUpPos = self.findNeighbour(stat, neighbourStep, -1, maxUpPos)
        text = html[maxUpPos*each: maxDownPos*each]
        start = text.find('>') + 1
        end = text.rfind('<')
        return text[start: end]

    # 寻找最密集的p标签所在段落
    def findMax(self, slope):
        maxUp = 0
        maxDown = 0
        maxUpPos = 0
        maxDownPos = 0
        for i in range(0, len(slope)):
            if slope[i] > maxUp:
                maxUp = slope[i]
                maxUpPos = i
            rev_i = len(slope) - i - 1
            if slope[rev_i] < maxDown:
                maxDown = slope[rev_i]
                maxDownPos = rev_i
        return (maxUpPos, maxDownPos)

    # 寻找相邻的可能正文
    def findNeighbour(self, stat, neighbourStep, direction, pos):
        # direction = 1向后搜索, -1向前搜索
        i = pos + direction
        zeroCount = 0
        while i > 0 and i < len(stat):
            if stat[i] == 0:
                zeroCount += 1
            else:
                pos = i
            if zeroCount > neighbourStep:
                break
            i += direction
        return pos
    #将HTML拆分为若干份，统计每一份中p标签的数量
    def statistic(self, html, blockCount = 20):
        total = len(html)
        each = int(math.ceil(total / blockCount))
        stat = [0] * blockCount
        reParagraph = re.compile("</{0,1}p.*?>", re.IGNORECASE)
        links = reParagraph.finditer(html)
        for i in links:
            sec = i.start() / each
            stat[sec] += 1
        return stat


class NewsHelper:
    
    def __init__(self):
        self.repo = NewsRepository('repo.s3db')
        pass

    def fetch(self, url):
        opener = urllib.FancyURLopener()
        data = opener.open(url).read()
        return data
    
    def saveToDb(self, html):
        parser = HtmlContentParser()
        content = parser.getContent(html)
        content = filters.strip_tags(content)
        filters = FilterTag.FilterTag()
        title = parser.getTitle(html)
        self.repo.add(title, content)

class DiscuzAdapter:
    
    def addUser(self, username):
        params = urllib.urlencode({'username': username})
        url = 'http://localhost:9000/discuzAdapter/?r=WebService/AddUser'
        req = urllib2.Request(url, params)
        res = urllib2.urlopen(req)
        html = res.read()
        print html
    
    def addUserAvatar(self, username, url):
        params = urllib.urlencode({'username': username, 'url': url})
        url = 'http://localhost:9000/discuzAdapter/?r=WebService/AddUserAvatar'
        req = urllib2.Request(url, params)
        res = urllib2.urlopen(req)
        html = res.read()
        print html

        

class App:
    
    def __init__(self):
        self.NewsHelper = NewsHelper()
        self.discuz = DiscuzAdapter()
        pass
    
    def run(self):
        html = commonlang.TextFileHelper.read('item.html');
        soup = BeautifulSoup(html)
        tags = soup.find_all('div', class_='l_post')
        count = 1
        for tag in tags:
            user = self.getUser(tag)
            print "# POST"
            print user[0], user[1]
            print self.getContent(tag)
            if count == 1:
                self.discuz.addUser(user[0])
                self.discuz.addUserAvatar(user[0], user[1])
                break;
            count+=1
        pass

    def getUser(self, tag):
        tag = tag.find('div', class_ = 'd_author')
        tag = tag.find('img')
        ret = (tag['username'], tag['src'])
        return ret

    def getContent(self, tag):
        tag = tag.find('div', class_ = 'd_post_content')
        return tag

    def run1(self):
        html = commonlang.TextFileHelper.read('list.html');
        links = self.getLinks(html)
        for link in links:
            print link[0], link[1]
        pass

    def getLinks(self, html):
        links = re.findall('<a\s+.*?href="(/p/[^"]*?)"\s+.*?>(.*?)</a>', html);
        return links;
    
    def save(self):
        html = self.NewsHelper.fetch('http://news.qq.com/');
        commonlang.TextFileHelper.write('qqindex.html', html);
        
    def gethtml(self):
        html = commonlang.TextFileHelper.read('news1.html');
        return html

if __name__ == "__main__":
    app = App();
    app.run();
    
