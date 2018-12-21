#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

from six.moves import map
from cytoolz.curried import concat
import sys

class Text(object):
    @classmethod
    def groupcomplete(self, it, is_complete):
        """
        is_complete returns true if the argument forms a complete group.
        """
        g = []
        #
        for e in it:
            n = g + [e]
            if is_complete(n):
                yield n
                g = []
            else:
                g = n
        #
        # yield the final incomplete group
        if g:
            yield g

    @classmethod
    def splitter2(self, bufs, eol):
        return map(eol[:0].join, self.groupcomplete(concat(bufs), lambda e: e == eol))

    @classmethod
    def splitter3(self, bufs, eol):
        # converted bytes to ints
        eol_ints = list(concat([eol]))
        cb = concat(bufs)
        is_complete = lambda g: g[-len(eol_ints):] == eol_ints
        gc = Text.groupcomplete(cb, is_complete)
        result = map(bytes, gc)
        return result

    if sys.version_info.major == 2:
        splitter = splitter2

    if sys.version_info.major == 3:
        splitter = splitter3

