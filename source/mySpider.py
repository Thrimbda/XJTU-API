# -*- coding: utf-8 -*-
# @Author: Macpotty
# @Date:   2016-05-22 15:35:19
# @Last Modified by:   Michael
# @Last Modified time: 2016-10-11 18:06:32
import requests
from bs4 import BeautifulSoup
from collections import deque
import utils
import FileModule
import traceback
import threading
import re
import json
import types


class Spider:
    """
    @brief      Class for spider.
    """
    def __init__(self, url, record=False):
        self.session = requests.Session()
        self.headers = {'Connection': 'keep-alive',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding': 'gzip',
                        'Accept-Language': 'zh-CN,zh;q=0.8',
                        'Referer': 'https://www.baidu.com/link?url=YEhWaYGOPw1mlBWWji4kqYkbuQYoRfmYE94YXDz7Dwm&wd=&eqid=d69a671b000e59e70000000357406ffe',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36',
                        # 'X-Requested-With': 'XMLHttpRequest'
                        }
        self.rootUrl = url
        self.currUrl = self.rootUrl
        self.response = self.session.get(self.rootUrl)
        if self.response.status_code != 200:
            self.response.raise_for_status()
        self.soup = BeautifulSoup(self.response.text, 'html.parser')
        self.urls = deque()
        self.urls.append(self.rootUrl)
        self.visited = set()
        self.visited |= {self.currUrl}
        self.cnt = 0
        self.fobj = None
        if record:
            self.fobj = FileModule.FileModule()

    def soupGen(self):
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def postForm(self, process=None, autoCollect=True, postURL=None, **payload):
        if autoCollect:
            token = {}
            for i in self.soup.find_all('input', type='hidden', value=True):
                token[i.get('name')] = i.get('value')
            payload = dict(token, **payload)
        if process is not None:
            if isinstance(process, types.FunctionType) or isinstance(process, types.MethodType):
                payload, postURL = process(payload)
            else:
                raise TypeError(repr(type(process)) + 'is not a function.')
        if postURL is None:
            postURL = self.currUrl
        self.response = self.session.post(postURL, data=payload, headers=self.headers)
        # print(self.response.text)
        if self.response.status_code != 200:
            self.response.raise_for_status()
        self.soupGen()

    def getSite(self, url):
        self.currUrl = url
        self.visited |= {self.currUrl}
        self.response = self.session.get(self.currUrl, headers=self.headers)
        self.soupGen()

    def getUrls(self):
        raise NotImplementedError

    def refresh(self):
        self.currUrl = self.response.url
        self.visited |= {self.currUrl}
        self.response = self.session.get(self.currUrl, headers=self.headers)
        self.soupGen()

    def openQueue(self, function=None, *args, **kargs):
        try:
            self.currUrl = self.urls.popleft()
        except IndexError:
            print("try to pop from a empty deque.")
        else:
            if self.currUrl not in self.visited:
                self.getSite(self.currUrl)
                # print('already grabed:' + str(self.cnt) + '    grabing <---  ' + self.currUrl)
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
        self.teachingAssessModule = utils.TeachingAssessUtil(self.soup, self.currUrl)
        self.scheduleModule = utils.ScheduleUtil(self.soup, self.currUrl)

    def soupGen(self):
        super(XJTUSpider, self).soupGen()
        self.teachingAssessModule.update(self.soup, self.currUrl)
        self.scheduleModule.update(self.soup, self.currUrl)

    def getSoup(self):
        return self.soup

    def login(self, username, password):
        print('loading... this may take few seconds.')
        self.getSite('https://cas.xjtu.edu.cn/login?service=http%3A%2F%2F' + self.service + '.xjtu.edu.cn%2Findex.portal')
        self.postForm(username=username, password=password, postURL='https://cas.xjtu.edu.cn/login?service=http%3A%2F%2F' + self.service + '.xjtu.edu.cn%2Findex.portal')
        self.getSite(self.__getStub())
        print('login successful.')

    def logout(self):
        self.getSite(self.rootUrl + '/logout.portal')
        print('logout.')

    def teachingAssess(self, autoMode=True, index=None, fraction=None, pgyj=None, ztpj=None):
        self.getSite('http://ssfw.xjtu.edu.cn/index.portal?.pn=p1142_p1182_p1183')
        self.urls.extend(self.teachingAssessModule.getTeachingAssessUrls())
        while self.urls:
            self.openQueue(function=self.teachingAssessModule.assessObjGen)
        if autoMode:
            print('start auto assess...')
            for index, assessObj in enumerate(self.teachingAssessModule.assessObjs):
                self.getSite(self.teachingAssessModule.assessObjs[index].url)
                self.postForm(index=index, process=self.teachingAssessModule.teachingAssessPayloadGen)
            print('all done.')
        else:
            print('start specific assess...')
            print('----judging assessment infomation...')
            if index is None:
                assessList = []
                print("info: no index info, please give one.")
                for index, assessobj in enumerate(self.teachingAssessModule.assessObjs):
                    assessList.append((index, assessobj.name))
                    print(index, assessobj.name)
                return assessList
            elif fraction is None:
                print("info: no fraction info, please give it.")
                print(self.teachingAssessModule.assessObjs[index].name, self.teachingAssessModule.assessObjs[index])
                return self.teachingAssessModule.assessObjs[index].name, self.teachingAssessModule.assessObjs[index].content
            else:
                print('----info is good. start assess...')
                self.teachingAssessModule.assessObjs[index].setFraction(fraction)
                if ztpj is not None:
                    self.teachingAssessModule.assessObjs[index].ztpj = ztpj
                if pgyj is not None:
                    self.teachingAssessModule.assessObjs[index].pgyj = pgyj
                self.getSite(self.teachingAssessModule.assessObjs[index].url)
                self.postForm(index=index, process=self.teachingAssessModule.teachingAssessPayloadGen)
                print('done')

    def schedule(self):
        self.getSite('http://ssfw.xjtu.edu.cn/pnull.portal?.pen=pe801&.f=f1821&action=print&executeName=print&xnxqdm=20161&newSearch=true')
        self.scheduleModule.scheduleGen()
        return self.scheduleModule.schedule

    def __getStub(self):
        """
        get the stub url from the sneaky redirect page which looks very innocent.
        """
        return re.findall("direct\\('(.*?)'\\);", self.soup.find('a', onclick=True)['onclick'])[0]

    def __getPostInfo(self):
        self.jsonStr = json.loads(self.session.get('http://ssfw.xjtu.edu.cn/pnull.portal?.pen=pe1061&.pmn=view&action=optionsRetrieve&className=com.wiscom.app.w5ssfw.pjgl.domain.V_PJGL_XNXQ&namedQueryId=&displayFormat={json}&useBaseFilter=true').text)

    def mainCtl(self):
        try:
            self.getUrls()
        except requests.HTTPError as e:
            print(e)
        while self.urls:
            self.openQueue(function=self.postForm, process=self.teachingAssess, autoCollect=True)
        if self.fobj is not None:
            self.fobj.fileEnd()
