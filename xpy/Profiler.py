
#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

import sys
from collections import Counter
import time
import os

class Profiler(object):
    times = Counter()
    @classmethod
    def show_profiler(self):
        # self.times
        pass
        # count = 90
        total_time = sum(self.times.values())
        top = sorted(self.times.items(), key = lambda kv: kv[1])
        print('-' * 80)
        for (key, t) in top:
            print('%0.8f%%: %s' % (100 * t / total_time, key))
            
        # print(top)

    @classmethod
    def start(self):

        focus = '_create'

        def is_focus(code):
            # return code.co_name == 'errcheck'
            return True
            return code.co_name == '_create' and code.co_filename == 'nodes/graphtype.py'

        tf = lambda: time.time()
        tf = lambda: os.times()[0]

        times = Counter()
        self.times = times

        v = [
            tf(),
            False, # in_focus
        ]

        stack = []

        events = set()
        in_focus = False

        def profile(frame, event, arg):

            # print(event + ' ' + frame.f_code.co_name + ' ' + str(frame.f_lineno))
            t1 = tf()

            key = frame.f_code

            if event.endswith('all'):
                if is_focus(key):
                    v[1] = True
                stack.append((key, t1))
            elif event.endswith('urn'):
                if len(stack):
                    if v[1]:
                        (key, t0) = stack.pop()

                        function_time = t1 - t0
                        times[key] += function_time

                        if is_focus(key):
                            # switch out of focus
                            v[1] = False

                        # print(function_time)

                if t1 - v[0] > 1:
                    self.show_profiler()
                    v[0] = t1

            return profile

        sys.setprofile(profile)

