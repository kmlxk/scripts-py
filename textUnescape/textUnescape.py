#coding:utf-8
#!/usr/bin/python
#indent=4

import sys,os
import getopt
import re

from xkutils import * 

class App:

    """
    帮助信息
    """
    def printHelp(self):
        print 'textUnescape.py'
        print '===Usage==='
        print 'python textUnescape.py -d 项目路径';
        print '-h,--help: 打印帮助';
        print '-d,--dirpath : 项目文件夹路径';
    
    def parseFile(self, filepath):
        raw = TextFileHelper.read(filepath);
        print 'parseFile', filepath
        encoding = TextFileHelper.getEncoding(raw)
        unicodeStr = TextFileHelper.getUnicode(raw);
        content = StringHelper.unescape(unicodeStr)
        TextFileHelper.write(filepath, content.encode(encoding) );

    def parseDir(self, dirpath):
        fileCount=0
        for rootDir,dirs,files in os.walk(dirpath):
            for filename in files:
                ext=filename.split('.')
                ext=ext[-1]
                # 只处理指定的文件类型
                if(ext in ['cs']):
                    filepath = rootDir + os.sep + filename
                    fileCount += 1
                    self.parseFile(filepath)
                    print '[.]parse file:', filename
        print 'Total Files: ', fileCount
        
    """
    程序入口main
    """
    def main(self, argv):
        try:
            opts, args = getopt.getopt(argv[1:], 'hd:', ['dirpath='])
        except getopt.GetoptError, err:
            print str(err)
            self.printHelp()
            sys.exit(2)
        for o, a in opts:
            if o in ('-h', '--help'):
                self.printHelp()
                sys.exit(1)
            elif o in ('-d', '--dirpath'):
                dirpath = a;
            else:
                print 'unhandled option'
                sys.exit(3)

        print dirpath
        self.parseDir(dirpath);

if __name__ == '__main__':
    app = App()
    argv = sys.argv
    #这是方便调试用的
    #argv = ['filename.py', '-d', r'K:\csharp\QQGroupMsgGrab\lib\CWebQQ1.2.24\src\CWebQQ1.2.24-src\CTool']
    app.main(argv)
