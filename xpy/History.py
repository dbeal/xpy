#!/usr/bin/env python3

import os
import readline
from functools import reduce
import inspect

class History(object):
    @staticmethod
    def get_last(line_count):
        l = readline.get_current_history_length()
        lines = []
        for i in range(max(l - line_count, 0), l):
            line = readline.get_history_item(i)
            lines.append(line)
        return lines

    @staticmethod
    def show(line_count):
        print('\n'.join(History.get_last(line_count)))

