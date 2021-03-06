#!/usr/bin/env python
#coding=utf-8
# -*- coding: utf-8 -*-
#
# 抓取百度贴吧的帖子，导入到discuz论坛中
#

# system
import os
import sys
import getopt
import re

# misc
import json
import time
import types
import urllib
import urllib2
import codecs

import chardet

# html
from bs4 import BeautifulSoup

# customed
import commonlang
import FilterTag
import DiscuzAdapter
import HtmlContentParser

# logging
import logging
import logging.config
logging.config.fileConfig("BaoshanNews.log.conf")
logger = logging.getLogger("filelog")

reload(sys)
sys.setdefaultencoding( "utf-8" )

__author__="kmlxk@163.com"
__date__ ="$2014-7-18 13:48:13$"

def gb2utf8(s):
    return s.encode('utf-8')
    # print s, chardet.detect(s)
    # return s.encode('utf-8')

class BaoshanNews:
    
    def __init__(self, adapterUrl):
        self.discuz = DiscuzAdapter.DiscuzAdapter(adapterUrl, logger)
        self.tagfilter = FilterTag.FilterTag()
        self.htmlParser = HtmlContentParser.HtmlContentParser()
        self.maxNewsCount = 50
    
    # 处理首页
    def parseList(self, url, excludekey, fid):
        html = commonlang.TextFileHelper.read('baoshannews-list.html');
        print 'get list'
        #html = commonlang.HttpHelper.get(url)
        links = self.getLinks(html)
        count = 0
        excludekeys = excludekey.split('|')
        for link in links:
            count += 1
            if count > self.maxNewsCount:
                break
            url = link[0]
            title = link[1]
            dates = re.findall('/(\d{4}\/\d{1,2}\/\d{1,2})/', url);
            date = dates[0]
            date = date.replace('/', '-')
            logger.debug(title)
            isExclude = False
            for ex in excludekeys:
                if title.find(ex) >= 0:
                    isExclude = True
                    break
            if isExclude:
                continue
            print 'get news: ', title.decode('utf-8')
            content = commonlang.HttpHelper.get(url)
            print 'parse news'
            self.parseNews(title, content, date, fid)

    def parseNews(self, title, html, date, fid):
        soup = BeautifulSoup(html, from_encoding='gbk')
        content = soup.find_all('div', class_='content')
        bbcode = self.toBBCode(unicode(content[0]))
        bbcode = self.tagfilter.strip_tags(bbcode)
        content = bbcode
        ret = self.discuz.addThread({'fid': fid, 'username': 'admin', 'title': title, 'created':date, 'content': content})
        logger.debug("addThread: " + ret)

    def getLinks(self, html):
        soup = BeautifulSoup(html, from_encoding='gbk')
        tags = soup.find_all('ul', class_='list-all')
        ret = []
        for tag in tags:
            links = tag.find_all('a')
            for link in links:
                ret.append((link.get('href'), link.string))
        return ret;

    def toBBCode(self, html):
        re1 = re.compile('<img[^>]*?src="(.*?)"[^>]*?>', re.IGNORECASE)
        result, number = re1.subn(lambda x:'\n[img]http://bbs.com/remoteimg.php?url='+x.group(1)+'[/img]\n', html)
        return result

class App:

    """
    帮助信息
    """
    def printHelp(self):
        print 'scripts-py.discuzbuild.BaoshanNews.py'
        print '=== 百度新闻抓取 ==='
        print '=== Usage ==='
        print 'python BaoshanNews.py -d 项目路径';
        print '-h,--help: 打印帮助';
        print '-d,--dirpath : 项目文件夹路径';
            
    """
    程序入口main
    """
    def main(self, argv):
        # 处理参数
        try:
            opts, args = getopt.getopt(argv[1:], 'ha:e:', ['help', 'adapterurl=', 'url=', 'excludekey=', 'fid='])
        except getopt.GetoptError, err:
            print str(err)
            self.printHelp()
            sys.exit(2)
        # 根据参数执行
        excludekey = ''
        for k, v in opts:
            if k in ('-h', '--help'):
                self.printHelp()
                sys.exit(1)
            elif k in ('-a', '--adapterurl'):
                adapterUrl = v;
            elif k in ('--url'):
                url = v;
            elif k in ('-e', '--excludekey'):
                excludekey = v;
            elif k in ('--fid'):
                fid = v;
            else:
                print 'unhandled option'
                sys.exit(3)

        contentFetcher = BaoshanNews(adapterUrl)
        print contentFetcher.parseList(url, excludekey, fid)

def main():
    app = App()
    argv = sys.argv
    #这是方便调试用的
    argv = ['filename.py', '-a', r'http://bbs.com/discuzadapter', '--url', 'http://www.baoshan.cn/561/more/605/more605.htm', '-e', '吧规|广告', '--fid', '2']
    app.main(argv)

if __name__ == '__main__':
    main()


