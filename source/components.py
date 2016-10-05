# -*- coding: utf-8 -*-
# @Author: Michael
# @Date:   2016-10-05 11:35:00
# @Last Modified by:   Michael
# @Last Modified time: 2016-10-05 12:16:41


class AssessComp(object):
    """docstring for AssessComp"""
    ztpj = None
    # overall evaluation
    pjyj = None
    # assess opinion
    url = None
    # url of the assessment
    fraction = {}

    def __init__(self, url):
        super(AssessComp, self).__init__()
        self.url = url
