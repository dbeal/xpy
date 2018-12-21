
#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

import os

class File(object):
    @classmethod
    def streamer(self, fd, chunk):
        while True:
            buf = os.read(fd, chunk)
            if buf:
                yield buf
            else:
                break

