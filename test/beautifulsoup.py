#coding:utf-8
#!/usr/bin/python

from bs4 import BeautifulSoup

doc = [
    '<html><head><title>Page title</title></head>',
    '<body><p id="firstpara" align="center">This is paragraph <b>one</b>.',
    '<p id="secondpara" align="blah">This is paragraph <b>two</b>.',
    '</html>'
]
# BeautifulSoup 接受一个字符串参数
soup = BeautifulSoup(''.join(doc))