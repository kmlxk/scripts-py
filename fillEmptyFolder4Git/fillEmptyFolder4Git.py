# encoding: UTF-8

import sys,os
import getopt
import re

import logging
import logging.config
#logging.config.fileConfig("logging.conf")
#logger = logging.getLogger("filelog")
#logger.debug(filepath + ": " + str(total))

"""
这个脚本用于处理“git中怎么提交空文件夹”的问题
在git中的空文件夹不能纳入版本管理，checkout时空文件夹也不能同步创建。
因此此脚本通过在空文件夹下面创建index.html的方法，强制让git把空文件夹纳入版本管理。
"""

class EmptyFolderFiller:
    filename = 'index.html'

    #检查文件夹是否空
    def isFolderEmpty(self, path):
        list = os.listdir(path)#列出目录下的所有文件和目录
        return len(list) == 0;

    #填充空文件夹
    def fillFolder(self, path):
        list = os.listdir(path)#列出目录下的所有文件和目录
        for line in list:
            filepath = os.path.join(path, line)
            if os.path.isdir(filepath):
                if self.isFolderEmpty(filepath):
                    print 'create '+self.filename+' in', filepath;
                    self.writeTextFile(os.path.join(filepath, self.filename), '');
                #如果filepath是目录，则再列出该目录下的所有文件
                self.fillFolder(filepath);

    #写入文本文件
    def writeTextFile(self, filepath, content):
        f=open(filepath,'w');
        f.write(content)
        f.close()

class App:

    """
    帮助信息
    """
    def printHelp(self):
        print 'fillEmptyFolder4Git.py'
        print '===Usage==='
        print 'python fillEmptyFolder4Git.py -d 项目路径';
        print '-h,--help: 打印帮助';
        print '-d,--dirpath : 项目文件夹路径';
            
    """
    程序入口main
    """
    def main(self, argv):
        # 处理参数
        try:
            opts, args = getopt.getopt(argv[1:], 'hd:f:', ['dirpath=', 'help', 'filename='])
        except getopt.GetoptError, err:
            print str(err)
            self.printHelp()
            sys.exit(2)
        # 根据参数执行
        filler = EmptyFolderFiller()
        for o, a in opts:
            if o in ('-h', '--help'):
                self.printHelp()
                sys.exit(1)
            elif o in ('-d', '--dirpath'):
                dirpath = a;
            elif o in ('-f', '--filename'):
                filename = a;
                filler.filename = filename;
            else:
                print 'unhandled option'
                sys.exit(3)

        print dirpath
        filler.fillFolder(dirpath);

if __name__ == '__main__':
    app = App()
    argv = sys.argv
    #这是方便调试用的
    #argv = ['filename.py', '-d', r'F:\apmxe\htdocs\kmcfinet\extapp\overrides', '-f', 'readme.md']
    app.main(argv)

