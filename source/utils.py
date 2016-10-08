# -*- coding: utf-8 -*-
# @Author: Michael
# @Date:   2016-10-04 01:01:58
# @Last Modified by:   Michael
# @Last Modified time: 2016-10-08 15:35:02
import requests
import traceback
import components
from collections import deque


class BaseUtil(object):
    """docstring for BaseUtil"""
    def __init__(self, soup):
        super(BaseUtil, self).__init__()
        self.soup = soup

    def update(self, soup):
        self.soup = soup


class TeachingAssessUtil(BaseUtil):
    def __init__(self, soup):
        super(TeachingAssessUtil, self).__init__(soup)
        self.assessComps = []

    def assessmentsGen(self):
        assessments = {}
        for index, value in enumerate(self.soup.find('table', attrs={'class': 'portlet-table'}).find_all('tr')[2].find_all('td')[3:]):
            if value.div is not None:
                print(value)
                assessments[5 - index] = value.div.input.get('value')
        return assessments

    def assessmentsContentGen(self):
        assessmentsContent = {}
        for row in self.soup.find('table', attrs={'class': 'portlet-table'}).find_all('tr')[2:-2]:
            print(row.find_all('td'))
            assessmentsContent[row.find_all('td')[2].text.strip()] = 5
        return assessmentsContent

    def getTeachingAssessPayload(self, token):
        """this function is totally XJTUic.
           once administrator change those value of checkboxes.
           we done.

        use it to do the ting teaching assessment.
        """
        if token.get('zbbm') is not None:
            token.pop('zbbm')
            if '实验' in self.soup.body.text:
                assessments = self.assessmentsGen()
                assessGrade = [5, 5, 5, 5, 5, 5, 5, 5, 4]
            else:
                assessments = self.assessmentsGen()
                assessGrade = [5, 5, 5, 5, 5, 5, 5, 5, 5, 4]
            token['ztpj'] = '老师认真负责'
            token['pgyj'] = '满意'
            token['sfytj'] = 'true'
            token['type'] = '2'
            token['actionType'] = '2'
            print(token)
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
            payload = list(token.items())
            list(set(zbbm))
            for item in zbbm:
                payload.append(('zbbm', item))
            try:
                url = 'http://ssfw.xjtu.edu.cn/index.portal' + self.soup.find('form', action=True).get('action')
            except AttributeError as e:
                print(e)
                raise requests.HTTPError['NONONO']
            print(payload)
        return payload, url

    def getTeachingAssessUrls(self):
        urls = deque()
        try:
            for item in self.soup.find('table', attrs={'class': 'portlet-table'}).find_all('a', href=True):
                if item.text != '评教':
                    continue
                url = item.get('href')
                urls.append('http://ssfw.xjtu.edu.cn/index.portal' + url)
                print('appended queue --->' + url)
            return urls
        except AttributeError as e:
            print(self.response)
            print(self.response.status_code)
            print(e)
            print("No such class in this page: %s" % self.currUrl)
        except requests.HTTPError as e:
            traceback.print_exc()
        except Exception:
            raise Exception


class ScheduleUtil(BaseUtil):
    """docstring for ScheduleUtil"""
    def __init__(self, soup):
        super(ScheduleUtil, self).__init__(soup)
        self.schedule = components.ScheduleComp()

    def scheduleGen(self):
        self.schedule.name = self.soup.find('td', attrs={'class': 'SStitleTd'}).div.text
        for row, item in enumerate(self.soup.find('table', id='queryForm').find_all('tr')):
            if item.th is not None:
                for vol, value in enumerate(item.find_all('th', attrs={'class': False})):
                    self.schedule.schedule[row][vol] = value.text.replace('\n', '').replace('\xa0', '')
            else:
                for vol, value in enumerate(item.find_all('td', attrs={'class': False})):
                    if self.schedule.schedule[row][vol] == '':
                        self.schedule.schedule[row][vol] = value.text.replace('\n', '').replace('\xa0', '')
                        if vol != 0 and self.schedule.schedule[row][vol] != '':
                            self.schedule.timetable[row][vol] = False
                        if value['rowspan'] == '2':
                            self.schedule.schedule[row + 1][vol] = value.text.replace('\n', '').replace('\xa0', '')
                            self.schedule.timetable[row + 1][vol] = False
            if row == 11:
                break

    def getWebSchedule(self):
        return str(self.soup.find('table', id='queryForm'))
