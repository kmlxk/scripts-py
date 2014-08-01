import re
import urllib
import urllib2

def gb2utf8(s):
    return s.encode('utf-8')
    # print s, chardet.detect(s)
    # return s.encode('utf-8')

class DiscuzAdapter:
    
    def __init__(self, baseurl, logger):
        self.baseurl = baseurl
        self.logger = logger

    def httppost(self, url, data):
        params = urllib.urlencode(data)
        html = ''
        try:
            self.logger.debug('post: ' + url + ', ' + params)
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
