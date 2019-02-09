#!/usr/bin/env python3
#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

import sys
import os
import code
import inspect
import traceback
import time
import importlib

from cytoolz import curry

import greenlet

from collections import OrderedDict
import code

class ResumEx(Exception):
    pass

#
# resumable exception
#
def resumex(ex):
    while True:
        if isinstance(ex, Exception):
            XPY.print_exception(ex)
            if isinstance(ex, ResumEx):
                ex = greenlet.getcurrent().parent.switch()
            else:
                ex = greenlet.getcurrent().parent.throw(ex)
        else:
            ex = greenlet.getcurrent().parent.switch()

ResumEx.resumex = greenlet.greenlet(resumex)

#
# raise resumable exception
#
def rese(ex):
    result = ResumEx.resumex.switch(ex)
    return result

if 0:
    import collections
    #
    if hasattr(collections, 'abc'):
        from collections.abc import Mapping
    else:
        from collections import Mapping
    #
    class ShadowDict(Mapping):
        #
        # write to self.__dict__ directly to shadow a value in another dict
        #

        #
        def __init__(self, other):
            self.other = other
            #
        #
        def __iter__(self):
            return []
            #
        #
        def __len__(self):
            return 0
            #
        #
        def __getitem__(self, name):
            #
            print('looking for name', name, 'in', 'self', self.__dict__.keys())
            #
            if name in self.__dict__:
                #
                print('found', name, 'in', self.__dict__.keys())
                #
                result = self.__dict__[name]
                #
                if name in self.other:
                    print(' '.join([self.__class__.__name__, 'is', 'shadowing', name, 'in', 'other']))
            else:
                #
                print('looking for name', name, 'in', 'other', self.__dict__.keys())
                #
                result = self.other[name]
            #
            return result
            #
        #
        def __setitem__(self, name, value):
            #
            if name in self.__dict__:
                self.__dict__[name] = value
            else:
                self.other[name] = value
            #
    #

from .Colors import Colors
from .Micros import Micros as M
from .ConsoleImports import ConsoleImports
from .Anymethod import anymethod

