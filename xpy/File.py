
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

