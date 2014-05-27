#-*-encoding:utf-8-*-
"""
这个脚本用于处理“git中怎么提交空文件夹”的问题
在git中的空文件夹不能纳入版本管理，checkout时空文件夹也不能同步创建。
因此此脚本通过在空文件夹下面创建index.html的方法，强制让git把空文件夹纳入版本管理。
"""
import os

#检查文件夹是否空
def checkEmptyDir(path):
    list = os.listdir(path)#列出目录下的所有文件和目录
    return len(list) == 0;

#填充空文件夹
def fillEmptyDir(path):
    list = os.listdir(path)#列出目录下的所有文件和目录
    for line in list:
        filepath = os.path.join(path, line)
        if os.path.isdir(filepath):
            if checkEmptyDir(filepath):
                print 'create index.html in', filepath;
                writeTextFile(os.path.join(filepath, 'index.html'), '');
            #如果filepath是目录，则再列出该目录下的所有文件
            fillEmptyDir(filepath);

#写入文本文件
def writeTextFile(filepath, content):
    f=open(filepath,'w');
    f.write(content)
    f.close()

#
def listIndexOf(myList,value): 
    for v in range(0,len(myList)): 
        pos = myList[v].find(value);
        if pos >= 0:            
            break; 
    return v
#

print fillEmptyDir(os.getcwd())
