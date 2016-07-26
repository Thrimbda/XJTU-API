
# -*- coding: utf-8 -*-
# @Author: Macpotty
# @Date:   2016-05-28 23:46:45
# @Last Modified by:   Macpotty
# @Last Modified time: 2016-06-08 21:21:36


class FileModule:
    def __init__(self):
        self.fobj = open('spiderIndent.html', 'w')
        self.fobj.write("""<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>spiderInfo</title>
    </head>
    <body>""")

    def fileWrite(self, text, isWriteline=False):
        if isWriteline:
            self.fobj.writeline(text)
        else:
            self.fobj.write(text)

    def fileEnd(self):
        self.fobj.write("""    </body>
</html>""")
        self.fobj.close()
