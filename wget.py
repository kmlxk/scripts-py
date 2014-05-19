#!/usr/bin/env python
#wget program

import sys,urllib,httplib,urlparse

def reporthook(*progress_bar_info):
    show_progress_bar_inf=progress_bar_info
    block_numbers=show_progress_bar_inf[0]
    block_size=show_progress_bar_inf[1]
    file_total_size=show_progress_bar_inf[2]
    temp_file_total_size=block_numbers*block_size
    if temp_file_total_size>file_total_size:
        print "Download Successful!"
    else:
        print str(float(temp_file_total_size)/file_total_size*100)[0:5]+"%"


def check_file_exists(url):
    host,path=urlparse.urlsplit(url)[1:3]
    if ':' in host:
        host,port=host.split(':',1)
        try:
            port=int(port)
        except ValueError:
            print 'invalid port number %r' %(port,)
            sys.exit(1) 
    else:
         port=80

    connection=httplib.HTTPConnection(host,port)
    connection.request("HEAD",path)
    resp=connection.getresponse()
    return resp.status

if __name__=='__main__':
    for url in sys.argv[1:]:
        status=check_file_exists(url)
        i=url.rfind('/')
        file=url[i+1:]
        if status==404:
            print file,"not exist!"
            sys.exit(1)
        print url,"->",file
        urllib.urlretrieve(url,file,reporthook)