# -*- coding: utf-8 -*-
# @Author: Macpotty
# @Date:   2016-05-22 15:35:19
# @Last Modified by:   Macpotty
# @Last Modified time: 2016-09-17 15:01:56
import requests
from bs4 import BeautifulSoup
from collections import deque
import FileModule
import traceback
import threading
import re
import json


class Spider:
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

    def postForm(self, process=None, autoCollect=True, postURL=None, **payload):
        if autoCollect:
            token = {}
            for i in self.soup.find_all('input', type='hidden', value=True):
                token[i.get('name')] = i.get('value')
            payload = dict(token, **payload)
        if process is not None:
            payload, self.currUrl = process(payload)
        if postURL is None:
            postURL = self.currUrl
        self.response = self.session.post(postURL, data=payload, headers=self.headers)
        print(payload)
        if self.response.status_code != 200:
            self.response.raise_for_status()
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def getSite(self, url):
        self.currUrl = url
        self.visited |= {self.currUrl}
        self.response = self.session.get(self.currUrl, headers=self.headers)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def getUrls(self):
        raise NotImplementedError

    def getStub(self):
        return re.findall("direct\\('(.*?)'\\);", self.soup.find('a', onclick=True)['onclick'])[0]

    def refresh(self):
        self.currUrl = self.response.url
        self.visited |= {self.currUrl}
        self.response = self.session.get(self.currUrl, headers=self.headers)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

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
    """docstring for XJTUSpider"""
    def __init__(self, url, record=False):
        super(XJTUSpider, self).__init__(url, False)

    def getUrls(self):
        try:
            for item in self.soup.find('tavle', attrs={'class': 'portlet-table'}).find_all('a', href=True):
                if item.text != '评教':
                    continue
                url = item.get('href')
                self.urls.append(url)
                print('appended queue --->' + url)
        except AttributeError as e:
            print(self.response)
            print(self.response.status_code)
            print(e)
            print("No such class in this page: %s" % self.currUrl)
        except Exception:
            raise Exception

    def teachingAssess(self, token):
        """this function is totally XJTUic.
           once administrator change those value of checkboxes.
           we done.

        use it to do the ting teaching assessment.
        :type assessGrades: List[grade]
        """
        if '实验教师' in self.soup.body.text:
            assessments = {1: 'PJDJ0441', 2: 'PJDJ0475', 3: 'PJDJ0476', 4: 'PJDJ0477', 5: 'PJDJ0478', 6: 'PJDJ0479'}
            assessGrade = [1, 1, 1, 1, 2]
        elif '实验辅助人员' in self.soup.body.text:
            assessments = {1: 'PJDJ0441', 2: 'PJDJ0475', 3: 'PJDJ0476', 4: 'PJDJ0477', 5: 'PJDJ0478', 6: 'PJDJ0479'}
            assessGrade = [1, 1, 1, 2]
        else:
            assessments = {1: 'PJDJ0410', 2: 'PJDJ0411', 3: 'PJDJ0382', 4: 'PJDJ0383', 5: 'PJDJ0412', 6: 'PJDJ0385'}
            assessGrade = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2]
        token['ztpj'] = '老师认真负责'
        token['pgyj'] = '满意'
        token['sfytj'] = 'true'
        token['type'] = '2'
        token['actionType'] = '2'
        token.pop('zbbm')
        zbbm = []
        name = None
        assessIndex = -1
        for item in self.soup.find('table', id=True).find_all('input', attrs={'name': True, 'value': True}):
            if 'pfdj' in item.get('name') and item.get('name') != name:
                name = item.get('name')
                assessIndex += 1
                token[name] = assessments[assessGrade[assessIndex]]
            if 'qz_' in item.get('name'):
                token[item.get('name')] = '20'
            if 'zbbm' in item.get('name'):
                zbbm.append(item.get('value'))
        list(set(zbbm))
        payload = list(token.items())
        for item in zbbm:
            payload.append(('zbbm', item))
        try:
            url = 'http://ssfw.xjtu.edu.cn/index.portal' + self.soup.find('form', action=True).get('action')
        except AttributeError as e:
            print(e)
            raise requests.HTTPError['NONONO']
        return payload, url

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
                self.fobj.fileEnd()
                traceback.print_exc()
            finally:
                self.cnt += 1

    def getPostInfo(self):
        self.jsonStr = json.loads(self.session.get('http://ssfw.xjtu.edu.cn/pnull.portal?.pen=pe1061&.pmn=view&action=optionsRetrieve&className=com.wiscom.app.w5ssfw.pjgl.domain.V_PJGL_XNXQ&namedQueryId=&displayFormat={json}&useBaseFilter=true').text)

    def mainCtl(self, week):
        self.getPostInfo()
        print(self.jsonStr, self.jsonStr['options'])
        self.postForm(postURL='http://ssfw.xjtu.edu.cn/index.portal?.p=Znxjb20ud2lzY29tLnBvcnRhbC5zaXRlLmltcGwuRnJhZ21lbnRXaW5kb3d8ZjExNjF8dmlld3xub3JtYWx8YWN0aW9uPXF1ZXJ5', newSearch='true', pc=self.jsonStr['options'][week]['code'])
        try:
            self.getUrls()
        except requests.HTTPError as e:
            print(e)
        while self.urls:
            self.openQueue(function=self.postForm, process=self.teachingAssess, autoCollect=False)
        if self.fobj is not None:
            self.fobj.fileEnd()
