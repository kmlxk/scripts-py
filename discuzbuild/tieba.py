#!/usr/bin/env python
#coding=gbk
# -*- coding: gbk -*-
#
# ץȡ�ٶ����ɵ����ӣ����뵽discuz��̳��
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
import math

import chardet

# html
from bs4 import BeautifulSoup

# customed
import commonlang
import FilterTag

# logging
import logging
import logging.config
logging.config.fileConfig("tieba.log.conf")
logger = logging.getLogger("filelog")

reload(sys)
sys.setdefaultencoding( "gbk" )

# �����Ǹ��ܾ��������
# console codec: gbk
# log codec: title.encode('utf-8')

__author__="kmlxk@163.com"
__date__ ="$2014-7-18 13:48:13$"

def gb2utf8(s):
    return s.encode('utf-8')
    # print s, chardet.detect(s)
    # return s.encode('utf-8')

class DiscuzAdapter:
    
    def __init__(self, baseurl):
        self.baseurl = baseurl;
        pass

    def httppost(self, url, data):
        params = urllib.urlencode(data)
        html = ''
        try:
            logger.debug('post: ' + url + ', ' + params)
            req = urllib2.Request(url, params)
            # req.add_header("Content-Type", "text/html; charset=utf-8")
            res = urllib2.urlopen(req)
            html = res.read()
        except Exception, ex:
            print Exception,":httppost:",ex
        return html
    
    def addUser(self, username):
        params = {'username': gb2utf8(username)}
        url = self.baseurl + '/index.php?r=WebService/addUser'
        return self.httppost(url, params)
    
    def addUserAvatar(self, username, url):
        params = {'username': gb2utf8(username), 'url': url}
        url = self.baseurl + '/index.php?r=WebService/addUserAvatar'
        return self.httppost(url, params)
    
    def addThread(self, dictData):
        params = dictData
        url = self.baseurl + '/index.php?r=WebService/addThread'
        return self.httppost(url, params)

    def addPost(self, dictData):
        params = dictData
        url = self.baseurl + '/index.php?r=WebService/addPost'
        return self.httppost(url, params)

    def toBBCode(self, html):
        re1 = re.compile('<img[^>]*?src="(.*?)"[^>]*?>', re.IGNORECASE)
        result, number = re1.subn(lambda x:'\n[img]http://bbs.com/remoteimg.php?url='+x.group(1)+'[/img]\n', html)
        return result

class Tieba:
    
    def __init__(self, adapterUrl):
        self.discuz = DiscuzAdapter(adapterUrl)
        self.tagfilter = FilterTag.FilterTag()
    
    # ������ҳ
    def parseList(self, keyword, excludekey, fid):
        #html = commonlang.TextFileHelper.read('list.html');
        print 'get list'
        url = 'http://tieba.baidu.com/f?kw=%B1%A3%C9%BD%D1%A7%D4%BA' 
        #��ɽѧԺ
        html = commonlang.HttpHelper.get(url)
        links = self.getLinks(html)
        excludekeys = excludekey.split('|')
        for link in links:
            title = link[2]
            isExclude = False
            for ex in excludekeys:
                if title.find(ex) >= 0:
                    isExclude = True
                    break
            if isExclude:
                continue
            print 'get thread: ', title
            url = 'http://tieba.baidu.com/' + link[1]
            content = commonlang.HttpHelper.get(url)
            print 'parse thread'
            self.parseThread(content, fid)

    def parseThread(self, html, fid):
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
                ret = self.discuz.addUser(user[0])
                logger.debug(ret)
                if user[1].find('head_80.jpg') < 0:
                    ret = self.discuz.addUserAvatar(user[0], user[1])
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
        links = re.findall('<div class="([^"]+)">[^<]*<a\s+.*?href="(/p/[^"]*?)".*?>(.*?)</a>', html);
        return links;
    
    def save(self):
        html = commonlang.HttpHelper.get('http://news.qq.com/');
        commonlang.TextFileHelper.write('qqindex.html', html);
        
    def gethtml(self):
        html = commonlang.TextFileHelper.read('news1.html');
        return html

class App:

    """
    ������Ϣ
    """
    def printHelp(self):
        print 'scripts-py.discuzbuild.tieba.py'
        print '=== �ٶ���������ץȡ ==='
        print '=== Usage ==='
        print 'python tieba.py -d ��Ŀ·��';
        print '-h,--help: ��ӡ����';
        print '-d,--dirpath : ��Ŀ�ļ���·��';
            
    """
    �������main
    """
    def main(self, argv):
        # �������
        try:
            opts, args = getopt.getopt(argv[1:], 'ha:k:e:', ['help', 'adapterurl=', 'keyword=', 'excludekey=', 'fid='])
        except getopt.GetoptError, err:
            print str(err)
            self.printHelp()
            sys.exit(2)
        # ���ݲ���ִ��
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

        tieba = Tieba(adapterUrl)
        print tieba.parseList(keyword, excludekey, fid)

def main():
    app = App()
    argv = sys.argv
    #���Ƿ�������õ�
    argv = ['filename.py', '-a', r'http://bbs.com/discuzAdapter', '-k', '��ɽ', '-e', '�ɹ�|���', '--fid', '38']
    app.main(argv)

if __name__ == '__main__':
    main()
