#!/usr/bin/env python3

from xpy import *
# import xpy
# from xpy.XPY import XPY
#with XPY() as xpy:
#    xpy.run()

class Bar(object):
    x = 6

class Y(object):
    def __init__(self):
        self.v = 2

# global y
y = Y()

class Foo(object):
    def __init__(self):
        print('here')
        self.x = 5

        # local y shadows global y
        y = Y()
        # additional completion attribute only for local y
        y.q = 7
        y.v = 16

        fn = lambda: Bar.x

        print('locals is globals', locals() is globals())

        print('dir', dir())
        # xpy = XPY(); xpy.start_console()
        xpy_start_console()

        # see what xpy did
        # import pdb;pdb.set_trace()

        print('continuing')


f = Foo()
print('f', f.x)
