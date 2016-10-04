# -*- coding: utf-8 -*-
# @Author: Macpotty
# @Date:   2016-05-22 15:35:19
# @Last Modified by:   Michael
# @Last Modified time: 2016-10-04 18:40:02
import requests
from bs4 import BeautifulSoup
from collections import deque
import utils
import FileModule
import traceback
import threading
import re
import json


class Spider:
    """
    @brief      Class for spider.
    """
    def __init__(self, url, record=False):
        self.__session = requests.Session()
        self.__headers = {'Connection': 'keep-alive',
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                          'Accept-Encoding': 'gzip',
                          'Accept-Language': 'zh-CN,zh;q=0.8',
                          'Referer': 'https://www.baidu.com/link?url=YEhWaYGOPw1mlBWWji4kqYkbuQYoRfmYE94YXDz7Dwm&wd=&eqid=d69a671b000e59e70000000357406ffe',
                          'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36',
                          # 'X-Requested-With': 'XMLHttpRequest'
                          }
        self.rootUrl = url
        self.currUrl = self.rootUrl
        self.response = self.__session.get(self.rootUrl)
        if self.response.status_code != 200:
            self.response.raise_for_status()
        self.__soup = BeautifulSoup(self.response.text, 'html.parser')
        self.urls = deque()
        self.urls.append(self.rootUrl)
        self.visited = set()
        self.visited |= {self.currUrl}
        self.cnt = 0
        self.fobj = None
        if record:
            self.fobj = FileModule.FileModule()

    def __soupGen(self):
        self.__soup = BeautifulSoup(self.response.text, 'html.parser')

    def postForm(self, process=None, autoCollect=True, postURL=None, **payload):
        if autoCollect:
            token = {}
            for i in self.__soup.find_all('input', type='hidden', value=True):
                token[i.get('name')] = i.get('value')
            payload = dict(token, **payload)
        if process is not None:
            payload, self.currUrl = process(payload)
        if postURL is None:
            postURL = self.currUrl
        self.response = self.__session.post(postURL, data=payload, headers=self.__headers)
        print(payload)
        if self.response.status_code != 200:
            self.response.raise_for_status()
        self.__soupGen()

    def getSite(self, url):
        self.currUrl = url
        self.visited |= {self.currUrl}
        self.response = self.__session.get(self.currUrl, headers=self.__headers)
        self.__soupGen()

    def getUrls(self):
        raise NotImplementedError

    def refresh(self):
        self.currUrl = self.response.url
        self.visited |= {self.currUrl}
        self.response = self.__session.get(self.currUrl, headers=self.__headers)
        self.__soupGen()

    def openQueue(self, function=None, *args, **kargs):
        try:
            self.currUrl = self.urls.popleft()
        except IndexError:
            print("try to pop from a empty deque.")
        else:
            if self.currUrl not in self.visited:
                self.getSite(self.currUrl)
                print('already grabed:' + str(self.cnt) + '    grabing <---  ' + self.currUrl)
                try:
                    if function is not None:
                        function(*args, **kargs)
                except Exception:
                    if self.fobj is not None:
                        self.fobj.fileEnd()
                    traceback.print_exc()
                finally:
                    self.cnt += 1

    def mainCtl(self):
        raise NotImplementedError

    def multiThreadMainCtl(self):
        threads = []
        for i in range(4):
            threads.append(threading.Thread(target=self.mainCtl))
            threads[i].start()


class XJTUSpider(Spider):
    """
    A spider form of XJTU sites API
    single thread, but will extend to muti-thread after.
    """
    def __init__(self, url, record=False):
        self.rootUrl = 'http://' + url + '.xjtu.edu.cn/'
        self.service = url
        super(XJTUSpider, self).__init__(self.rootUrl, False)
        self.teachingAssessModule = utils.TeachingAssessUtil(self.__soup)

    def __soupGen(self):
        super(XJTUSpider, self).__soupGen()
        self.teachingAssessModule.update(self.__soup)

    def getSoup(self):
        return self.__soup

    def login(self, username, password):
        self.getSite('https://cas.xjtu.edu.cn/login?service=http%3A%2F%2F' + self.service + '.xjtu.edu.cn%2Findex.portal')
        self.postForm(username=username, password=password, postURL='https://cas.xjtu.edu.cn/login?service=http%3A%2F%2F' + self.service + '.xjtu.edu.cn%2Findex.portal')
        self.getSite(self.__getStub())
        print(self.__soup.text)

    def logout(self):
        self.getSite(self.rootUrl + '/logout.portal')

    def teachingAssess(self, autoMode=True):
        self.getSite('http://ssfw.xjtu.edu.cn/index.portal?.pn=p1142_p1182_p1183')
        self.urls.extend(self.teachingAssessModule.getTeachingAssessUrls())
        if not autoMode:
            pass
        else:
            while self.urls:
                self.openQueue(function=self.postForm, process=self.teachingAssessModule.getTeachingAssessPayload)

    def __getStub(self):
        """
        get the stub url from the sneaky redirect page which looks very innocent.
        """
        return re.findall("direct\\('(.*?)'\\);", self.__soup.find('a', onclick=True)['onclick'])[0]

    def __getPostInfo(self):
        self.jsonStr = json.loads(self.__session.get('http://ssfw.xjtu.edu.cn/pnull.portal?.pen=pe1061&.pmn=view&action=optionsRetrieve&className=com.wiscom.app.w5ssfw.pjgl.domain.V_PJGL_XNXQ&namedQueryId=&displayFormat={json}&useBaseFilter=true').text)

    def mainCtl(self):
        try:
            self.getUrls()
        except requests.HTTPError as e:
            print(e)
        while self.urls:
            self.openQueue(function=self.postForm, process=self.teachingAssess, autoCollect=True)
        if self.fobj is not None:
            self.fobj.fileEnd()
