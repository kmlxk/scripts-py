# encoding: UTF-8

import sys,os
import getopt
import re


import logging
import logging.config
logging.config.fileConfig("codelines.log.conf")
logger = logging.getLogger("filelog")


"""
�ýű�����ͳ�ƴ�����
����ָ��Ŀ¼�µĴ����ļ����ͣ����ų����õĵ��������ļ�
Author: kmlxk0[at]gmail.com
"""


class ListHelper:

    @staticmethod
    def contains(li, item):
        pass
        

class App:

    """
    ����ļ���������
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
    �Ƿ��ų�Ŀ¼
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
    �Ƿ��ų��ļ�
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
    ͳ����Ŀ��������
    """
    def statisticProject(self, baseDir):
        #baseDir=r'C:\wamp\www\mydns'
        #TODO: �пհ���Щ�ų�·��֮������ɲ��������봫��
        #���·��Ϊbase+/lib���ų�
        exceptDirsStartwith = [baseDir+'/PISWeb/lib', baseDir+'/PISWeb/bin', baseDir+r'PISWeb\js\foundation', baseDir+r'PISWeb\js\vendor'];
        #�������·���а���.svn���ų�
        exceptDirsContains = ['.svn'];
        #����ļ���ƥ������ģʽ���ų�
        exceptFiles = ['jquery(.*?)\.js','jquery(.*?)\.css','foundation(.*?)\.css','bootstrap(.*?)\.js'];
        
        exceptDirsStartwith = [item.replace('/', os.sep) for item in exceptDirsStartwith];
        lineCount=0
        fileCount=0
        for rootDir,dirs,files in os.walk(baseDir):
            # �ų�Ŀ¼
            if self.isExceptDir(exceptDirsStartwith, exceptDirsContains, rootDir):
                logger.debug("exceptDir: " + rootDir)
                continue;
            print '[.]parse dir:', rootDir
            for filename in files:
                # �ų��ļ�
                if self.isExceptFile(exceptFiles, filename):
                    continue;
                ext=filename.split('.')
                ext=ext[-1]
                # ֻͳ��ָ�����ļ�����
                if(ext in ['php','css','js','html', 'cs', 'aspx']):
                    filepath = rootDir + os.sep + filename
                    fileCount += 1
                    lines = self.getCodelineCount(filepath)
                    lineCount += lines
                    print '[.]parse file:', filename, lines
        print 'Total Files: ', fileCount
        print 'Total Lines:', lineCount

    """
    ������Ϣ
    """
    def printHelp(self):
        print 'codeline.py'
        print '===Usage==='
        print 'python codeline.py -d path_of_the_project'
        print '-h,--help: print help message.'
        print '-d,--dirpath : directory of project'

    """
    �������main
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
    #���Ƿ�������õ�
    #argv = ['F:\\cmdtools\\codelines.py', '-d', r'F:\workspace\vs2010\PISWeb']
    app.main(argv)
