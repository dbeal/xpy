#!/usr/bin/env python3

import sys
import os
import code
import inspect
import traceback
import time

from cytoolz import curry

from .Colors import Colors
from .Micros import Micros as m
from .ConsoleImports import ConsoleImports

class XPY(object):

    # TODO: better handling of multiple console instances
    is_readline_busy = False

    def __init__(self):
        # holders for the compiled code
        self.source = []
        self.code = None

    def hello(self, text):
        """Encode and send text to the programmer."""
        return m.w2(text.encode())

    def Hello(self, msg):
        """Call hello with {template} tokens formatted to the caller's local scope."""
        return self.hello(msg.format(**inspect.currentframe().f_back.f_locals))

    def put(self, *msg):
        """Send serialized message to the programmer."""
        return m.w2((repr(msg) + '\n').encode())

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
            self.put('__exit__', 'self', self, 'exc_type', exc_type, 'exc_val', exc_val, 'exc_tb', exc_tb)
        self.commit_history()

    def setup_tab_completion(self, namespaces):
        if self.repo_history is not None:
            import rlcompleter
            import readline
            def completer(namespaces):
                def fn(text, state):
                    # combined namespace takes last precedence
                    combined = {}
                    for ns in namespaces:
                        combined.update(ns)
                    comp = rlcompleter.Completer(combined)
                    # prime the matches
                    for i in range(state + 1):
                        result = comp.complete(text, i)
                    return result
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

    def run(self, with_globals, with_locals, is_polluted = True):
        from six.moves import input

        g = with_globals
        l = with_locals

        if l is None:
            l = g

        if is_polluted:
            # be nice and add some gadgets to the console namespace
            # g.update(globals())
            g.update(filter(lambda kv: not kv[0].startswith('_'), ConsoleImports.__dict__.items()))
            # add more trinkets
            l['xpy'] = self
        else:
            # give a hoot and don't pollute
            pass

        # readline can only support one instance at a time

        # Make sure to search both global and local namespaces for
        # autocomplete, but the results aren't duplicated if locals and globals
        # are identical.
        #
        # In the stock Python interactive console, locals() is globals(), so
        # rlcompleter only bothers to search globals(), i.e., console __main__.
        #
        # In the event that globals() is not locals(), and a local parameter
        # shadows a global, the local variable takes precedence.
        self.setup_tab_completion([g, l])

        # Time each code execution.
        self.t0 = 0.0
        self.t1 = 0.0

        while True:
            # readline gets messed up with color prompt
            # prompt = Colors.GREY + ('%0.9f' % (self.t1 - self.t0)) + Colors.NORM + ' ' + Colors.GREEN + '!' + Colors.YELLOW + '!' + Colors.BLUE + '!' + Colors.NORM + ' '
            prompt = ''.join((('%0.9f' % (self.t1 - self.t0)), ' ', '!', '!', '!', ' '))
            try:
                try:
                    line = input(prompt)
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
        self.source.append(source)
        source = source.rstrip()
        if not source:
            source = 'None'
        if '\n' in source:
            self.code = compile(source, '<interactive console>', 'exec')
        else:
            self.code = compile(source, '<interactive console>', 'single')
        self.t0 = time.time()
        exec(self.code, g, l)
        self.t1 = time.time()

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
                    lines = self.source[-1].rstrip().split('\n')
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

def xpy_start_console(with_globals = None, with_locals = None):
    """
    If run without globals or locals, take those values from the caller's
    frame.
    """
    result = 1

    import inspect

    frame = inspect.currentframe().f_back

    if with_globals is None:
        with_globals = frame.f_globals

    if with_locals is None:
        with_locals = frame.f_locals

    with XPY() as xpy:
        result = xpy.run(with_globals, with_locals, is_polluted = True)

    return result

