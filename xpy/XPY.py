#!/usr/bin/env python3

import sys
import os
import code
import inspect
import traceback

from .Clip import Clip
from .Plot import Plot
from .Colors import Colors

from cytoolz import curry

R0 = curry(os.read)(0)
W1 = curry(os.write)(1)
W2 = curry(os.write)(2)

class XPY(object):

    # TODO: better handling of multiple console instances
    is_readline_busy = False

    def __init__(self):
        # holders for the compiled code
        self.source = None
        self.code = None

    def hello(self, msg):
        """Encode and send a message to the programmer."""
        W2(msg.encode())

    def __enter__(self):
        if self.is_readline_busy:
            self.hello('readline is busy\n')
            self.repo_history = None
        else:
            XPY.is_readline_busy = True
            self.setup_history()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.hello(str(('__exit__', 'self', self, 'exc_type', exc_type, 'exc_val', exc_val, 'exc_tb', exc_tb)) + '\n')
        self.commit_history()

    def setup_tab_completion(self, namespaces):
        if self.repo_history is not None:
            import rlcompleter
            import readline
            def completer(namespaces):
                comps = [rlcompleter.Completer(ns) for ns in namespaces]
                def fn(text, state):
                    for (i, comp) in enumerate(comps):
                        c = comp.complete(text, state)
                        if c is not None:
                            # self.hello(str(('found completion of', text, 'in namespace', i, c)) + '\n')
                            return c
                    return None
                return fn
            readline.set_completer(completer(namespaces))
            readline.parse_and_bind('tab: complete')
        else:
            self.hello('not setting up tab completion\n')

    def setup_history(self):
        from .RepoHistory import RepoHistory
        self.repo_history = RepoHistory('~/.pyhist')
        self.repo_history.clone()

    def commit_history(self):
        if self.repo_history is not None:
            self.repo_history.commit()
        else:
            self.hello('not committing history\n')

    def run(self, frame = None):
        from six.moves import input

        if frame is None:
            import inspect
            frame = inspect.currentframe()
            # go back to the caller's frame
            frame = frame.f_back

        # make copies of the globals and locals dicts so they can be owned by
        # the new frame
        g = dict(frame.f_globals)
        l = dict(frame.f_locals)

        # don't keep a reference to the frame
        del frame

        # be nice and add some gadgets to the console namespace
        g.update(globals())

        l['xpy'] = self

        # readline can only support one instance at a time
        self.setup_tab_completion([l, g])

        while True:
            try:
                try:
                    line = input('!!! ')
                except EOFError as e:
                    self.hello('\n')
                    break
                else:
                    self.exec_source(line, g, l)
            except:
                (_, ex, tb) = sys.exc_info()

                self.print_traceback(tb)
                self.print_exception(ex)

        return 33

    def exec_source(self, source, g, l):
        source = source.rstrip()
        if source:
            self.source = source
            if '\n' in source:
                self.code = compile(source, '<interactive console>', 'exec')
            else:
                self.code = compile(source, '<interactive console>', 'single')
            exec(self.code, g, l)

    def print_context_line(self, color, lineno, line):
        self.hello(' ' + color + ('% 4d' % lineno) + Colors.NORM + ': ' + color + line.rstrip() + Colors.NORM + '\n')

    def getsourcelines(self, frame):
        import inspect
        result = []
        path = inspect.getfile(frame)

        with open(path) as infile:
            lines = list(infile)
            firstlineno = frame.f_code.co_firstlineno
            lnotab = frame.f_code.co_lnotab
            if type(lnotab) is str:
                lnotab = [ord(l) for l in lnotab]
            frame_line_count = sum([lnotab[i * 2 + 1] for i in range(len(lnotab) // 2)]) + 1
            for i in range(firstlineno, firstlineno + frame_line_count):
                result.append(lines[i - 1])
            result = [result, firstlineno]

        return result

    def print_traceback(self, tb):
        import inspect

        is_top_only = False

        top = tb
        while top.tb_next is not None:
            top = top.tb_next
        top = top.tb_frame

        frames = [top]
        while frames[-1].f_back is not None:
            frames.append(frames[-1].f_back)

        frames.reverse()

        bottom = frames[0]

        last_path = None

        for frame in frames:
            try:
                path = inspect.getfile(frame)
            except TypeError as e:
                path = '<unknown path>'

            if path != last_path:
                last_path = path
                path = path + Colors.WHITE + ':'
            else:
                path = '...'

            self.hello(Colors.WHITE + path + Colors.NORM + '\n')

            try:
                sourcelines = self.getsourcelines(frame)
            except IOError as e:
                if frame.f_code == self.code:
                    lines = self.source.split('\n')
                    firstlineno = self.code.co_firstlineno
                    sourcelines = [lines, firstlineno]
                else:
                    sourcelines = []

            if sourcelines:
                (lines, firstlineno) = sourcelines
                for (lineno, line) in zip(range(firstlineno, firstlineno + len(lines)), lines):
                    if frame == tb.tb_frame:
                        if lineno == tb.tb_lineno:
                            color = Colors.RED
                        elif lineno == frame.f_lineno:
                            color = Colors.YELLOW
                        elif is_top_only and lineno > tb.tb_lineno and lineno > frame.f_lineno:
                            break
                        else:
                            color = Colors.NORM
                    else:
                        if lineno == frame.f_lineno:
                            if frame.f_code == self.code:
                                color = Colors.MAGENTA
                            else:
                                color = Colors.RED
                        elif is_top_only and lineno > frame.f_lineno:
                            break
                        else:
                            color = Colors.NORM

                    self.print_context_line(color, lineno, line)

    def print_exception(self, ex):
        self.hello(Colors.RED + str(ex.__class__) + Colors.NORM + ': ' + Colors.YELLOW + str(ex) + Colors.NORM + '\n')

def xpy_start_console():
    import inspect
    result = 1
    with XPY() as xpy:
        result = xpy.run(inspect.currentframe().f_back)
    return result

