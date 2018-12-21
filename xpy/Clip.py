#!/usr/bin/env python3

#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

import os
import readline
from functools import reduce
import inspect

from .History import History

class Clip(object):
    @staticmethod
    def paste():
        result = None
        with os.popen('xsel -o') as infile:
            result = infile.read()
        return result

    @staticmethod
    def copy(buf):
        with os.popen('xsel -i', 'w') as outfile:
            outfile.write(buf)
        
    @staticmethod
    def show():
        print(Clip.paste().rstrip('\n'))

    @staticmethod
    def indent_len(line):
        return len(line) - len(line.lstrip('\t '))

    @staticmethod
    def minimize_indent(source):
        lines = source.split('\n')
        lines = list(filter(lambda line: len(line.strip()) > 0, lines))
        lines = list(filter(lambda line: not line.strip().startswith('#'), lines))
        min_indent = reduce(lambda i0, i1: i1 if i0 is None else min(i0, i1), map(Clip.indent_len, lines), None)
        source = '\n'.join((map(lambda line: line[min_indent:], lines)))

        return source

    @staticmethod
    def compile():
        result = None
        source = Clip.paste()
        if source:
            # fix indent
            source = Clip.minimize_indent(source)

            code = compile(source, __name__, 'exec')
            result = (source, code)
        return result

    @staticmethod
    def copy_from_history(line_count):
        lines = History.get_last(line_count)
        buf = '\n'.join(lines)
        Clip.copy(buf)

    @staticmethod
    def paste_into_history(is_split_lines = False):
        code = Clip.compile()
        if code is not None:
            (source, code) = code
            if is_split_lines:
                for line in source.split('\n'):
                    if line:
                        readline.add_history(line)
                        print(line)
            elif source:
                print(source)
                readline.add_history(source)

    @staticmethod
    def run(_globals = None, _locals = None):
        """Run the contents of the clipboard within the caller's frame."""
        result = None
        code = Clip.compile()
        if code is not None:
            (source, code) = code
            # print(source)
            frame = inspect.currentframe()
            frame = frame.f_back
            result = frame
            #
            if _globals is None:
                _globals = frame.f_globals
            if _locals is None:
                _locals = frame.f_locals
            #
            exec(code, _globals, _locals)
        else:
            print('failed to compile')
        return result


