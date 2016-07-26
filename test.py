# -*- coding: utf-8 -*-
# @Author: Macpotty
# @Date:   2016-04-19 17:12:04
# @Last Modified by:   Macpotty
# @Last Modified time: 2016-05-22 15:55:17
import urllib.request
import urllib
import socket
# import os
import re
import http.cookiejar
import gzip
from collections import deque


def myOpener(head={'Connection': 'keep-alive',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Language': 'zh-CN,zh;q=0.8',
                   'Referer': 'https://www.baidu.com/link?url=YEhWaYGOPw1mlBWWji4kqYkbuQYoRfmYE94YXDz7Dwm&wd=&eqid=d69a671b000e59e70000000357406ffe',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36'}):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header
    return opener


def unzip(data):
    try:
        data = gzip.decompress(data)
    except TypeError:
        print("already unziped")
    return data


queue = deque()
visited = set()
opener = myOpener()

url = 'http://www.douban.com/'

queue.append(url)
cnt = 0

while queue:
    url = queue.popleft()
    visited |= {url}

    print('already grabed:' + str(cnt) + '    grabing <---  ' + url)
    cnt += 1
    try:
        urlop = opener.open(url, timeout=2)
    except UnicodeError as e:
        print(e)
        url = urllib.parse.unquote(urllib.parse.quote(url)).replace('\\x', '%')
        print(url)
        urlop = opener.open(url, timeout=2)
    except socket.timeout:
        continue
    except urllib.error.URLError as e:
        print(e)
        continue

    if 'html' not in urlop.getheader('Content-Type'):
        continue

    # try:
    data = urlop.read().decode('utf-8')
    data = unzip(data)
    # except Exception as e:
    #     print(e)
    #     continue

    linkre = re.compile('href="(.+?)"')
    for x in linkre.findall(data):
        if 'http' in x and x not in visited:
            queue.append(x)
            print('appended queue --->' + x)
