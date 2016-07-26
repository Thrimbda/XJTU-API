# -*- coding: utf-8 -*-
# @Author: Macpotty
# @Date:   2016-05-22 15:35:19
# @Last Modified by:   Macpotty
# @Last Modified time: 2016-07-25 17:58:13
import requests
from bs4 import BeautifulSoup
from collections import deque
import FileModule
import traceback
import time


class Spider:
    def __init__(self, url, record=False):
        self.session = requests.Session()
        self.headers = {'Connection': 'keep-alive',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding': 'gzip',
                        'Accept-Language': 'zh-CN,zh;q=0.8',
                        'Referer': 'https://www.baidu.com/link?url=YEhWaYGOPw1mlBWWji4kqYkbuQYoRfmYE94YXDz7Dwm&wd=&eqid=d69a671b000e59e70000000357406ffe',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36',
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
            self.FileModule = FileModule.FileModule()

    def postForm(self, process=None, autoCollect=True, judgeCondition='', **payload):
        if judgeCondition != '' and judgeCondition not in self.soup.body.text:
            return
        if autoCollect:
            token = {}
            for i in self.soup.find_all('input', type='hidden', value=True):
                token[i.get('name')] = i.get('value')
            payload = dict(token, **payload)
        if process is not None:
            payload, self.currUrl = process(payload)
        self.response = self.session.post(self.currUrl, data=payload, headers=self.headers)
        if self.response.status_code != 200:
            self.response.raise_for_status()
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def getSite(self, url):
        self.currUrl = url
        self.visited |= {self.currUrl}
        self.response = self.session.get(self.currUrl, headers=self.headers)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def getUrls(self):
        # for i in self.soup.find_all('a', href=True):
        try:
            for item in self.soup.find('table', attrs={'class': True, 'id': True}).find_all('a', href=True):
                url = item.get('href')
                print(url not in self.visited and item.get_text() == '评教')
                if url not in self.visited and item.get_text() == '评教':
                    if url[0] == '?':
                        url = 'http://ssfw.xjtu.edu.cn/index.portal' + url
                    self.urls.append(url)
                    print('appended queue --->' + url)
        except AttributeError as e:
            print(self.response)
            print(self.response.status_code)
            print(e)
            print("No such class in this page: %s" % self.currUrl)

    def refresh(self):
        self.currUrl = self.response.url
        self.visited |= {self.currUrl}
        self.response = self.session.get(self.currUrl, headers=self.headers)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def openQueue(self, function=None, *args, **kargs):
        self.currUrl = self.urls.popleft()
        if self.currUrl not in self.visited:
            self.getSite(self.currUrl)
            print('already grabed:' + str(self.cnt) + '    grabing <---  ' + self.currUrl)
            try:
                if function is not None:
                    function(*args, **kargs)
            except Exception:
                traceback.print_exc()
            self.cnt += 1

    def mainCtl(self):
        while self.urls:
            self.openQueue(function=self.postForm, process=mySpider.teachingAssess, autoCollect=True, judgeCondition='总体评价', assessGrade=[1, 1, 1, 1, 2])
            # time.sleep(2)
            try:
                self.getUrls()
            except requests.HTTPError as e:
                print(e)
                break
            else:
                print('done!')
        if self.fobj is not None:
            self.FileModule.fileEnd()

    def teachingAssess(self, token, assessGrade=[1, 1, 1, 1, 2]):
        """this function is very XJTUic.
           once administrator change those value of checkboxes.
           we done.

        use it to do the tiring teaching assessment.
        :type assessGrades: List[grade]
        """
        if '实验教师' in self.soup.body.text:
            assessments = {1: 'PJDJ0441', 2: 'PJDJ0475', 3: 'PJDJ0476', 4: 'PJDJ0477', 5: 'PJDJ0478', 6: 'PJDJ0479'}
        else:
            assessments = {1: 'PJDJ0410', 2: 'PJDJ0411', 3: 'PJDJ0382', 4: 'PJDJ0383', 5: 'PJDJ0412', 6: 'PJDJ0385'}
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

if __name__ == '__main__':
    try:
        mySpider = Spider('https://cas.xjtu.edu.cn/login?service=http%3A%2F%2Fssfw.xjtu.edu.cn%2Findex.portal')
        mySpider.postForm(username='siyuan.mac', password='960627Xc!')
        # mySpider.urls.append('http://ssfw.xjtu.edu.cn/index.portal?.pn=p1142_p1182_p1183')
        # mySpider.mainCtl()
        mySpider.getSite("http://ssfw.xjtu.edu.cn/index.portal?ticket=ST-202218-qcHC3XPCgOQj9n5eCJHD-gdscas01")
        mySpider.getSite("http://ssfw.xjtu.edu.cn/index.portal?ticket=ST-202254-LB3IUMf9ceYuD6ooiP6X-gdscas01")
        time.sleep(6)
        mySpider.refresh()
        mySpider.getSite('http://ssfw.xjtu.edu.cn/pnull.portal?.pen=pe801&.f=f1821&action=print&executeName=print&xnxqdm=20161&newSearch=true')
        mySpider.refresh()
        print(mySpider.soup.body.text)
        # mySpider.refresh()
        # print(mySpider.soup.body.text)
        # print(mySpider.soup.body)
    except requests.HTTPError as e:
        print(e)
    # else:
        # mySpider.mainCtl()
    # print(mySpider.soup.body.text)
