#!/usr/bin/env python3

import sys
from .XPY import *

class Main(object):
    @classmethod
    def main(self):
        x = XPY()
        return x.run(globals())

if __name__ == '__main__':
    sys.exit(Main.main())
