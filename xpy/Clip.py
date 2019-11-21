#!/usr/bin/env python3

#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

import os
import readline
from functools import reduce
import inspect

from .History import History
#
import tempfile
#

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
        # remove comments
        lines = list(filter(lambda line: not line.strip().startswith('#'), lines))
        min_indent = reduce(lambda i0, i1: i1 if i0 is None else min(i0, i1), map(Clip.indent_len, lines), None)
        source = '\n'.join((map(lambda line: line[min_indent:], lines)))

        return source

    @staticmethod
    def paste_source():
        result = None
        text = Clip.paste()
        if text is not None:
            #
            # fix indent
            #
            source = Clip.minimize_indent(text)
            #
            result = source
            #
        #
        return result

    #
    # keep temp files around for tracebacks
    #
    is_unlink_tempfile = 0
    is_use_tempfile = 1
    is_reuse_pid_tempfile = 0
    is_reuse_global_tempfile = 0
    #
    # TODO: place these in separate temp directory
    #
    global_temp_path = os.path.join(tempfile.gettempdir(), 'Clip.txt')
    #
    @staticmethod
    def make_tempfile():
        #
        if Clip.is_reuse_global_tempfile:
            #
            path = Clip.global_temp_path
            #
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o600)
            #
        elif Clip.is_reuse_pid_tempfile:
            #
            path = os.path.join(tempfile.tempdir, 'Clip.' + str(os.getpid()))
            #
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o600)
            #
        else:
            #
            (fd, path) = tempfile.mkstemp(prefix = 'Clip.')
            #
        #
        return (fd, path)
        #
    #
    @staticmethod
    def compile():
        result = None
        source = Clip.paste_source()
        if source:
            #
            # must use mode = 'exec' to compile multiple lines
            #
            if Clip.is_use_tempfile:
                #
                (fd, path) = Clip.make_tempfile()
                #
                with os.fdopen(fd, 'wb') as outfile:
                    outfile.write(source.encode())
                    #
                #
            else:
                path = __name__
            #
            code = compile(source, path, 'exec')
            #
            result = (source, code)
            #
        #
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
            #
            (source, code) = code
            #
            try:
                #
                if is_split_lines:
                    for line in source.split('\n'):
                        if line:
                            readline.add_history(line)
                            print(line)
                elif source:
                    print(source)
                    readline.add_history(source)
                    #
                #
            #
            finally:
                #
                # clean up temp file
                #
                if Clip.is_should_unlink(code):
                    os.unlink(code.co_filename)
                    #
                #
            #
        #
    #

    @staticmethod
    def is_should_unlink(code):
        is_should_unlink = Clip.is_unlink_tempfile and Clip.is_use_tempfile and not (Clip.is_reuse_pid_tempfile or Clip.is_reuse_global_tempfile)
        result = is_should_unlink
        return result
        #
    #
    @staticmethod
    def run(_globals = None, _locals = None):
        """Run the contents of the clipboard within the caller's frame."""
        result = None
        comp = Clip.compile()
        if comp is not None:
            #
            (source, code) = comp
            #
            result = (source, code)
            #
            # print(source)
            #
            frame = inspect.currentframe().f_back
            #
            # result = frame
            #
            if _globals is None:
                _globals = frame.f_globals
            if _locals is None:
                _locals = frame.f_locals
            #
            if Clip.is_use_tempfile:
                try:
                    #
                    exec(code, _globals, _locals)
                    #
                except Exception:
                    raise
                else:
                    #
                    # clean up temp file
                    #
                    if Clip.is_should_unlink(code):
                        os.unlink(code.co_filename)
                        #
                    #
            else:
                exec(code, _globals, _locals)
            #
        else:
            print('failed to compile')
        #
        return result
    #
#

