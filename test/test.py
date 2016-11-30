# -*- coding: utf-8 -*-
# @Author: Michael
# @Date:   2016-12-01 02:11:24
# @Last Modified by:   Michael
# @Last Modified time: 2016-12-01 02:30:49
import os
from source.mySpider import XJTUSpider

if __name__ == '__main__':
    mySpider = XJTUSpider('ssfw')
    mySpider.login(username=os.environ.get('username'), password=os.environ.get('password'))
    mySpider.teachingAssess(autoMode=False)
    mySpider.teachingAssess(autoMode=False, index=0)
    mySpider.schedule()
    mySpider.logout()
