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
logging.config.fileConfig("baidunews.log.conf")
logger = logging.getLogger("filelog")

reload(sys)
sys.setdefaultencoding( "utf-8" )

__author__="kmlxk@163.com"
__date__ ="$2014-7-18 13:48:13$"

def gb2utf8(s):
    return s.encode('utf-8')
    # print s, chardet.detect(s)
    # return s.encode('utf-8')

class BaiduNews:
    
    def __init__(self, adapterUrl):
        self.discuz = DiscuzAdapter.DiscuzAdapter(adapterUrl, logger)
        self.tagfilter = FilterTag.FilterTag()
        self.htmlParser = HtmlContentParser.HtmlContentParser()
    
    # 处理首页
    def parseList(self, keyword, excludekey, fid):
        #html = commonlang.TextFileHelper.read('list.html');
        print 'get list'
        url = 'http://news.baidu.com/ns?word=%B1%A3%C9%BD&tn=news&from=news&cl=2&rn=20&ct=1' 
        #保山学院
        html = commonlang.HttpHelper.get(url)
        links = self.getLinks(html)
        excludekeys = excludekey.split('|')
        for link in links:
            url = link[0]
            title = link[1]
            title = self.tagfilter.strip_tags(title)
            isExclude = False
            for ex in excludekeys:
                if title.find(ex) >= 0:
                    isExclude = True
                    break
            if isExclude:
                continue
            print 'get news: ', title
            content = commonlang.HttpHelper.get(url)
            print 'parse news'
            self.parseNews(title, content, fid)
            return

    def parseNews(self, title, html, fid):
        content = self.htmlParser.getContent(html)
        content = self.tagfilter.strip_tags(content)
        print title.decode('utf-8')
        print content.decode('utf-8')
        return
        #html = commonlang.TextFileHelper.read('item.html');
        soup = BeautifulSoup(html)
        print soup.originalEncoding
        tags = soup.find_all('div', class_='l_post')
        count = 1
        for tag in tags:
            user = self.getUser(tag)
            print " #Post " + str(count) 
            title = self.getTitle(soup)
            content = self.getContent(tag)
            content = content.decode('utf-8')
            username = user[0]
            datafield = tag['data-field']
            created = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}', str(datafield));
            created = created[0] + ':00'
            bbcode = self.discuz.toBBCode(content)
            bbcode = self.tagfilter.strip_tags(bbcode)
            content = bbcode
            if count == 1:
                ret = self.discuz.addUser(gb2utf8(username))
                logger.debug(ret)
                if user[1].find('head_80.jpg') < 0:
                    ret = self.discuz.addUserAvatar(gb2utf8(username), user[1])
                    logger.debug(ret)
                ret = self.discuz.addThread({'fid': fid, 'username': username.encode('utf-8'), 'title': title.encode('utf-8'), 'created':created, 'content': content.encode('utf-8')})
                logger.debug("addThread: " + ret)
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
                ret = self.discuz.addPost({'threadid': threadId, 'username': username.encode('utf-8'), 'created':created, 'content': content.encode('utf-8')})
                logger.debug(ret)
            count+=1
        pass

    def getUser(self, tag):
        tag = tag.find('div', class_ = 'd_author')
        tag = tag.find('img')
        ret = (str(tag['username']), str(tag['src']))
        #ret = (tag['username'], tag['src'])
        return ret

    def getContent(self, tag):
        content = tag.find('div', class_ = 'd_post_content')
        return str(content)

    def getTitle(self, soap):
        tag = soap.find('h1', class_ = 'core_title_txt')
        return str(''.join(tag.stripped_strings))

    def getLinks(self, html):
        links = re.findall('<h3\s+class="c-title"><a\s+href="([^"]*?)"[^>]*?>(.*?)</a>', html);
        return links;
    
    def save(self):
        html = commonlang.HttpHelper.get('http://news.qq.com/');
        commonlang.TextFileHelper.write('qqindex.html', html);
        
    def gethtml(self):
        html = commonlang.TextFileHelper.read('news1.html');
        return html

class App:

    """
    帮助信息
    """
    def printHelp(self):
        print 'scripts-py.discuzbuild.tieba.py'
        print '=== 百度贴吧帖子抓取 ==='
        print '=== Usage ==='
        print 'python tieba.py -d 项目路径';
        print '-h,--help: 打印帮助';
        print '-d,--dirpath : 项目文件夹路径';
            
    """
    程序入口main
    """
    def main(self, argv):
        # 处理参数
        try:
            opts, args = getopt.getopt(argv[1:], 'ha:k:e:', ['help', 'adapterurl=', 'keyword=', 'excludekey=', 'fid='])
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
            elif k in ('-k', '--keyword'):
                keyword = v;
            elif k in ('-e', '--excludekey'):
                excludekey = v;
            elif k in ('--fid'):
                fid = v;
            else:
                print 'unhandled option'
                sys.exit(3)

        contentFetcher = BaiduNews(adapterUrl)
        print contentFetcher.parseList(keyword, excludekey, fid)

def main():
    app = App()
    argv = sys.argv
    #这是方便调试用的
    argv = ['filename.py', '-a', r'http://bbs.com/discuzadapter', '-k', '保山', '-e', '吧规|广告', '--fid', '38']
    app.main(argv)

if __name__ == '__main__':
    main()


