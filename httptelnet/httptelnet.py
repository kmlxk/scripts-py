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
import time
import math
import thread
import threading
import collections
import getopt
import types
import socket

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
        print '[get]:', url
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
        response = urllib2.urlopen(request, data=None, timeout=30)
        text = response.read()
        return text

def getDateTimeStr():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

class ComputerStatusThread(threading.Thread):

    def __init__(self, app, interval):
        self.httpclient = HttpClient()
        threading.Thread.__init__(self)
        self.app = app
        self.interval = interval
        self.isRunning = True
    
    def run(self):
        while self.isRunning:
            try:
                self.httpclient.get(self.app.url + '?r=computer/UpdateByName&name=httptelnet.'+self.app.uid+'&status=1&memo=' + str(self.app.runCount))
                time.sleep(self.interval)
            except:
                pass

    def stop(self):
        self.isrunning = False


class App:

    def __init__(self):
        self.runCount = 0
        self.httpclient = HttpClient()

    """
    帮助信息
    """
    def printHelp(self):
        print 'httptelnet.py'
        print '===Usage==='
        print 'python httptelnet.py -l http://www.portso.com.cn/apps/deDaemon.php -u userid'
        print '-h,--help: print help message.'
        print '-l,--listen: 服务接口地址'
        print '-u,--uid: 用户id'

    def loadParameters(self, argv):
        self.uid = 'auto'
        try:
            opts, args = getopt.getopt(argv[1:], 'hl:u:', ['help', 'listen=', 'uid='])
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
            elif key in ('-u', '--uid'):
                self.uid = value
            else:
                print 'unhandled option'
                sys.exit(3)
        if self.uid == 'auto':
            self.uid = socket.gethostname()
        print 'startup httptelnet server...  uid:', self.uid

    def run(self):
        while True:
            try:
                self.runCount = self.runCount + 1
                strJson = self.httpclient.get(self.url + '?r=comet/subscribe&names=httptelnet.'+self.uid+'.cmd')
                obj = json.loads(strJson)
                if type(obj) is types.DictType and obj.has_key('success') and obj['success'] == True: 
                    if obj['data']['status'] == 1:
                        for k in obj['data']['events']:
                            cmd = obj['data']['events'][k]
                            print '[cmd]', cmd
                            lines = os.popen(cmd).readlines()
                            # ret = os.system(cmd)
                            post = ''.join(lines)
                            post = post.decode('gbk')
                            self.httpclient.post(self.url + '?r=comet/publish&name=httptelnet.'+self.uid+'.ret', urllib.urlencode({'memo':post}))
            except:
                pass

if __name__ == '__main__':
    app = App()
    argv = sys.argv
    #这是方便调试用的
    argv = ['filename.py', '-l', r'http://www.portso.com.cn/apps/deDaemon.php']
    app.loadParameters(argv)
    computerStatusThread = ComputerStatusThread(app, 300)
    computerStatusThread.start()
    app.run()
