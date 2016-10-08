# -*- coding: utf-8 -*-
# @Author: Michael
# @Date:   2016-10-05 11:35:00
# @Last Modified by:   Michael
# @Last Modified time: 2016-10-08 10:41:56


class BaseComp(object):
    """docstring for BaseComp"""
    name = None

    def __init__(self):
        super(BaseComp, self).__init__()

    def getName(self):
        return self.name


class AssessComp(BaseComp):
    """docstring for AssessComp"""
    ztpj = None
    # overall evaluation
    pjyj = None
    # assess opinion
    fraction = {}

    def __init__(self, url):
        super(AssessComp, self).__init__()
        self.url = url


class ScheduleComp(BaseComp):
    """docstring for ScheduleComp"""

    def __init__(self):
        super(ScheduleComp, self).__init__()
        self.schedule = [['' for i in range(8)] for j in range(12)]
        self.timetable = [[True for i in range(8)] for j in range(12)]
