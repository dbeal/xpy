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
#
import re
#

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
from .Clip import Clip
from .ObjectAsDict import ObjectAsDict

class XPY(object):
    #
    Clip = Clip
    #
    xpy_ref_name = 'xpy'
    #

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

    def setup_tab_completion(self, execution):
        #
        if 1 or self.repo_history is not None:
            #
            import readline
            #
            if 0:
                #
                # TODO: fix this completer using Python AST parsing
                #
                def completer():
                    #
                    # closure around comp variable
                    #
                    #
                    # match builtins like str, buffer, etc.
                    #
                    try:
                        import __builtin__
                        builtins = __builtin__
                    except ModuleNotFoundError as e:
                        import builtins
                    #
                    builtins = builtins.__dict__.keys()
                    #
                    # match language keywords like while, do, import, etc.
                    #
                    import keyword
                    #
                    keywords = keyword.kwlist
                    #
                    comp = {}
                    #
                    def _matchfn(text):
                        if text.startswith('_'):
                            def _match(attr):
                                result = 0
                                if attr.startswith(text):
                                    result = 1
                                return result
                        else:
                            def _match(attr):
                                # print('attr', attr)
                                result = 0
                                if not attr.startswith('_'):
                                    if attr.startswith(text):
                                        result = 1
                                return result
                        return _match
                    #
                    def fn(text, state):
                        #
                        try:
                            #
                            # print('text', text, 'state', state)
                            # print('get_line_buffer', readline.get_line_buffer())
                            # print('get_begidx', readline.get_begidx())
                            # print('get_endidx', readline.get_endidx())
                            #
                            if state == 0:
                                #
                                # scan for matches only when state == 0
                                #
                                key = text.rsplit('.', 1)
                                #
                                # print('text', text, 'key', key)
                                #
                                if len(key) > 1:
                                    objexpr = key[0]
                                    text = key[1]
                                else:
                                    objexpr = None
                                    text = key[0]
                                #
                                # print('objexpr', objexpr, 'text', text)
                                #
                                if objexpr is not None:
                                    obj = eval(objexpr, execution.g, execution.l)
                                else:
                                    obj = None
                                #
                                # print('obj', obj)
                                #
                                # save to state dict
                                #
                                comp['obj'] = obj
                                comp['objexpr'] = objexpr
                                comp['text'] = text
                                #
                                # assumes dir(None) == dir()
                                #
                                if obj is not None:
                                    #
                                    # print('using obj', obj)
                                    #
                                    attrs = dir(obj)
                                else:
                                    #
                                    attrs = [
                                        keywords,
                                        builtins,
                                        execution.g.keys(),
                                        execution.l.keys(),
                                    ]
                                    #
                                    attrs = reduce(list.__add__, attrs, [])
                                    #
                                #
                                # print('attrs', attrs)
                                #
                                matches = filter(_matchfn(text), attrs)
                                #
                                comp['matches'] = matches
                                #
                            else:
                                obj = comp['obj']
                                objexpr = comp['objexpr']
                                text = comp['text']
                                #
                                matches = comp['matches']
                                #
                            #
                            if state < len(matches):
                                if objexpr is not None:
                                    result = objexpr + '.' + matches[state]
                                else:
                                    result = matches[state]
                                    #
                                #
                            #
                            else:
                                result = None
                                #
                            #
                            # print('result', result)
                            #
                            return result
                            #
                        except Exception as e:
                            self.print_exception(e)
                            result = None
                            #
                        #
                    return fn
                    #
                #
                # avoid delimiters so we can do our own parsing
                #
                readline.set_completer_delims('')
                readline.set_completer(completer())
                #
            else:
                #
                import rlcompleter
                #
                def completer(self):
                    def fn(text, state):
                        # combined namespace takes last precedence
                        # print('namespaces', namespaces)
                        assert type(text) is str
                        assert type(state) is int
                        # print('state', state)
                        #
                        combined = {}
                        combined.update(execution.g)
                        combined.update(execution.l)
                        #
                        comp = rlcompleter.Completer(combined)
                        #
                        # prime the matches
                        #
                        for i in range(state + 1):
                            result = comp.complete(text, i)
                        #
                        # avoid completing a function identifier with an open parens
                        #
                        result = result.rstrip('()')
                        #
                        return result
                    return fn
                    #
                #
                readline.set_completer(completer(self))
                #
            #
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
        self.Clip.copy(buf)
        
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

    def run(self, with_globals, with_locals, is_polluted = False, level = 0):

        g = with_globals
        l = with_locals

        if l is None:
            l = g

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
        execution.is_add_xpy_ref = True
        #
        execution.t0 = 0.0
        execution.t1 = 0.0
        #
        # process level
        #
        execution.level = level
        #
        # exception info from sys.exc_info()
        #
        execution.exc_info = sys.exc_info()
        execution.path = '<xpy>'
        #
        # for reading code input with readline support
        #
        raw_input = code.InteractiveConsole().raw_input

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
        #
        self.setup_tab_completion(execution)

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
                    exc_info = sys.exc_info()
                    execution.exc_info = exc_info
                    (exc_type, ex, tb) = exc_info
                    self.hello('\n')
                    self.print_exception(ex)
                except EOFError as e:
                    self.hello('\n')
                    break
                else:
                    pass
            #
            if self._is_use_substitutions:
                if source is not None:
                    while True:
                        #
                        expsrc = self._run_command_substitutions(source)
                        #
                        # print('expsrc', expsrc, 'source')
                        #
                        if expsrc is not None and expsrc is not source:
                            source = expsrc
                        else:
                            break
                        #
                    # may return None
                else:
                    expsrc = source
                #
            else:
                expsrc = source
            #
            # print('expsrc', expsrc)
            #
            if expsrc is not None:
                #
                execution.source = expsrc
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
                    # print('added expsrc', expsrc)
                    self.macro.append(expsrc)
        #
        if execution.level > 0:
            self.__pushprocessexit()
        #
        return True

    #
    # list of commands
    #
    # perform literal textual substitutions
    #
    _is_use_substitutions = True
    _substitution_escape = ':'
    _substitutions = {
        #
        # function_name: (args, body),
        #
        ':cdmod': (('modname',), 'xpy.cdmod("modname")', 'change current module'),
        ':cd': (('modname',), ':cdmod modname', 'shorthand for :cdmod'),
        ':cliprun': ((), '_cliprun = xpy.Clip.run()', 'run source code in system clipboard'),
        ':help': ((), 'xpy.list_commands()', 'list commands'),
        ':histcopy': (('line_count',), 'xpy.Clip.copy_from_history(line_count)', 'copy a number of lines from history into clipboard'),
        ':histpaste': ((), 'xpy.Clip.paste_into_history()', 'paste system clipboard source into history'),
        ':reload': ((), 'xpy.reload()', 'reload current module'),
        ':r': ((), ':reload', 'shorthand for :reload'),
    }
    _cmd_pat = re.compile('^(' + '|'.join(_substitutions.keys()) + ')\\b')
    #
    @anymethod
    def list_commands(self):
        #
        for (name, (sig, body, msg)) in self._substitutions.items():
            #
            line = ' '.join(map(str, [name] + list(sig) + ['=', body, msg]))
            #
            print(line)
        #
    #
    @anymethod
    def _parse_command(self, source):
        #
        cmd = ()
        #
        match = self._cmd_pat.search(source)
        #
        if match is not None:
            #
            fn = match.group(0)
            #
            args = source[len(fn):].split()
            #
            cmd = (fn, args)
            #
        #
        return cmd
    #
    @anymethod
    def _run_command_substitutions(self, source):
        #
        expsrc = source
        #
        if self._is_use_substitutions:
            #
            cmd = self._parse_command(source)
            #
            if cmd:
                #
                # print('cmd', cmd)
                #
                (fn, args) = cmd
                #
                # print('fn', fn, 'args', args)
                #
                if fn in self._substitutions:
                    #
                    match = self._substitutions[fn]
                    #
                    # print('match', match)
                    #
                    # function signature and body
                    #
                    # substitute the string 'x' in sig with arg within the
                    # expansion body
                    #
                    (sig, body, msg) = match
                    #
                    expansion = body
                    #
                    if len(args) == len(sig):
                        for (s, a) in zip(sig, args):
                            expansion = expansion.replace(s, a)
                            #
                        #
                        #print('expansion', expansion)
                        #
                        expsrc = expansion
                        #
                    else:
                        #
                        msg = ' '.join(map(str, [
                            'wrong number of arguments',
                            'for command substitution', source,
                            'expected', sig,
                            'received', args,
                        ]))
                        #
                        self.print_exception(TypeError(msg))
                        #
                        expsrc = None
                        #
                    #
                else:
                    msg = ' '.join(map(str, [
                        'unknown command substitution', source,
                    ]))
                    #
                    self.print_exception(TypeError(msg))
                    #
                    expsrc = ''
                #
            #
        #
        return expsrc
        #
    #
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

    #
    def get_self_from(self, obj):
        #
        if isinstance(obj, ObjectAsDict):
            #
            _self = getattr(obj._obj, 'self', None)
            #
        else:
            _self = obj.get('self')
            #
        #
        return _self
        #
    #
    @staticmethod
    def runin(obj):
        #
        # run clipboard source with obj.__dict__ as locals()
        #
        mod = XPY.get_obj_module(obj)
        #
        _globals = mod.__dict__
        #
        _locals = ObjectAsDict(obj)
        #
        code = XPY.Clip.run(_globals, _locals)
        #
        result = code
        #
        return result
        #
    #
    @classmethod
    def get_obj_name(self, obj):
        #
        if isinstance(obj, type):
            #
            # class name
            #
            name = obj.__name__
        else:
            #
            # add () parens to indicate instance
            #
            name = obj.__class__.__name__ + '()'
            #
        #
        return name
    #
    def get_name_from(self, obj):
        #
        if isinstance(obj, ObjectAsDict):
            #
            name = self.get_obj_name(obj._obj)
            #
        else:
            name = obj.get('__name__')
            #
        #
        return name
        #
    #
    def get_exec_name(self, execution):
        #
        g = execution.g
        l = execution.l
        #
        globalname = self.get_name_from(g)
        #
        path = [globalname]
        #
        if l is not g:
            #
            localname = self.get_name_from(l)
            #
            if localname is not None:
                #
                path.append(localname)
                #
            #
        #
        _self = self.get_self_from(l)
        #
        if _self is None:
            #
            _self = self.get_self_from(g)
            #
        #
        if _self is not None:
            #
            self_name = self.get_obj_name(_self)
            #
            path.append(self_name)
        #
        full_name = ' '.join(path)
        #
        result = full_name
        #
        return result
        #
    #
    def get_prompt(self, execution):
        # readline gets messed up with color prompt
        # prompt = Colors.GREY + ('%0.9f' % (self.t1 - self.t0)) + Colors.NORM + ' ' + Colors.GREEN + '!' + Colors.YELLOW + '!' + Colors.BLUE + '!' + Colors.NORM + ' '
        #
        exec_name = self.get_exec_name(execution)
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
            exec_name,
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
            execution.exc_info = sys.exc_info()
            self.print_exception(execution.exc_info[1])
        else:
            #
            if execution.is_polluted:
                #
                # pollute the environment with xpy objects
                #
                self.pollute(execution.g, execution.l)
            #
            if execution.is_add_xpy_ref:
                self.add_xpy_ref(execution.g, execution.l)
            #
            #
            # Time each code execution.
            #
            try:
                execution.t0 = time.time()
                self.execution = execution
                #
                exec(execution.code, execution.g, execution.l)
            except:
                execution.t1 = time.time()
                #
                execution.exc_info = sys.exc_info()
                #
                # self.print_traceback(execution.exc_info)
                self.print_execution_info(execution)
            else:
                #
                # print('ok')
                #
                execution.result = True
            finally:
                #
                # break cyclic references
                #
                del self.execution
                execution.t1 = time.time()
            #
            # post execution pollution
            #
            if execution.is_polluted:
                #
                # TODO: clean up pollution
                #
                pass
            #
            if execution.is_add_xpy_ref:
                #
                # self.remove_xpy_ref(execution.g, execution.l)
                #
                pass
            #
        #
        return execution.result
        #
    #
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
                code = compile(source, execution.path, 'exec')
            else:
                code = compile(source, execution.path, 'single')
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
    def print_traceback(self, exc_info = None, max_context_lines = 1):
        top = self.get_traceback_top(exc_info)
        self.print_backframes(top, max_context_lines = max_context_lines)

    @anymethod
    def get_traceback_top(self, exc_info = None):
        if exc_info is None:
            exc_info = sys.exc_info()
        (_, ex, tb) = exc_info
        top = tb
        while top.tb_next is not None:
            top = top.tb_next
        top = top.tb_frame
        return top

    @anymethod
    def print_backframes(self, top, tb = None, max_context_lines = 1):
        import inspect

        # max_context_lines = 3
        #
        is_top_only = False

        frames = [top]
        while frames[-1].f_back is not None:
            frames.append(frames[-1].f_back)

        frames.reverse()

        last_path = None
        is_ellipsis = False
        if_print_funcname = False

        for frame in frames:
            path = self.get_frame_path(frame)

            if path != last_path:
                last_path = path
                #
                path = path + Colors.WHITE + ':'
                #
                self.hello(Colors.WHITE + path + Colors.NORM + '\n')
                #
                is_ellipsis = False
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
                        is_ellipsis = False
                    elif abs(linedelta) == max_context_lines:
                        if not is_ellipsis:
                            is_ellipsis = True
                            self.hello(Colors.WHITE + '...' + Colors.NORM + '\n')
                    elif lineno == firstlineno:
                        if if_print_funcname:
                            self.print_context_line(color, lineno, line)
                            is_ellipsis = False
                    else:
                        #
                        # line ignored
                        #
                        pass
                    #

    @classmethod
    def get_frame_path(self, frame):
        #
        try:
            path = inspect.getfile(frame)
        except TypeError as e:
            path = '<unknown path>'
        #
        return path
        #
    #
    @classmethod
    def print_execution_info(self, execution):
        #
        exc_info = execution.exc_info
        #
        top = self.get_traceback_top(exc_info)
        #
        path = self.get_frame_path(top)
        #
        if path != execution.path:
            #
            self.print_traceback(exc_info, max_context_lines = 1)
            # trace = ''.join([Colors.WHITE, path, ': ', str(top.f_lineno), ' ', Colors.NORM])
            #
            # self.hello(trace + '\n')
            #
        #
        (_, ex, tb) = exc_info
        #
        self.print_exception(ex)
        #
    #
    @classmethod
    def print_exception(self, ex = None):
        if ex is None:
            exc_info = sys.exc_info()
            (_, ex, tb) = exc_info
        #
        self.hello(Colors.RED + str(ex.__class__.__module__ + '.' + ex.__class__.__name__) + Colors.NORM + ((': ' + Colors.YELLOW + str(ex) + Colors.NORM) if str(ex) else '') + '\n')
        #
        if isinstance(ex, SyntaxError):
            self.print_syntax_error(ex)
            #
        #
    #
    @classmethod
    def print_syntax_error(self, ex):
        #
        text = ex.text
        #
        if (text is not None) and (ex.offset is not None):
            self.print_context_line(Colors.NORM, ex.lineno, text[:ex.offset - 1] + Colors.BGRED + Colors.WHITE + text[ex.offset - 1: ex.offset] + Colors.NORM + text[ex.offset:])
            #
        #
    #
    def pollute(self, g, l):
        #
        # be nice and add some gadgets to the console namespace
        #
        pollution = OrderedDict(filter(lambda kv: not kv[0].startswith('_'), ConsoleImports.__dict__.items()))
        #
        # pollute locals
        #
        d = l
        #
        for (k, v) in pollution.items():
            if k in d:
                if d[k] is not v:
                    #
                    print(' '.join(['warning:', k, 'shadows', 'global']))
                    #
                #
            #
            d.update(pollution)
            #
        #
    #
    def add_xpy_ref(self, _globals, _locals):
        """
        add reference to this object to __builtins__ dict
        """
        if 1:
            add_to = __builtins__
        else:
            add_to = _globals
        #
        name = self.xpy_ref_name
        #
        if name in add_to:
            if add_to[name] is not self:
                    #
                    print(' '.join(['warning:', name, 'shadows', 'local']))
                    #
                #
            #
        #
        add_to[name] = self
        #
    #
    def newloc(___xpy___, **new_locals):
        #
        # use globals from execution frame along with a new locals dict
        #
        ___xpy___.switch(___xpy___.execution.g, new_locals)
        #
    #
    def switch(self, g, l):
        #
        # Python requires exec globals to be a dict
        #
        assert type(g) is dict
        #
        self.execution.g = g
        self.execution.l = l
        #
        if self.execution.is_polluted:
            self.pollute(self.execution.g, self.execution.l)
            #
        #
        if self.execution.is_add_xpy_ref:
            self.add_xpy_ref(self.execution.g, self.execution.l)
            #
        #
        self.setup_tab_completion(self.execution)
        #
    #
    def closure(self):
        #
        # TODO: create a closure and switch context
        #
        def fn():
            # global self
            g = self.execution.g
            # del self
            #
            # don't use context manager since repo history will be written
            #
            xpy = XPY()
            #
            l = locals()
            #
            del l['g']
            del l['self']
            #
            l['xpy'] = xpy
            #
            result = xpy.run(g, locals())
            #
            print('exiting fn')
            #
            return result
            #
        #
        fn()
        #
    #
    def cdobj(self, obj, l_obj = None):
        #
        # use object dict as locals
        #
        if l_obj is not None:
            #
            # use two objects
            #
            self.switch(ObjectAsDict(obj), ObjectAsDict(l_obj))
        else:
            self.switch(self.execution.g, ObjectAsDict(obj))
        #
    #
    @classmethod
    def get_obj_module(self, obj):
        #
        import types
        #
        if isinstance(obj, types.ModuleType):
            mod = obj
        else:
            if isinstance(obj, type):
                cls = obj
            else:
                cls = obj.__class__
            #
            mod = sys.modules[cls.__module__]
            #
        #
        result = mod
        #
        return result
    #
    @classmethod
    def getpath(self, obj):
        #
        mod = self.get_obj_module(obj)
        #
        path = mod.__file__
        #
        result = path
        #
        return result
        #
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
        is_use_globals = 1
        is_use_execution_context = 0
        #
        _globals = mod.__dict__
        #
        if is_use_globals:
            _locals = _globals
        elif is_use_execution_context:
            _locals = self.execution.l
        else:
            #
            # create a locals dict and store it on the module in a hidden variable
            #
            localsname = '__xpy_locals__'
            #
            if localsname not in mod.__dict__:
                mod.__dict__[localsname] = {}
            #
            _locals = mod.__dict__[localsname]
            #
        #
        self.switch(_globals, _locals)
        #
        # self.pollute(self.g, self.l)
        #
        # add reference to module within locals
        #
        # self.l['__mod__'] = mod

    @classmethod
    def _reload(self, mod):
        #
        # in order to work with python2 or 3
        #
        if 'reload' in __builtins__:
            #
            # python 2
            #
            reload(mod)
            #
        else:
            #
            # python 3
            #
            import importlib
            importlib.reload(mod)
            #
        #
    #
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
                    #
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

def start_console(with_globals = None, with_locals = None, is_polluted = False):
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
        result = xpy.run(with_globals, with_locals, is_polluted = is_polluted)
        #

    return result

xpy_start_console = start_console

class Main(object):
    @classmethod
    def main(self):
        xpy_start_console()
