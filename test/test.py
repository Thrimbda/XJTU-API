# -*- coding: utf-8 -*-
# @Author: Michael
# @Date:   2016-12-01 02:11:24
# @Last Modified by:   Michael
# @Last Modified time: 2016-12-01 03:22:19
import os
# import sys
# sys.path.append("..")
from source.mySpider import XJTUSpider

if __name__ == '__main__':
    mySpider = XJTUSpider('ssfw')
    if mySpider.login(username=os.environ.get('username'), password=os.environ.get('password')) == 0:
        mySpider.teachingAssess(autoMode=False)
        mySpider.teachingAssess(autoMode=False, index=0)
        mySpider.schedule()
        mySpider.logout()
