#!/usr/bin/env python
#coding=utf-8
# -*- coding: utf-8 -*-

import math
import re

class HtmlContentParser:
    
    def __init__(self):
        pass
    
    #将HTML拆分为若干份，找出p数量最多的段
    def getContent(self, html, blockCount = 40, neighbour = 0.15):
        total = len(html)
        each = int(math.ceil(total / blockCount))
        stat = self.statistic(html, blockCount)
        neighbourStep = int(math.ceil(neighbour * blockCount))
        # 计算斜率
        slope = [0 for i in range(0, len(stat))]
        for i in range(0, len(stat)):
            if i == 0:
                slope[i] = 0
            else:
                slope[i] = stat[i] - stat[i-1]
        # 寻找最密集的p标签所在段落
        maxUpPos, maxDownPos = self.findMax(slope)
        # 最密集的p段位于 [maxUpPos, maxDownPos] 之间
        # 扩展前后搜寻
        maxDownPos = self.findNeighbour(stat, neighbourStep, 1, maxDownPos)
        maxUpPos = self.findNeighbour(stat, neighbourStep, -1, maxUpPos)
        text = html[maxUpPos*each: maxDownPos*each]
        start = text.find('>') + 1
        end = text.rfind('<')
        return text[start: end]

    # 寻找最密集的p标签所在段落
    def findMax(self, slope):
        maxUp = 0
        maxDown = 0
        maxUpPos = 0
        maxDownPos = 0
        for i in range(0, len(slope)):
            if slope[i] > maxUp:
                maxUp = slope[i]
                maxUpPos = i
            rev_i = len(slope) - i - 1
            if slope[rev_i] < maxDown:
                maxDown = slope[rev_i]
                maxDownPos = rev_i
        return (maxUpPos, maxDownPos)

    # 寻找相邻的可能正文
    def findNeighbour(self, stat, neighbourStep, direction, pos):
        # direction = 1向后搜索, -1向前搜索
        i = pos + direction
        zeroCount = 0
        while i > 0 and i < len(stat):
            if stat[i] == 0:
                zeroCount += 1
            else:
                pos = i
            if zeroCount > neighbourStep:
                break
            i += direction
        return pos
    #将HTML拆分为若干份，统计每一份中p标签的数量
    def statistic(self, html, blockCount = 20):
        total = len(html)
        each = int(math.ceil(total / blockCount))
        stat = [0] * blockCount
        reParagraph = re.compile("</{0,1}p.*?>", re.IGNORECASE)
        links = reParagraph.finditer(html)
        for i in links:
            sec = i.start() / each
            stat[sec] += 1
        return stat
