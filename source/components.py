# -*- coding: utf-8 -*-
# @Author: Michael
# @Date:   2016-10-05 11:35:00
# @Last Modified by:   Michael
# @Last Modified time: 2016-10-11 17:24:07
import exceptions


class BaseComp(object):
    """docstring for BaseComp"""
    name = None
    url = None

    def __init__(self):
        super(BaseComp, self).__init__()

    def getName(self):
        return self.name

    def getUrl(self):
        return self.url


class AssessComp(BaseComp):
    """docstring for AssessComp"""
    ztpj = '老师认真负责'
    # overall evaluation
    pgyj = '满意'
    # assess opinion

    def __init__(self, name, postUrl, url, content, assessments):
        super(AssessComp, self).__init__()
        self.postUrl = postUrl
        self.url = url
        self.name = name
        self.content = content
        self.assessments = assessments

    def __str__(self):
        content = ''
        for key in self.content:
            content += '\n\t' + str(key[0]) + ': ' + str(key[1])
        return 'subject: %s\ncontent: %s\nsummary: %s\nidea: %s\n' % (self.name, content, self.ztpj, self.pgyj)

    def setFraction(self, assessFraction):
        if len(assessFraction) != len(self.content):
            raise exceptions.FractionException('number of fraction you give (%d) cannot pair with number of options(%d)' % (len(assessFraction), len(self.content)))
        for index, item in enumerate(assessFraction):
            if type(item) is not int or item > 5 or item < 0:
                raise exceptions.FractionException('fraction value error.')
            self.content[index][1] = item


class ScheduleComp(BaseComp):
    """docstring for ScheduleComp"""

    def __init__(self):
        super(ScheduleComp, self).__init__()
        self.schedule = [['' for i in range(8)] for j in range(12)]
        self.timetable = [[True for i in range(8)] for j in range(12)]

    def __str__(self):
        return self.schedule
