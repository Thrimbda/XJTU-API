# -*- coding: utf-8 -*-
# @Author: Macpotty
# @Date:   2016-09-17 13:24:41
# @Last Modified by:   Macpotty
# @Last Modified time: 2016-09-17 13:37:34
import traceback


def openqueue(func):
    def wrapper(self, *args, **kargs):
        try:
            self.currUrl = self.urls.popleft()
        except IndexError:
            print("try to pop from a empty deque.")
        else:
            if self.currUrl not in self.visited:
                self.getSite(self.currUrl)
                print('already grabed:' + str(self.cnt) + '    grabing <---  ' + self.currUrl)
                try:
                    func(*args, **kargs)
                except Exception:
                    self.fobj.fileEnd()
                    traceback.print_exc()
                finally:
                    self.cnt += 1
    return wrapper


class A(object):
    cnt = 1

    def test(self, func):
        def wrapper(self, *args, **kargs):
            print('hello %s.' % func.__name__, self.cnt)
            func()
        return wrapper

    @test
    def foo(self):
        print('asdasd')

if __name__ == '__main__':
    a = A
    a.foo()
