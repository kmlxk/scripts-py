#!/bin/sh -
#coding: utf8
"exec" "python" "-O" "$0" "$@"

__doc__ = """Tiny HTTP Proxy.

This module implements GET, HEAD, POST, PUT and DELETE methods
on BaseHTTPServer, and behaves as an HTTP proxy.  The CONNECT
method is also implemented experimentally, but has not been
tested yet.

Any help will be greatly appreciated.        SUZUKI Hisao

TinyHttpPoxy是一個簡單的Http代理程式，但是有一個不足的地方是不支持二級代理，
文章http://www.cnblogs.com/lexus/archive/2013/01/08/2851565.html中提到的代码支持带验证的二级代理

但是没法支持带验证信息的代理，
于是在HTTP请求中增加了用户名密码信息，发送到一级代理即可
根据同样的方法，HTTPS二级代理也是类似，
一增加的步骤是在CONNECT阶段增加用户名密码信息，发送到一级代理即可
Author: kmlxk0[at]gmail.com

"""

__version__ = "0.2.1"

import sys, os
import BaseHTTPServer, select, socket, SocketServer, urlparse
import base64
import getopt

class ProxyHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    __base = BaseHTTPServer.BaseHTTPRequestHandler
    __base_handle = __base.handle

    server_version = "TinyHTTPProxy/" + __version__
    rbufsize = 0                        # self.rfile Be unbuffered

    def handle(self):
        (ip, port) =  self.client_address
        if hasattr(self, 'allowed_clients') and ip not in self.allowed_clients:
            self.raw_requestline = self.rfile.readline()
            if self.parse_request(): self.send_error(403)
        else:
            self.__base_handle()

    def _connect_to(self, netloc, soc):
        i = netloc.find(':')
        if i >= 0:
            host_port = netloc[:i], int(netloc[i+1:])
        else:
            host_port = netloc, 80
        print "[.]soc.connect %s:%d" % host_port
        try: soc.connect(host_port)
        except socket.error, arg:
            try: msg = arg[1]
            except: msg = arg
            self.send_error(404, msg)
            return 0
        return 1

    def do_CONNECT(self):
        # 对于HTTPS的二级代理, 客户端发送CONNECT指令到TinyHTTPProxy
        # TinyHTTPProxy转发携带了用户名密码的CONNECT指令到一级代理服务器
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print '[.]self._connect_to ' , self.path
            if self._connect_to(app.proxy_host_port, soc):
                print '[v]self._connect_to ' , self.path, soc.getpeername()
                self.log_request(200)
                soc.send(self.raw_requestline)
                self.headers['Proxy-Authorization'] = app.header_authorization
                self.headers['Connection'] = 'close'
                for key_val in self.headers.items():
                    soc.send("%s: %s\r\n" % key_val)
                soc.send("\r\n")
                self._read_write(soc)
        finally:
            print "[v]Socket.closed"
            soc.close()
            self.connection.close()

    def do_GET(self):
        (scm, netloc, path, params, query, fragment) = urlparse.urlparse(
            self.path, 'http')
        print "[.]CMD:", self.raw_requestline
        if scm != 'http' or fragment or not netloc:
            self.send_error(400, "bad url %s" % self.path)
            return
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fid = None
        try:
            if self._connect_to(app.proxy_host_port, soc):
                self.log_request()
                getStr = "%s %s %s\r\n" % (
                    self.command,
                    urlparse.urlunparse((scm, netloc, path, params, query, '')),
                    self.request_version)
                soc.send(getStr)
                self.headers['Proxy-Authorization'] = app.header_authorization
                self.headers['Connection'] = 'close'
                del self.headers['Proxy-Connection']
                for key_val in self.headers.items():
                    # print "%s: %s" % key_val # debug
                    soc.send("%s: %s\r\n" % key_val)
                soc.send("\r\n")
                self._read_write(soc)
        finally:
            print "[v]Socket.closed"
            soc.close()
            self.connection.close()

    def _read_write(self, soc, max_idling=20):
        print '[.]_read_write' , soc.getpeername()
        print '[ ]self.connection' , self.connection.getpeername()
        iw = [self.connection, soc]
        ow = []
        count = 0
        while 1:
            count += 1
            # select函数的参数是3个列表，包含整数文件描述符，或者带有可返回文件描述符的fileno()方法对象。
            # 在Windows下，它只能用于sockets
            # 第一个参数是需要等待输入的对象，第二个指定等待输出的对象，
            # 第三个参数指定异常情况的对象。第四个参数则为设置超时时间，是一个浮点数。指定以秒为单位的超时值。
            # select函数将会返回一组文件描述符，包括输入，输出以及异常
            (ins, _, exs) = select.select(iw, ow, iw, 3)
            if exs: break 
            if ins:
                for i in ins:
                    # 根据可读的socket确定输出的socket
                    if i is soc:
                        out = self.connection
                        sys.stdout.write("<-")#server->client
                        sys.stdout.flush()
                    else:
                        out = soc
                        sys.stdout.write("->")#client->server
                        sys.stdout.flush()
                    data = i.recv(8192)
                    if data:
                        out.send(data)
                        #print '[v]Recv&Send:', data # debug
                        count = 0
            else:
                print "[v]Idle", count
            if count == max_idling: break

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT  = do_GET
    do_DELETE=do_GET

class ThreadingHTTPServer (SocketServer.ThreadingMixIn,
                           BaseHTTPServer.HTTPServer): pass

class App:
    """
    帮助信息
    """
    def printHelp(self):
        print 'TinyHTTPProxy.py'
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
        port = 8000
        try:
            opts, args = getopt.getopt(argv[1:], 'hl:s:a:', ['help', 'listen=', 'server=', 'auth='])
        except getopt.GetoptError, err:
            print str(err)
            self.printHelp()
            sys.exit(2)
        for o, a in opts:
            if o in ('-h', '--help'):
                self.printHelp()
                sys.exit(1)
            elif o in ('-s', '--server'):
                self.proxy_host_port = a
            elif o in ('-a', '--auth'):
                self.proxy_user_password = a
            elif o in ('-l', '--listen'):
                port = int(a)
            else:
                print 'unhandled option'
                sys.exit(3)
        self.header_authorization = 'Basic ' + base64.encodestring(self.proxy_user_password);
        self.header_authorization = self.header_authorization.replace('\n','').replace('\r','');
        
        sys.argv = ['filename.py', port]
        BaseHTTPServer.test(ProxyHandler, ThreadingHTTPServer)

if __name__ == '__main__':
    app = App()
    argv = sys.argv
    #这是方便调试用的
    #argv = ['filename.py', '-l', '8020', '-s', r'host:password', '-a', r'domain\username:password']
    app.main(argv)
