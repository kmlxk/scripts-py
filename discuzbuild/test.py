#!/usr/bin/env python
#coding=utf-8
# -*- coding: utf-8 -*-

import re
import FilterTag

html = """<li class="result" id="3"><h3 class="c-title"><a href="http://www.yn.xinhuanet.com/2014-08/01/c_133524593.htm"
    data-click="{
      'f0':'77A717EA',
      'f1':'9F63F1E4',
      'f2':'4CA6DE6B',
      'f3':'54E5343F',
      't':'1406907226'
      }"

                target="_blank"
            
    ><em>保山</em>110kV黄大双回线成功投运</a></h3><span class="c-author">&nbsp;新华网云南频道&nbsp;2014-08-01 11:48:46</span><div class="c-summary"><a class="c_photo" href="http://www.yn.xinhuanet.com/2014-08/01/c_133524593.htm" target="_blank" ><img src="http://t11.baidu.com/it/u=2758189216,675019279&amp;fm=55&amp;s=1786B540861F7FCE71B00D510300C0DB&amp;w=121&amp;h=81&amp;img.JPEG" alt="" /></a>2014年7月25日19时07分,<em>保山</em>电网新建线路110kV黄大Ⅰ、Ⅱ回线投产操作完毕,一二次设备、线路带电运行正常,标志着110kV黄大Ⅰ、Ⅱ回线成功投运。该线路顺利投运,...&nbsp;<a href="http://cache.baidu.com/c?m=9d78d513d9d431ac4f9e95697c1dc0166f40c72362d88a5339968449e07946040223f4bb50694c13d3b2363c5df50e0fb6a77065377471eac4d58848debd8528598a2d29721f9b1005d46dacca4722c1269751e8b81990e0b66d&amp;p=89769a4786cc4bfd43a8ca394a&amp;newp=8c759a4f91904ead1bf6d42f4453d8304503c522239687787fd5980f&user=baidu&fm=sc&query=%B1%A3%C9%BD&qid=a54f1ff40000677e&p1=3" 
      data-click="{'fm':'sc'}"
        target="_blank"  class="c-cache">百度快照</a></div></li>
"""

links = re.findall('<h3\s+class="c-title"><a\s+href="([^"]*?)"[^>]*?>(.*?)</a>', html);

f = FilterTag.FilterTag()

print f.strip_tags(links[0][1].decode('utf-8'))

# print html.decode('utf-8')