class XPY(object):

    # TODO: better handling of multiple console instances
    is_readline_busy = False

    def __init__(self):
        # holders for the compiled code
        self.source = []
        self.code = None

    @classmethod
    def hello(self, text):
        """Encode and send text to the programmer."""
        return M.w2(text.encode())

    @classmethod
    def Hello(self, msg):
        """Call hello with {template} tokens formatted to the caller's local scope."""
        return self.hello(msg.format(**inspect.currentframe().f_back.f_locals))

    @classmethod
    def put(self, *msg):
        """Send serialized message to the programmer."""
        return M.w2((repr(msg) + '\n').encode())

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
        if 1 or self.repo_history is not None:
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

    @staticmethod
    def copy_from_history(line_count):
        l = readline.get_current_history_length()
        lines = []
        for i in range(max(l - line_count, 0), l):
            line = readline.get_history_item(i)
            lines.append(line)
        buf = '\n'.join(lines)
        Clip.copy(buf)
        
    def setup_tracing(self):
        def trace(frame, event, arg):
            if event == 'exception':
                # print('frame', frame, 'event', event, 'arg', arg)
                (exc_type, ex, tb) = arg
                # self.print_exception(ex)
                # print('ex', ex, 'tb', tb)
            # sys.settrace(None)
            return trace
        sys.settrace(trace)
        # xpy_start_console()

    def setup_greenlet(self):
        pass

    def record(self):
        if not self.is_recording:
            self.macro[:] = []
            self.is_recording = 1
            #
            # print('started macro record')
            #

    def stop(self):
        if self.is_recording:
            self.is_recording = 0
            #
            # print('stopped macro record')
            #

            #
            # skip initial record command
            #
            self.macro[:] = self.macro[1:]

    def play(self):
        self.stop()
        #
        # print('playing macro', self.macro)
        #
        self.input.extend(self.macro)

    def run(self, with_globals, with_locals, is_polluted = True):

        g = with_globals
        l = with_locals

        if l is None:
            l = g

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

        # self.setup_tracing()
        # self.setup_profiler()

        #
        # setup macro
        #
        self.is_recording = 0
        self.macro = []
        #
        # macro is placed in input queue
        #
        self.input = []
        #
        # create type
        #
        Execution = type('Execution', (), {})
        #
        execution = Execution()
        #
        # save references to environment
        #
        execution.g = g
        execution.l = l
        #
        execution.is_polluted = is_polluted
        #
        execution.t0 = 0.0
        execution.t1 = 0.0
        #
        # process level
        #
        execution.level = 0
        #
        # for switching context into module
        #
        self.locals = locals()
        #
        # for reading code input with readline support
        #
        raw_input = code.InteractiveConsole().raw_input

        while True:
            prompt = self.get_prompt(execution)
            # os.write(2, prompt)
            #
            source = None
            #
            if len(self.input):
                #
                # print('input', self.input)
                #
                source = '\n'.join(self.input)
                #
                self.input[:] = []
                #
            else:
                try:
                    source = raw_input(prompt)
                except KeyboardInterrupt as ke:
                    (exc_type, ex, tb) = sys.exc_info()
                    self.hello('\n')
                    self.print_exception(ex)
                except EOFError as e:
                    self.hello('\n')
                    break
                else:
                    pass
            #
            # print('source', source)
            #
            if source is not None:
                #
                execution.source = source
                #
                if self.compile_and_exec(execution):
                    #
                    # print('ok')
                    #
                    pass
                #
                # record afterwards
                #
                if self.is_recording:
                    # print('added source', source)
                    self.macro.append(source)
        #
        if execution.level > 0:
            self.__pushprocessexit()
        #
        return True

    @anymethod
    def format_times(self, t0, t1):
        dt = t1 - t0
        result = '%0.9f' % dt
        #
        if 0:
            #
            # show suffix
            #
            dt = t1 - t0
            #
            if dt < 1e-6:
                #
                # nanoseconds
                #
                suf = 'ns'
                scale = 1e9
            elif dt < 1e-3:
                suf = 'us'
                scale = 1e6
            elif dt < 1:
                suf = 'ms'
                scale = 1e3
            else:
                suf = 's'
                scale = 1e0

            dti = '%0.3f' % (dt * scale)
            result = str(dti) + suf
            result = '%0.9f' % dt + ' (' + result + ')'

        if 0:
            prefix = ''.join((
                Colors.RLGREEN,
                '+',
                Colors.RLNORM,
            ))
            fill = ''.join((
                Colors.RLGREY,
                '.',
                Colors.RLNORM,
            ))
            width = 9
            dt = int(1e9 * (t1 - t0))
            n = dt
            return [c
                for ns in [str(n)]
                for pad in [fill * max(width - len(ns), 0)]
                for c in [pad + ns]
            ][0]

        return result

    def get_prompt(self, execution):
        # readline gets messed up with color prompt
        # prompt = Colors.GREY + ('%0.9f' % (self.t1 - self.t0)) + Colors.NORM + ' ' + Colors.GREEN + '!' + Colors.YELLOW + '!' + Colors.BLUE + '!' + Colors.NORM + ' '
        #
        prompt = ''.join((
            Colors.RLGREEN,
            '+' * (execution.level + 1),
            Colors.RLNORM, ' ',
            self.format_times(execution.t0, execution.t1),
            Colors.RLNORM, ' ',
            Colors.RLBLUE,
            #
            # name of current module context
            #
            execution.g['__name__'],
            #
            Colors.RLNORM, ' ',
            Colors.RLGREY, '!', '!', '!',
            #
            Colors.RLNORM, ' ',
            # Colors.HOME(100, 50),
        ))
        if 0:
            for c in Colors.__dict__:
                if type(c) is str:
                    prompt = prompt.replace(c, '\001' + c + '\002')
        result = prompt
        return result

    def compile_and_exec(self, execution):
        #
        execution.result = False
        #
        try:
            execution = self.compile_source(execution)
        except:
            self.print_exception(sys.exc_info()[1])
        else:
            #
            if execution.is_polluted:
                #
                # pollute the environment with xpy objects
                #
                self.pollute(execution.g, execution.l)
            #
            #
            # Time each code execution.
            #
            try:
                execution.t0 = time.time()
                self.execution = execution
                #
                exec(execution.code, execution.g, execution.l)
                #
                # break cyclic references
                #
                del self.execution
                execution.t1 = time.time()
            except:
                execution.t1 = time.time()
                #
                self.print_traceback()
                self.print_exception()
            else:
                #
                # print('ok')
                #
                execution.result = True
            #
            # post execution pollution
            #
            if execution.is_polluted:
                #
                # TODO: clean up pollution
                #
                pass


        return execution.result

    def print_syntax_error(self, se):
        with open(se.filename) as infile:
            lines = list(infile)
            se.filename
            se.lineno
            se.msg
            se.offset
            se.text

    def compile_source(self, execution):
        source = execution.source
        source = source.rstrip()
        if source == '.':
            if len(self.source):
                source = self.source[-1]
                #
                assert execution.code
            else:
                source = 'None'
                execution.code = None
        else:
            execution.code = None
        #
        if not source:
            source = 'None'
        #
        if not execution.code:
            self.source.append(source)
            if '\n' in source:
                code = compile(source, '<interactive console>', 'exec')
            else:
                code = compile(source, '<interactive console>', 'single')
            execution.code = code
        return execution

    @classmethod
    def print_context_line(self, color, lineno, line):
        self.hello(' ' + color + ('% 4d' % lineno) + Colors.NORM + ': ' + color + (line or '').rstrip() + Colors.NORM + '\n')

    @anymethod
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

    code = None
    source = []

    @anymethod
    def print_traceback(self, tb = None):
        top = self.get_traceback_top(tb)
        self.print_backframes(top)

    @anymethod
    def get_traceback_top(self, tb = None):
        if tb is None:
            (_, ex, tb) = sys.exc_info()
        top = tb
        while top.tb_next is not None:
            top = top.tb_next
        top = top.tb_frame
        return top

    @anymethod
    def print_backframes(self, top, tb = None):
        import inspect

        max_context_lines = 3
        #
        is_top_only = False

        frames = [top]
        while frames[-1].f_back is not None:
            frames.append(frames[-1].f_back)

        frames.reverse()

        last_path = None

        for frame in frames:
            try:
                path = inspect.getfile(frame)
            except TypeError as e:
                path = '<unknown path>'

            if path != last_path:
                last_path = path
                path = path + Colors.WHITE + ':'
                self.hello(Colors.WHITE + path + Colors.NORM + '\n')
            else:
                path = '...'

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
                    if tb is not None and frame == tb.tb_frame:
                        linedelta = lineno - tb.tb_lineno
                        #
                        if lineno == tb.tb_lineno:
                            color = Colors.RED
                        elif lineno == frame.f_lineno:
                            color = Colors.YELLOW
                        elif is_top_only and lineno > tb.tb_lineno and lineno > frame.f_lineno:
                            break
                        else:
                            color = Colors.NORM
                    else:
                        linedelta = lineno - frame.f_lineno
                        #
                        if lineno == frame.f_lineno:
                            if frame.f_code == self.code:
                                color = Colors.MAGENTA
                            else:
                                color = Colors.RED
                        elif is_top_only and lineno > frame.f_lineno:
                            break
                        else:
                            color = Colors.NORM

                    if abs(linedelta) < max_context_lines:
                        self.print_context_line(color, lineno, line)
                    elif abs(linedelta) == max_context_lines:
                        self.hello(Colors.WHITE + '...' + Colors.NORM + '\n')

    @classmethod
    def print_exception(self, ex = None):
        if ex is None:
            (_, ex, tb) = sys.exc_info()
        self.hello(Colors.RED + str(ex.__class__.__module__ + '.' + ex.__class__.__name__) + Colors.NORM + ((': ' + Colors.YELLOW + str(ex) + Colors.NORM) if str(ex) else '') + '\n')
        if isinstance(ex, SyntaxError):
            if ex.offset is not None:
                self.print_context_line(Colors.NORM, ex.lineno, ex.text[:ex.offset - 1] + Colors.BGRED + Colors.WHITE + ex.text[ex.offset - 1: ex.offset] + Colors.NORM + ex.text[ex.offset:])
            else:
                self.print_context_line(Colors.NORM, ex.lineno, ex.text)

    #
    def pollute(self, g, l):
        #
        # be nice and add some gadgets to the console namespace
        #
        pollution = OrderedDict(filter(lambda kv: not kv[0].startswith('_'), ConsoleImports.__dict__.items()))
        #
        for (k, v) in pollution.items():
            if k in g:
                if g[k] is not v:
                    #
                    print(' '.join(['warning:', k, 'shadows', 'global']))
                    #
            g.update(pollution)
        #
        # add more trinkets
        #
        k = 'xpy'
        #
        if k in l:
            if l[k] is not self:
                    #
                    print(' '.join(['warning:', k, 'shadows', 'local']))
                    #
        l[k] = self
    #
    def switch(self, g, l):
        #
        self.setup_tab_completion([g, l])
        #
        self.execution.g = g
        self.execution.l = l
        #
        if self.execution.is_polluted:
            self.pollute(self.execution.g, self.execution.l)
    #
    def cdmod(self, modname, package = None):
        #
        back = inspect.currentframe().f_back
        #
        back__name__ = back.f_globals['__name__']
        #
        back__package__ = back.f_globals['__package__']
        #
        if modname == '..':
            #
            # cd up to parent module
            #
            modname = back__name__.rsplit('.', 1)[0]
            package = back__package__
        #
        # switch context to module
        #
        mod = importlib.import_module(modname, back__package__)

        #
        # switch context
        #
        # in module context, locals() is globals()
        #
        self.switch(mod.__dict__, mod.__dict__)
        #
        # self.pollute(self.g, self.l)
        #
        # add reference to module within locals
        #
        # self.l['__mod__'] = mod

    @classmethod
    def _reload(self, modname):
        #
        # in order to work with python2 or 3
        #
        if 'reload' in __builtins__:
            # python 2
            reload(modname)
        else:
            # python 3
            import importlib
            importlib.reload(modname)

    def reload(self, modname = None):
        #
        # reload only the current module
        #
        back = inspect.currentframe().f_back
        #
        back__name__ = back.f_globals['__name__']
        #
        if modname is None:
            #
            modname = back__name__

        if modname is not None:
            #
            #
            #
            mod = sys.modules.get(modname)
            #
            if mod is not None:
                #
                # mod is replaced
                #
                # erase everything in module except for name
                #
                mod__name__ = mod.__name__
                #
                o = mod.__dict__.copy()
                #
                mod.__dict__.clear()
                #
                mod.__name__ = mod__name__
                #
                try:
                    #
                    # choose python2 or python3 import
                    #
                    self._reload(mod)
                except Exception as e:
                    #
                    # restore old module keys
                    #
                    mod.__dict__.update(o)
                    #
                    # forward exception
                    #
                    raise
                else:
                    pass
            else:
                #
                # print('initial import of ' + modname)
                #
                #
                mod = importlib.import_module(modname)
        #
        # reload current module
        #

        #
        # switch to new reloaded module
        #
        self.cdmod(modname)

    def refresh(self, regex):
        #
        # reload the current module
        #
        back = inspect.currentframe().f_back
        #
        back__name__ = back.f_globals['__name__']
        #
        # unload all modules by regex pattern and then reload the current module
        #
        import re
        #
        pat = re.compile('^' + regex)
        #
        match_count = 0
        #
        for (name, mod) in list(sys.modules.items()):
            if pat.match(name):
                sys.modules.pop(name)
                match_count += 1
        #
        if not match_count:
            print('no modules matched pattern', regex)
        #
        # now reload current module
        #
        self.reload(back__name__)

    def __pushprocessexit(self):
        """
        invoked by child when pushed child process exits
        """
        self.repo_history.write_history()
        #
        # print('child wrote history file')
        #
        os._exit(0)

    def push(self):
        """
        fork and have parent wait
        used to save and restore state 
        """
        pid = os.fork()
        if pid:
            os.waitpid(pid, 0)
            #
            self.repo_history.read_history()
            #
            # print('parent read history file')
            #
        else:
            #
            # wont work unless called within an evaluation
            #
            self.execution.level += 1
            #
            # self.repo_history.write_history()

def start_console(with_globals = None, with_locals = None, is_polluted = True):
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
        #
        # with_locals['xpy'] = xpy
        #
        result = xpy.run(with_globals, with_locals, is_polluted = is_polluted)

    return result

xpy_start_console = start_console
