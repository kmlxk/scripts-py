#!/usr/bin/env python
#coding=gbk
# -*- coding: gbk -*-
#
# 抓取百度贴吧的帖子，导入到discuz论坛中
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

import logging
import logging.config
logging.config.fileConfig("getthread.log.conf")
logger = logging.getLogger("filelog")


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
        filters = FilterTag.FilterTag()
        content = filters.strip_tags(content)
        title = parser.getTitle(html)
        self.repo.add(title, content)

class DiscuzAdapter:

    def httppost(self, url, data):
        params = urllib.urlencode(data)
        html = ''
        try:
            req = urllib2.Request(url, params)
            res = urllib2.urlopen(req)
            html = res.read()
        except Exception, ex:
            print Exception,":httppost:",ex
        return html
    
    def addUser(self, username):
        params = {'username': username}
        url = 'http://localhost:9000/discuzAdapter/?r=WebService/addUser'
        return self.httppost(url, params)
    
    def addUserAvatar(self, username, url):
        params = {'username': username, 'url': url}
        url = 'http://localhost:9000/discuzAdapter/?r=WebService/addUserAvatar'
        return self.httppost(url, params)

    
    def addThread(self, dictData):
        params = dictData
        url = 'http://localhost:9000/discuzAdapter/?r=WebService/addThread'
        return self.httppost(url, params)

    def addPost(self, dictData):
        params = dictData
        url = 'http://localhost:9000/discuzAdapter/?r=WebService/addPost'
        return self.httppost(url, params)

    def toBBCode(self, html):
        re1 = re.compile('<img[^>]*?src="(.*?)"[^>]*?>', re.IGNORECASE)
        result, number = re1.subn(lambda x:'\n[img]http://localhost:9000/discuz/remoteimg.php?url='+x.group(1)+'[/img]\n', html)
        return result

class App:
    
    def __init__(self):
        self.newsHelper = NewsHelper()
        self.discuz = DiscuzAdapter()
        self.tagfilter = FilterTag.FilterTag()

    def run(self):
        #html = commonlang.TextFileHelper.read('list.html');
        url = 'http://tieba.baidu.com/f?kw=%B1%A3%C9%BD%D1%A7%D4%BA' 
        #保山学院
        html = self.newsHelper.fetch(url)
        links = self.getLinks(html)
        for link in links:
            print link[0], link[1]
            url = 'http://tieba.baidu.com/' + link[0]
            content = self.newsHelper.fetch(url)
            fid = 36
            self.parseThread(content, fid)

    def parseThread(self, html, fid):
        #html = commonlang.TextFileHelper.read('item.html');
        soup = BeautifulSoup(html)
        tags = soup.find_all('div', class_='l_post')
        count = 1
        for tag in tags:
            user = self.getUser(tag)
            print "# POST " , count
            title = self.getTitle(soup)
            content = self.getContent(tag)
            datafield = tag['data-field']
            created = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}', str(datafield));
            created = created[0] + ':00'
            bbcode = self.discuz.toBBCode(content)
            bbcode = self.tagfilter.strip_tags(bbcode)
            content = bbcode
            if count == 1:
                ret = self.discuz.addUser(user[0])
                logger.debug(ret)
                if user[1].find('head_80.jpg') < 0:
                    ret = self.discuz.addUserAvatar(user[0], user[1])
                    logger.debug(ret)
                ret = self.discuz.addThread({'fid': fid, 'username': user[0], 'title': title, 'created':created, 'content': content})
                logger.debug(ret)
                obj = json.loads(ret)
                if obj['success']:
                    threadId = obj['data']['tid']
                else:
                    break;
            else:
                ret = self.discuz.addUser(user[0])
                logger.debug(ret)
                if user[1].find('head_80.jpg') < 0:
                    ret = self.discuz.addUserAvatar(user[0], user[1])
                    logger.debug(ret)
                ret = self.discuz.addPost({'threadid': threadId, 'username': user[0], 'created':created, 'content': content})
                logger.debug(ret)
            count+=1
        pass

    def getUser(self, tag):
        tag = tag.find('div', class_ = 'd_author')
        tag = tag.find('img')
        ret = (str(tag['username']), str(tag['src']))
        return ret

    def getContent(self, tag):
        content = tag.find('div', class_ = 'd_post_content')
        return str(content)

    def getTitle(self, soap):
        tag = soap.find('h1', class_ = 'core_title_txt')
        return str(''.join(tag.stripped_strings))

    def getLinks(self, html):
        links = re.findall('<a\s+.*?href="(/p/[^"]*?)"\s+.*?>(.*?)</a>', html);
        return links;
    
    def save(self):
        html = self.newsHelper.fetch('http://news.qq.com/');
        commonlang.TextFileHelper.write('qqindex.html', html);
        
    def gethtml(self):
        html = commonlang.TextFileHelper.read('news1.html');
        return html

if __name__ == "__main__":
    app = App();
    app.run();
    
