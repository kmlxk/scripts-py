# encoding: UTF-8

import sys,os
import getopt
import re


import logging
import logging.config
logging.config.fileConfig("codelines.log.conf")
logger = logging.getLogger("filelog")


"""
该脚本用于统计代码量
遍历指定目录下的代码文件类型，可排除引用的第三方库文件
Author: kmlxk0[at]gmail.com
"""


class ListHelper:

    @staticmethod
    def contains(li, item):
        pass
        

class App:

    """
    获得文件代码行数
    """
    def getCodelineCount(self, filepath):
        total=0
        fp = open(filepath,"r")
        for lines in fp:
            if(lines.split()):
                total+=1
        logger.debug(filepath + ": " + str(total))
        fp.close();
        return total
    """
    是否排除目录
    """
    def isExceptDir(self, exceptDirsStartwith, exceptDirsContains, dirpath):
        for item in exceptDirsStartwith:
            if dirpath.startswith(item):
                return True;
        for item in exceptDirsContains:
            if dirpath.find(item)>=0:
                return True;
        return False;

    """
    是否排除文件
    """
    def isExceptFile(self, exceptList, filename):
        for item in exceptList:
            if self.isMatchFile(item, filename):
                return True;
        return False;
        
    def isMatchFile(self, pattern, filename):
        pattern = re.compile(pattern);
        match = pattern.match(filename);
        return match != None;


    """
    统计项目代码行数
    """
    def statisticProject(self, baseDir):
        #baseDir=r'C:\wamp\www\mydns'
        #TODO: 有空把这些排除路径之类的做成参数化放入传入
        #如果路径为base+/lib则排除
        exceptDirsStartwith = [baseDir+'/PISWeb/lib', baseDir+'/PISWeb/bin', baseDir+r'PISWeb\js\foundation', baseDir+r'PISWeb\js\vendor'];
        #如果包含路径中包含.svn则排除
        exceptDirsContains = ['.svn'];
        #如果文件名匹配正则模式：排除
        exceptFiles = ['jquery(.*?)\.js','jquery(.*?)\.css','foundation(.*?)\.css','bootstrap(.*?)\.js'];
        
        exceptDirsStartwith = [item.replace('/', os.sep) for item in exceptDirsStartwith];
        lineCount=0
        fileCount=0
        for rootDir,dirs,files in os.walk(baseDir):
            # 排除目录
            if self.isExceptDir(exceptDirsStartwith, exceptDirsContains, rootDir):
                logger.debug("exceptDir: " + rootDir)
                continue;
            print '[.]parse dir:', rootDir
            for filename in files:
                # 排除文件
                if self.isExceptFile(exceptFiles, filename):
                    continue;
                ext=filename.split('.')
                ext=ext[-1]
                # 只统计指定的文件类型
                if(ext in ['php','css','js','html', 'cs', 'aspx']):
                    filepath = rootDir + os.sep + filename
                    fileCount += 1
                    lines = self.getCodelineCount(filepath)
                    lineCount += lines
                    print '[.]parse file:', filename, lines
        print 'Total Files: ', fileCount
        print 'Total Lines:', lineCount

    """
    帮助信息
    """
    def printHelp(self):
        print 'codeline.py'
        print '===Usage==='
        print 'python codeline.py -d path_of_the_project'
        print '-h,--help: print help message.'
        print '-d,--dirpath : directory of project'

    """
    程序入口main
    """
    def main(self, argv):
        try:
            opts, args = getopt.getopt(argv[1:], 'hd:', ['help', 'dirpath='])
        except getopt.GetoptError, err:
            print str(err)
            self.printHelp()
            sys.exit(2)
        for o, a in opts:
            if o in ('-h', '--help'):
                self.printHelp()
                sys.exit(1)
            elif o in ('-d', '--dirpath'):
                self.statisticProject(a)
                sys.exit(0)
            else:
                print 'unhandled option'
                sys.exit(3)
        self.printHelp()
        sys.exit(1)

if __name__ == '__main__':
    app = App()
    argv = sys.argv
    #这是方便调试用的
    #argv = ['F:\\cmdtools\\codelines.py', '-d', r'F:\workspace\vs2010\PISWeb']
    app.main(argv)
