#!/usr/bin/env python3

import tempfile
import binascii
import os

class Clip(object):
    @staticmethod
    def get():
        result = None
        with os.popen('xsel -o') as infile:
            result = infile.read()
        return result

    @staticmethod
    def put(buf):
        with os.popen('xsel -i', mode = 'w') as outfile:
            outfile.write(buf)
        
    @staticmethod
    def show():
        print(Clip.get().rstrip('\n'))

    @staticmethod
    def compile():
        result = None
        source = Clip.get()
        if source:
            # fix indent
            lines = source.split('\n')
            lines = list(filter(lambda line: len(line.strip()) > 0, lines))
            min_indent = reduce(lambda i0, i1: min(i0, i1), map(lambda line: len(line) - len(line.lstrip('\t ')), lines))
            source = '\n'.join((map(lambda line: line[min_indent:], lines)))

            code = compile(source, __name__, 'exec')
            result = (source, code)
        return result

    @staticmethod
    def write_from_history(line_count):
        l = readline.get_current_history_length()
        lines = []
        for i in range(max(l - line_count, 0), l):
            line = readline.get_history_item(i)
            lines.append(line)
        buf = '\n'.join(lines)
        Clip.put(buf)

    @staticmethod
    def read_to_history():
        code = Clip.compile()
        if code is not None:
            (source, code) = code
            print(source)
            for line in source.split('\n'):
                readline.add_history(line)

    @staticmethod
    def run():
        # Clip.show()
        code = Clip.compile()
        if code is not None:
            (source, code) = code
            print(source)
            exec(code, globals())
        else:
            print('failed to compile')

