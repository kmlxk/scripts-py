#!/usr/bin/env python
# encoding: UTF-8

import getopt
import logging
import logging.config
import urllib
import thread
import sys
import os

logging.config.fileConfig( os.path.dirname(sys.argv[0]) + "\\datacente-dns.log.conf")
logger = logging.getLogger("filelog")

from threading import Timer
import threading
import time

import datetime

class App:
    computerName = 'e6440';
    interval = 2
    #serverUrl = 'http://220.165.250.133:2195/datacenter/public/index.php';
    serverUrl = 'http://www.dev91.ml/datacenter/public/index.php';
    timer = None

    """
    帮助信息
    """
    def printHelp(self):
        print 'dnsdatacenter.py'
        print '===Usage==='
        print 'python dnsdatacenter.py -s server_url'
        print '-h,--help: print help message.'
        print '-s,--server : server url'

    def updateIp(self):
        ret = None
        try:
            params = urllib.urlencode({'key': 'pim.equips.'+self.computerName+'.ip', 'value': '{$ip}'})
            f = urllib.urlopen(self.serverUrl+'?r=appapi/kv/set', params)
            ret = f.read()
            logger.debug("updateIp: " + ret)
            # 获得当前时间
            now = datetime.datetime.now() # ->这是时间数组格式
            # 转换为指定的格式:
            strDatetime = now.strftime("%Y-%m-%d %H:%M:%S")
            print "["+strDatetime+"] updateIp: " + ret
            self.timer = threading.Timer(self.interval, self.updateIp)
            self.timer.start() 
        except Exception, e:   
            logger.error(e)
        return ret

    def startTimer(self):
        logger.debug("startTimer: " + str(self.interval))
        self.timer = threading.Timer(self.interval, self.updateIp)
        self.timer.start() 

    """
    程序入口main
    """
    def main(self, argv):
        try:
            opts, args = getopt.getopt(argv[1:], 'hn:i:s:', ['help', 'name=', 'interval=', 'server='])
        except getopt.GetoptError, err:
            print str(err)
            self.printHelp()
            sys.exit(2)
        for key, value in opts:
            if key in ('-h', '--help'):
                self.printHelp()
                sys.exit(1)
            elif key in ('-s', '--server'):
                self.serverUrl = value;
            elif key in ('-n', '--name'):
                self.computerName = value;
            elif key in ('-i', '--interval'):
                self.interval = int(value);
            else:
                print 'unhandled option ' + key + '=' + value
        self.startTimer();


if __name__ == '__main__':
    app = App()
    argv = sys.argv
    #这是方便调试用的
    #argv = ['dns_datacenter.py', '-s', r'http://220.165.250.133:2195/datacenter/public/index.php']
    app.main(argv)
