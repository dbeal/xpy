
#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

import inspect
import sys
import os

def EA(*args, **kwargs):
    return (args, kwargs)
    
def FL(msg):
    """Format {template} tokens with the caller's locals."""
    result = msg
    frame = inspect.currentframe()
    if frame is not None:
        back = frame.f_back
        d = dict(back.f_globals, **back.f_locals)
        result = msg.format(**d)
    return result

def ls(regex_match_pattern = '.', sort_index = None):
    """list objects in current scope"""
    #
    # sort by indices in order
    #
    if sort_index is None:
        sort_index = (0, 1, 2)
        #
    if type(sort_index) not in (tuple, list):
        sort_index = [sort_index]
    #
    if regex_match_pattern is not None:
        import re
        pat = re.compile(regex_match_pattern)
    else:
        pat = None
    #
    rows = []
    #
    back = inspect.currentframe().f_back
    #
    d = dict(back.f_globals)
    d.update(back.f_locals)
    #
    for (n, o) in d.items():
        row = []
        #
        # source file or module origin
        #
        if hasattr(o, '__module__'):
            filesource = o.__module__
        elif hasattr(o, '__file__'):
            filesource = o.__file__
        else:
            filesource = '<unknown>'
        #
        row.append(filesource)
        #
        # class origin
        #
        row.append(o.__class__.__name__)
        #
        if hasattr(o, '__name__'):
            name = o.__name__
            if name != n:
                n = str(name) + ' as ' + n
        else:
            name = n
        # row.append(o.__name__ if hasattr(o, '__name__'))
        row.append(n)
        #
        rows.append(row)

    raw_rows = rows
    #
    # do sorting first
    #
    rows = sorted(rows, key = lambda row: tuple(row[si].lower() for si in sort_index))
    #
    # do filtering next
    #
    rows = rows_filtered = rows if pat is None else list(filter(lambda row: any(pat.search(c) for c in row), rows))
    #
    # do column padding next
    #
    maxl = None if not rows else [max(len(rows[j][i]) for j in range(len(rows))) for i in range(len(rows[0]))]
    #
    just = column_justification = [(str.rjust, ' '), (str.rjust, ' '), (str.ljust, ' ')]
    #
    rows = justified_rows = [[(just[i][0])(row[i], maxl[i], just[i][1]) for i in range(len(row))] for row in rows]

    os.write(1, (''.join([' '.join(row) + '\n' for row in rows])).encode('utf8'))

    # return raw_rows
        
def lsmod(mod):
    return list(filter(lambda x: isinstance(x, type) and x.__module__ == mod.__name__, mod.__dict__.values()))

def modref():
    #
    # TODO: show module references for types
    #
    backdict = dict(inspect.currentframe().f_back.f_globals)
    #
    #
    for (n, v) in backdict.items():
        if isinstance(v, type):
            pass
            
        

